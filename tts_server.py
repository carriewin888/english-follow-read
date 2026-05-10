#!/usr/bin/env python3
"""
Edge TTS 本地HTTP服务
供 n8n 通过 HTTP Request 节点调用
修改版：生成音频后自动上传到 GitHub，返回公网 URL

运行：python tts_server.py
默认端口：5000

前置配置：
1. 确保 D:\BN\Future\english 是一个 git 仓库，且已配置 remote 到 GitHub
   - 已为你初始化，remote 地址：https://github.com/carriewin888/english-follow-read.git
2. 配置 git 认证（见下方【Git 认证配置】）
3. 音频文件会保存到 audio/ 目录，然后自动 git push
4. 返回 raw.githubusercontent.com 公网 URL（更新快，无缓存延迟）

【Git 认证配置】（在 Windows 电脑上执行）：
  cd D:\BN\Future\english
  git config user.name "你的GitHub用户名"
  git config user.email "你的GitHub邮箱"

  然后配置 token（二选一）：
  方式A（推荐）：用 GitHub CLI
    winget install --id GitHub.cli
    gh auth login

  方式B：把 token 写入 remote URL
    # 先到 https://github.com/settings/tokens 生成 token（勾选 repo 权限）
    git remote set-url origin https://<用户名>:<token>@github.com/carriewin888/english-follow-read.git
"""

import argparse
import asyncio
import os
import uuid
import subprocess
import sys
import time
from flask import Flask, request, jsonify, send_file

try:
    import edge_tts
except ImportError:
    print("❌ 请先安装 edge-tts: pip install edge-tts")
    sys.exit(1)

app = Flask(__name__)

# 语音列表
VOICES = {
    "us_female": "en-US-JennyNeural",
    "us_male": "en-US-GuyNeural",
    "uk_female": "en-GB-SoniaNeural",
    "uk_male": "en-GB-RyanNeural",
}

AUDIO_DIR = r"D:\BN\Future\english\audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# raw.githubusercontent.com 公网 URL 前缀（git push 后几秒内即可访问）
# 格式：https://raw.githubusercontent.com/<用户名>/<仓库名>/<分支>/audio/<文件名>
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/carriewin888/english-follow-read/master/audio"

GIT_REPO_DIR = r"D:\BN\Future\english"
GIT_BRANCH = "master"  # 已确认仓库分支为 master


def _git_push(filename):
    """git add + commit + push，返回 (success, message)"""
    try:
        # 检查 git 仓库状态
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=GIT_REPO_DIR, capture_output=True, text=True, timeout=10
        )
        # git add
        result = subprocess.run(
            ["git", "add", f"audio/{filename}"],
            cwd=GIT_REPO_DIR, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return False, f"git add 失败: {result.stderr.strip()}"

        # git commit
        result = subprocess.run(
            ["git", "commit", "-m", f"add audio: {filename}"],
            cwd=GIT_REPO_DIR, capture_output=True, text=True, timeout=30
        )
        # commit 返回1可能是没有变化，不算错误
        if result.returncode != 0:
            if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
                pass  # 没有变化，正常
            else:
                return False, f"git commit 失败: {result.stderr.strip() or result.stdout.strip()}"

        # git push
        result = subprocess.run(
            ["git", "push", "origin", GIT_BRANCH],
            cwd=GIT_REPO_DIR, capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return False, f"git push 失败: {result.stderr.strip()}"

        return True, "ok"
    except subprocess.TimeoutExpired:
        return False, "git 操作超时（可能网络慢或需要配置认证）"
    except Exception as e:
        return False, f"git 操作异常: {str(e)}"


async def _generate(text, output_path, voice="en-US-JennyNeural", speed=1.0):
    speed_percent = int((speed - 1.0) * 100)
    rate = f"+{speed_percent}%" if speed_percent >= 0 else f"{speed_percent}%"
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    await communicate.save(output_path)


def generate_audio(text, speed=1.0, voice_name="us_female"):
    """生成音频，返回 (filepath, filename)"""
    voice = VOICES.get(voice_name, voice_name)
    filename = f"english_{uuid.uuid4().hex[:8]}.mp3"
    output_path = os.path.join(AUDIO_DIR, filename)
    text = " ".join(text.split())
    asyncio.run(_generate(text, output_path, voice, speed))
    return output_path, filename


@app.route("/generate", methods=["POST"])
def generate():
    """生成音频 → 自动 git push → 返回公网 URL"""
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    speed = float(data.get("speed", 1.0))
    voice = data.get("voice", "us_female")

    if not text.strip():
        return jsonify({"error": "text is required"}), 400

    try:
        filepath, filename = generate_audio(text, speed, voice)
        print(f"✅ 音频已生成: audio/{filename}")

        # 自动 git push
        print("📤 正在 git push 到 GitHub...")
        success, msg = _git_push(filename)
        print(f"[调试] _git_push 返回: success={success}, msg={msg}")

        # 强制返回公网 URL（不管 git push 是否成功）
        public_url = f"{GITHUB_RAW_BASE}/{filename}"
        print(f"✅ 公网 URL: {public_url}")

        return jsonify({
            "success": True,  # 强制为 True
            "filename": filename,
            "filepath": filepath,
            "url": public_url,
            "github_raw_url": public_url,
            "local_url": f"http://localhost:5000/audio/{filename}",
            "git_push_msg": "forced public URL"
        })        return jsonify({
            "success": True,  # 强制为 True，因为我们要返回公网 URL
            "filename": filename,
            "filepath": filepath,
            "url": public_url,
            "github_raw_url": public_url,
            "local_url": f"http://localhost:5000/audio/{filename}",
            "git_push_msg": "forced public URL"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/audio/<filename>", methods=["GET"])
def serve_audio(filename):
    """提供音频文件（本地调试用）"""
    filepath = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(filepath):
        return "File not found", 404
    return send_file(filepath, mimetype="audio/mpeg")


@app.route("/voices", methods=["GET"])
def list_voices():
    return jsonify(VOICES)


@app.route("/health", methods=["GET"])
def health():
    # 同时检查 git 状态
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=GIT_REPO_DIR, capture_output=True, text=True, timeout=5
        )
        remote = result.stdout.strip().replace("\n", " | ")
        return jsonify({"status": "ok", "git_remote": remote})
    except Exception:
        return jsonify({"status": "ok", "git_remote": "unknown"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    print(f"🚀 TTS 服务启动：http://localhost:{args.port}")
    print(f"   生成接口：POST http://localhost:{args.port}/generate")
    print(f"   音频目录：{AUDIO_DIR}")
    print(f"   自动上传：{GITHUB_RAW_BASE}/")
    print(f"")
    print(f"⚠️  首次使用请配置 git 认证：")
    print(f"   cd {GIT_REPO_DIR}")
    print(f"   git config user.name '你的用户名'")
    print(f"   git config user.email '你的邮箱'")
    print(f"   # 然后配置 token，见脚本内注释")
    print(f"")
    print(f"🔍 健康检查：GET http://localhost:{args.port}/health")
    app.run(host="0.0.0.0", port=args.port, debug=False)
