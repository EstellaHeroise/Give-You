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
| 🖥️ **桌面通用版** / Desktop | 独立运行的桌面程序，不依赖任何 AI 平台 | `D:\deepseek-price-alert\desktop`（安装时可自定义） |
| 🤖 **WorkBuddy 适配版** / WorkBuddy | 已安装 WorkBuddy 的用户，对话中直接触发检查 | `~/.workbuddy/skills/deepseek-price-alert`（WorkBuddy 自动识别） |

### 使用方法 / How to install

1. 下载 `deepseek-price-alert-setup-<version>.zip` 并解压
2. 双击 `install.bat`（Windows），或运行 `python installer.py`
3. 浏览器自动打开图形安装向导
4. 选择 **桌面通用版** 或 **WorkBuddy 适配版**（可勾选开机自启、同时安装桌面联动程序、安装后自动删除安装包等选项）
5. 点击「开始安装」，自动完成文件复制与配置
6. （默认开启）安装完成后自动删除下载的 ZIP 与解压目录，不留垃圾文件

> 安装向导为本地网页（`http://127.0.0.1:8765`），不上传任何数据。
> 若想保留安装包，在安装界面取消勾选「安装完成后自动删除下载的安装包」即可。
>
> 如果黑窗里提示「端口 8765 被占用」，不用管，安装向导会自动换到 8766~8774 里的空闲端口，并把这行地址打印出来。

**⚠️ 请优先使用最新版（0.9.1 及以后）**：这些版本内置便携 Python，解压双击即可用，电脑上装不装 Python 都行。
**0.8.0 及更早的版本没有内置 Python**，需要电脑里已经装好 Python 3.8+ 并加入 PATH，否则双击 `install.bat` 后黑窗会提示找不到 Python、浏览器也不会打开。除非有特殊理由，不要在 0.8.0 上排查问题。

**安装完成后如何运行桌面版**：前往 `D:\deepseek-price-alert\desktop`，双击 `run.bat` 即可（同样无需安装 Python，它用的是安装时自带的内置 Python）。首次运行请先执行一次 `run.bat --init` 建立价格基线。

### WorkBuddy 适配版使用方式

安装后，在 WorkBuddy 对话中输入以下指令即可触发：

- 「DeepSeek 降价了吗？」→ 自动运行 `--once` 检查
- 「查看 DeepSeek 价格历史」→ 自动运行 `--history`
- 「设置 DeepSeek 开机提醒」→ 自动运行 `--setup-startup`

---

### 卸载 / Uninstall

装好之后，**安装根目录**（默认 `D:\deepseek-price-alert\`）里会有一个 **`uninstall.bat`**，双击它就能一键清理：

1. 停止本工具的进程（按命令行精确匹配，不会误杀你其它的 Python 程序）
2. 移除开机自启
3. 删除每日定时提醒
4. 删除 WorkBuddy 技能（如果装过）
5. 删除程序文件夹

卸载完成后**建议重启一次电脑**，确认右下角不再弹出提醒。

> 手动卸载也行，共 4 处，删完即可：
> 1. 安装目录（默认 `D:\deepseek-price-alert`）
> 2. 启动文件夹里的 `deepseek_price_alert.vbs`（`Win + R` 输入 `shell:startup` 可直接打开）
> 3. `%USERPROFILE%\.workbuddy\skills\deepseek-price-alert`（WorkBuddy 技能版）
> 4. 解压出来的安装包文件夹（不是程序本体，可删可留）

---

## 🆕 更新日志 / Changelog

### v0.9.2（2026-11-03）
- 🐛 **修开机自启失效的隐藏 Bug**：以前自启脚本里写的是「安装包解压目录」里的 Python，用户一删安装包，开机提醒就**静默失效**（不报错、就是不提醒了）。现在统一指向安装目录内的内置 Python
- 🐛 **每日定时提醒同一问题一并修复**
- 🧹 **新增一键卸载 `uninstall.bat`**：双击即清理进程 / 自启 / 定时任务 / WorkBuddy 技能 / 程序文件夹
- 🏷️ WorkBuddy 技能 `SKILL.md` 里的版本号从 `0.8.0` 校正为当前版本

### v0.9.1（2026-11-02）
- 🪟 **报错不再一闪而过**：`install.bat` 改成在当前窗口里直接运行安装服务，日志和报错全部留在黑窗中，失败时窗口会停住等你截图
- 🔌 **端口占用自动顺延**：8765 被占用时自动改用 8766~8774 的空闲端口，并在日志里写明改用了哪个
- 🈶 **中文不再乱码**：`install.bat` 开头加 `chcp 65001`
- 💡 **找不到内置 Python 时给出可操作提示**：直接告诉用户「多半是只解压了 install.bat」以及正确的解压步骤
- 🔇 更新检查遇到 404（仓库暂无 Releases）时不再打印「检查更新失败」，避免误导

### v0.9.0（2026-11-01）
- 🐍 **内置便携 Python**：安装包自带 Windows 便携 Python（瘦身后约 31MB），下载解压双击即可用，**无需用户自行安装 Python**
- 🧹 **启动器洗白**：重写 `install.bat`，去掉"静默后台启动""一股脑清空代理变量"等易被杀软误报的特征；健康检查改用 `curl --noproxy`，避免本机代理干扰
- 🚀 **自动生成 run.bat**：安装完成后可直接双击 `run.bat` 启动（内部用内置 Python）；开机自启 / 定时任务也会自动指向内置 Python
- 📁 **默认安装路径调整**：桌面版默认装到 `D:\deepseek-price-alert`（安装界面可自定义）；WorkBuddy 版默认装到 `~/.workbuddy/skills/deepseek-price-alert`（WorkBuddy 自动识别）
- 🛡️ **文档新增「被杀软拦截怎么办」**：说明浏览器 / Defender / SmartScreen 误报的处理方法
- 📦 安装包新增 `python/`（内置运行时），整包约 9.8MB

### v0.8.0
- 二合一安装包（桌面版 + WorkBuddy 版），图形化本地网页安装向导
- 自动更新检测、开机提醒、每日定时提醒

---

## ✨ 特性 / Features

- 🎯 **只监控 DeepSeek 官方 API 定价**（`api-docs.deepseek.com/quick_start/pricing`），不是第三方转售平台
- 🔔 **降价自动弹窗提醒**（Windows / macOS / Linux 原生通知，无需任何第三方库），可选弹窗+系统提示音
- 🚀 **开机提醒**：设备每次开机自动检查一次价格，有降价才提醒
- ⏰ **每日定时提醒**：设定固定时间，每天到点自动检查一次价格
- 💰 **价格单位可自选**：`$ / 1M tokens`（官方口径）、`¥ / 万token`（直观感受"一分钱一万token"）、`¥ / 百万token`，或自动同时显示两种
- 🔥 **大额优惠重点提醒**：降幅 ≥50% **或** 价格达到 `¥0.01/万token`（一分钱级）时，自动用 🔥 重点标记
- 📢 **官方公告监控**：自动监控 DeepSeek 官方 `/updates` 公告列表，发现降价/优惠/新模型公告立即提醒
- 🎨 **风格在安装时就能选**（v0.9.3 起）：安装向导里展开「🎨 想换个提醒的样子吗？」即可选终端输出风格、价格显示单位、提醒方式，装完即生效，无需手动搬配置文件；另有 `style_preview.html`（12 种风格纯预览）与 `style_picker.html`（装完想改时用）
- 📜 **价格历史自动记录**（`price_history.json`），涨价也会记录（仅日志，不弹窗）
- 🐍 **纯 Python 标准库，零依赖** —— clone 下来就能跑，不用 `pip install` 任何东西
- 🌍 **跨平台**：Windows / macOS / Linux 都支持
- 💻 **命令行友好**：`--init`、`--once`、`--history`、`--version`、`--help`、`--check-update`、`--setup-startup`、`--remove-startup`、`--setup-schedule HH:MM`、`--remove-schedule`、`--status`
- 🔄 **自动更新检测**：脚本与安装向导启动时自动检查 GitHub 最新版本，发现新版提示下载（配合 GitHub Releases 使用）
- 🧹 **安装后自动清理**：安装完成后可自动删除下载的安装包（ZIP）与解压目录，省空间、不留垃圾文件（可在安装界面取消勾选）

---

## 🎨 风格选择 / Style Picker

### 推荐：在安装向导里直接选（v0.9.3 起）

双击 `install.bat` 打开安装页面后，展开中间那一栏「🎨 想换个提醒的样子吗？」，点你喜欢的卡片，然后点「开始安装」。

选好的风格会由安装程序**直接写进 `config.json`**，装完打开就是你要的样子 —— 不需要再去下载一个 `config.json` 再手动拖进安装目录。

可选的只有**主脚本真正会读取**的三项：

| 配置项 | 作用 | 可选值 |
|---|---|---|
| `terminal_style` | 命令行里的输出排法 | `log` 日志 / `table` 表格 / `compact` 紧凑 |
| `price_unit` | 价格用哪种口径显示 | `auto` 自动 / `usd_per_1m` / `cny_per_10k` / `cny_per_1m` |
| `reminder_channel` | 弹窗时要不要响 | `popup` 只弹窗 / `popup_sound` 弹窗+声音 |

> 安装向导里也会给出「风格预览页」的链接，点开即可看全部 12 种风格（弹窗 4 · 终端 4 · 主题 4）。
>
> ⚠️ **说明**：`notification_style`（自定义弹窗外观）与 `window_theme`（窗口主题）目前**主脚本并未读取**，所以安装向导里不提供这两个选项，只在预览页展示。选了不生效的选项比没有选项更误导人，因此暂不开放。

### 装完之后想改风格

- **重新跑一次安装包**：再选一次，覆盖写入 `config.json` 即可（不会动你的价格历史）
- **或者打开 `style_picker.html`**：点击选择后由浏览器下载一个 `config.json`，手动放到工具目录（与 `deepseek_price_alert.py` 同级）。这一路径仍保留，作为不重装时的兜底
- **或者直接编辑 `config.json`**：字段就是上表那几项，改完存盘，下次运行生效

### 预览全部风格

打开 `style_preview.html` 可**纯预览**全部风格（三组 × 4 种），通知弹窗同时展示「系统原生弹窗」和「自定义风格弹窗」两种方式。

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

- **无需安装 Python**：安装包已内置便携 Python，双击 `install.bat` 即可，安装后工具自带运行环境
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

## 🛡️ 关于杀毒软件 / 如果被拦截怎么办

本工具**不含任何恶意代码**，但安装包里的 `install.bat`（批处理脚本）和内置的 Python 运行环境，有时会被 Windows Defender / 浏览器「误报」或「拦截」。这是免费、未签名小工具的常见现象，并非真的有毒。

如果下载或运行时遇到拦截，按下面处理：

- **浏览器提示「此文件可能有害」**：这是下载标记（Mark of the Web）的常规警告，点「保留」/「仍要下载」即可。
- **Windows Defender 删除 / 拦截 `install.bat` 或 `python`**：打开 Windows 安全中心 → 病毒和威胁防护 → 保护历史记录 → 找到本工具相关项 → 「允许」/「还原」。
- **SmartScreen 提示「Windows 已保护你的电脑」**（多见于 .exe，本安装包是脚本，较少出现）：点「详细信息」→「仍要运行」。
- **实在不放心**：本工具全部是可读的 Python 源码（`installer.py` / `deepseek_price_alert.py`），可自行用任意杀软或 virustotal.com 扫描，也可在 GitHub 查看完整源码。

> 为什么会被误报？杀软靠「行为像不像坏软件」来判断。安装器会启动本地网页服务、往用户目录写文件——这些行为「长相」和某些病毒相似，所以可能被拦。我们已经把脚本写得尽量透明（不隐藏窗口、不乱改系统设置）。

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