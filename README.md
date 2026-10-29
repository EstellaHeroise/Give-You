# DeepSeek Price Alert 🎉📉

> **Monitor DeepSeek official API pricing and get alerted when token prices drop.**
> **监控 DeepSeek 官方 API 价格，降价时自动提醒你。**

一个零依赖、跨平台的 DeepSeek 官方 API 降价提醒小工具。每天(或按你的计划)检查一次官方定价页，一旦发现 token 价格下降，立刻弹窗通知你，并自动记录价格变化历史。

A zero-dependency, cross-platform alert tool for DeepSeek official API price drops. It checks the official pricing page on your schedule, pops a desktop notification when token prices drop, and keeps a local price history automatically.

---

## ✨ 特性 / Features

- 🎯 **只监控 DeepSeek 官方 API 定价**（`api-docs.deepseek.com/quick_start/pricing`），不是第三方转售平台
- 🔔 **降价自动弹窗提醒**（Windows / macOS / Linux 原生通知，无需任何第三方库）
- 💰 **双口径均价**：同时显示 `$ / 1M tokens`（官方口径）和 `¥ / 万token`（人民币，直观感受"一分钱一万token"）
- 🔥 **大额优惠重点提醒**：降幅 ≥50% **或** 价格达到 `¥0.01/万token`（一分钱级）时，自动用 🔥 重点标记
- 📢 **官方公告监控**：自动监控 DeepSeek 官方 `/updates` 公告列表，发现降价/优惠/新模型公告立即提醒
- 🎨 **风格预览与选择**：提供 `style_preview.html`（纯预览）和 `style_picker.html`（点击选择并保存到 `config.json`），支持通知弹窗 / 终端输出 / 窗口主题三组风格
- 📜 **价格历史自动记录**（`price_history.json`），涨价也会记录（仅日志，不弹窗）
- 🐍 **纯 Python 标准库，零依赖** —— clone 下来就能跑，不用 `pip install` 任何东西
- 🌍 **跨平台**：Windows / macOS / Linux 都支持
- 💻 **命令行友好**：`--init`、`--once`、`--history`

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

> 注：当前版本的主脚本实际弹窗仍用系统原生通知（最稳定）；自定义风格弹窗样式通过 `style_preview.html` 预览展示，供未来 GUI 版本参考。

---

## 📦 快速开始 / Quick Start

### 环境要求 / Requirements

- Python 3.8+（无需安装任何第三方包 / No third-party packages needed）
- 能访问 `api-docs.deepseek.com` 的网络

### 1. 下载 / Download

```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/deepseek-price-alert.git
cd deepseek-price-alert
```

> 把 `<YOUR_GITHUB_USERNAME>` 替换成你自己的 GitHub 用户名。
> Replace `<YOUR_GITHUB_USERNAME>` with your own GitHub username.

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

---

## ⏰ 定时自动检查 / Schedule it

手动运行只是第一步。要真正"每天自动提醒"，请用系统自带的任务计划程序：

### Windows（任务计划程序 / Task Scheduler）

1. 打开「任务计划程序」（Win+R 输入 `taskschd.msc`）
2. 创建基本任务 → 触发器选「每天」→ 设置时间（比如 09:00）
3. 操作选「启动程序」，程序填：
   ```
   python
   ```
   参数填：
   ```
   D:\路径\到\deepseek-price-alert\deepseek_price_alert.py --once
   ```
4. 完成。之后每天到点自动检查一次。

### macOS（launchd） / Linux（cron）

macOS 用 `launchd`，Linux 用 `crontab`，网上有很多现成教程；核心就是把 `--once` 命令按计划跑起来。

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
├── README.md                 # 本文档 / This doc
└── LICENSE                   # MIT 协议
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

---

## 📄 许可证 / License

MIT License. See [LICENSE](LICENSE).

---

*Made with ❤️ for the DeepSeek API community.*