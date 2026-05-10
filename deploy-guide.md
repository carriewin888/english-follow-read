# 📖 英语跟读打分系统 - 完整部署指南

## 🏗️ 系统架构

```
n8n 工作流（每晚8点自动执行）
    │
    ├─ AI英语老师 → 生成学习内容
    │                   │
    │                   ├─ Edge TTS → 生成音频MP3
    │                   │
    │                   └─ 生成跟读网页链接
    │
    └─ WxPusher推送微信（HTML消息，内嵌音频播放器和跟读链接）
            │
            ├─ 📝 英文原文 + 🎧 朗读音频
            ├─ 📚 重点词汇 + 📖 句型
            └─ 🔗 跟读打分网页链接

微信用户
    │
    ├─ 点击音频链接 → 微信内置浏览器播放音频
    │
    └─ 点击跟读链接 → 打开跟读网页 → 录音3遍 → AI打分 → 显示结果
```

---

## 📁 文件清单

| 文件 | 说明 |
|------|------|
| `D:\BN\Future\english\tts_server.py` | Edge TTS 音频生成服务 |
| `D:\BN\Future\english\hf_score_service.py` | 跟读评分服务（Whisper识别） |
| `D:\BN\Future\english\follow_read.html` | 跟读打分网页（录音界面） |
| `D:\BN\Future\english\english-tutor-agent-v2.json` | n8n工作流文件 |
| `D:\BN\Future\english\requirements.txt` | Python依赖 |
| `D:\BN\Future\english\hf_Dockerfile` | HuggingFace部署配置 |

---

## 🚀 第一步：本地测试（必做）

### 1.1 安装 Python 虚拟环境和依赖

打开 **PowerShell**（右键开始菜单 → Windows PowerShell）：

```powershell
# 创建虚拟环境
cd D:\BN\Future\english
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 1.2 启动 Edge TTS 音频服务（端口5000）

新开一个 PowerShell 窗口：

```powershell
cd D:\BN\Future\english
.\venv\Scripts\Activate.ps1
python tts_server.py --port 5000
```

**保持这个窗口开着！**

### 1.3 启动跟读评分服务（端口8000）

再新开一个 PowerShell 窗口：

```powershell
cd D:\BN\Future\english
.\venv\Scripts\Activate.ps1
python -m uvicorn hf_score_service:app --host 0.0.0.0 --port 8000
```

**首次启动会下载 Whisper 模型（约2分钟），请耐心等待。**

看到 `Uvicorn running on http://0.0.0.0:8000` 即启动成功。

### 1.4 验证服务是否正常

打开浏览器访问：

| 服务 | 测试地址 | 期望返回 |
|------|----------|----------|
| Edge TTS | `http://localhost:5000/health` | `{"status":"ok"}` |
| 评分服务 | `http://localhost:8000/health` | `{"status":"ok"}` |

### 1.5 测试音频生成

```bash
curl -X POST http://localhost:5000/generate -H "Content-Type: application/json" -d "{\"text\":\"Hello world!\",\"speed\":1.0}"
```

应该在 `D:\BN\Future\english\audio\` 目录看到生成的 MP3 文件。

### 1.6 测试跟读网页

双击打开 `follow_read.html`，在浏览器里测试录音功能。

---

## 🌐 第二步：部署到云端（让微信能访问）

### 方案 A：Hugging Face Spaces（免费，推荐）

#### 创建 Space

1. 访问 https://huggingface.co/new-space
2. 选择 **Docker** → **Dockerfile**
3. Space 名称：`english-follow-read`
4. SDK 选择 **Docker**
5. 点击创建

#### 上传文件

在 Space 仓库中上传以下文件（复制内容）：

| 文件 | 内容来源 |
|------|----------|
| `Dockerfile` | 复制 `hf_Dockerfile` 的内容 |
| `hf_score_service.py` | 复制 `hf_score_service.py` 的内容 |
| `requirements.txt` | 复制 `requirements.txt` 的内容 |

#### 等待构建（约5-10分钟）

构建完成后，访问：
```
https://你的用户名.english-follow-read.hf.space/health
```

应该看到：`{"status":"ok"}`

**记下这个地址**：`https://你的用户名-english-follow-read.hf.space`

---

## 📱 第三步：部署跟读网页到 Vercel

### 创建 GitHub 仓库

1. 打开 https://github.com/new
2. 仓库名称：`english-follow-read`
3. 设为 **Private**（可选）
4. 不初始化 README

### 上传跟读网页

1. 克隆仓库到本地
2. 把 `follow_read.html` 放入仓库根目录
3. 提交并推送

### 部署到 Vercel

1. 访问 https://vercel.com
2. 用 GitHub 登录
3. 点击 **Import Project**
4. 选择刚才的 GitHub 仓库
5. 点击 **Deploy**

部署完成后获得网址，如：
```
https://english-follow-read.vercel.app
```

**记下这个地址**

### 修改网页中的 API 地址

在 `follow_read.html` 文件中找到这行：
```javascript
const API_BASE = "";
```

改为：
```javascript
const API_BASE = "https://你的用户名-english-follow-read.hf.space";
```

重新提交到 GitHub，Vercel 会自动重新部署。

---

## 🔧 第四步：修改 n8n 工作流

### 4.1 修改"格式化推送内容"节点

将推送内容改为 **HTML 格式**（contentType=2），嵌入音频播放器和跟读链接：

```javascript
// 完整的HTML推送内容（请复制到Code节点）
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
const grammar = extractSection(['===GRAMMAR==='], raw) || '';
const quiz = extractSection(['===QUIZ==='], raw) || '';
const encouragement = extractSection(['===ENCOURAGEMENT==='], raw) || '';

// 音频URL（公网可访问的地址）
const audioUrl = audioResult.data && audioResult.data.url 
    ? audioResult.data.url.replace('localhost:5000', '192.168.2.49:5000')
    : '';

// 跟读网页链接
const followReadUrl = `https://english-follow-read.vercel.app/follow_read.html?title=${encodeURIComponent(topicInfo.topic_emoji + ' 跟读练习')}&date=${encodeURIComponent(topicInfo.date)}&text=${encodeURIComponent(english)}&vocab=${encodeURIComponent(vocabulary)}&patterns=${encodeURIComponent(patterns)}`;

const html = `
<h2>${topicInfo.topic_emoji} 每日英语伴学</h2>
<p><b>${topicInfo.date} · ${topicInfo.topic_name}</b></p>

<hr/>

<h3>📝 英文原文</h3>
<p>${english}</p>

${audioUrl ? `<p><audio controls src="${audioUrl}" style="width:100%"></audio></p>` : ''}

<hr/>

<h3>🌏 中文译文</h3>
<p>${translation}</p>

<hr/>

<h3>📚 重点词汇</h3>
<p>${vocabulary}</p>

<hr/>

<h3>🔑 重点句型</h3>
<p>${patterns}</p>

<hr/>

<h3>📐 语法要点</h3>
<p>${grammar}</p>

<hr/>

<h3>✅ 今日小测</h3>
<p>${quiz}</p>

<hr/>

<h3>💪 今日鼓励</h3>
<p>${encouragement}</p>

<hr/>

<h3>🎯 跟读练习</h3>
<p>点击下方链接，进行跟读打分练习：</p>
<p><a href="${followReadUrl}">📖 点击进入跟读练习 →</a></p>

<hr/>

<p style="color:#999;font-size:12px">由AI英语伴学Agent自动生成 | 宁波初二专属</p>
`;

return [{
  json: {
    title: `${topicInfo.topic_emoji} 每日英语 | ${topicInfo.topic_name}`,
    content: html,
    topic: topicInfo.topic_name,
    date: topicInfo.date,
    english_text: english,
    audio_url: audioUrl,
    follow_read_url: followReadUrl
  }
}];
```

### 4.2 修改 WxPusher 节点

将 `contentType` 从 `3`（markdown）改为 `2`（HTML）：

```json
{
  "appToken": "AT_vmEhrI8hwfvXhd2CnPm4p4Qacbf0APdc",
  "content": {{ JSON.stringify($json.content) }},
  "contentType": 2,
  "uids": ["UID_XJ0hQ6FIq6Iqlu5hbIOD5Rx3N7lF"],
  "summary": {{ JSON.stringify($json.title) }}
}
```

---

## ⚠️ 重要：解决公网访问问题

### 问题
微信内置浏览器访问的是 `http://192.168.2.49:5000`，这是局域网地址，微信打不开。

### 解决方案：内网穿透

在运行 TTS 服务的电脑（`192.168.2.49`）上，下载并运行 **ngrok**：

1. 注册账号：https://ngrok.com
2. 下载 ngrok：https://ngrok.com/download
3. 解压后运行：
   ```bash
   ngrok http 5000
   ```
4. 复制显示的 **Forwarding** 地址（如 `https://xxxx.ngrok.io`）

然后在 n8n 工作流中，把音频 URL 的地址从 `http://192.168.2.49:5000` 改为 ngrok 的公网地址。

---

## 🎯 打分维度说明

| 维度 | 满分 | 计算方式 |
|------|------|---------|
| 清晰度 | 100 | Whisper 识别置信度 |
| 发音准确性 | 100 | 识别文本 vs 原文词汇匹配率 |
| 朗读完整性 | 100 | 识别文本长度 / 原文长度 |
| 完成遍数 | 100 | 3遍=100分，2遍=66分，1遍=33分 |

**总分 = 清晰度×0.2 + 准确性×0.35 + 完整性×0.25 + 遍数×0.2**

---

## 📞 需要帮助？

把错误信息截图发给我，我帮你调试！

---

**版本信息**
- 更新日期：2026-05-09
- Whisper模型：base（英文识别准确率约85-90%）
