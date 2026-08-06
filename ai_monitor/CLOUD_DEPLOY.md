# 云端部署指南（全程免费方案：GitHub Pages + 微信提醒）

把每日 AI 海外动态简报流水线迁移到 GitHub Actions 云端运行，**零成本**：

- **调度执行**：GitHub Actions（私有仓库每月 2000 分钟免费，每天约跑 5-15 分钟）
- **LLM 分析**：Google Gemini 免费档（约 1500 次请求/天），智谱 GLM-4-Flash 备用
- **网页发布**：GitHub Pages（免费静态托管，每天一页，自动积累历史归档）
- **微信提醒**：Server酱 / PushPlus（免费，微信扫码绑定，每天 1-2 条）

**交付形态**：不依赖邮箱 —— 每天 7 点微信收到提醒（含网页链接），点开即看完整简报；
网页版有固定地址，可随时回看任意一天的历史。

## 一、代码已就绪

| 文件 | 作用 |
|---|---|
| `ai_monitor/llm_analyze.py` | 调用 LLM API 生成 `llm_analysis.json`（5 字段），Gemini 主用 + GLM 备用自动切换 |
| `ai_monitor/publish_pages.py` | 发布步骤：复制简报 → `docs/briefings/` + 生成归档索引 `docs/index.html` + 微信提醒 |
| `ai_monitor/wechat_notify.py` | 微信推送（Server酱/PushPlus），也用于失败通知 |
| `ai_monitor/run_daily.py` | 编排：monitor → llm_analyze → gen_enhanced → publish，失败自动微信通知 |
| `ai_monitor/requirements.txt` | 依赖清单 |
| `ai_monitor/.env.example` | 环境变量模板（含全部说明） |
| `.github/workflows/daily.yml` | 每日 23:00 UTC（北京 7:00）定时任务 + 发布 Pages + 保活 commit |

现有 `config.py` / `monitor.py` / `llm_enhance.py` / `gen_enhanced_from_json.py` **零改动**。
（`send_email.py` 已移除 —— 不再使用邮件交付）

## 二、需要准备的 3 个免费账号

1. **GitHub 账号**：https://github.com （私有仓库免费）
2. **Gemini API Key**（LLM，必填）：
   - 打开 https://aistudio.google.com/apikey ，用 Google 账号登录
   - 点 **Create API key** 生成，复制保存（免费档足够每日用量）
   - 可选备用：智谱 https://open.bigmodel.cn 注册后创建 API Key（GLM-4-Flash 免费）
3. **微信提醒 Key**（必填，二选一）：
   - **Server酱**：https://sct.ftqq.com → 微信扫码登录 → 复制 **SENDKEY**（普通用户每天约 5 条，够用）
   - **PushPlus**：https://www.pushplus.plus → 微信扫码登录 → 复制 **token**（每天约 200 条）

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
| `WECHAT_NOTIFY_KEY` | ✅ | Server酱 SENDKEY 或 PushPlus token |
| `WECHAT_NOTIFY_TYPE` | 可选 | `serverchan`（默认）或 `pushplus` |

## 五、启用 GitHub Pages（一次性）

仓库页面 → **Settings → Pages** → Source 选 **Deploy from a branch** →
Branch 选 **main** + 目录选 **/docs** → Save。

此后每次 workflow 运行，`docs/` 内容会自动发布，当日简报地址为：

```
https://<你的用户名>.github.io/<仓库名>/briefings/YYYY-MM-DD.html
```

归档首页（列出所有历史简报）：`https://<你的用户名>.github.io/<仓库名>/`

## 六、手动触发验证

1. 仓库 → **Actions** → 左侧 **AI Monitor Daily Briefing** → **Run workflow** → 运行
2. 等 3-10 分钟，绿色对勾 = 成功
3. **微信**收到 `【AI海外动态】简报已更新` 提醒（含网页链接）
4. 打开链接确认简报正常显示
5. 失败时微信会收到"运行失败"提醒，可在 Actions 日志中查看详细报错

## 七、验证稳定后停用本地自动化

确认连续 2-3 天正常后，停用本机 WorkBuddy 中的自动化任务
（ID: `automation-1785717785294`，名称：AI海外动态监测每日简报），
避免本地与云端重复生成。

## 八、定时、发布与保活说明

- 定时：cron `0 23 * * *`（UTC）= 北京时间每天早上 7:00（有数分钟延迟，属正常）
- **发布**：workflow 最后的保活步骤会把 `docs/` 与 `.keepalive` 一起 commit + push，
  触发 GitHub Pages 自动更新
- **保活**：每天自动 commit 一次，防止 GitHub 因仓库 60 天无活动而暂停定时任务

## 九、成本与限额

| 项目 | 免费额度 | 本任务用量 |
|---|---|---|
| GitHub Actions | 2000 分钟/月（私有仓库） | 约 150-450 分钟/月 |
| GitHub Pages | 无限流量（仓库 ≤1GB） | 每天几 KB |
| Gemini Flash | 约 1500 次请求/天 | 每天约 10-30 次 |
| GLM-4-Flash | 完全免费 | 备用 |
| Server酱 / PushPlus | 每天 5 条 / 200 条 | 每天 1-2 条 |

**总计：¥0/年。**

## 十、常见问题

- **429 限流**：Gemini 免费档并发高会限流，脚本已内置重试，并在连续失败后自动切到备用供应商
- **微信没收到**：先确认 Secrets 里 `WECHAT_NOTIFY_KEY` 已配置；Server酱/PushPlus 需先扫码绑定微信并关注服务号
- **Pages 页面 404**：确认 Settings → Pages 里分支选 main、目录选 /docs；推送后等 1-2 分钟再访问
- **想换模型**：不用改代码，改 Secrets 里的 `LLM_MODEL`（需在 workflow 中暴露该变量），或直接编辑 `llm_analyze.py` 顶部默认值；OpenRouter 用户可把 base_url/model 换成任意模型
