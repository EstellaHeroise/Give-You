---
name: deepseek-price-alert
display_name: DeepSeek 官方 API 降价提醒
display_name_en: DeepSeek Official API Price Drop Alert
description: 监控 DeepSeek 官方 API 定价页与官方公告，token 降价时提醒用户。支持查看当前价格、建立价格基线、单次检查、查看历史、设置开机自启/每日定时提醒。触发词：DeepSeek 降价、DeepSeek 价格、token 降价、查看 DeepSeek 价格、deepseek price、降价提醒、价格监控、deepseek-price-alert。
description_zh: 监控 DeepSeek 官方 API 定价页（api-docs.deepseek.com/quick_start/pricing）与官方公告（/updates），一旦 token 价格下降或官方发布降价/优惠公告，立即提醒用户。可查看当前各模型价格、价格历史、建立基线，并支持开机自启与每日定时提醒。零第三方依赖，纯 Python 标准库。
description_en: Monitor DeepSeek official API pricing page and announcements; alert the user when token prices drop. Supports viewing current prices, price history, baseline init, and one-time checks. Zero third-party dependencies (Python stdlib only).
category: 开发工具
version: 0.9.2
author: deepseek-price-alert
license: 原创使用许可 (Original Works License)
visibility: "public"
---

# DeepSeek 官方 API 降价提醒

监控 DeepSeek 官方 API 定价，token 降价时自动提醒用户。数据来自官方定价页 `api-docs.deepseek.com/quick_start/pricing` 与官方公告 `/updates`，非第三方转售平台。

## 何时使用本技能

- 用户想知道 DeepSeek API 当前各模型的价格
- 用户想检查 DeepSeek 是否降价 / 有无优惠活动
- 用户想查看历史价格记录
- 用户想设置开机自启或每日定时提醒
- 用户说「DeepSeek 降价提醒」「token 降价」「查看 DeepSeek 价格」等

## 前置要求

- Python 3.8+（无需安装任何第三方包）
- 能访问 `api-docs.deepseek.com` 的网络

## 文件说明

本技能随安装包附带一个独立脚本 `deepseek_price_alert.py`，所有命令都通过它执行。脚本路径可由用户配置，默认与本 SKILL.md 同目录。

## 执行步骤

### 1. 定位脚本

脚本位于本技能目录下（`<skill_dir>/deepseek_price_alert.py`）。若用户自定义过安装路径，以 `config.json` 中的 `script_path` 为准。

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/deepseek_price_alert.py"
```

### 2. 根据用户意图选择命令

| 用户需求 | 命令 |
|---|---|
| 查看当前价格 / 检查是否降价 | `python "$SCRIPT" --once` |
| 建立价格基线（首次使用） | `python "$SCRIPT" --init` |
| 查看历史价格记录 | `python "$SCRIPT" --history` |
| 检查是否有新版本 | `python "$SCRIPT" --check-update` |
| 设置开机自启（Windows） | `python "$SCRIPT" --setup-startup` |
| 取消开机自启（Windows） | `python "$SCRIPT" --remove-startup` |
| 设置每日定时提醒（Windows） | `python "$SCRIPT" --setup-schedule 09:30` |
| 取消每日定时提醒（Windows） | `python "$SCRIPT" --remove-schedule` |
| 查看提醒功能状态（Windows） | `python "$SCRIPT" --status` |

### 3. 执行并解读输出

运行对应命令后，向用户解释结果：

- **`--once`**：若发现降价，输出会包含 `📉`（普通降价）或 `🔥`（大额优惠：降幅≥50% 或 ≤¥0.01/万token）标记，以及模型名、指标、新旧价格、降幅百分比。此时应主动提醒用户「DeepSeek 降价了」并给出具体条目。
- **`--once`**：若价格无变化，输出 `价格无下降变化 / No price drop detected.`，应告知用户当前价格稳定。
- **`--init`**：输出各模型价格基线，表示首次建立成功。
- **`--history`**：按模型打印历史价格，最后附已见公告数。
- **`--status`**：显示开机自启/每日定时提醒是否启用、当前提醒方式（popup 仅弹窗 / popup_sound 弹窗+声音）。

### 4. 处理错误

若命令返回非 0 退出码：

- 网络失败：`抓取/解析价格失败 / Fetch or parse failed: ...` → 检查网络或稍后重试。
- 时间格式错误：`定时提醒 --setup-schedule` 需 24 小时制 `HH:MM`。
- 非 Windows 平台：`开机自启目前仅支持 Windows` → 提示用户该功能仅 Windows 可用。

## 注意事项

- 价格数据来自 DeepSeek 官方文档页面，抓取解析可能因页面改版失效。
- 本技能非 DeepSeek 官方出品，价格仅供参考，实际计费以 DeepSeek 官方为准。
- 脚本会自动生成 `price_history.json`、`monitor.log`、`config.json` 到脚本所在目录。
- 提醒方式默认 `popup`（仅弹窗）；可通过 `style_picker.html` 或编辑 `config.json` 改为 `popup_sound`（弹窗+声音）。