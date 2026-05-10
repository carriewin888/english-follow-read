# 英语跟读评分系统 - 详细技术报告

**版本**: v3.0  
**更新日期**: 2026-05-09  
**作者**: AI英语伴学Agent  

---

## 目录

1. [系统概述](#1-系统概述)
2. [文件结构](#2-文件结构)
3. [功能模块详解](#3-功能模块详解)
4. [技术架构](#4-技术架构)
5. [操作步骤](#5-操作步骤)
6. [使用说明](#6-使用说明)
7. [API接口文档](#7-api接口文档)
8. [评分算法详解](#8-评分算法详解)
9. [部署指南](#9-部署指南)
10. [故障排查](#10-故障排查)

---

## 1. 系统概述

本系统是一套完整的**英语跟读评分与测试平台**，专为中国初二学生设计，集成了：

- **跟读评分**：基于 Whisper 语音识别的发音评分系统
- **趣味测试**：支持听音选义、听音拼写、句型填空、语法问答四种题型
- **音频生成**：基于 Edge TTS 的英语语音合成
- **AI聊天**：接入 DeepSeek API 的英语对话练习

系统支持通过微信公众号推送每日学习内容，用户点击即可进入跟读练习。

### 核心特性

| 特性 | 说明 |
|------|------|
| 🎙️ 语音识别 | 使用 OpenAI Whisper 模型，英文识别准确率 85-90% |
| 📊 多维度评分 | 清晰度、准确性、完整性、完成遍数四个维度 |
| 🌐 跨平台 | 支持微信内置浏览器、PC浏览器、移动端浏览器 |
| 🔊 语音合成 | 支持美式/英式/澳式多种英语发音 |
| 🤖 AI对话 | 三种聊天模式（中英双语/全英文/自由聊） |
| 📱 响应式设计 | 移动端优先的 UI 设计 |

---

## 2. 文件结构

```
D:\BN\future\english\
├── 核心服务文件
│   ├── hf_score_service.py      # 跟读评分服务（Whisper后端，FastAPI）
│   ├── mock_score_service.py    # 模拟评分服务（测试用，Flask）
│   ├── generate_audio.py        # Edge TTS 音频生成脚本
│   └── start_score_server.bat  # Windows 一键启动评分服务
│
├── 前端页面
│   ├── follow_read.html        # 跟读练习页面（录音+打分）
│   ├── quiz.html               # 答题测试页面（四种题型）
│   ├── chat.html               # AI聊天页面（英语对话练习）
│   ├── test-entry.html         # 测试入口页面
│   └── quiz-url-generator.html # 测试链接生成器（工具）
│
├── 配置与文档
│   ├── requirements.txt        # Python 依赖清单
│   ├── hf_Dockerfile          # HuggingFace 部署配置
│   ├── deploy-guide.md        # 完整部署指南
│   ├── quiz-guide.md          # 测试功能说明
│   ├── checklist.md           # 开发检查清单
│   ├── english-tutor-agent-v2.json      # n8n 工作流配置
│   └── english-tutor-agent-workflow.json # 工作流备份
│
├── 数据文件
│   ├── sample-quiz.json       # 测试题目示例数据
│   └── audio/                 # 生成的音频文件目录
│       ├── english_41563f74.mp3
│       ├── english_49ef8689.mp3
│       └── ...
│
└── 工具
    └── ffmpeg-master-latest-win64-gpl/  # FFmpeg 工具集
        └── bin/
            ├── ffmpeg.exe     # 音频格式转换工具
            ├── ffplay.exe     # 音频播放工具
            └── ffprobe.exe    # 音频信息分析工具
```

### 关键文件说明

| 文件 | 大小 | 作用 | 访问方式 |
|------|------|------|----------|
| `hf_score_service.py` | ~4KB | 评分后端服务 | 后端 API |
| `follow_read.html` | ~9KB | 跟读前端页面 | 浏览器直接打开 |
| `quiz.html` | ~12KB | 答题前端页面 | 浏览器直接打开 |
| `chat.html` | ~7KB | AI聊天页面 | 浏览器直接打开 |
| `generate_audio.py` | ~4KB | 音频生成脚本 | 命令行调用 |

---

## 3. 功能模块详解

### 3.1 跟读评分模块

#### 功能流程

```
用户打开跟读页面
    ↓
显示今日学习内容（课文/词汇/句型）
    ↓
用户点击"跟读"按钮 → 开始录音（共3遍）
    ↓
每遍录音完成后可回听
    ↓
3遍完成后点击"提交打分"
    ↓
音频上传到 hf_score_service → Whisper 识别 → 计算分数
    ↓
返回四个维度分数 + 总分 → 前端展示
    ↓
可选：进入答题测试
```

#### 跟读页面功能

- **课文跟读**：跟读完整的英文课文
- **词汇跟读**：跟读重点词汇（显示音标和释义）
- **句型跟读**：跟读重点句型
- **录音回听**：每遍录音完成后显示播放条，可回听
- **重新跟读**：打分完成后可重置，重新录制

#### 页面元素

| 元素 | 说明 |
|------|------|
| 课文原文区 | 显示英文原文，背景高亮 |
| 重点词汇区 | 显示单词、音标、中文释义 |
| 重点句型区 | 显示重点句型 |
| 跟读按钮 | 每个模块独立按钮，显示当前遍数（第1/3遍） |
| 回放下拉 | 每遍录音完成后显示播放条 |
| 提交按钮 | 3遍完成后出现 |
| 打分卡片 | 显示四个维度分数和总分（渐变紫色卡片） |

### 3.2 答题测试模块

#### 支持的题型

| 题型 | 类型标识 | 说明 | 交互方式 |
|------|----------|------|----------|
| 听音选义 | `listen_choice` | 听单词发音，选择中文意思 | 点击选项 |
| 听音拼写 | `listen_spell` | 听单词发音，拼写英文 | 输入文本框 |
| 句型填空 | `sentence_blank` | 选择合适词汇填入句子空白 | 点击选项 |
| 语法问答 | `grammar_choice` | 选择语法正确的句子 | 点击选项 |

#### 答题页面功能

- **倒计时器**：默认10分钟（600秒），最后60秒变红警告
- **进度显示**：第 X 题 / 共 Y 题
- **上一题按钮**：可返回修改已答题目
- **多种题型**：自动根据题型渲染不同交互界面
- **单词发音**：点击单词可播放英语发音（Web Speech API）
- **提交确认**：最后一题点击后提交，显示成绩
- **成绩展示**：显示分数、等级评价、错题回顾

#### 答题状态管理

```javascript
// 答案存储格式
answers = [
  undefined,        // 第1题未答
  2,                // 第2题选了选项C（index=2）
  "banana",         // 第3题拼写了"banana"
  undefined,        // 第4题未答（提交后判错）
  0                 // 第5题选了选项A
]
```

### 3.3 音频生成模块

#### 功能说明

使用 Microsoft Edge TTS 服务生成高质量的英语语音，无需 API Key，完全免费。

#### 支持的语音

| 别名 | 语音名称 | 说明 |
|------|----------|------|
| `us_female` | `en-US-JennyNeural` | 美式女声（推荐，清晰自然） |
| `us_male` | `en-US-GuyNeural` | 美式男声 |
| `uk_female` | `en-GB-SoniaNeural` | 英式女声 |
| `uk_male` | `en-GB-RyanNeural` | 英式男声 |
| `au_female` | `en-AU-NatashaNeural` | 澳式女声 |
| `au_male` | `en-AU-WilliamNeural` | 澳式男声 |

#### 使用方法

```bash
# 生成音频（从命令行输入文本）
python generate_audio.py --text "Hello, world!" --voice us_female --speed 1.0 --output "output.mp3"

# 从文件读取文本
python generate_audio.py --file "text.txt" --voice us_female

# 列出所有可用语音
python generate_audio.py --list-voices
```

### 3.4 AI聊天模块

#### 聊天模式

| 模式 | 标识 | 说明 |
|------|------|------|
| 中英双语 | `bilingual` | AI用英文回复，复杂地方用中文解释 |
| 全英文 | `english` | AI只用英文回复（CEFR A2-B1水平） |
| 自由聊 | `free` | 中英文混合，AI引导并纠正错误 |

#### 功能特性

- **实时对话**：基于 DeepSeek API 的流式对话
- **语音播放**：AI回复可点击播放发音
- **模式切换**：随时切换聊天模式
- **对话历史**：保留当前会话的对话历史
- **自动朗读**：AI回复后自动朗读英文部分

---

## 4. 技术架构

### 4.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                       用户端（微信/浏览器）                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ follow_read │  │   quiz.html │  │   chat.html │      │
│  │   .html     │  │             │  │             │      │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │
│         │                  │                  │                │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          │                  │                  │  DeepSeek API
          │                  │                  └──────────────→
          │                  │
          │    ┌─────────────┴─────────────┐
          │    │      hf_score_service       │
          │    │   （FastAPI + Whisper）    │
          │    │   端口：8000               │
          │    └─────────────┬─────────────┘
          │                  │
          └──────────────────┘
                     │
        ┌────────────┴────────────┐
        │                          │
        ▼                          ▼
  Whisper 模型              FFmpeg（音频转换）
  (base, ~140MB)           (webm → wav)
```

### 4.2 技术栈

#### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 后端开发语言 |
| FastAPI | 0.104.1 | Web 框架 |
| Uvicorn | 0.24.0 | ASGI 服务器 |
| OpenAI Whisper | 20250625 | 语音识别模型 |
| FFmpeg | - | 音频格式转换 |
| Edge TTS | latest | 语音合成 |

#### 前端

| 技术 | 用途 |
|------|------|
| HTML5 | 页面结构 |
| CSS3 | 样式（渐变、动画、响应式） |
| JavaScript (Vanilla) | 交互逻辑 |
| MediaRecorder API | 录音功能 |
| Web Speech API | 语音播放 |
| Fetch API | 后端通信 |

---

## 5. 操作步骤

### 5.1 本地开发环境搭建

#### 步骤1：创建虚拟环境

```powershell
cd D:\BN\future\english
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1
```

#### 步骤2：安装依赖

```powershell
pip install -r requirements.txt
```

**requirements.txt 内容**：
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
openai-whisper==20250625
python-multipart==0.0.6
edge-tts  # 音频生成需要
```

#### 步骤3：启动评分服务

**方法一**：双击运行（推荐）
```
double-click: start_score_server.bat
```

**方法二**：命令行启动
```powershell
cd D:\BN\future\english
.\venv\Scripts\Activate.ps1
python -m uvicorn hf_score_service:app --host 0.0.0.0 --port 8000 --reload
```

> ⚠️ **首次启动会下载 Whisper base 模型（约140MB），请耐心等待（约1-3分钟）**

#### 步骤4：验证服务

打开浏览器访问：
- 评分服务：`http://localhost:8000/health`
- 期望返回：`{"status":"ok","model":"whisper-base"}`

### 5.2 跟读功能测试

#### 步骤1：配置 API 地址

编辑 `follow_read.html`，找到：
```javascript
const API_BASE = "http://localhost:8000";
```

如果需要局域网其他设备访问，改为你的 IP：
```javascript
const API_BASE = "http://192.168.2.49:8000";
```

#### 步骤2：准备测试数据

在浏览器中打开 `follow_read.html`，并通过 URL 参数传入内容：

```
follow_read.html?title=测试课文&text=Hello, this is a test.&vocab=hello|/həˈləʊ/|你好&patterns=How are you?
```

**参数说明**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `title` | 课文标题 | `Unit 1 Lesson 1` |
| `date` | 日期 | `2026-05-09` |
| `text` | 课文原文 | `Hello, this is...` |
| `vocab` | 词汇列表 | `word\|phonetic\|meaning\|word2\|...` |
| `patterns` | 重点句型 | `How are you?\|I am fine.` |
| `quiz_url` | 测试链接 | `quiz.html?quiz=...` |

#### 步骤3：开始跟读

1. 点击「🎙️ 跟读课文（第 1/3 遍）」
2. 允许浏览器访问麦克风
3. 朗读课文内容
4. 点击「⏹️ 点击停止」
5. 可回听第1遍录音
6. 重复以上步骤完成第2遍、第3遍
7. 3遍完成后点击「📤 提交打分」
8. 查看打分结果

### 5.3 答题功能测试

#### 步骤1：准备题目数据

创建 JSON 格式的题库文件（参考 `sample-quiz.json`）：

```json
{
  "title": "英语趣味测试",
  "date": "2026-05-09",
  "time_limit": 600,
  "questions": [
    {
      "type": "listen_choice",
      "word": "apple",
      "options": ["苹果", "香蕉", "橙子", "葡萄"],
      "answer": 0
    },
    {
      "type": "listen_spell",
      "word": "banana",
      "answer": "banana",
      "hint": "提示：一种黄色的水果"
    }
  ]
}
```

#### 步骤2：生成测试链接

**方法一**：使用 Quiz URL 生成器

1. 在浏览器中打开 `quiz-url-generator.html`
2. 粘贴 JSON 数据到文本框
3. 点击「🔗 生成测试链接」
4. 复制生成的链接

**方法二**：手动编码

```javascript
// 1. 将 JSON 转为 Base64
const jsonStr = JSON.stringify(quizData);
const base64 = btoa(unescape(encodeURIComponent(jsonStr)));

// 2. 生成 URL
const url = `quiz.html?quiz=${encodeURIComponent(base64)}`;
```

#### 步骤3：答题

1. 打开生成的测试链接
2. 点击「🚀 开始挑战」
3. 倒计时开始（默认10分钟）
4. 逐题作答
5. 可点击「← 上一题」返回修改
6. 最后一题点击「📊 提交测试」
7. 查看成绩

---

## 6. 使用说明

### 6.1 跟读页面使用说明

#### 页面布局

```
┌─────────────────────────────────┐
│  📖 英语跟读练习               │  ← 标题
│  2026-05-09                    │  ← 日期
├─────────────────────────────────┤
│  📝 课文原文                   │
│  ┌───────────────────────────┐  │
│  │ (课文内容)                │  │  ← 课文原文区
│  └───────────────────────────┘  │
│  [🎙️ 跟读课文（第 1/3 遍）]   │  ← 跟读按钮
│  ┌───────────────────────────┐  │
│  │ 🔊 第1遍  [播放条]       │  │  ← 回放区
│  └───────────────────────────┘  │
├─────────────────────────────────┤
│  📚 重点词汇                   │
│  hello  /həˈləʊ/  你好         │  ← 词汇区
│  world  /wɜːld/  世界          │
│  [🎙️ 跟读词汇（第 1/3 遍）]   │
├─────────────────────────────────┤
│  🔑 重点句型                   │
│  How are you?                  │  ← 句型区
│  [🎙️ 跟读句型（第 1/3 遍）]   │
├─────────────────────────────────┤
│  [📤 提交打分]                 │  ← 提交按钮（3遍后显示）
├─────────────────────────────────┤
│  ┌─────────────────────────┐    │
│  │  本次跟读得分            │    │  ← 打分结果卡片
│  │     85 分               │    │
│  │ 清晰度        80分      │    │
│  │ 发音准确性    90分      │    │
│  │ 朗读完整性    85分      │    │
│  │ 完成遍数      100分     │    │
│  │ [🔄 重新跟读]           │    │
│  │ [🎮 开始测试挑战]       │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
```

#### 注意事项

1. **麦克风权限**：首次使用需允许浏览器访问麦克风
2. **录音遍数**：每个模块需录音3遍才能提交
3. **网络要求**：评分需要访问后端 API（ Whisper 识别）
4. **浏览器兼容**：推荐使用 Chrome/Edge 浏览器

### 6.2 答题页面使用说明

#### 题型详解

**1. 听音选义（listen_choice）**

```
┌─────────────────────────────────┐
│  🔊 苹果  (点击可播放发音)     │  ← 单词显示区（点击播放）
│  请听发音，选择正确的中文意思：  │
│  ┌───────────────────────────┐  │
│  │ 苹果  (正确选项，绿色)     │  │  ← 选项按钮
│  │ 香蕉  (错误答案，红色)     │  │
│  │ 橙子                      │  │  (未选，灰色)
│  │ 葡萄                      │  │
│  └───────────────────────────┘  │
│  [← 上一题]  [确认答案]        │  ← 导航按钮
└─────────────────────────────────┘
```

**2. 听音拼写（listen_spell）**

```
┌─────────────────────────────────┐
│  [🔊 点击播放发音]             │  ← 播放按钮
│  请听发音，拼写正确的英文单词：  │
│  ┌───────────────────────────┐  │
│  │ banana                   │  │  ← 输入框
│  └───────────────────────────┘  │
│  提示：一种黄色的水果           │  ← 提示信息
│  [← 上一题]  [确认答案]        │
└─────────────────────────────────┘
```

**3. 句型填空（sentence_blank）**

```
┌─────────────────────────────────┐
│  请选择合适的词填入空白处：      │
│  ┌───────────────────────────┐  │
│  │ I [_____] to school.     │  │  ← 句子显示（空白）
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ go    (正确选项)           │  │  ← 选项按钮
│  │ goes                      │  │
│  │ going                     │  │
│  │ went                      │  │
│  └───────────────────────────┘  │
│  [← 上一题]  [确认答案]        │
└─────────────────────────────────┘
```

**4. 语法问答（grammar_choice）**

```
┌─────────────────────────────────┐
│  Choose the correct sentence:    │  ← 问题
│  ┌───────────────────────────┐  │
│  │ He don't like it.  (错)   │  │  ← 选项按钮
│  │ He doesn't like it. (对)   │  │
│  │ He not like it.  (错)     │  │
│  └───────────────────────────┘  │
│  [← 上一题]  [确认答案]        │
└─────────────────────────────────┘
```

#### 答题规则

1. **时间限制**：默认10分钟，最后60秒倒计时变红
2. **空题处理**：未答题提交后判为错误
3. **返回修改**：提交前可随时返回修改已答题目
4. **提交后**：显示正确答案，禁止修改

#### 成绩等级

| 分数范围 | 等级 | 评价 |
|----------|------|------|
| 90-100 | ⭐ | 太棒了！你是英语小天才！ |
| 70-89 | 👍 | 不错哦！继续加油！ |
| 60-69 | 💪 | 再加把劲，你可以的！ |
| 0-59 | 📖 | 多多练习，下次一定更好！ |

---

## 7. API接口文档

### 7.1 跟读评分 API

#### 接口信息

- **路径**：`/score`
- **方法**：`POST`
- **Content-Type**：`multipart/form-data`

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `audios` | File[] | 是 | 录音文件数组（支持多个遍次） |
| `original_text` | String | 是 | 原文文本 |
| `type` | String | 是 | 跟读类型（`text`/`vocab`/`pattern`） |
| `rounds` | Integer | 是 | 完成遍数（1-3） |

#### 请求示例

```javascript
const formData = new FormData();
formData.append("audios", audioBlob1, "round_1.webm");
formData.append("audios", audioBlob2, "round_2.webm");
formData.append("audios", audioBlob3, "round_3.webm");
formData.append("original_text", "Hello, world!");
formData.append("type", "text");
formData.append("rounds", "3");

fetch("http://localhost:8000/score", {
  method: "POST",
  body: formData
})
.then(resp => resp.json())
.then(result => console.log(result));
```

#### 响应格式

```json
{
  "clarity": 80,
  "accuracy": 90,
  "completeness": 85,
  "rounds": 100,
  "total": 87,
  "recognized": "Hello, world!"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `clarity` | Integer | 清晰度得分（0-100） |
| `accuracy` | Integer | 发音准确性得分（0-100） |
| `completeness` | Integer | 朗读完整性得分（0-100） |
| `rounds` | Integer | 完成遍数得分（0-100） |
| `total` | Integer | 总分（0-100） |
| `recognized` | String | Whisper 识别的文本 |

#### 其他接口

**健康检查**

```
GET /health

响应：
{
  "status": "ok",
  "model": "whisper-base"
}
```

**根路径**

```
GET /

响应：
{
  "service": "英语跟读评分服务",
  "version": "3.0",
  "endpoints": ["/score", "/health"]
}
```

### 7.2 音频生成 API（可选）

如果使用 `tts_server.py`（Edge TTS 服务）：

**生成音频**

```
POST /generate
Content-Type: application/json

{
  "text": "Hello, world!",
  "speed": 1.0,
  "voice": "en-US-JennyNeural"
}

响应：
{
  "status": "ok",
  "url": "http://localhost:5000/audio/english_xxx.mp3"
}
```

---

## 8. 评分算法详解

### 8.1 评分维度

#### 1. 发音准确性（Accuracy）- 权重 35%

**计算方式**：
```python
# 提取词集合（去除标点）
orig_words = set(w.lower().strip(".,!?;:") for w in original_text.split())
recog_words = set(w.lower().strip(".,!?;:") for w in recognized_text.split())

# 计算重叠率
overlap = len(orig_words & recog_words)
accuracy = int(overlap / len(orig_words) * 100)
```

**示例**：
- 原文：`"Hello, world! How are you?"`
- 识别：`"Hello world How are you"`
- 重叠词：5个（hello, world, how, are, you）
- 准确性：`5/5 * 100 = 100分`

#### 2. 朗读完整性（Completeness）- 权重 25%

**计算方式**：
```python
length_ratio = len(recognized_text) / len(original_text)
completeness = int(min(1.0, max(0, length_ratio)) * 100)
```

**示例**：
- 原文长度：25字符
- 识别长度：20字符
- 完整性：`20/25 * 100 = 80分`

#### 3. 清晰度（Clarity）- 权重 20%

**计算方式**：
```python
clarity = int(accuracy * 0.6 + completeness * 0.4)
```

综合考虑准确性和完整性。

#### 4. 完成遍数（Rounds）- 权重 20%

**计算方式**：
```python
rounds_score = min(100, rounds * 33)
```

| 遍数 | 得分 |
|------|------|
| 1遍 | 33分 |
| 2遍 | 66分 |
| 3遍 | 100分 |

### 8.2 总分计算

```python
raw_total = int(
    clarity * 0.2 + 
    accuracy * 0.35 + 
    completeness * 0.25 + 
    rounds_score * 0.2
)

# 惩罚：准确性极低时，总分打对折
if accuracy < 30:
    raw_total = int(raw_total * 0.5)

total = max(0, min(100, raw_total))
```

### 8.3 特殊情况处理

| 情况 | 处理 |
|------|------|
| 识别文本为空或 <3字符 | 总分=5分（极低分） |
| 准确性 < 30% | 总分打5折 |
| 所有遍次识别失败 | 返回总分=5分 |

### 8.4 评分示例

**示例1：朗读准确**

```
原文：Hello, world! How are you?
识别：Hello world How are you
遍数：3遍

准确性：100分  (5/5词正确)
完整性：91分   (23/25字符)
清晰度：96分   (100*0.6 + 91*0.4)
遍数：  100分  (3*33)

总分 = 96*0.2 + 100*0.35 + 91*0.25 + 100*0.2
     = 19.2 + 35 + 22.75 + 20
     = 97分
```

**示例2：朗读不完整**

```
原文：Hello, world! How are you?
识别：Hello world
遍数：2遍

准确性：40分  (2/5词正确)
完整性：36分  (11/25字符)
清晰度：38分  (40*0.6 + 36*0.4)
遍数：  66分  (2*33)

总分 = 38*0.2 + 40*0.35 + 36*0.25 + 66*0.2
     = 7.6 + 14 + 9 + 13.2
     = 44分
```

**示例3：没读（识别为空）**

```
原文：Hello, world!
识别：（空）
遍数：3遍

总分 = 5分（极低分）
```

---

## 9. 部署指南

### 9.1 本地部署（开发测试）

#### 环境要求

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 后端运行环境 |
| FFmpeg | any | 音频转换工具 |
| 浏览器 | Chrome/Edge | 前端访问 |

#### 快速启动

1. 双击运行 `start_score_server.bat`
2. 等待 Whisper 模型加载（首次约2分钟）
3. 浏览器打开 `follow_read.html`

### 9.2 云端部署（生产环境）

#### Hugging Face Spaces 部署（评分服务）

**步骤1：创建 Space**

1. 访问 https://huggingface.co/new-space
2. 选择 **Docker** → **Dockerfile**
3. Space 名称：`english-follow-read`
4. SDK 选择 **Docker**

**步骤2：上传文件**

在 Space 仓库中上传以下文件：

| 文件 | 来源 |
|------|------|
| `Dockerfile` | 复制 `hf_Dockerfile` 的内容 |
| `hf_score_service.py` | 复制 `hf_score_service.py` 的内容 |
| `requirements.txt` | 复制 `requirements.txt` 的内容 |

**步骤3：等待构建**

构建完成后访问：
```
https://你的用户名-english-follow-read.hf.space/health
```

**hf_Dockerfile 内容**：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hf_score_service.py .

EXPOSE 7860
CMD ["uvicorn", "hf_score_service:app", "--host", "0.0.0.0", "--port", "7860"]
```

> ⚠️ **注意**：HuggingFace Spaces 默认端口是 7860，不是 8000！

#### Vercel 部署（前端页面）

**步骤1：创建 GitHub 仓库**

```bash
git init
git add follow_read.html quiz.html chat.html
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/english-follow-read.git
git push -u origin main
```

**步骤2：部署到 Vercel**

1. 访问 https://vercel.com
2. 用 GitHub 登录
3. 点击 **Import Project**
4. 选择刚才的 GitHub 仓库
5. 点击 **Deploy**

**步骤3：修改 API 地址**

在 `follow_read.html` 中修改：

```javascript
// 修改前
const API_BASE = "http://localhost:8000";

// 修改后
const API_BASE = "https://你的用户名-english-follow-read.hf.space";
```

重新提交到 GitHub，Vercel 会自动重新部署。

### 9.3 n8n 工作流集成

#### 工作流概述

```
定时触发（每晚8点）
    ↓
AI英语老师（生成学习内容）
    ↓
├─ Edge TTS → 生成音频 MP3
├─ 生成跟读网页链接
└─ 生成答题网页链接
    ↓
WxPusher推送微信
    ↓
用户收到消息 → 点击链接 → 跟读/答题
```

#### 格式化推送内容（Code 节点）

```javascript
const aiOutput = $('AI英语老师').first().json;
const audioResult = $('生成音频文件').first().json;
const topicInfo = $('7日话题轮换').first().json;

// 提取AI输出的各部分
const raw = aiOutput.output || aiOutput.text || '';

function extractSection(markers, text) {
  for (const m of markers) {
    const regex = new RegExp(m + '[\\s\\S]*?([\\s\\S]*?)(?====|$)', 'i');
    const match = text.match(regex);
    if (match && match[1] && match[1].trim()) return match[1].trim();
  }
  return '';
}

const english = extractSection(['===ENGLISH==='], raw) || '';
const translation = extractSection(['===TRANSLATION==='], raw) || '';
const vocabulary = extractSection(['===VOCABULARY==='], raw) || '';
const patterns = extractSection(['===PATTERNS==='], raw) || '';
const quiz = extractSection(['===QUIZ==='], raw) || '';

// 跟读网页链接
const followReadUrl = `https://english-follow-read.vercel.app/follow_read.html?title=${encodeURIComponent(topicInfo.topic_emoji + ' 跟读练习')}&date=${encodeURIComponent(topicInfo.date)}&text=${encodeURIComponent(english)}&vocab=${encodeURIComponent(vocabulary)}&patterns=${encodeURIComponent(patterns)}`;

// 生成 HTML 推送内容
const html = `
<h2>${topicInfo.topic_emoji} 每日英语伴学</h2>
<p><b>${topicInfo.date} · ${topicInfo.topic_name}</b></p>
<hr/>
<h3>📝 英文原文</h3>
<p>${english}</p>
${audioUrl ? `<p><audio controls src="${audioUrl}" style="width:100%"></audio></p>` : ''}
<hr/>
<h3>📚 重点词汇</h3>
<p>${vocabulary}</p>
<hr/>
<h3>🔑 重点句型</h3>
<p>${patterns}</p>
<hr/>
<h3>🎯 跟读练习</h3>
<p><a href="${followReadUrl}">📖 点击进入跟读练习 →</a></p>
`;

return [{
  json: {
    title: `${topicInfo.topic_emoji} 每日英语 | ${topicInfo.topic_name}`,
    content: html,
    follow_read_url: followReadUrl
  }
}];
```

#### WxPusher 节点配置

```json
{
  "appToken": "AT_你的AppToken",
  "content": "{{ $json.content }}",
  "contentType": 2,
  "uids": ["UID_你的用户ID"],
  "summary": "{{ $json.title }}"
}
```

> **注意**：`contentType` 设为 `2` 表示 HTML 格式。

---

## 10. 故障排查

### 10.1 跟读评分问题

#### 问题1：评分一直很高（90+分）

**原因**：可能运行的是 `mock_score_service.py`（模拟服务），返回随机分数。

**解决**：
1. 确保运行的是 `hf_score_service.py`
2. 检查 `follow_read.html` 中的 `API_BASE` 地址是否正确
3. 访问 `http://localhost:8000/health` 验证服务

#### 问题2：评分一直很低（0-20分）

**原因**：Whisper 识别失败，识别文本为空。

**解决**：
1. 检查麦克风是否正常工作
2. 朗读声音是否足够大
3. 检查 FFmpeg 是否正确安装（音频格式转换）
4. 查看服务端日志，看是否有错误

#### 问题3：提交后一直转圈

**原因**：后端服务未启动或地址配置错误。

**解决**：
1. 检查后端服务是否运行
2. 打开浏览器开发者工具（F12）→ Network 标签，查看请求状态
3. 检查是否有 CORS 错误

### 10.2 答题页面问题

#### 问题1：空题点"下一题"卡死

**状态**：✅ 已修复（2026-05-09）

**修复内容**：
- 空题也可确认（判为错误），不再卡死
- 按钮始终可点击

#### 问题2：无法返回修改已答题目

**状态**：✅ 已修复（2026-05-09）

**修复内容**：
- 新增「← 上一题」按钮
- 提交前可自由返回修改所有题目
- 提交后禁止修改

#### 问题3：题目数据无法加载

**原因**：JSON 格式错误或编码问题。

**解决**：
1. 确保 JSON 格式正确（可用 JSON 校验工具检查）
2. 确保使用 Base64 编码传递数据
3. 检查浏览器控制台是否有错误

### 10.3 音频生成问题

#### 问题1：`edge-tts` 模块未找到

**解决**：
```powershell
pip install edge-tts
```

#### 问题2：生成的音频无法播放

**原因**：音频文件路径错误或格式不支持。

**解决**：
1. 检查输出文件路径是否正确
2. 确保浏览器支持 MP3 格式
3. 尝试使用其他浏览器

### 10.4 部署问题

#### 问题1：HuggingFace Space 构建失败

**检查**：
1. `Dockerfile` 内容是否正确
2. `requirements.txt` 中的依赖是否存在
3. 查看 Space 的 Build 日志

#### 问题2：Vercel 部署后页面无法访问

**检查**：
1. 确保 `follow_read.html` 在仓库根目录
2. 检查 Vercel 部署日志
3. 确保 API_BASE 地址已修改为 HuggingFace Space 地址

---

## 附录

### A. 完整文件清单

| 文件 | 大小 | 行数 | 说明 |
|------|------|------|------|
| `hf_score_service.py` | 4.2KB | 171行 | 跟读评分后端服务 |
| `follow_read.html` | 9.1KB | 301行 | 跟读练习前端页面 |
| `quiz.html` | 12.3KB | 483行 | 答题测试前端页面 |
| `chat.html` | 7.8KB | 226行 | AI聊天前端页面 |
| `generate_audio.py` | 4.0KB | 139行 | Edge TTS 音频生成脚本 |
| `quiz-url-generator.html` | 2.5KB | 73行 | 测试链接生成器 |
| `start_score_server.bat` | 416B | 13行 | Windows 启动脚本 |
| `sample-quiz.json` | 746B | 41行 | 测试题目示例 |
| `requirements.txt` | 113B | 4行 | Python 依赖清单 |
| `hf_Dockerfile` | 273B | 13行 | HuggingFace 部署配置 |
| `deploy-guide.md` | 8.5KB | 354行 | 完整部署指南 |
| `quiz-guide.md` | - | - | 答题功能说明 |
| `checklist.md` | - | - | 开发检查清单 |

### B. Python 依赖详解

```
fastapi==0.104.1          # Web 框架
uvicorn[standard]==0.24.0 # ASGI 服务器（包含 websockets 支持）
openai-whisper==20250625  # Whisper 语音识别
python-multipart==0.0.6   # 解析 multipart/form-data
edge-tts                   # Microsoft Edge TTS（可选，音频生成用）
```

### C. Whisper 模型选择

| 模型 | 大小 | 相对速度 | 准确率 | 推荐场景 |
|------|------|----------|--------|----------|
| `tiny` | 75MB | ~32x | 低 | 快速测试 |
| `base` | 140MB | ~16x | 中 | **推荐（平衡）** |
| `small` | 460MB | ~6x | 高 | 高精度要求 |
| `medium` | 1.5GB | ~2x | 更高 | 服务器部署 |
| `large` | 2.9GB | 1x | 最高 | 不推荐（太慢） |

> 当前系统使用 `base` 模型，准确率约 85-90%。

### D. 浏览器兼容性

| 浏览器 | 录音 | 播放 | 语音合成 | 推荐 |
|--------|------|------|----------|------|
| Chrome 80+ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| Edge 80+ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| Firefox 80+ | ✅ | ✅ | ❌ | ⭐⭐⭐ |
| Safari 14+ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ |
| 微信内置浏览器 | ✅ | ✅ | ❌ | ⭐⭐⭐ |

> **注意**：微信内置浏览器不支持 Web Speech API，语音播放功能不可用。

### E. 联系人和支持

如有问题，请联系：

- **技术支持**：通过 AI英语伴学Agent 工作流反馈
- **GitHub**：提交 Issue
- **文档更新**：2026-05-09

---

**报告结束**

*本文档由 AI英语伴学Agent 自动生成，最后更新于 2026-05-09*
