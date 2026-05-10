from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import librosa
import io

app = FastAPI()

# 允许跨域（重要！否则前端无法调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "English Follow Read Scoring Service"}

@app.post("/score")
async def score_audio(
    audio: UploadFile = File(...),
    reference_text: str = None
):
    """
    评分接口
    - audio: 上传的音频文件
    - reference_text: 参考文本（可选）
    """
    try:
        # 读取音频文件
        audio_data = await audio.read()
        audio_file = io.BytesIO(audio_data)
        
        # 使用 librosa 加载音频
        y, sr = librosa.load(audio_file, sr=16000)
        
        # 简单的音频特征提取（示例）
        # 实际生产环境应该用语音识别API（如 Google ASR、Azure Speech）
        duration = librosa.get_duration(y=y, sr=sr)
        rms = librosa.feature.rms(y=y).mean()
        
        # 模拟评分逻辑（0-100分）
        # 这里应该接入真实的 ASR 服务进行发音评分
        score = min(95, max(60, 70 + rms * 100))  # 示例评分
        
        return {
            "score": round(score, 1),
            "duration": round(duration, 2),
            "feedback": "发音不错！继续努力！" if score > 80 else "需要多练习哦！"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评分失败: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
