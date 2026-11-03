# Changelog / 更新日志

本项目所有重要变更都会记录在此文件中，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 风格，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)（语义化版本）。

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v0.9.4] - 2026-11-04

### 修复 / Fixed
- **卸载后残留空文件夹，必须手动再删一次**：后台清理进程的「当前工作目录」正好是待删文件夹，而 Windows 不允许删除任何进程的当前工作目录，于是 `rd /s /q` 删光了里面的文件、却删不掉文件夹本身，留下一个空壳。
  现在卸载脚本先 `cd /d "%TEMP%"`，清理脚本开头也先切目录，并把删除重试 5 次（防止杀毒软件正在扫描、文件句柄未释放）
- 卸载脚本的步骤编号与提示文字同步更新（4 步 → 5 步）

### 新增 / Added
- **`改风格.bat` + `desktop/style_tool.py`（一键改风格）**：双击打开一个只在本机可见的页面，当前设置已预选，改完点「保存并生效」直接写入 `config.json`。
  不重装任何程序文件、不动价格历史，保存成功后服务自动关闭
  - 只提供主脚本真正读取的三项（终端输出 / 价格单位 / 提醒方式），与安装向导保持一致，不提供选了也不生效的项
  - 非法值丢弃、非法请求不写盘；`config.json` 里其它字段（如 `window_theme`）原样保留

### 变更 / Changed
- 安装结果新增 `helpers` 字段，记录 `uninstall.bat` / `改风格.bat` 的实际落地路径
- 安装包内新增 `改风格.bat`、`desktop/style_tool.py`

## [v0.9.3] - 2026-11-03

### 新增 / Added
- **风格选择合并进安装向导**：安装页面里新增「🎨 想换个提醒的样子吗？」区块，展开即可选终端输出风格、价格显示单位、提醒方式，**点「开始安装」时直接写进 `config.json`**。装完就是配好的，不用再单独打开 `style_picker.html` 再把下载的 `config.json` 手动拖进安装目录（那是最容易卡住的一步）
- 安装向导内可直接打开风格预览页：新增 `GET /style_preview` 与 `GET /style_picker` 路由，页面里的链接点开即看，不必去翻安装包文件夹

### 变更 / Changed
- **只提供真正生效的选项**：`notification_style`（通知外观）与 `window_theme`（窗口主题）在主脚本里并未被读取，因此**不放进安装向导的可选列表**，改为链接到预览页展示，避免「选了却不生效」。可选的三项为 `terminal_style` / `price_unit` / `reminder_channel`，均在主脚本中有实际调用点
- **重装不冲掉用户已有风格**：只有用户真正点过的项目才会提交；没点过的、或先前手动改过的配置原样保留（`config.json` 已存在且未提交风格时不做覆盖）
- 安装结果里新增 `configs` 字段，页面上会显示风格写入的具体路径

### 修复 / Fixed
- `installer.html` 版本号兜底值仍硬编码为 `0.5.0`，接口取不到时页面会露出旧版本号，已改为 `0.9.3`

## [v0.9.2] - 2026-11-03

### 修复 / Fixed
- **开机自启指向错误的 Python**：以前写进启动文件夹的路径是「安装包解压目录」里的 Python，用户一旦删掉安装包，开机自启就静默失效（不报错、就是不提醒了）。现在优先指向安装目录内的 `python\python.exe`，与安装包解压目录无关
- **每日定时提醒同样的路径问题**：计划任务也改为指向安装目录内的内置 Python
- **WorkBuddy 技能版本号**：`SKILL.md` 里还写着 `version: 0.8.0`，已校正为当前版本

### 新增 / Added
- **一键卸载脚本 `uninstall.bat`**：安装后放在安装根目录，双击即可清理 — 停止本工具进程（按命令行精确匹配，不影响其它 Python 程序）、移除开机自启、删除每日定时任务、删除 WorkBuddy 技能、删除程序文件夹

### 变更 / Changed
- 安装包内新增 `uninstall.bat`

## [v0.9.1] - 2026-11-02

### 变更 / Changed
- **启动器改为在当前窗口运行**：不再用 `start` 另开一个一闪而过的窗口，安装服务的日志、报错全部留在黑窗里，失败时窗口会停住并显示错误（便于截图反馈）
- **端口被占用自动顺延**：默认 8765 被占用（常见于上一次安装窗口没关）时，自动在 8765~8774 之间找空闲端口，并在日志里说明改用了哪个
- **中文不再乱码**：install.bat 开头加 `chcp 65001`，黑窗里的中文提示正常显示
- **找不到内置 Python 时给出可操作提示**：明确指出「多半是只解压了 install.bat」以及正确解压步骤
- 更新检查遇到 404（仓库暂无 Releases）时不再打印「检查更新失败」，避免误导

### 文档 / Docs
- README 补充：0.9.1 及以后无需安装 Python；0.8.0 需要系统 Python，建议直接使用最新版

## [v0.9.0] - 2026-11-01

### 新增 / Added
- 内置便携 Python：安装包自带 Windows 便携 Python（瘦身后约 31MB），下载解压双击即可用，无需用户自行安装 Python
- 自动生成 run.bat：安装完成后直接双击 run.bat 即可运行（内部使用内置 Python）；开机自启 / 定时任务自动指向内置 Python
- 安装界面支持自定义安装路径（auto-dir 输入框）

### 变更 / Changed
- 启动器洗白：重写 install.bat，去掉静默后台启动、一股脑清空代理变量等易被杀软误报的特征；健康检查改用 curl --noproxy
- 默认安装路径：桌面版默认 D:\deepseek-price-alert；WorkBuddy 版默认 ~/.workbuddy/skills/deepseek-price-alert（WorkBuddy 自动识别）

### 文档 / Docs
- README 新增「被杀软拦截怎么办」说明；版本号升级至 0.9.0

## [v0.4] - 2026-10-30

### 新增 / Added

- 🚀 **开机提醒**：设备每次开机自动触发一次价格检查（Windows「启动」文件夹 + VBS 静默运行）
  - Startup reminder: auto-run a price check on every boot (Windows Startup folder + silent VBS).
  - `python deepseek_price_alert.py --setup-startup` 启用
  - `python deepseek_price_alert.py --remove-startup` 取消
- ⏰ **每日定时提醒**：用户设定固定时间，每天到点自动检查一次价格（Windows 任务计划程序）
  - Daily scheduled reminder via Windows Task Scheduler.
  - `python deepseek_price_alert.py --setup-schedule 09:30` 启用（时间可自定义）
  - `python deepseek_price_alert.py --remove-schedule` 取消
- 🔔 **提醒方式选择**：通过 `config.json` 的 `reminder_channel` 字段选择
  - Reminder channel: `popup`（仅弹窗，默认）/ `popup_sound`（弹窗 + 系统提示音）。
- 📋 **状态查看**：`--status` 一键显示开机提醒、每日定时提醒、当前提醒方式是否已启用
  - Status command: check startup / daily reminder / reminder channel at a glance.
- 🧩 **开机提醒与每日定时提醒相互独立**，可分别开关、互不影响
  - Startup reminder and daily reminder are fully independent.

### 说明 / Notes

- 定时任务通过 Windows 任务计划程序（schtasks）创建，为跨平台通用实现预留了接口；macOS / Linux 用户可用系统自带的 launchd / cron 实现同样的效果。

---

## [v0.3] - 2026-10-30

### 新增 / Added

- 💰 **价格显示单位可自选**（`--unit` 配置，通过 `config.json` 的 `price_unit` 字段）
  - User-selectable price display unit.
  - `auto`：自动同时显示美元与人民币（默认，如 `$0.6/1M = ¥0.0426/万token`）
  - `usd_per_1m`：官方美元口径 `$X/1M`
  - `cny_per_10k`：人民币 / 万token（直观感受"一分钱一万token"）
  - `cny_per_1m`：人民币 / 百万token（官方口径）
- 🎨 `style_picker.html` 新增「④ 价格显示单位」选择区，带实时预览，保存时一并写入 `config.json`
  - Style picker gains a price-unit selector with live preview.

### 内部实现 / Internal

- 新增换算函数 `to_cny_per_10k(usd_per_1m, rate)`：`usd / 100 * rate`
- 新增 `format_price_for_display(price, unit, rate)` 统一格式化输出

---

## [v0.2] - 2026-10-30

### 新增 / Added

- 💱 **均价双口径显示**：同时展示 `$ / 1M tokens`（官方口径）与 `¥ / 万token`（直观口径）
  - Dual-currency price display: USD per 1M tokens + CNY per 10K tokens.
- 🔥 **大额优惠重点提醒**：降幅 ≥50% **或** 折算价达到 `¥0.01/万token`（一分钱级）时，自动加 🔥 重点标记
  - Big-deal highlight: drop ≥50% or penny-level price (≤¥0.01/10K tokens) gets a 🔥 mark.
- 📢 **官方公告监控**：自动抓取 DeepSeek 官方 `/updates` 公告列表，发现降价 / 优惠 / 新模型公告立即提醒
  - Official `/updates` announcements monitoring.
- 🎨 **风格预览与选择**：
  - `style_preview.html`：纯预览页，一次性展示全部 12 种风格（通知弹窗 / 终端输出 / 窗口主题 三组 × 4 款），通知弹窗同时预览「系统原生弹窗」与「自定义风格弹窗」
  - `style_picker.html`：交互选择页，点击卡片选择风格，保存时下载 `config.json`，主脚本自动应用

### 变更 / Changed

- 提醒弹窗文案升级：包含模型名、价格变化、降幅百分比
- 终端输出支持 4 种风格（`log` / `table` / `color` / `compact`）

---

## [v0.1] - 2026-10-30

### 初始版本 / Initial release

- 🎯 **核心功能**：零第三方依赖的 Python 脚本，监控 DeepSeek 官方 API 定价页（`api-docs.deepseek.com/quick_start/pricing`）
  - Zero-dependency Python script monitoring the official DeepSeek pricing page.
- 🔔 **降价自动提醒**：检测到价格下降立即弹窗通知 + 写入日志
  - Desktop notification + log on price drop.
- 📜 **价格历史记录**：`price_history.json` 保存价格快照，`monitor.log` 记录运行日志
  - Local price history and run logs.
- 💻 **命令行接口**：`--init`（建立基线）、`--once`（检查一次）、`--history`（查看历史）
  - CLI: `--init` / `--once` / `--history`.
- 🌍 **跨平台通知**：Windows（`MessageBoxW`）、macOS（`osascript`）、Linux（`notify-send`）
  - Cross-platform native notifications.
- 📄 **开源化准备**：`README.md`（中英双语）、`LICENSE`（MIT）、`.gitignore`
  - Open-source ready: bilingual README, MIT license, .gitignore.

---

## [v0.5] - 2026-10-30

### 新增 / Added

- 📦 **二合一安装包**：一个 ZIP 安装包同时包含「桌面通用版」与「WorkBuddy 适配版」，下载一次即可选择安装
  - All-in-one installer ZIP bundling both the Desktop Edition and the WorkBuddy Edition.
- 🖥️ **图形安装向导**（`installer.py` + `installer.html` + `install.bat`）：双击 `install.bat` 自动打开本地网页，展示两个版本卡片供选择，一键完成安装
  - GUI installer: a local web page (`http://127.0.0.1:8765`) with two edition cards; one-click install.
  - 可选「开机自启」「同时安装桌面联动程序」「自定义安装目录」等选项
- 🤖 **WorkBuddy Skill 版**：新增 `SKILL.md`，安装为 WorkBuddy 用户级 skill（`~/.workbuddy/skills/deepseek-price-alert`），对话中直接触发「DeepSeek 降价了吗」等指令
  - WorkBuddy Skill edition: installs into WorkBuddy's user skills directory and can be triggered in chat.
- 🔧 **打包脚本**（`build_release.py`）：一条命令生成 `dist/deepseek-price-alert-setup-<version>.zip`
  - Release packaging script: build the all-in-one ZIP with one command.

### 结构说明 / Structure

- `desktop/`：桌面通用版文件（主脚本 + 风格页 + 文档）
- `skill/`：WorkBuddy 版文件（SKILL.md + 主脚本 + 风格页）
- 两个版本安装目录完全分离，互不冲突（桌面版 `~/deepseek-price-alert/desktop`，WorkBuddy 版 `~/.workbuddy/skills/deepseek-price-alert`）

---

## [v0.6.0] - 2026-10-30

### 新增 / Added

- 🔄 **自动更新检测**：脚本与安装向导启动时自动检查 GitHub 最新版本，发现新版提示下载
  - Auto update check: the script and installer query the GitHub latest release and notify when a new version exists.
- 💻 **新增命令 `--check-update`**：手动检查是否有新版本
  - New CLI command `--check-update` for manual update checks.
- 📢 **安装向导启动时检测更新**（`installer.py`），打印最新版本提示
  - The installer also checks for updates on startup.

### 说明 / Notes

- 检测逻辑内置在 `deepseek_price_alert.py` 与 `installer.py` 中：
  - 主脚本每次 `--once` / 开机 / 定时检查时静默检测，**有新版才提示**，无更新不打扰
  - 安装向导启动时检测一次，发现新版打印下载地址
- GitHub 仓库地址已配置为 `EstellaHeroise/Give-You`（`tool-deepseek` 分支），配合 GitHub Releases 发布即可使用自动更新检测
- 当前仅**提示**，不自动下载替换（保持零依赖与安全）；未来可扩展为自动下载安装包

---

## [v0.7.0] - 2026-10-30

### 变更 / Changed

- 📜 **许可证变更**：由 MIT 协议改为**原创使用许可**（Original Works License）
  - License changed from MIT to the **Original Works License**.
- 核心条款：
  - ✅ 免费使用
  - ✅ 允许修改与二次开发
  - 📣 **修改并分发时，请提前告知作者**
  - ℹ️ 修改版本请保留本许可声明与出处
- 📇 **作者联系方式**：B站 伊斯-Estella / 邮箱 estellaheroise@foxmail.com / 微信 Heroise-9632
  - Author contact info added to LICENSE and README.
- 原创声明沿用作品集定稿措辞：「本作品由 久禾 原创，欢迎在它的基础上继续创作；若作修改，请让作者知晓。」

### 说明 / Notes

- 此许可是**源码可见、免费使用、二改需告知作者**的专属许可，非 MIT 宽松许可，也非"完全不开源"。
- LICENSE / README / desktop / skill 各副本已同步更新。

---

## [v0.8.0] - 2026-10-31

### 新增 / Added

- 🧹 **安装后自动删除安装包**：安装向导新增「安装完成后自动删除下载的安装包」选项（默认勾选），安装成功后可自动删除 ZIP 与解压目录，不留垃圾文件。
  - Auto-cleanup: after a successful install, the installer can delete the downloaded ZIP and its unpacked folder (optional, on by default).
- 🏷️ **源码原创声明**：主脚本开头加入定稿死代码声明「本作品由 久禾 原创，二改后请告知作者。 · 第一版 · 2026.10.30」
  - Original-work notice added at the top of the main script.

### 变更 / Changed

- 版本号同步升级至 v0.8.0（主脚本 / 安装向导 / 打包脚本 / SKILL.md）。
- `install.bat` 启动时自动定位并传递安装包 ZIP 路径给安装器（通过环境变量 `DEEPSEEK_ALERT_SETUP_ZIP`），安装成功后精确删除该 ZIP。

### 说明 / Notes

- 自动清理功能受保护：不会误删用户主目录、源码项目目录；仅在安装成功后执行。
- 用户可在安装界面取消勾选「安装完成后自动删除下载的安装包」来保留安装包。

---

## 🔮 后续计划 / Planned

- [x] 推送 GitHub 开源（已完成：托管于 `EstellaHeroise/Give-You` 的 `tool-deepseek` 分支，占位符已全部替换）
- [ ] Server酱 / 微信 / 邮件 / Bark 等更多通知渠道
- [ ] 限时活动页（非定价页）的降价监控
- [ ] GUI 版本（将 `style_preview.html` 中预览的自定义弹窗风格落地为真实弹窗）

---

*本文件会随每次功能更新持续追加记录。*
*This file is maintained with every release.*