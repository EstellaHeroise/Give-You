# DeepSeek Price Alert 🎉📉

> **Monitor DeepSeek official API pricing and get alerted when token prices drop.**
> **监控 DeepSeek 官方 API 价格，降价时自动提醒你。**

一个零依赖、跨平台的 DeepSeek 官方 API 降价提醒小工具。每天(或按你的计划)检查一次官方定价页，一旦发现 token 价格下降，立刻弹窗通知你，并自动记录价格变化历史。

A zero-dependency, cross-platform alert tool for DeepSeek official API price drops. It checks the official pricing page on your schedule, pops a desktop notification when token prices drop, and keeps a local price history automatically.

---

## ✨ 特性 / Features

- 🎯 **只监控 DeepSeek 官方 API 定价**（`api-docs.deepseek.com/quick_start/pricing`），不是第三方转售平台
- 🔔 **降价自动弹窗提醒**（Windows / macOS / Linux 原生通知，无需任何第三方库）
- 📜 **价格历史自动记录**（`price_history.json`），涨价也会记录（仅日志，不弹窗）
- 🐍 **纯 Python 标准库，零依赖** —— clone 下来就能跑，不用 `pip install` 任何东西
- 🌍 **跨平台**：Windows / macOS / Linux 都支持
- 💻 **命令行友好**：`--init`、`--once`、`--history`

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