"""
Hugging Face Spaces 评分服务 v3
接收录音 → Whisper 识别 → 打分 → 返回结果
使用 subprocess 调用 ffmpeg，不依赖 pydub
"""

import tempfile
import os
import subprocess
import whisper
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="英语跟读评分服务")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载 Whisper 模型
print("📥 正在加载 Whisper 模型（请稍候）...")
model = whisper.load_model("base")
print("✅ Whisper 模型加载完成！")


def convert_to_wav(input_path: str, output_path: str) -> bool:
    """用 ffmpeg 将音频转换为 16kHz 单声道 WAV"""
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-acodec", "pcm_s16le",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    except Exception as e:
        print(f"ffmpeg 转换失败: {e}")
        return False


def calculate_scores(original_text: str, recognized_text: str, rounds: int) -> dict:
    """
    计算四个维度的分数（0-100）
    核心原则：读得差 → 低分；没读 → 极低分
    """
    orig_text = original_text.strip()
    recog_text = recognized_text.strip()

    # ===== 情况1：识别文本为空或极短 → 极低分 =====
    if not recog_text or len(recog_text) < 3:
        rounds_score = min(100, rounds * 33)
        return {
            "clarity": 5,
            "accuracy": 0,
            "completeness": 0,
            "rounds": rounds_score,
            "total": 5,
            "recognized": recog_text
        }

    # 提取词集合（去除标点）
    orig_words = set(w.lower().strip(".,!?;:") for w in orig_text.split() if w)
    recog_words = set(w.lower().strip(".,!?;:") for w in recog_text.split() if w)

    # ===== 发音准确性：识别词与原文词的重叠率 =====
    if orig_words and recog_words:
        overlap = len(orig_words & recog_words)
        accuracy = int(overlap / len(orig_words) * 100)
    elif orig_words:
        accuracy = 0
    else:
        accuracy = 50
    accuracy = max(0, min(100, accuracy))

    # ===== 朗读完整性：识别文本长度 / 原文长度 =====
    if len(orig_text) > 0:
        length_ratio = len(recog_text) / len(orig_text)
        completeness = int(min(1.0, max(0, length_ratio)) * 100)
    else:
        completeness = 50
    completeness = max(0, min(100, completeness))

    # ===== 清晰度：结合准确性和完整性 =====
    clarity = int(accuracy * 0.6 + completeness * 0.4)
    clarity = max(0, min(100, clarity))

    # ===== 完成遍数 =====
    rounds_score = min(100, rounds * 33)

    # ===== 总分 =====
    raw_total = int(clarity * 0.2 + accuracy * 0.35 + completeness * 0.25 + rounds_score * 0.2)

    # 惩罚：准确性极低时，总分打对折
    if accuracy < 30:
        raw_total = int(raw_total * 0.5)

    total = max(0, min(100, raw_total))

    return {
        "clarity": clarity,
        "accuracy": accuracy,
        "completeness": completeness,
        "rounds": rounds_score,
        "total": total,
        "recognized": recog_text
    }


@app.post("/score")
async def score_audio(
    audios: list[UploadFile] = File(...),
    original_text: str = Form(...),
    type: str = Form(...),
    rounds: int = Form(...)
):
    """接收录音文件，进行评分"""
    all_text = []

    for audio_file in audios:
        contents = await audio_file.read()

        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        wav_path = tmp_path + ".wav"

        try:
            if convert_to_wav(tmp_path, wav_path):
                result = model.transcribe(wav_path, language="en")
                all_text.append(result["text"])
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            if os.path.exists(wav_path):
                os.unlink(wav_path)

    recognized_text = " ".join(all_text)

    # 如果所有遍次都识别失败，直接返回极低分
    if not recognized_text.strip():
        return JSONResponse(content={
            "clarity": 5,
            "accuracy": 0,
            "completeness": 0,
            "rounds": min(100, rounds * 33),
            "total": 5,
            "recognized": ""
        }, status_code=200)

    scores = calculate_scores(original_text, recognized_text, rounds)
    return JSONResponse(content=scores, status_code=200)


@app.get("/health")
async def health():
    return {"status": "ok", "model": "whisper-base"}


@app.get("/")
async def root():
    return {"service": "英语跟读评分服务", "version": "3.0", "endpoints": ["/score", "/health"]}
