# 跟读+测试+聊天 完整集成指南

## 架构总览

```
n8n 每晚8点运行
    ├─ AI英语老师 → 生成学习内容 + Quiz题目（JSON）
    ├─ TTS生成音频 → 课文朗读MP3
    ├─ 组装 follow_read.html 链接（带入 quiz_url 参数）
    └─ WxPusher 推送微信
            │
            ├─ 📖 跟读练习（3遍录音→打分）
            │       └─ 打分完成后 → 显示「开始测试」按钮
            │
            ├─ 🎮 趣味测试（10分钟，听音选义/拼写/填空/语法）
            │       └─ 测试结束 → 显示「和AI聊天」按钮
            │
            └─ 💬 英语聊天（和AI老师自由对话）
```

---

## 第一步：更新 AI 英语老师的提示词

在 n8n 中找到「7日话题轮换」Code 节点，把 `chatInput` 数组里的 `===QUIZ===` 部分**整段替换**为：

```
  '',
  '===QUIZ_JSON===',
  '请以纯JSON数组格式输出10道测试题，不要添加```或任何说明文字。',
  '题型包括：',
  '1. listen_choice（听音选义）：给word字段，quiz页面会朗读单词，学生选中文意思',
  '2. listen_spell（听音拼写）：给word字段，学生听后拼写英文',  
  '3. sentence_blank（句型填空）：给sentence（用___表示空白）和options',
  '4. grammar_choice（语法选择）：给question和options',
  '',
  'JSON格式示例：',
  '[{"type":"listen_choice","word":"apple","options":["苹果","香蕉","橙子","葡萄"],"answer":0},',
  ' {"type":"listen_spell","word":"banana","hint":"黄色的水果","answer":"banana"},',
  ' {"type":"sentence_blank","sentence":"I ___ a student.","options":["am","is","are"],"answer":0},',
  ' {"type":"grammar_choice","question":"Which is correct?","options":["He go","He goes","He going"],"answer":1}]',
  '',
  '要求：listen_choice 3道，listen_spell 3道，sentence_blank 2道，grammar_choice 2道',
  '单词必须来自今日重点词汇，语法点必须来自今日语法要点。',
  '注意：只输出纯JSON数组，不要用```包裹，不要写任何说明。',
```

---

## 第二步：在 n8n 中新增「解析Quiz JSON」节点

在「AI英语老师」节点**后面**，新增一个 **Code 节点**：

- **名称**：`解析Quiz JSON`
- **语言**：JavaScript
- **代码**：

```javascript
const aiOutput = $('AI英语老师').first().json;
const raw = aiOutput.output || aiOutput.text || '';

// 提取 ===QUIZ_JSON=== 和 === 之间的内容
let quizJson = null;
const match = raw.match(/===QUIZ_JSON===([\s\S]*?)(?====|$)/);
if (match) {
  let jsonStr = match[1].trim();
  // 去掉可能的 ```json ``` 包裹
  jsonStr = jsonStr.replace(/```json|```/g, '').trim();
  try {
    quizJson = JSON.parse(jsonStr);
  } catch(e) {
    console.log('JSON解析失败:', e.message);
  }
}

// 备用题目（AI失败时）
if (!Array.isArray(quizJson) || quizJson.length === 0) {
  quizJson = [
    {"type":"sentence_blank","sentence":"I ___ a student.","options":["am","is","are"],"answer":0},
    {"type":"grammar_choice","question":"Which is correct?","options":["He go to school.","He goes to school.","He going to school."],"answer":1},
    {"type":"listen_choice","word":"apple","options":["苹果","香蕉","冰淇淋","汽车"],"answer":0},
    {"type":"listen_spell","word":"happy","hint":"快乐的","answer":"happy"}
  ];
}

// Base64 编码，用于 URL 参数
const jsonStr = JSON.stringify(quizJson);
const base64 = Buffer.from(jsonStr).toString('base64');

// quiz.html 的访问地址（部署后替换成真实地址）
const QUIZ_BASE_URL = "http://你的域名/quiz.html";  // ← 改成你的地址
const quizUrl = QUIZ_BASE_URL + "?quiz=" + encodeURIComponent(base64);

// chat.html 的访问地址
const CHAT_BASE_URL = "http://你的域名/chat.html";
const chatUrl = CHAT_BASE_URL + "?topic=" + encodeURIComponent($('7日话题轮换').first().json.topic_name || '每日英语');

return [{
  json: {
    quiz_json: quizJson,
    quiz_base64: base64,
    quiz_url: quizUrl,
    chat_url: chatUrl
  }
}];
```

---

## 第三步：更新「格式化推送内容」节点

找到「格式化推送内容」Code 节点，在 `markdown` 变量**末尾**追加：

```javascript
// 在现有 markdown 后面追加：
markdown += '\n\n---\n\n## 🎮 跟读测试\n';
markdown += '跟读完成后，来挑战10分钟趣味测试吧！\n';
markdown += '👉 <a href="' + $('解析Quiz JSON').first().json.quiz_url + '">点击开始测试</a>\n';

markdown += '\n\n---\n\n## 💬 英语聊天\n';
markdown += '测试完成后，还可以和AI老师自由聊天哦！\n';
markdown += '👉 <a href="' + $('解析Quiz JSON').first().json.chat_url + '">点击进入聊天</a>\n';
```

同时，把 `follow_read` 的链接也加上 `quiz_url` 参数，让跟读页打分后可以直接跳转测试：

在「格式化推送内容」节点里找到 `followReadUrl` 相关代码，改为：

```javascript
// follow_read 链接加上 quiz_url 参数
const quizUrlParam = encodeURIComponent($('解析Quiz JSON').first().json.quiz_url || '');
const chatUrlParam = encodeURIComponent($('解析Quiz JSON').first().json.chat_url || '');
const followReadUrl = "follow_read.html?text=..." + "&quiz_url=" + quizUrlParam + "&chat_url=" + chatUrlParam;
```

---

## 第四步：部署网页文件

把以下文件传到你的 Web 服务器（或 Vercel）：

| 文件 | 说明 |
|------|------|
| `follow_read.html` | 跟读练习页（已含跳测试按钮） |
| `quiz.html` | 趣味测试页（Web Speech API 发音） |
| `chat.html` | 英语聊天页（需填 DeepSeek API Key） |

**重要**：`chat.html` 第 88 行需要填入你的 DeepSeek API Key：

```javascript
const API_KEY = "sk-your-deepseek-api-key";  // ← 填入你的 Key
```

---

## 本地测试步骤

### 1. 测试跟读页
```bash
# 启动评分服务
cd D:\BN\Future\english
python -m uvicorn hf_score_service:app --host 0.0.0.0 --port 8000

# 浏览器打开（需要改 API_BASE 为本地地址）
# 用 live server 或直接双击打开 follow_read.html
```

### 2. 测试 Quiz 页
用浏览器打开 `quiz-url-generator.html`，生成测试链接后打开。

### 3. 测试聊天页
打开 `chat.html` 前，先填入 API Key。

---

## ⚠️ 注意事项

1. **ngrok 地址会变**：每次重启 ngrok，TTS 音频链接会失效。正式部署建议用固定域名。
2. **chat.html 的 API Key 安全**：前端暴露 API Key 有风险，建议通过 n8n Webhook 转发。
3. **HuggingFace 评分服务**：免费 Spaces 会休眠，首次调用需等待约30秒唤醒。
