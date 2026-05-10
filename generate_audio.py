#!/usr/bin/env python3
"""
Edge TTS 音频生成脚本
用法：python generate_audio.py --text "文本内容" --speed 1.0 --output "输出路径.mp3"
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime

try:
    import edge_tts
except ImportError:
    print("❌ 请先安装 edge-tts: pip install edge-tts")
    sys.exit(1)

# 推荐的英语语音列表
VOICE_LIST = {
    "us_female": "en-US-JennyNeural",      # 美式女声，清晰自然
    "us_male": "en-US-GuyNeural",          # 美式男声
    "uk_female": "en-GB-SoniaNeural",      # 英式女声
    "uk_male": "en-GB-RyanNeural",         # 英式男声
    "au_female": "en-AU-NatashaNeural",    # 澳式女声
    "au_male": "en-AU-WilliamNeural",      # 澳式男声
}

async def generate_audio(text, output_path, voice="en-US-JennyNeural", speed=1.0):
    """
    生成音频文件
    
    Args:
        text: 要合成的文本
        output_path: 输出文件路径
        voice: 语音名称
        speed: 语速 (0.6-1.2, 1.0为正常速度)
    """
    # 将速度转换为 SSML 格式
    # edge-tts 使用百分比：+10% 表示1.1倍速，-10% 表示0.9倍速
    speed_percent = int((speed - 1.0) * 100)
    if speed_percent >= 0:
        rate = f"+{speed_percent}%"
    else:
        rate = f"{speed_percent}%"
    
    print(f"🎙️ 正在生成音频...")
    print(f"   语音: {voice}")
    print(f"   语速: {speed}x ({rate})")
    print(f"   文本长度: {len(text)} 字符")
    
    # 创建 communicator
    communicate = edge_tts.Communicate(
        text, 
        voice=voice,
        rate=rate
    )
    
    # 保存音频
    await communicate.save(output_path)
    
    # 获取文件大小
    file_size = os.path.getsize(output_path) / 1024  # KB
    print(f"✅ 音频生成成功！")
    print(f"   文件路径: {output_path}")
    print(f"   文件大小: {file_size:.1f} KB")
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Edge TTS 英语音频生成工具")
    parser.add_argument("--text", type=str, help="要合成的文本")
    parser.add_argument("--file", type=str, help="从文件读取文本")
    parser.add_argument("--output", type=str, help="输出文件路径（.mp3）")
    parser.add_argument("--voice", type=str, default="en-US-JennyNeural",
                        help=f"语音名称。可选：{', '.join(VOICE_LIST.keys())}")
    parser.add_argument("--speed", type=float, default=1.0,
                        help="语速 (0.6-1.2, 默认1.0)")
    parser.add_argument("--list-voices", action="store_true",
                        help="列出所有可用的英语语音")
    
    args = parser.parse_args()
    
    # 列出语音
    if args.list_voices:
        print("📢 可用的英语语音：")
        for key, value in VOICE_LIST.items():
            print(f"  {key:15} -> {value}")
        return
    
    # 读取文本
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ 文件不存在: {args.file}")
            sys.exit(1)
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        # 从标准输入读取
        print("请输入要合成的文本（Ctrl+D结束）：")
        text = sys.stdin.read()
    
    if not text or not text.strip():
        print("❌ 文本不能为空！")
        sys.exit(1)
    
    # 清理文本（移除过多的换行）
    text = " ".join(text.split())
    
    # 确定输出路径
    if args.output:
        output_path = args.output
    else:
        # 默认保存到 D:\BN\Future\english\audio\
        audio_dir = r"D:\BN\Future\english\audio"
        os.makedirs(audio_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(audio_dir, f"english_{timestamp}.mp3")
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 验证语速范围
    if args.speed < 0.5 or args.speed > 2.0:
        print(f"⚠️  警告：语速 {args.speed} 可能不合适，建议使用 0.6-1.2")
    
    # 处理语音名称（支持别名）
    voice = VOICE_LIST.get(args.voice, args.voice)
    
    # 异步生成音频
    asyncio.run(generate_audio(text, output_path, voice, args.speed))
    
    # 输出文件路径（供n8n读取）
    print(f"\nOUTPUT_FILE:{output_path}")

if __name__ == "__main__":
    main()
