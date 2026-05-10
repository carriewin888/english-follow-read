# 英语伴学Agent - 文件清单 & 测试检查表

## 📂 文件清单

| 文件 | 位置 | 用途 | 状态 |
|------|------|------|------|
| `tts_server.py` | D:\BN\Future\english\ | TTS音频生成服务 | ✅ 已有 |
| `hf_score_service.py` | D:\BN\Future\english\ | Whisper评分服务 | ✅ 新建 |
| `follow_read.html` | D:\BN\Future\english\ | 跟读练习页（含回听+跳转测试） | ✅ 已更新 |
| `quiz.html` | D:\BN\Future\english\ | 趣味测试页（Web Speech发音） | ✅ 新建 |
| `chat.html` | D:\BN\Future\english\ | 英语聊天页 | ✅ 新建 |
| `quiz-url-generator.html` | D:\BN\Future\english\ | Quiz链接生成器（本地测试用） | ✅ 新建 |
| `sample-quiz.json` | D:\BN\Future\english\ | 测试用样本数据 | ✅ 新建 |
| `hf_Dockerfile` | D:\BN\Future\english\ | HuggingFace Docker配置 | ✅ 新建 |
| `requirements.txt` | D:\BN\Future\english\ | Python依赖 | ✅ 已更新 |
| `quiz-guide.md` | D:\BN\Future\english\ | 集成指南 | ✅ 已更新 |
| `english-tutor-agent-v2.json` | D:\BN\Future\english\ | n8n工作流 | ⚠️ 需更新 |
| `deploy-guide.md` | D:\BN\Future\english\ | 部署指南 | ✅ 已有 |
| `start_score_server.bat` | D:\BN\Future\english\ | 评分服务启动脚本 | ✅ 新建 |

---

## ✅ 本地测试检查表

### 阶段一：跟读录音打分
- [ ] 激活虚拟环境：`venv\Scripts\activate`
- [ ] 启动TTS服务：`python tts_server.py --port 500`
- [ ] 启动评分服务：`python -m uvicorn hf_score_service:app --host 0.0.0.0 --port 800`
- [ ] 浏览器打开 `follow_read.html`（直接双击或用live server）
- [ ] 填入测试数据或用URL参数传入内容
- [ ] 点击录音 → 朗读 → 再次点击停止（✅ 可回听）
- [ ] 录满3遍 → 点击「提交打分」
- [ ] 看到打分结果（清晰度/准确性/完整性/遍数）
- [ ] 显示「🎮 开始测试挑战」按钮（✅ 跳转quiz）

### 阶段二：趣味测试
- [ ] 用 `quiz-url-generator.html` 生成测试链接
- [ ] 打开测试链接，点击「开始挑战」
- [ ] 听音选义题：点击单词发音 → 选择中文意思
- [ ] 听音拼写题：听发音 → 输入英文单词
- [ ] 句型填空题：选择正确答案填空
- [ ] 语法问答题：选择正确语法选项
- [ ] 10分钟倒计时正常显示
- [ ] 提交后显示成绩 + 评语
- [ ] 点击「💬 和AI老师聊天」按钮跳转

### 阶段三：英语聊天
- [ ] 打开 `chat.html`，填入DeepSeek API Key
- [ ] 选择「🌏 中英双语」模式，发送消息
- [ ] AI回复显示，可点击🔊播放发音
- [ ] 切换「🇬🇧 全英文」模式，AI只回复英文
- [ ] 切换「✏️ 自由聊」模式，可随意对话

---

## 🔗 n8n 工作流更新检查表

在 n8n 界面操作（非手动编辑JSON）：

### 步骤1：更新「7日话题轮换」节点
- [ ] 在 `chatInput` 数组中找到 `===QUIZ===` 部分
- [ ] 替换为 `===QUIZ_JSON===` 新提示词（见 `quiz-guide.md` 第一步）

### 步骤2：新增「解析Quiz JSON」节点
- [ ] 在「AI英语老师」节点后面新增 Code 节点
- [ ] 名称：`解析Quiz JSON`
- [ ] 粘贴 `quiz-guide.md` 第二步中的代码
- [ ] 修改 `QUIZ_BASE_URL` 和 `CHAT_BASE_URL` 为你的实际地址

### 步骤3：更新「格式化推送内容」节点
- [ ] 在 markdown 末尾追加 quiz 链接和 chat 链接
- [ ] 在 follow_read 链接里加上 `quiz_url=` 参数

### 步骤4：导入/更新工作流
- [ ] 将更新后的 `english-tutor-agent-v2.json` 导入 n8n
- [ ] 激活工作流
- [ ] 手动触发测试（点击「Execute Workflow」）
- [ ] 检查微信是否收到完整推送（含跟读链接+测试链接）

---

## 📝 部署检查表（公网可访问）

### TTS 服务（音频生成）
- [ ] 本地电脑运行 `tts_server.py`
- [ ] 安装并配置 ngrok：`ngrok http 500`
- [ ] 记录生成的 `https://xxx.ngrok-free.app` 地址

### 评分服务（Whisper）
- [ ] 注册 HuggingFace 账号
- [ ] 创建新 Space（Docker模板）
- [ ] 上传 `hf_score_service.py` + `hf_Dockerfile` + `requirements.txt`
- [ ] 等待部署完成（约5分钟）
- [ ] 记录 Space 的公开访问地址

### 网页文件（follow_read + quiz + chat）
- [ ] 注册 Vercel 账号
- [ ] 上传 `follow_read.html` + `quiz.html` + `chat.html`
- [ ] 设置环境变量（`chat.html` 的 API_KEY 可通过 Vercel Functions 隐藏）
- [ ] 记录三个页面的公开访问地址

### 最终整合
- [ ] 修改 `follow_read.html` 第 89 行 `API_BASE = "你的HF地址"`
- [ ] 修改 n8n 「解析Quiz JSON」节点的 `QUIZ_BASE_URL` 和 `CHAT_BASE_URL`
- [ ] 修改 `chat.html` 中的 `API_KEY`（或用 Vercel Serverless Function 代理）
- [ ] 整体端到端测试：微信接收推送 → 跟读 → 测试 → 聊天

---

## 🆘 常见问题

**Q：跟读页录音后一直"录音中"不停止？**
A：已修复，现在点击同一按钮可停止录音。

**Q：提交打分显示"未配置评分服务地址"？**
A：打开 `follow_read.html`，修改第 89 行 `const API_BASE = "http://localhost:800"`（本地）或 HF 地址（部署后）。

**Q：测试页听不到发音？**
A：浏览器可能不支持 Web Speech API，请用 Chrome 或 Edge。`speak()` 函数已做兼容处理。

**Q：HuggingFace  Spaces 免费版会休眠？**
A：是的，15分钟无访问会休眠。首次唤醒需约30秒，这是免费版限制。

**Q：ngrok 免费版地址每次都变？**
A：是的。可以考虑付费版固定地址，或改用其他方式穿透（如 Cloudflare Tunnel）。
