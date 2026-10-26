# 图标体系 · Icons(Assets)

> skill 的图标资产与管理规范。**核心原则:按图标能否被字体承载,分两类管理。**

## 一、图标分类与选用规则(决策依据)

| 图标类型 | 特征 | 用什么格式 | 存放位置 | 引用方式 |
|---|---|---|---|---|
| **通用单色图标** | 线性/面性,纯单色,无渐变无动画(返回/搜索/设置/分享…) | **IconFont 字体** | `fonts/` | `<i class="iconfont icon-xxx">` |
| **渐变/特效图标** | 含渐变、内阴影等,字体无法承载(底部导航选中态…) | **SVG** | `bottom-nav/`、`gradient/` | 直接引用 .svg |
| **动画图标** | 含动效(呼吸/旋转/Lottie…) | **SVG+CSS / Lottie JSON** | `gradient/`(简单)或外部资源库(复杂) | 引用文件或写引用说明 |

**判断流程**:图标是纯单色且无动效 → 用字体(方案一);带渐变/特效/动画 → 用 SVG 或 Lottie(方案二)。**字体绝不能承载渐变与动画**,这是分类的根本原因。

## 二、方案一:IconFont 字体(通用图标)

- 字体文件:`fonts/iconfont.woff2`
- 样式表:`fonts/iconfont.css`(含 @font-face + 全部类名)
- **用法**:页面引入 iconfont.css,写 `<i class="iconfont icon-sousuo"></i>`;颜色用 CSS `color`(继承 currentColor)、大小用 `font-size`。顶部导航图标常用 `font-size:24px`(实现)= 48×48(750标注)。
- **扩展**:新增通用图标时,在 iconfont 平台更新字体库 → 替换 woff2 + 重新生成 css(需联网,由用户在 iconfont 操作后提供文件)。

### 常用图标(类名 · unicode · 含义)

| 类名 | unicode | 含义 |
|---|---|---|
| `icon-shibai` | \e633 | 失败 |
| `icon-shuoming` | \e634 | 说明 |
| `icon-shixinjiantou-shang` | \e635 | 实心箭头上 |
| `icon-huanyihuan` | \e637 | 刷新/换一换 |
| `icon-gengduo` | \e638 | 更多 |
| `icon-shezhi` | \e639 | 设置 |
| `icon-guanbi` | \e63a | 关闭 |
| `icon-cebianlan` | \e63d | 侧边栏/汉堡 |
| `icon-chenggong` | \e63f | 成功 |
| `icon-xiaoxi` | \e61e | 消息 |
| `icon-fenxiang` | \e620 | 分享 |
| `icon-rili` | \e623 | 日历 |
| `icon-pinglun` | \e624 | 评论 |
| `icon-sousuo` | \e626 | 搜索 |
| `icon-shixinjiantou-you` | \e628 | 实心箭头右 |
| `icon-shouqi` | \e629 | 收起 |
| `icon-weixin` | \e62a | 微信 |
| `icon-shijian` | \e62b | 时间 |
| `icon-guanzhu` | \e62c | 关注 |
| `icon-jiazixuan` | \e62d | 加自选 |
| `icon-shixinjiantou-zuo` | \e62f | 实心箭头左 |
| `icon-saoyisao` | \e630 | 扫一扫 |
| `icon-zhihuitou` | \e60c | 智能投顾/机器人 |
| `icon-tongzhi` | \e60d | 通知 |
| `icon-zhankai` | \e60f | 展开 |
| `icon-shixinjiantou-xia` | \e612 | 实心箭头下 |
| `icon-tuichu` | \e616 | **线性返回**(二级导航返回用此:线性 `<`;字面"退出"易误导,勿与实心 `icon-shixinjiantou-zuo` 混用)/ 退出 |
| `icon-shoucang` | \e619 | 收藏 |
| `icon-shanchuzixuan` | \e61a | 删除自选 |

### 其余图标
`icon-tianjia` · `icon-qiehuanheiban` · `icon-licaishouye` · `icon-jiesuo` · `icon-changwaizhuanchangnei` · `icon-dingtoujisuanqi` · `icon-biaotouguanli` · `icon-biaodelianjie` · `icon-dingyue` · `icon-bangzhu` · `icon-bianji` · `icon-qiehuanbaiban` · `icon-honglizaitouzi` · `icon-shouyijisuanqi` · `icon-pengyouquan` · `icon-guanhuaibanqiehuan` · `icon-zhiding` · `icon-xianshi` · `icon-qupinglun` · `icon-suoding` · `icon-tiaozhuangengduo-juzhongduiqi` · `icon-zixuanzijin` · `icon-xianjinfenhong` · `icon-tiaozhuangengduo-youduiqi` · `icon-zixuanzixun` · `icon-sousuoguanbi` · `icon-yincang` · `icon-shezixuan` · `icon-guandian`

> 共 58 个图标,完整 unicode 映射见 `fonts/iconfont.css`。

## 三、方案二:SVG(渐变/特效图标)

### 底部导航栏(`bottom-nav/`)
48×48(实现24)。**选中态带径向渐变(CP1浅端 #FF7067 → CP0品牌色 #F93838),必须 SVG**;未选中态单色已设 currentColor(也可改用字体)。

| Tab | 未选中 | 选中(渐变) |
|---|---|---|
| 首页 | `home-inactive.svg` | `home-active.svg` |
| 自选 | `watchlist-inactive.svg` | `watchlist-active.svg` |
| 交易 | `trade-inactive.svg` | `trade-active.svg` |
| 理财 | `finance-inactive.svg` | `finance-active.svg` |
| 我的 | `mine-inactive.svg` | `mine-active.svg` |
| 首页刷新态 | — | `home-refresh.svg` |

### 其他渐变/特效图标(`gradient/`)
带渐变/特效的图标,导出 SVG 放此处。已登记:

| 文件 | 含义 | 用途 | 规格 |
|---|---|---|---|
| `xiaobao.svg` | AI智能体小宝(正常态) | 自选/交易/理财左侧图标 | 180×182,多重渐变 |
| `xiaobao-thinking.svg` | 小宝(思考中态) | 小宝加载/思考状态 | 204×204,多重渐变 |
| `agent-close.svg` | 智能体导航关闭按钮 | 智能体场景右侧关闭 | 48×48,线性渐变圆形 |

### 复杂动画图标
逐帧动画/Lottie 等二进制大资源**不放进 skill 本体**,skill 只写引用说明(资源名+外部路径),资源放设计资源库。

## 四、目录总览
```
assets/icons/
├── ICONS.md          本文件(管理规范+索引)
├── fonts/            通用图标字体
│   ├── iconfont.woff2
│   └── iconfont.css
├── bottom-nav/       底部导航SVG(选中态渐变)
└── gradient/         其他渐变/特效图标SVG(预留)
```

## v3.10.0 新增(从自选页拆出)

> **命名**:文件用 ASCII 名(跨平台/打包稳),下表「原名」为 Figma 中文层名,便于检索。
> **目录规则**:通用图标 → `icons/common/`;场景图标 → `icons/{场景}/`(如 `market/`)。

### common/(通用图标)
| 文件 | 原名 | 用途 |
|---|---|---|
| common/sort-triangle.svg | 三角排序 | 列表表头排序·默认(双三角灰 #CCC),16×24 |
| common/sort-triangle-up.svg | 三角排序_上_ | 升序态(上三角 #F93838) |
| common/sort-triangle-down.svg | 三角排序_下_ | 降序态(下三角 #F93838) |

### market/(行情场景图标,含自选)
| 文件 | 原名 | 用途 |
|---|---|---|
| market/edit.svg | 编辑 | 列表表头-左·编辑,32px |
| market/multi-column.svg | 多股同列 | 列表表头-左·多股同列,32px |
| market/trend-off.svg | 走势图(未开启) | 列表表头-左·走势图关,32px |
| market/trend-on.svg | 走势图(已开启) | 列表表头-左·走势图开,32px |
| market/add-stock.svg | 添加股票 | 自选-按钮·添加股票 |
| market/image-recognition.svg | 图片识别 | 自选-按钮·图片识股 |
| market/signal-on-light.svg | 自选信号-开启-白版 | 自选tab·信号开(浅底) |
| market/signal-on-dark.svg | 自选信号-开启-黑版 | 自选tab·信号开(深底) |
| market/signal-off-light.svg | 自选信号-关闭-白版 | 自选tab·信号关(浅底) |
| market/signal-off-dark.svg | 自选信号-关闭-黑版 | 自选tab·信号关(深底) |
| market/signal-disabled-light.svg | 自选信号-禁用-白版 | 自选tab·信号禁用(浅底) |
| market/signal-disabled-dark.svg | 自选信号-禁用-黑版 | 自选tab·信号禁用(深底) |

引用用相对路径,如 `assets/icons/common/sort-triangle.svg`、`assets/icons/market/edit.svg`。

## 底部信息栏 资产(v3.17.0 新增 · SVG)
| 文件 | 路径 | 是什么 | 尺寸 |
|---|---|---|---|
| `shishi.svg` | `assets/icons/market/` | 实时(异动活跃)红波形 | 32×32 |
| `dajia-zaikan.svg` | `assets/icons/gradient/` | 大家都在看 蓝渐变字标 | 140×44 |
| `agent-orb-wave.svg` | `assets/icons/gradient/` | 智能体球(球+声波,一级底导用) | 132×132 |
> 设置icon 复用 `icon-shezhi`;列表更多 ">" 为参考实现内联细 chevron,非独立库图标。

## [待] 库内无资产 / 易混澄清(v3.18.0,据多模型使用反馈)
**规范点名但库内无 SVG/iconfont 资产**(用前别找,直接按标注处理,勿手画占位当真资产):
- **筛选漏斗**(行情二级 tab 筛选 `93:3639`/`93:3664`):库内无漏斗图标 → iconfont 近似或省略。
- **火箭**(components §三.2 个股异动「火箭 28M」):库内无 rocket SVG → iconfont 箭头替代或省略。
**易混(别用错)**:
- **小宝** = top-nav 顶部机器人 72×76 = `assets/icons/gradient/xiaobao.svg`(静态机器人);**v3.21.0 起 sandbox-header 内含 `<symbol id="gj-xb">`,粘了 sandbox-header 即可 `<svg width=W height=H><use href="#gj-xb"/></svg>`(原比例 180×182),无需手抄 svg;
- **智能体球 agent-orb-wave** = 一级页面底部导航栏 132×132 球+声波 = `assets/icons/gradient/agent-orb-wave.svg`。
两者**不同物、不可互相占位**:top-nav 用 xiaobao,底导用 agent-orb-wave。

## `agent-orb-wave.svg` 用法(v3.19.2,据 claude design 反馈)
它是**完整智能体球**(含头像,文件内已内嵌约 197KB PNG,**不是空 href、不是只有声波**)。
- **按相对路径整文件引用**:`<img src="…/agent-orb-wave.svg">` 或 CSS `background`。
- **勿手抄 / 内联它的 base64**:197KB 超长,模型生成时会被截断 → 脸丢失,只剩白圆+声波竖条。
- **勿替换成更轻的占位**。完整版同样内嵌在 `bottom-info-bar.html`(同一张 197KB PNG)。

