# 云端部署指南（全程免费方案）

把每日 AI 海外动态简报流水线迁移到 GitHub Actions 云端运行，**零成本**：

- **调度执行**：GitHub Actions（私有仓库每月 2000 分钟免费，每天约跑 5-15 分钟）
- **LLM 分析**：Google Gemini 免费档（约 1500 次请求/天），智谱 GLM-4-Flash 备用
- **发信**：QQ 邮箱 SMTP（免费，授权码）

## 一、代码已就绪

本地新增/改动的文件：

| 文件 | 作用 |
|---|---|
| `ai_monitor/llm_analyze.py` | 替代智能体步骤：调用 LLM API 生成 `llm_analysis.json`（含 title_cn/summary_cn/importance_score 等 5 字段），多供应商自动切换 |
| `ai_monitor/send_email.py` | 替代 agent-mail：QQ 邮箱 SMTP 发送增强版简报（465 SSL，也兼容 Outlook 587） |
| `ai_monitor/run_daily.py` | 编排：monitor → llm_analyze → gen_enhanced → send_email，失败自动发通知 |
| `ai_monitor/requirements.txt` | 依赖清单 |
| `ai_monitor/.env.example` | 环境变量模板（含全部说明） |
| `.github/workflows/daily.yml` | 每日 23:00 UTC（北京 7:00）定时任务 + 保活 commit |

现有 `config.py` / `monitor.py` / `llm_enhance.py` / `gen_enhanced_from_json.py` **零改动**。

## 二、需要准备的 3 个免费账号

1. **GitHub 账号**：https://github.com （私有仓库免费）
2. **Gemini API Key**（主 LLM，必填）：
   - 打开 https://aistudio.google.com/apikey ，用 Google 账号登录
   - 点 **Create API key** 生成，复制保存（免费档足够每日用量）
   - 可选备用：智谱 https://open.bigmodel.cn 注册后创建 API Key（GLM-4-Flash 免费）
3. **QQ 邮箱授权码**（发信，必填）：
   - 登录 QQ 邮箱网页版 → 设置 → 账户
   - 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务** → 开启 **POP3/SMTP 服务**
   - 按提示用手机发短信验证 → 生成 16 位授权码（形如 `abcd efgh ijkl mnop`）
   - ⚠️ 授权码不是 QQ 密码！

## 三、推送代码到 GitHub

在项目根目录（`C:\Users\xugel\WorkBuddy\智库助手`）执行：

```bash
# 1. GitHub 网页上新建私有仓库（New repository → Private，不要勾选任何初始化选项）
# 2. 关联远程仓库（换成你的用户名和仓库名）
git remote add origin https://github.com/<你的用户名>/<仓库名>.git

# 3. 推送（分支名可能是 master，按 git branch 结果调整）
git push -u origin main
```

## 四、配置 Secrets（密钥）

仓库页面 → **Settings → Secrets and variables → Actions → New repository secret**，逐个添加：

| Secret 名 | 必填 | 值 |
|---|---|---|
| `LLM_API_KEY` | ✅ | Gemini API Key |
| `LLM_FALLBACK_API_KEY` | 可选 | 智谱 API Key（建议配置，双保险） |
| `SMTP_USER` | ✅ | 发件 QQ 邮箱 |
| `SMTP_PASS` | ✅ | 16 位 QQ 邮箱授权码 |
| `MAIL_TO` | 可选 | 收件邮箱，默认=发件邮箱（即自己发给自己） |

## 五、手动触发验证

1. 仓库 → **Actions** → 左侧 **AI Monitor Daily Briefing** → **Run workflow** → 运行
2. 等 3-10 分钟，绿色对勾 = 成功
3. 检查收件箱（含垃圾邮件）是否收到 `【AI海外动态】智能增强简报` 邮件
4. 失败时查看运行日志，常见原因：Key 填错、授权码带了空格、授权码不是 QQ 密码

## 六、验证稳定后停用本地自动化

确认连续 2-3 天邮件正常后，停用本机 WorkBuddy 中的自动化任务
（ID: `automation-1785717785294`，名称：AI海外动态监测每日简报），
避免本地与云端重复发信。

## 七、定时与保活说明

- 定时：cron `0 23 * * *`（UTC）= 北京时间每天早上 7:00
- GitHub Actions 定时有数分钟延迟，属正常
- 已内置**保活机制**：每天运行后自动 commit 一次 `.keepalive` 时间戳并 push，
  防止 GitHub 因仓库 60 天无活动而自动暂停定时任务

## 八、成本与限额

| 项目 | 免费额度 | 本任务用量 |
|---|---|---|
| GitHub Actions | 2000 分钟/月（私有仓库） | 约 150-450 分钟/月 |
| Gemini Flash | 约 1500 次请求/天 | 每天约 10-30 次 |
| GLM-4-Flash | 完全免费 | 备用 |
| QQ 邮箱 SMTP | 免费（普通账户每天约 500 封） | 每天 1 封 |

**总计：¥0/年。**

## 九、常见问题

- **429 限流**：Gemini 免费档并发高会限流，脚本已内置重试，并在连续失败后自动切到备用供应商
- **邮件进垃圾箱**：QQ 邮箱发往 Outlook 属跨域投递，首次可能进垃圾箱，把发件地址加入白名单或点一次"这不是垃圾邮件"即可
- **想换回 Outlook 发信**：无需改代码，把 Secrets 里的 `SMTP_HOST`/`SMTP_PORT` 改掉即可（脚本已支持 465 SSL 与 587 STARTTLS 两种模式；注意 workflow 目前只传了 SMTP_USER/SMTP_PASS，如需自定义 host/port 请在 daily.yml 中补充对应 env）
- **想换模型**：不用改代码，改 Secrets 里的 `LLM_MODEL`（需在 workflow 中暴露该变量），或直接编辑 `llm_analyze.py` 顶部默认值；OpenRouter 用户可把 base_url/model 换成任意模型
