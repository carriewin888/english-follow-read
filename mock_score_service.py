"""
本地模拟评分服务（替代 hf_score_service.py）
无需 whisper/ffmpeg，直接返回模拟分数，方便本地测试完整流程

运行：
  venv\Scripts\activate
  python mock_score_service.py
默认端口：8000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)


@app.route("/score", methods=["POST"])
def mock_score():
    """模拟打分，返回随机分数（75~95之间）"""
    rounds = int(request.form.get("rounds", 3))
    type_name = request.form.get("type", "text")

    # 模拟分数：遍数越多分数越高
    base = 70 + rounds * 5
    clarity = min(95, base + random.randint(-10, 10))
    accuracy = min(95, base + random.randint(-10, 10))
    completeness = min(100, base + random.randint(-5, 15))
    rounds_score = min(100, rounds * 33)
    total = int((clarity + accuracy + completeness + rounds_score) / 4)

    return jsonify({
        "clarity": clarity,
        "accuracy": accuracy,
        "completeness": completeness,
        "rounds": rounds_score,
        "total": total,
        "recognized": "模拟识别文本（本地测试模式）"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "mode": "mock"})


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "模拟评分服务（本地测试用）",
        "note": "如需真实打分，请使用 hf_score_service.py"
    })


if __name__ == "__main__":
    print("🧪 模拟评分服务启动：http://localhost:8000")
    print("   POST /score  → 返回模拟分数")
    print("   GET  /health → 健康检查")
    print("⚠️  这是测试用模拟服务，真实打分请使用 hf_score_service.py")
    app.run(host="0.0.0.0", port=8000, debug=False)
