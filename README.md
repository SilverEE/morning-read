---
AIGC:
    Label: "1"
    ContentProducer: 001191110102MACQD9K64018705
    ProduceID: 2380863929060667_0-data_volume/7647477898818945331-files/所有对话/主对话/晨间轻读/README.md
    ReservedCode1: ""
    ContentPropagator: 001191110102MACQD9K64028705
    PropagateID: 2380863929060667#1780659410137
    ReservedCode2: ""
---
# 晨间轻读

> 每日早上7点，天气+热点+名言+歌曲，准时推送到微信 ☀️

## ✨ 功能

- 🌤 **实时天气** — 自动获取所在城市天气，支持浏览器自动定位
- 📰 **热点新闻** — 聚合36氪、机器之心、Hacker News、TechCrunch 四大源
- 💡 **每日一言** — 80+ 条有深度的中外名言随机推送
- 🎵 **今日推荐** — 80+ 首精选中外歌曲随机推荐
- 📱 **微信推送** — 通过Server酱推送到微信，支持多人同时接收
- ⚙️ **网页设置** — 支持开启/关闭推送、修改城市、GitHub同步

## 🚀 部署步骤（零编程基础友好）

### 第一步：Fork 仓库

1. 登录 [GitHub](https://github.com)
2. 访问本仓库页面，点击右上角 **Fork** 按钮
3. 等待 Fork 完成，你将拥有一个属于自己的仓库副本

> 也可以直接创建新仓库（名称建议 `morning-read`），上传本项目所有文件。

### 第二步：上传文件

确保你的仓库包含以下文件结构：

```
morning-read/
├── .github/
│   └── workflows/
│       └── daily-push.yml    # GitHub Actions 定时推送
├── config.json                # 配置文件
├── daily_push.py              # 推送脚本
├── quotes.json                # 名言库
├── songs.json                 # 歌曲库
├── index.html                 # 网页前端
└── README.md                  # 说明文档
```

### 第三步：开启 GitHub Pages

1. 进入你的仓库 → **Settings** → **Pages**
2. Source 选择 **Deploy from a branch**
3. Branch 选择 **main**，文件夹选 **/ (root)**
4. 点击 **Save**
5. 等待1-2分钟，页面顶部会显示你的网站地址：`https://你的用户名.github.io/morning-read/`

### 第四步：添加 GitHub Secret（SCT Keys）

1. 注册 [Server酱](https://sct.ftqq.com/)，微信扫码登录
2. 在Server酱后台获取你的 **SendKey**（格式：`SCTxxxxxTzxxxxxx`）
3. 进入你的 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions**
4. 点击 **New repository secret**
5. Name 填 `SCT_KEYS`，Value 填你的 SendKey（多个接收人用逗号分隔，格式：`key1:备注1,key2:备注2`）
6. 点击 **Add secret** 保存

### 第五步：启用 GitHub Actions

1. 进入仓库 → **Actions** 标签页
2. 如果看到提示，点击 **I understand my workflows, go ahead and enable them**
3. 在左侧找到 **Daily Push - 晨间轻读** 工作流
4. 点击 **Enable workflow**（如已启用则无需操作）
5. 可以点击 **Run workflow** 按钮手动测试一次推送

### 第六步：访问网页

打开 `https://你的用户名.github.io/morning-read/` 即可看到晨间轻读页面。

## ⚙️ 配置说明

### config.json

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `enabled` | 是否启用推送 | `true` |
| `location` | 天气城市 | `"福州"` |
| `push_time` | 推送时间（仅展示，实际由cron控制） | `"07:00"` |
| `receivers` | 推送接收人列表，每项含 `name` 和 `sct_key` | `[]` |

### 添加推送接收人

支持给多个微信同时推送，有两种方式：

**方式一：网页端（推荐）**
1. 打开晨间轻读网页 → 点击 ⚙️ 设置
2. 在「推送接收人」区域，输入备注名和 Server酱 Key
3. 点击「添加」即可，自动同步到 GitHub

**方式二：手动编辑 config.json**
```json
{
  "receivers": [
    {"name": "我", "sct_key": "SCTxxx..."},
    {"name": "家人", "sct_key": "SCTyyy..."},
    {"name": "朋友", "sct_key": "SCTzzz..."}
  ]
}
```

**方式三：环境变量（适用于 GitHub Actions）**
1. 在 GitHub Secrets 中添加 `SCT_KEYS`
2. 格式：`key1:备注名1,key2:备注名2`（也可以只填 key，用逗号分隔）
3. 例如：`SCT359745TzFT:我,SCT888888AbCd:家人`

### 修改推送时间

默认推送时间为北京时间每天 **07:00**。如需修改：

1. 打开 `.github/workflows/daily-push.yml`
2. 修改 cron 表达式：`- cron: '0 23 * * *'`
3. 注意：GitHub Actions 使用 UTC 时区，北京时间 = UTC + 8
4. 例如改为北京时间 08:00 推送，cron 应为 `'0 0 * * *'`

### 修改天气城市

- **网页端**：点击右上角 ⚙️ → 输入城市名 → 自动更新
- **配置文件**：修改 `config.json` 中的 `location` 字段

## 🔑 获取 Server酱 Key

1. 访问 [Server酱官网](https://sct.ftqq.com/)
2. 使用微信扫码登录
3. 在 [Key页面](https://sct.ftqq.com/sendkey) 复制你的 SendKey
4. 将 Key 添加到 GitHub Secrets（名称 `SCT_KEYS`）或写入 `config.json` 的 `receivers` 数组

## 🔐 创建 GitHub PAT（用于网页端设置同步）

网页端的推送开关和城市修改需要同步到 GitHub 仓库，需要配置 Personal Access Token：

1. 登录 GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
2. 点击 **Generate new token**
3. Token name：随意填写，如 `morning-read`
4. Expiration：选择有效期（建议90天或自定义）
5. Repository access：选择 **Only select repositories**，选你的 `morning-read` 仓库
6. Permissions → Repository permissions → **Contents** → 选择 **Read and write**
7. 点击 **Generate token**
8. 复制生成的 Token（只显示一次！）
9. 在晨间轻读网页 → 设置面板 → 输入 Token → 保存

## 📦 依赖

- **Python 推送脚本**：`requests`、`feedparser`（`pip install requests feedparser`）
- **前端**：无额外依赖，纯 HTML/CSS/JS
- **API**：
  - [Open-Meteo](https://open-meteo.com/)（天气，免费无需Key）
  - [rss2json](https://rss2json.com/)（RSS代理，免费）
  - [Server酱](https://sct.ftqq.com/)（微信推送，免费版每天5条）

## 📝 常见问题

**Q: 推送没有收到？**
- 检查 GitHub Actions 是否正常运行（Actions 标签页查看运行记录）
- 检查 SCT_KEYS 是否正确配置（Secret 名称必须是 `SCT_KEYS`）
- 检查 config.json 中 enabled 是否为 true
- 检查 config.json 中 receivers 是否有内容
- Server酱免费版每天限额5条（多个接收人共享额度）

**Q: 天气显示"数据暂不可用"？**
- 可能是 Open-Meteo API 暂时不可用，稍后刷新即可
- 检查城市名是否正确（支持中文城市名）

**Q: 新闻为空？**
- RSS 源可能暂时不可用
- rss2json 免费版有请求限制，频繁刷新可能触发限制

**Q: 如何手动触发推送？**
- GitHub 仓库 → Actions → Daily Push → Run workflow

## 📄 License

MIT

---

> 本内容由 Coze AI 生成，请遵循相关法律法规及《人工智能生成合成内容标识办法》使用与传播。
