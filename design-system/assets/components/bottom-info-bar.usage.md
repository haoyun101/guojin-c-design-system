# bottom-info-bar · 轻量用法说明

> 目的:给 AI 生成一级页面时低成本复用 `bottom-info-bar.html`,避免默认全文读取 250KB 参考实现。真源仍是 `assets/components/bottom-info-bar.html`;本文件只写识别、状态映射和引用边界。

## 什么时候用

做一级页面底部导航时使用:首页 / 自选 / 交易 / 理财 / 我的。

不要把它和通用底导混用:
- 有悬浮智能体球 + 底部信息栏 = 用 `bottom-info-bar.html`
- 纯 N 等分白底条、无智能体球 = 用 `bottom-nav.html`

## 状态映射

| active tab | 信息栏 | 高度 | 说明 |
|---|---|---:|---|
| 首页 | 异动通知 | 60 | 实时图标 + 异动文字 |
| 自选 | 个股异动 | 84 | 可展开到盯盘面板 |
| 自选展开 | 盯盘面板 | 356 | 盯异动 / 盯主力 / 新理财等内容 |
| 我的 | 大家都在看 | 60 | 推荐文字 + `dajia-zaikan` 切图 |
| 交易 | 无信息栏 | 0 | 只保留底导 |
| 理财 | 无信息栏 | 0 | 只保留底导 |

## 复用方式

整包 / 本地 HTML 交付:
- 在 BOM 中引用 `assets/components/bottom-info-bar.html`
- 资产走相对路径,不要把 `agent-orb-wave.svg` 或字体 base64 贴进上下文

单文件 / widget:
- 优先判断是否真的需要高保真底导
- 需要时用 `sandbox-header.html` 提供字体、tokens 和 sprite
- `agent-orb-wave.svg` 约 197KB,不要 base64 内联;用相对路径、外链或占位说明

## 常用类名

| 类名 | 用途 |
|---|---|
| `gj-ibnav` | 一级页面底部导航整体 |
| `gj-ibn-orb` | 悬浮智能体球 |
| `gj-ibn-tab` | 底导 tab |
| `gj-ibi60` | 60 高信息栏 |
| `gj-ibi84` | 84 高信息栏 |
| `gj-ibi-handle` | 个股异动 / 盯盘拖动条 |

## AI 读取边界

默认不要全文读取 `bottom-info-bar.html`。

只在以下情况读全文:
- 要修改 `bottom-info-bar.html` 本身
- 要排查该组件内部 bug
- 本文件、`component-quickcards.md`、`library-index.json` 都无法回答具体结构问题
- 需要像素级自检且必须确认内部实现细节

生成页面时只要能识别“一级页面底导 = bottom-info-bar”,并在 BOM 中钉到该文件即可。
