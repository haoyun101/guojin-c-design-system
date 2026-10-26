#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面校验器(可靠性三层·第三层「确定性兜底」)。
用法:python3 scripts/check-page.py <生成的页面.html> [更多.html ...]
P0 = 硬违规(退出码 1,不准交付);P1 = 需复核(退出码仍 0,但必须逐条确认)。
v3.24.0:加 ① 模块间距漂移检测 ② 误报白名单(库片段值免计)③ 漏用库·底导(B1 保守)。
v3.29.5:加 AI 易用性 P1 复核:缺 BOM、疑似未套 page-shell、相对资产可能 404、数字未声明 tabular-nums。
"""
import sys, re, json, pathlib, glob
from spatial_tokens import audit as audit_spatial, LEGACY

ROOT = pathlib.Path(__file__).resolve().parent.parent
IDX = ROOT/"assets"/"library-index.json"

# 载入 token 十六进制(裸色检测用)
token_hex = {}
if IDX.exists():
    d = json.load(open(IDX, encoding="utf-8"))
    for sem, val in d.get("tokens", {}).items():
        for h in re.findall(r'#[0-9a-fA-F]{6}', val):
            token_hex[h.lower()] = sem

# 官方原值集:参考实现 / tokens 自带的 raw 值;页面复用库片段时这些值不算违规(误报白名单)
OFFICIAL_HEX = set(); OFFICIAL_ODD = set()
for _f in glob.glob(str(ROOT/"assets"/"components"/"*.html")):
    try: _t = open(_f, encoding="utf-8", errors="ignore").read()
    except Exception: continue
    for _h in re.findall(r'#[0-9a-fA-F]{6}', _t): OFFICIAL_HEX.add(_h.lower())
    for _n in re.findall(r'(\d+)px', _t):
        if int(_n) % 2: OFFICIAL_ODD.add(_n)
try:
    for _h in re.findall(r'#[0-9a-fA-F]{6}', (ROOT/"assets"/"design-tokens.css").read_text(encoding="utf-8")):
        OFFICIAL_HEX.add(_h.lower())
except Exception: pass
OFFICIAL_FS = set()   # 参考实现自带字号(图标字号 48 / 状态栏 30 / demo 标注 13·11 等),复用时免计
for _f in glob.glob(str(ROOT/"assets"/"components"/"*.html")):
    try: _t = open(_f, encoding="utf-8", errors="ignore").read()
    except Exception: continue
    for _n in re.findall(r'font-size:\s*(\d+)px', _t): OFFICIAL_FS.add(_n)

EMOJI = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\u2190-\u21FF\u2B00-\u2BFF]")
EMOJI_WL = set("★☆●◆▲▼→←↑↓")  # 文档锚点/示意符号/文本分隔箭头,非图标用途,免报(真箭头图标用 iconfont icon-shixinjiantou-*)
MOD_GAPS = {"8","16","24","32","40","48"}  # 模块级间距候选值
ASSET_RE = re.compile(r'(?:src|href)=["\']([^"\']+)["\']|url\((?!data:)([^)]+)\)')

def strip_noise(html):
    html = re.sub(r'url\(data:[^)]+\)', 'url(DATA)', html)
    html = re.sub(r'base64,[A-Za-z0-9+/=]+', 'base64,DATA', html)
    return html

def css_blocks(html):
    return re.findall(r'\{([^{}]*)\}', html)

def is_remote_or_special(path):
    path = path.strip().strip('"\'')
    return (
        not path or path.startswith("#") or path.startswith("data:") or
        re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', path) or
        path.startswith("//")
    )

def asset_exists(page, ref):
    ref = ref.strip().strip('"\'')
    if is_remote_or_special(ref):
        return True
    ref = ref.split("#", 1)[0].split("?", 1)[0]
    if not ref:
        return True
    candidates = [
        pathlib.Path(page).resolve().parent / ref,
        ROOT / ref,
    ]
    return any(p.exists() for p in candidates)

def check(path):
    p0, p1, info = [], [], []
    page_path = pathlib.Path(path).resolve()
    raw = page_path.read_text(encoding="utf-8", errors="ignore")
    html = strip_noise(raw)
    rel_path = ""
    try:
        rel_path = str(page_path.relative_to(ROOT))
    except Exception:
        rel_path = str(page_path)
    is_library_file = rel_path.startswith("assets/components/") or rel_path.startswith("assets/page-shells/")
    # 页面是否复用了 skill 库片段(参考实现/iconfont/sandbox)——决定误报白名单是否对裸色生效
    reuses_lib = bool(re.search(r'gj-tnav|gj-bn-|gj-bottomnav|gj-xb|gj-ibnav|gj-ibn-orb|gj-ibn-pill|gj-ibn-tab|gj-ibi-handle|gj-ibi-sig|bottom-info|bottom-nav|sandbox-header|class="iconfont"|icon-[a-z]', html))

    for line, prop, value in audit_spatial(raw):
        p0.append(f"{line}行: {prop}中的标准值应引用SP/RD: {value}")
    for old in LEGACY:
        if re.search(re.escape(old)+r"(?![\w-])", raw):
            p0.append(f"间距/圆角旧引用 {old} → 使用SP/RD")

    # --- P1: 缺 BOM/用料清单(闸门 A 复核) ---
    if not is_library_file and not re.search(r'BOM|用料清单|data-bom|gj-bom', raw, re.I):
        p1.append("未发现 BOM/用料清单标记 → 动手前应列组件/图标/token 的库内引用;若 BOM 在交付说明中,确认已随件提供")

    # --- P1: 疑似页面未套 page-shell(只对页面级结构保守提示) ---
    page_like = bool(re.search(r'<main\b|gj-module|bottomnav|gj-tnav|gj-ibnav|gj-bottomnav|class=["\'][^"\']*shell', html))
    uses_shell = bool(re.search(r'data-level=["\'][12]["\']|gj-module|assets/page-shells|page-shell|<main\b[^>]*>\s*<section', html))
    if page_like and not uses_shell and not is_library_file:
        p1.append("疑似页面级产物未套 page-shell / gj-module → 页面应优先使用 assets/page-shells,模块间距交给 <main> gap")

    # --- P1: 相对资产路径存在性(防单文件预览/导出 404) ---
    missing_assets = []
    for m in ASSET_RE.finditer(raw):
        ref = (m.group(1) or m.group(2) or "").strip()
        if is_remote_or_special(ref):
            continue
        # CSS url(...) 可能带引号或右括号前空格
        ref = ref.strip().strip('"\'')
        if not asset_exists(path, ref):
            missing_assets.append(ref)
    if missing_assets:
        sample = ", ".join(sorted(set(missing_assets))[:6])
        p1.append(f"相对资产路径可能 404:{sample} → 整包交付需带同级 assets;单文件/widget 应内联或粘 sandbox-header")

    # --- P0: CSS 三角形手画图标(border 拼三角) ---
    for blk in css_blocks(html):
        transp = len(re.findall(r'border-(?:top|bottom|left|right)\s*:[^;]*solid[^;]*transparent', blk))
        colored = len(re.findall(r'border-(?:top|bottom|left|right)\s*:[^;]*solid[^;]*(?:#|rgb|var\()', blk))
        if transp >= 2 and colored >= 1:
            p0.append("CSS 三角形手画图标(border 拼三角)→ 必须改用库内图标(iconfont 箭头/三角:icon-shixinjiantou-*、sort-triangle.svg)")

    # --- P1: 内联 <path>/<polygon> 疑似手画图标 ---
    n_path = len(re.findall(r'<path\s+d=', html)) + len(re.findall(r'<poly(?:gon|line)\s', html))
    if n_path:
        (info if reuses_lib else p1).append(
            f"内联 <path>/<polygon> 共 {n_path} 处 → " + ("页面已复用库片段,内联属正常(免计)" if reuses_lib else "确认是否本应来自库(iconfont/SVG);手搓页面请改引用库"))

    # --- P1: emoji 当图标(★☆ 等文档符号免报) ---
    em = set(EMOJI.findall(html)) - EMOJI_WL
    if em:
        p1.append(f"发现 emoji {' '.join(sorted(em))[:40]} → 若用作图标请换库内图标(emoji 非规范图标)")

    # --- P1: 裸色(命中 token 的十六进制却没走 var);库片段自带的官方原值免计 ---
    hits = {}
    for h, sem in token_hex.items():
        if re.search(r'(?:color|background|fill|stroke|border)[^;{}]*' + re.escape(h), html, re.I):
            hits[h] = sem
    new_hits = {h: s for h, s in hits.items() if not (reuses_lib and h in OFFICIAL_HEX)}
    off_hits = {h: s for h, s in hits.items() if reuses_lib and h in OFFICIAL_HEX}
    if new_hits:
        sample = "; ".join(f"{h}({s})" for h, s in list(new_hits.items())[:6])
        p1.append(f"裸色命中 token 共 {len(new_hits)} 种:{sample} → 应改用 token 变量 var(--xx)")
    if off_hits:
        info.append(f"裸色 {len(off_hits)} 种来自库片段官方原值(免计):{', '.join(list(off_hits)[:6])}")

    # --- P1: 字号不在 S1–S8 集合 ---
    try:
        _sset = set(re.findall(r'\|\s*S[1-8]\s*\|\s*(\d+)\s*\|', (ROOT/"references"/"foundations.md").read_text(encoding="utf-8")))
    except Exception:
        _sset = set()
    if _sset:
        _bad = sorted({n for n in re.findall(r'font-size:\s*(\d+)px', html)
                       if n not in _sset and not (reuses_lib and n in OFFICIAL_FS)}, key=int, reverse=True)
        if _bad:
            p1.append(f"字号不在 S1-S8 集合:页面出现 {', '.join(_bad[:8])}px → 应取规范字号({'/'.join(sorted(_sset,key=int,reverse=True))})")

    # --- P1: 数字字体 D-DIN 未改 GJType(页面全局有 GJType 则免——D-DIN 仅参考实现 fallback)---
    if not re.search(r'GJType', html) and not reuses_lib:
        for blk in re.findall(r'font-family\s*:[^;{}]*', html):
            if re.search(r'D-?DIN', blk, re.I) and 'GJType' not in blk:
                p1.append("font-family 含 D-DIN 但无 GJType → C 端数字字体应入库为 GJType"); break

    # --- P1: 数字字体未声明等宽数字 ---
    uses_num_font = bool(re.search(r'GJType|--font-num|--num|font-family\s*:[^;{}]*(?:DIN|monospace)', html, re.I))
    has_tnum = bool(re.search(r'font-variant-numeric\s*:\s*[^;{}]*tabular-nums|font-feature-settings\s*:\s*[^;{}]*["\']?tnum', html, re.I))
    if uses_num_font and not has_tnum:
        p1.append("发现数字字体/数字 token 但未声明 tabular-nums/tnum → 金额、价格、涨跌幅应开启等宽数字")

    # --- P1: 间距应为偶数(库片段自带的奇数值如 9/33 免计) ---
    odds = set()
    for decl in re.findall(r'(?:padding|margin|gap)(?:-(?:top|right|bottom|left))?:\s*([^;{}]+)', html):
        for n in re.findall(r'(\d+)px', decl):
            if int(n) % 2 and n not in OFFICIAL_ODD: odds.add(n)
    if odds:
        p1.append(f"间距非偶数(应 4 的倍数,特殊 2):{', '.join(sorted(odds,key=int)[:8])}px → 对齐基线粒度")

    # --- ① P1(新):模块间距漂移 —— 多个不同模块级 margin 撑间距 且无容器 gap ---
    mod_margins = {n for n in re.findall(r'margin-(?:top|bottom)\s*:\s*(\d+)px', html) if n in MOD_GAPS}
    has_gap_col = bool(re.search(r'flex-direction\s*:\s*column', html)) and bool(re.search(r'\bgap\s*:', html))
    if len(mod_margins) >= 2 and not has_gap_col:
        p1.append(f"模块垂直间距出现多个值 {', '.join(sorted(mod_margins,key=int))}px 且未用容器 gap → 跨模块间距易漂移,应套 page-shell(<main> flex-column + gap,一级16/二级24),勿每模块各自 margin/height 撑")

    # --- ③ P1(新·B1 保守):漏用库·底导 —— fixed/absolute 吸底栏却无库底导引用 ---
    has_fixed_bottom = bool(re.search(r'position\s*:\s*(?:fixed|absolute)[^{}]*?bottom\s*:\s*0(?:px)?\b', html)) or \
                       bool(re.search(r'bottom\s*:\s*0(?:px)?[^{}]*?position\s*:\s*(?:fixed|absolute)', html))
    uses_lib_nav = bool(re.search(r'gj-bn-|gj-bottomnav|gj-tnav|gj-ibnav|gj-ibn-orb|gj-ibn-pill|gj-ibn-tab|gj-ibi-handle|gj-ibi-sig|bottom-info|bottom-nav', html))
    if has_fixed_bottom and not uses_lib_nav:
        p1.append("疑似吸底栏/底部导航未用库组件 → 一级页底导应复用 bottom-info-bar.html(智能体球版)/ bottom-nav.html,勿自绘")

    return p0, p1, info

def main():
    files = sys.argv[1:]
    if not files:
        print("用法: python3 scripts/check-page.py <page.html> [...]"); sys.exit(2)
    total_p0 = 0
    for f in files:
        p0, p1, info = check(f)
        total_p0 += len(p0)
        print(f"\n=== {f} ===")
        if not p0 and not p1:
            print("  ✓ 通过(无 P0/P1)")
        for x in p0: print(f"  P0 ✗ {x}")
        for x in p1: print(f"  P1 ⚠ {x}")
        for x in info: print(f"  ℹ️ {x}")
    print(f"\n结果: {total_p0} P0" + ("  → 不准交付,先修 P0" if total_p0 else "  → 无硬违规(P1 仍需逐条复核)"))
    sys.exit(1 if total_p0 else 0)

if __name__ == "__main__":
    main()
