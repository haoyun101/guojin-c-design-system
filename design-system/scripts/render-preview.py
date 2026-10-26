#!/usr/bin/env python3
# 参考实现可视化冒烟:每个 components/*.html 套 design-tokens + iconfont 渲染成 PNG 供人工眼检。
# 用 playwright 真 Chromium(现代引擎:flex gap / woff2 / 绝对居中都正确;wkhtmltoimage 老 WebKit 会失真)。
# 依赖:pip install playwright && playwright install chromium。静态 validate 查不出 CSS 层叠/特异性/两态切换/间距这类视觉 bug,需此渲染兜底。
import re,os,glob,base64,pathlib,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from playwright.sync_api import sync_playwright
except Exception:
    sys.exit("需要 playwright:pip install playwright && playwright install chromium")
rootcss=re.search(r':root\s*\{.*?\n\}',open(f"{ROOT}/assets/design-tokens.css",encoding="utf-8").read(),re.S).group(0)
ico=open(f"{ROOT}/assets/icons/fonts/iconfont.css",encoding="utf-8").read()
woff2=base64.b64encode(open(f"{ROOT}/assets/icons/fonts/iconfont.woff2","rb").read()).decode()
ico=re.sub(r'src:[^;]+;', f'src:url("data:font/woff2;base64,{woff2}") format("woff2");', ico, count=1)
out="/tmp/skill-preview"; os.makedirs(out,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch()
    for f in sorted(glob.glob(f"{ROOT}/assets/components/*.html")):
        comp=open(f,encoding="utf-8").read()
        html=f"<!doctype html><meta charset=utf-8><style>{rootcss}\n{ico}\nbody{{margin:var(--SP0);background:#fff;font-family:'PingFang SC',system-ui,sans-serif}}#gjprev{{width:750px;background:#fff;padding:var(--SP6) var(--SP0)}}</style><div id=gjprev>{comp}</div>"
        tmp=f"{out}/_{os.path.basename(f)}"; pathlib.Path(tmp).write_text(html,encoding="utf-8")
        pg=b.new_page(viewport={"width":750,"height":1000},device_scale_factor=2)
        pg.goto("file://"+tmp); pg.wait_for_timeout(500)
        png=f"{out}/{os.path.basename(f)[:-5]}.png"
        pg.locator("#gjprev").screenshot(path=png); pg.close()
        print("rendered:",os.path.basename(png))
    b.close()
print("→ 打开 /tmp/skill-preview/*.png 人工眼检(两态切换/图标/间距/居中/是否压字)")
