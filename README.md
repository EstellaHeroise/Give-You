# DeepSeek Price Alert 🎉📉

> **Monitor DeepSeek official API pricing and get alerted when token prices drop.**
> **监控 DeepSeek 官方 API 价格，降价时自动提醒你。**

一个零依赖、跨平台的 DeepSeek 官方 API 降价提醒小工具。每天(或按你的计划)检查一次官方定价页，一旦发现 token 价格下降，立刻弹窗通知你，并自动记录价格变化历史。

A zero-dependency, cross-platform alert tool for DeepSeek official API price drops. It checks the official pricing page on your schedule, pops a desktop notification when token prices drop, and keeps a local price history automatically.

---

## 📦 二合一安装包 / All-in-One Installer

**一个安装包，两个版本，下载一次即可选择安装。**

The installer bundles both editions — download once, choose your edition during setup.

| 版本 Edition | 适用场景 | 安装位置 |
|---|---|---|
| 🖥️ **桌面通用版** / Desktop | 独立运行的桌面程序，不依赖任何 AI 平台 | `~/deepseek-price-alert/desktop`（可自定义） |
| 🤖 **WorkBuddy 适配版** / WorkBuddy | 已安装 WorkBuddy 的用户，对话中直接触发检查 | `~/.workbuddy/skills/deepseek-price-alert` |

### 使用方法 / How to install

1. 下载 `deepseek-price-alert-setup-<version>.zip` 并解压
2. 双击 `install.bat`（Windows），或运行 `python installer.py`
3. 浏览器自动打开图形安装向导
4. 选择 **桌面通用版** 或 **WorkBuddy 适配版**（可勾选开机自启、同时安装桌面联动程序、安装后自动删除安装包等选项）
5. 点击「开始安装」，自动完成文件复制与配置
6. （默认开启）安装完成后自动删除下载的 ZIP 与解压目录，不留垃圾文件

> 安装向导为本地网页（`http://127.0.0.1:8765`），不上传任何数据。
> 若想保留安装包，在安装界面取消勾选「安装完成后自动删除下载的安装包」即可。

### WorkBuddy 适配版使用方式

安装后，在 WorkBuddy 对话中输入以下指令即可触发：

- 「DeepSeek 降价了吗？」→ 自动运行 `--once` 检查
- 「查看 DeepSeek 价格历史」→ 自动运行 `--history`
- 「设置 DeepSeek 开机提醒」→ 自动运行 `--setup-startup`

---

## ✨ 特性 / Features

- 🎯 **只监控 DeepSeek 官方 API 定价**（`api-docs.deepseek.com/quick_start/pricing`），不是第三方转售平台
- 🔔 **降价自动弹窗提醒**（Windows / macOS / Linux 原生通知，无需任何第三方库），可选弹窗+系统提示音
- 🚀 **开机提醒**：设备每次开机自动检查一次价格，有降价才提醒
- ⏰ **每日定时提醒**：设定固定时间，每天到点自动检查一次价格
- 💰 **价格单位可自选**：`$ / 1M tokens`（官方口径）、`¥ / 万token`（直观感受"一分钱一万token"）、`¥ / 百万token`，或自动同时显示两种
- 🔥 **大额优惠重点提醒**：降幅 ≥50% **或** 价格达到 `¥0.01/万token`（一分钱级）时，自动用 🔥 重点标记
- 📢 **官方公告监控**：自动监控 DeepSeek 官方 `/updates` 公告列表，发现降价/优惠/新模型公告立即提醒
- 🎨 **风格预览与选择**：提供 `style_preview.html`（纯预览）和 `style_picker.html`（点击选择并保存到 `config.json`），支持通知弹窗 / 终端输出 / 窗口主题三组风格 + 价格单位 + 提醒方式
- 📜 **价格历史自动记录**（`price_history.json`），涨价也会记录（仅日志，不弹窗）
- 🐍 **纯 Python 标准库，零依赖** —— clone 下来就能跑，不用 `pip install` 任何东西
- 🌍 **跨平台**：Windows / macOS / Linux 都支持
- 💻 **命令行友好**：`--init`、`--once`、`--history`、`--version`、`--help`、`--check-update`、`--setup-startup`、`--remove-startup`、`--setup-schedule HH:MM`、`--remove-schedule`、`--status`
- 🔄 **自动更新检测**：脚本与安装向导启动时自动检查 GitHub 最新版本，发现新版提示下载（配合 GitHub Releases 使用）
- 🧹 **安装后自动清理**：安装完成后可自动删除下载的安装包（ZIP）与解压目录，省空间、不留垃圾文件（可在安装界面取消勾选）

---

## 🎨 风格预览与选择 / Style Preview & Picker

打开 `style_preview.html` 可**纯预览**全部风格（三组 × 4 种），通知弹窗同时展示「系统原生弹窗」和「自定义风格弹窗」两种方式。

打开 `style_picker.html` 可**点击选择**并生成 `config.json`，主脚本会自动应用。

```
python style_picker.html  # 浏览器打开, 点击选择, 点保存下载 config.json
```

把下载的 `config.json` 放到项目文件夹即可生效。

### 通知弹窗风格 / Notification styles

| 风格 | 说明 |
|---|---|
| `clean` 简洁 | 黑白灰，极简 |
| `playful` 活泼 | 彩色 + emoji，轻松醒目 |
| `minimal` 极简 | 大量留白，细线条 |
| `pro` 专业 | 深蓝底色，稳重正式 |

### 终端输出风格 / Terminal output styles

| 风格 | 说明 |
|---|---|
| `log` 日志 | `[时间] 消息` |
| `table` 表格 | `\| 时间 \| 消息 \|` 对齐列 |
| `color` 彩色 | 绿✓ 红✗ 黄! 多彩 |
| `compact` 紧凑 | 无时间戳，最短 |

### 窗口主题风格 / Window themes

| 风格 | 说明 |
|---|---|
| `light` 浅色 | 白底深字 |
| `dark` 深色 | 黑底浅字 |
| `system` 跟随系统 | 自动匹配深浅 |
| `blue` 蓝调 | 深蓝沉稳 |

### 价格显示单位 / Price units

| 单位 | 说明 | 示例 |
|---|---|---|
| `auto` 自动 | 同时显示美元和人民币 | `$0.6/1M = ¥0.0426/万token` |
| `usd_per_1m` | 官方美元口径 | `$0.6/1M` |
| `cny_per_10k` | 人民币 / 万token，直观感受一分钱 | `¥0.0426/万token` |
| `cny_per_1m` | 人民币 / 百万token，官方口径 | `¥4.26/百万token` |

> 注：当前版本的主脚本实际弹窗仍用系统原生通知（最稳定）；自定义风格弹窗样式通过 `style_preview.html` 预览展示，供未来 GUI 版本参考。

---

## 📦 快速开始 / Quick Start

### 环境要求 / Requirements

- Python 3.8+（无需安装任何第三方包 / No third-party packages needed）
- 能访问 `api-docs.deepseek.com` 的网络

### 1. 下载 / Download

```bash
git clone https://github.com/EstellaHeroise/Give-You.git
cd Give-You
git checkout tool-deepseek
```

> 项目托管在作品集仓库 `Give-You` 的 `tool-deepseek` 分支。
> The project lives in the `tool-deepseek` branch of the portfolio repo `Give-You`.

（或者直接下载 ZIP 解压 / Or just download the ZIP and extract it。）

### 2. 首次运行：建立价格基线 / First run: create baseline

```bash
python deepseek_price_alert.py --init
```

这会抓取当前官方价格并保存为基线，作为以后对比的起点。
This fetches the current official prices and saves them as the baseline.

### 3. 手动检查一次 / Run a one-time check

```bash
python deepseek_price_alert.py --once
```

如果发现价格比基线**低**，会弹出系统通知并写入日志。
If any price is lower than the baseline, you'll get a desktop notification + log entry.

### 4. 查看历史 / View price history

```bash
python deepseek_price_alert.py --history
```

### 5. 检查更新 / Check for updates

```bash
python deepseek_price_alert.py --check-update
```

脚本会访问 GitHub Releases API，发现新版本时提示下载。

---

## 🔄 自动更新检测 / Auto Update Check

项目已内置**自动更新检测**：

- **主脚本**：每次执行检查（`--once` / 开机 / 定时）时，静默检测 GitHub 最新版本；有新版本才提示，无更新不打扰。
- **安装向导**：每次启动时检测最新安装包版本，发现新版打印提示。
- **手动检查**：随时运行 `python deepseek_price_alert.py --check-update`。

> 说明：GitHub 仓库地址已配置为 `EstellaHeroise/Give-You`（`tool-deepseek` 分支）。检测功能配合 GitHub Releases 发布使用。当前仅提示，不自动下载替换（保持零依赖与安全）。

---

## ⏰ 开机提醒 + 每日定时提醒 / Startup & Daily Reminder

脚本内置了两种自动提醒功能，相互独立、可分别开关：

### 🚀 开机提醒 / Startup reminder

设备每次开机启动后，自动触发一次价格检查，**有降价才提醒**（不打扰）。

```bash
# 启用开机提醒
python deepseek_price_alert.py --setup-startup

# 取消开机提醒
python deepseek_price_alert.py --remove-startup
```

实现原理：在 Windows「启动」文件夹创建静默运行脚本，开机后自动执行 `--once`。

### ⏰ 每日定时提醒 / Daily reminder

每天固定时间自动触发一次价格检查，**有降价才提醒**。

```bash
# 启用每日定时提醒（例如每天 09:30）
python deepseek_price_alert.py --setup-schedule 09:30

# 取消每日定时提醒
python deepseek_price_alert.py --remove-schedule
```

实现原理：通过 Windows 任务计划程序创建每天运行一次的定时任务。

### 🔔 提醒方式 / Reminder channel

通过 `config.json` 的 `reminder_channel` 字段选择（可用 `style_picker.html` 或手动编辑）：

| 值 | 效果 |
|---|---|
| `popup` | 仅弹窗（默认，安静） |
| `popup_sound` | 弹窗 + 系统提示音（更醒目） |

### 📋 查看提醒状态

```bash
python deepseek_price_alert.py --status
```

显示开机提醒、每日定时提醒是否已启用，以及当前提醒方式。

> 提示：以上三个命令仅 Windows 支持。macOS / Linux 可用系统自带的 launchd / cron 实现同样的定时效果。

---

## 📊 输出示例 / Example output

```
[2026-10-30 02:09:21] 📉 deepseek-flash output_offpeak: $0.9 -> $0.6 (-33.3%)
[2026-10-30 02:09:21] 📉 deepseek-flash output_peak: $1.8 -> $1.2 (-33.3%)
[2026-10-30 02:09:21] 触发降价提醒 / Price drop alert triggered:
📉 deepseek-flash output_offpeak: $0.9 -> $0.6 (-33.3%)
📉 deepseek-flash output_peak: $1.8 -> $1.2 (-33.3%)
```

---

## 🗂 项目结构 / File structure

```
deepseek-price-alert/
├── deepseek_price_alert.py   # 主脚本 / Main script
├── style_preview.html        # 风格纯预览页 / Style preview page
├── style_picker.html         # 风格选择页(点击选择, 生成 config) / Style picker page
├── config.json               # 风格配置(由选择器生成) / Style config (generated)
├── price_history.json        # 价格历史快照（自动生成）/ Price history (auto-generated)
├── monitor.log               # 运行日志 / Log file
├── installer.py              # 二合一安装向导(后端) / All-in-one installer (backend)
├── installer.html            # 图形安装页面(前端) / Installer GUI page
├── install.bat               # Windows 双击启动安装向导 / Installer launcher (Windows)
├── build_release.py          # 打包安装包脚本 / Release packaging script
├── desktop/                  # 桌面通用版文件(打包用) / Desktop edition files (for packaging)
├── skill/                    # WorkBuddy 版文件(打包用) / WorkBuddy edition skill files
├── dist/                     # 生成的安装包 / Built release zips
├── CHANGELOG.md              # 更新日志 / Changelog
├── README.md                 # 本文档 / This doc
└── LICENSE                   # 原创使用许可 / Original Works License
```

---

## ⚠️ 说明 / Notes

- 价格数据来自 DeepSeek 官方文档页面，抓取解析可能因页面改版而失效；如失效欢迎提 Issue。
- 本项目**非 DeepSeek 官方**出品，与 DeepSeek / 幻方无任何从属关系。
- 价格仅供参考，实际计费以 DeepSeek 官方为准。
- 只监控"官方定价页上的价格变化"。官方若通过公告/活动页发布限时降价，需要额外抓取公告源，属扩展功能（欢迎 PR）。

---

## 🤝 贡献 / Contributing

欢迎提 Issue、PR，或者 star ⭐ 支持！如果你想加新功能（比如 Server酱/微信/邮件通知、活动公告监控），直接开 PR 就好。
如果你在它的基础上做了修改、二次开发，请记得**告知作者**（见下方联系方式），让作者知道你的创意。

---

## 📄 许可证 / License

**本作品由 久禾 原创，欢迎在它的基础上继续创作；若作修改，请让作者知晓。**

本项目采用**原创使用许可**（Original Works License），非 MIT 协议。核心条款：

- ✅ 免费使用
- ✅ 允许修改与二次开发
- 📣 **修改并分发时，请提前告知作者**
- ℹ️ 修改版本请保留本许可声明与出处

完整条款见 [LICENSE](LICENSE)。

### 联系作者 / Contact

- B站：伊斯-Estella → https://space.bilibili.com/476132546
- 邮箱：estellaheroise@foxmail.com
- 微信：Heroise-9632

---

*Made with ❤️ for the DeepSeek API community.*