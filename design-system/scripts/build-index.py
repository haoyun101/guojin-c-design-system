#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
库索引生成器(可靠性三层·第一层「降摩擦」)。
扫描真实文件 → 产出 assets/library-index.json + assets/icons/icon-palette.html。
索引是"语义/中文名 → 库内确切引用(iconfont class / SVG 路径 / 组件参考实现 / token 变量)"的唯一可查清单,
让"用库"比"手画/重写"更省事。任何资产变动后重跑本脚本。
"""
import os, re, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ICONS = ROOT / "assets" / "icons"
COMP = ROOT / "assets" / "components"

# ---- 1. IconFont(单色图标,优先级最高)----
gloss = {  # class -> 中文/语义(便于按中文检索)
 "bianji":"编辑","tianjia":"添加/加自选","tongzhi":"通知","shijian":"时间","rili":"日历",
 "biaotouguanli":"表头管理","xianshi":"显示","yincang":"隐藏","shezhi":"设置","sousuo":"搜索",
 "sousuoguanbi":"搜索关闭","xiaoxi":"消息","fenxiang":"分享","pengyouquan":"朋友圈","weixin":"微信",
 "saoyisao":"扫一扫","guanzhu":"关注","shoucang":"收藏","zhiding":"置顶","pinglun":"评论","qupinglun":"去评论",
 "guandian":"观点","dingyue":"订阅","bangzhu":"帮助","shuoming":"说明","biaodelianjie":"表单链接",
 "jiazixuan":"加自选","shezixuan":"设自选","shanchuzixuan":"删除自选","zixuanzijin":"自选资金/资金",
 "zixuanzixun":"自选资讯/资讯","licaishouye":"理财首页","xianjinfenhong":"现金分红","honglizaitouzi":"红利再投资",
 "shouyijisuanqi":"收益计算器","dingtoujisuanqi":"定投计算器","changwaizhuanchangnei":"场外转场内",
 "huanyihuan":"换一换","guanhuaibanqiehuan":"关怀版切换","qiehuanheiban":"切换黑版","qiehuanbaiban":"切换白版",
 "gengduo":"更多","tiaozhuangengduo-youduiqi":"跳转更多(右对齐)","tiaozhuangengduo-juzhongduiqi":"跳转更多(居中)",
 "shixinjiantou-shang":"实心箭头上","shixinjiantou-xia":"实心箭头下","shixinjiantou-zuo":"实心箭头左",
 "shixinjiantou-you":"实心箭头右","zhihuitou":"指回头","zhankai":"展开","shouqi":"收起","cebianlan":"侧边栏",
 "guanbi":"关闭","jiesuo":"解锁","suoding":"锁定","tuichu":"退出","chenggong":"成功","shibai":"失败",
}
icon_css = (ICONS/"fonts"/"iconfont.css").read_text(encoding="utf-8")
iconfont = {}
for m in re.finditer(r'\.icon-([a-z0-9-]+):before\s*\{\s*content:\s*"\\([a-f0-9]+)"', icon_css):
    cls, uni = m.group(1), m.group(2)
    iconfont[cls] = {"class": f"icon-{cls}", "unicode": uni, "gloss": gloss.get(cls, "")}

# ---- 2. SVG 图标(渐变/特效/多态,iconfont 没有的)----
svg = {}
for sub in ["common","market","bottom-nav","gradient"]:
    d = ICONS/sub
    if d.is_dir():
        for f in sorted(d.glob("*.svg")):
            svg[f"{sub}/{f.name}"] = ""

# ---- 3. 组件参考实现(全限定名 → 参考实现 / 文档位 / 形态变体导航)----
# 注:quickcard = 速查卡锚点。形态/变体/辨识的单一真源在 references/component-quickcards.md,
#     index 只存 name→库内引用(ref/html)+ quickcard 指针,不在此重述变体/辨识(避免两处漂移)。
QC = "references/component-quickcards.md"
components = {
 "C01 常规按钮":          {"ref":"references/components.md#一、常规按钮","html":"assets/components/button.html",
    "quickcard":QC+"#C01"},
 "C02 文字按钮":          {"ref":"references/components.md#二、文字按钮","html":None,
    "quickcard":QC+"#C02"},
 "C03 导航栏-顶部":        {"ref":"references/components.md#三、导航栏","html":"assets/components/top-nav.html",
    "quickcard":QC+"#C03-导航栏-顶部"},
 "C03 导航栏-底部·通用(规则集/可自定义N-tab)": {"ref":"references/components.md#三、导航栏","html":"assets/components/bottom-nav.html",
    "quickcard":QC+"#C03-导航栏-底部"},
 "C03 导航栏-底部·一级页面(智能体球+信息栏;首页/自选/我的/交易/理财用此)": {"ref":"references/components.md#三、导航栏","html":"assets/components/bottom-info-bar.html",
    "usage":"assets/components/bottom-info-bar.usage.md",
    "quickcard":QC+"#C03-导航栏-底部"},
 "C04 标题栏&tab":        {"ref":"references/components.md#四、标题栏","html":"assets/components/title-tab-bar.html",
    "quickcard":QC+"#C04"},
 "C05 开关":              {"ref":"references/components.md#五、开关","html":"assets/components/switch.html",
    "quickcard":QC+"#C05"},
 "C06 Toast":            {"ref":"references/components.md#六、Toast","html":"assets/components/toast.html",
    "quickcard":QC+"#C06"},
 "C07 时间轴":            {"ref":"references/components.md#七、时间轴","html":"assets/components/timeline.html",
    "quickcard":QC+"#C07"},
 "C08 单复选框":          {"ref":"references/components.md#八、单复选","html":"assets/components/radio-checkbox.html",
    "quickcard":QC+"#C08"},
 "C09 进度条":            {"ref":"references/components.md#九、进度条","html":"assets/components/progress.html",
    "quickcard":QC+"#C09"},
 "C10 分页符":            {"ref":"references/components.md#十、分页符","html":"assets/components/pagination.html",
    "quickcard":QC+"#C10"},
 "C11 占位图":            {"ref":"references/components.md#十一、占位图","html":"assets/components/placeholder.html",
    "quickcard":QC+"#C11"},
 "C12 图标宫格":          {"ref":"references/components.md#十二、图标宫格","html":"assets/components/icon-grid.html",
    "quickcard":QC+"#C12"},
 "C13 标签-通用":         {"ref":"references/components.md#十三、标签","html":"assets/components/tag.html",
    "quickcard":QC+"#C13"},
 "C13 标签-个股":         {"ref":"references/components.md#十三、标签","html":"assets/components/stock-tag.html",
    "quickcard":QC+"#C13"},
 "C14 列表表头":          {"ref":"references/components.md#十四、列表表头","html":"assets/components/list-header.html",
    "quickcard":QC+"#C14"},
 "C15 行情卡片":          {"ref":"references/components.md#十五、行情卡片","html":"assets/components/market-card.html",
    "quickcard":QC+"#C15"},
 "通用-状态栏":           {"ref":"references/components.md#三、导航栏","html":"assets/components/status-bar.html",
    "quickcard":QC+"#通用-状态栏"},
 "行情/自选个股列表项":    {"ref":"references/scenarios/market.md#3.1","html":"assets/components/scenarios/market/stock-list-item.html",
    "quickcard":QC+"#业务组件"},
 "行情/指数行情卡片":      {"ref":"references/scenarios/market.md#3.2","html":"assets/components/scenarios/market/stock-index-card.html",
    "quickcard":QC+"#业务组件"},
 "页面状态-骨架图":        {"ref":"references/skeleton.md","html":"assets/components/skeleton.html"},
}

# 组件在不同输出渠道下的资产可用性。
# true = 已自包含,可直接用于单文件/widget; partial = 依赖部分外部资产或需人工确认;
# false = 需要 sandbox-header 或整包相对路径资产,不宜直接单文件引用。
self_contained = {
 "C01 常规按钮": {"self_contained":True,"requires":"无(自包含:内联 iconfont woff2 + token 定义)","note":"DS v3.30.0 新增;六档 × 四风格 × 三状态 + XL 胶囊组合;运营气泡仅留槽位未画"},
 "C02 文字按钮": {"self_contained":"n/a","requires":"无独立参考实现;按 components.md 规格生成","note":"待补 text-button.html"},
 "C03 导航栏-顶部": {"self_contained":"partial","requires":"整包相对路径或粘贴 assets/components/sandbox-header.html","note":"图标字体/小宝资产需就绪"},
 "C03 导航栏-底部·通用(规则集/可自定义N-tab)": {"self_contained":False,"requires":"整包相对路径或粘贴 assets/components/sandbox-header.html","note":"依赖 bottom-nav SVG sprite"},
 "C03 导航栏-底部·一级页面(智能体球+信息栏;首页/自选/我的/交易/理财用此)": {"self_contained":"partial","requires":"优先读 bottom-info-bar.usage.md;整包相对路径;单文件时谨慎处理 agent-orb-wave 大资产","note":"大型参考实现不默认全文读取;agent-orb-wave 约197KB,勿 base64 内联"},
 "C04 标题栏&tab": {"self_contained":"partial","requires":"整包相对路径或粘贴 assets/components/sandbox-header.html","note":"图标字体需就绪"},
 "C05 开关": {"self_contained":True,"requires":"无额外资产","note":"可直接复用参考实现"},
 "C06 Toast": {"self_contained":True,"requires":"无额外资产","note":"可直接复用参考实现"},
 "C07 时间轴": {"self_contained":True,"requires":"无额外资产","note":"可直接复用参考实现"},
 "C08 单复选框": {"self_contained":True,"requires":"无额外资产","note":"可直接复用参考实现"},
 "C09 进度条": {"self_contained":"partial","requires":"整包相对路径; 依赖 assets/fonts/GJType-Medium.ttf","note":"可直接复用参考实现; 进度值使用 GJType Medium"},
 "C10 分页符": {"self_contained":True,"requires":"无额外资产","note":"可直接复用参考实现"},
 "C11 占位图": {"self_contained":True,"requires":"无额外资产","note":"可直接复用参考实现"},
 "C12 图标宫格": {"self_contained":"partial","requires":"整包相对路径或粘贴 assets/components/sandbox-header.html","note":"部分彩色图标仍待补"},
 "C13 标签-通用": {"self_contained":True,"requires":"无额外资产","note":"可直接复用参考实现"},
 "C13 标签-个股": {"self_contained":True,"requires":"无额外资产","note":"可直接复用参考实现"},
 "C14 列表表头": {"self_contained":False,"requires":"整包相对路径或粘贴 assets/components/sandbox-header.html","note":"依赖 common/market SVG 与图标字体"},
 "C15 行情卡片": {"self_contained":True,"requires":"无额外资产","note":"可直接复用参考实现"},
 "通用-状态栏": {"self_contained":True,"requires":"无额外资产","note":"可直接复用参考实现"},
 "行情/自选个股列表项": {"self_contained":False,"requires":"整包相对路径或粘贴 assets/components/sandbox-header.html","note":"依赖字体/标签等库片段"},
 "行情/指数行情卡片": {"self_contained":True,"requires":"已内嵌字体与核心样式","note":"可直接复用参考实现"},
 "页面状态-骨架图": {"self_contained":True,"requires":"无(复制 <script id=\"gj-skeleton\"> 整块)","note":"页面加载态;非独立组件,对已生成页面调用 GJSkeleton.apply(容器) 转换"},
}
for k, meta in self_contained.items():
    if k in components:
        components[k].update(meta)

# 校验 html 存在
for k,v in components.items():
    if v["html"] and not (ROOT/v["html"]).exists():
        v["html_missing"] = True

# ---- 4. 核心 token(语义 → 变量)----
tokens = {
 "涨/主色/CS1":"--cs1 #f93838","跌/CS2":"--cs2 #05b063","平/CS3":"--cs3 #55555e",
 "品牌主色/CP0":"--cp0 #f93838","功能蓝/CF3":"--cf3 #2b73ff","橙字/CF2":"--cf2 #ff7015",
 "主文本/CT1":"--ct1 #0f0f1b","次文本/CT3":"--ct3 #55555e","辅助文本/CT4":"--ct4 #87878d","反白/CT6":"--ct6 #fff",
 "卡片底/CB1":"--cb1 #fff","页面底/CB2":"--cb2 #f2f4f8","浅灰底/CB3":"--cb3 #f2f4f8","红淡底/CB13":"--cb13 rgba(249,56,56,.08)",
 "蓝淡底/CB14":"--cb14 rgba(43,115,255,.08)","绿淡底/CB27":"--cb27 rgba(5,176,99,.08)",
 "指数红5%/CB10":"--cb10 rgba(249,56,56,.05)","指数绿5%/CB11":"--cb11 rgba(5,176,99,.05)","指数灰5%/CB12":"--cb12 rgba(85,85,94,.05)",
 "描边红/CL3":"--cl3 #f93838","描边橙/CL4":"--cl4 #ff8533","描边蓝/CL5":"--cl5 #2b73ff",
 "数字字体":"GJType(C端统一;Figma 的 D-DIN 入库一律改 GJType)","中文字体":"PingFang SC",
}

# SP/RD entries are generated from the numeric source, not duplicated.
spatial_css = (ROOT/"assets"/"design-tokens.css").read_text(encoding="utf-8")
for token, value in re.findall(r"--((?:SP|RD)\d+)\s*:\s*(\d+)px", spatial_css):
    tokens[("间距/" if token.startswith("SP") else "圆角/")+token] = "--"+token+" "+value+"px"

index = {
 "_说明":"库内资产唯一可查索引。用任何资产前先在此查到确切引用;查不到才占位并标[待]。改资产后重跑 scripts/build-index.py。",
 "_优先级":"图标:单色先查 iconfont,再查 svg;组件:先查 components 参考实现(每条带 quickcard 锚点;形态/变体/辨识单一真源在 references/component-quickcards.md,index 不重述);颜色/字体:先查 tokens。",
 "icons":{"iconfont":iconfont,"svg":svg},
 "components":components,
 "tokens":tokens,
}
out = ROOT/"assets"/"library-index.json"
out.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"✓ library-index.json: {len(iconfont)} iconfont + {len(svg)} svg + {len(components)} 组件 + {len(tokens)} token")

# ---- 5. 图标 palette(人看的可复制清单)----
rows = []
for cls,info in sorted(iconfont.items()):
    rows.append(f'<div class="cell"><i class="iconfont icon-{cls}"></i><code>icon-{cls}</code><span>{info["gloss"]}</span></div>')
spatial_defs = " ".join("--"+k+":"+v+"px;" for k,v in re.findall(r"--((?:SP|RD)\d+)\s*:\s*(\d+)px", spatial_css))
# palette 页用到的颜色 token,值从 design-tokens.css 浅色段解析(不手抄)
_light = spatial_css[spatial_css.index(":root"):spatial_css.index('[data-theme="dark"] {')]
_defs = dict(re.findall(r"(--[A-Za-z][\w-]*):\s*([^;]+);", _light))
def _res(n, d=0):
    v = _defs.get(n, "").strip(); m = re.fullmatch(r"var\((--[\w-]+)\)", v)
    return _res(m.group(1), d + 1) if m and d < 6 else v
color_defs = "".join(n + ":" + _res(n) + ";" for n in ("--CB41", "--CB1", "--CL2", "--CT4", "--H11", "--B6"))
palette = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>图标库 palette</title>
<style>:root{{{spatial_defs} {color_defs}}}@font-face{{font-family:"iconfont";src:url("fonts/iconfont.woff2") format("woff2");}}
body{{font-family:"PingFang SC",system-ui,sans-serif;background:var(--CB41);padding:var(--SP6);margin:var(--SP0)}}
h1{{font-size:18px}}.tip{{font-size:12px;color:var(--CT4);margin-bottom:var(--SP4)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:var(--SP2)}}
.cell{{background:var(--CB1);border:1px solid var(--CL2);border-radius:var(--RD2);padding:var(--SP3) var(--SP2);text-align:center;display:flex;flex-direction:column;align-items:center;gap:var(--SP1)}}
.iconfont{{font-family:"iconfont";font-size:32px;font-style:normal;color:var(--H11)}}
code{{font-size:11px;color:var(--B6);word-break:break-all}}span{{font-size:11px;color:var(--CT4)}}</style></head>
<body><h1>国金证券 · IconFont 图标库({len(iconfont)})</h1>
<p class="tip">用法:<code>&lt;i class="iconfont icon-xxx"&gt;&lt;/i&gt;</code>。复制下面的 class 即可,别手画。单色图标一律用这里;渐变/多态见 assets/icons/ 下 SVG。</p>
<div class="grid">{"".join(rows)}</div></body></html>'''
(ICONS/"icon-palette.html").write_text(palette, encoding="utf-8")
print(f"✓ icon-palette.html")
