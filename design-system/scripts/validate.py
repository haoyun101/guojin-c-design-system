#!/usr/bin/env python3
"""国金DS skill 校验脚本 v1 (v3.7.1)
用法: python3 validate.py [skill根目录]      # 校验 skill 包
      python3 validate.py --site [站点目录]  # 部署包对账模式
P0 规则违例 exit 1。"""
import re,sys,os,glob
errs=[];warn=[]
def E(m):errs.append("P0 ✗ "+m)
def W(m):warn.append("P1 ⚠ "+m)
def check_skill(root):
    sk=open(f"{root}/SKILL.md",encoding="utf-8").read()
    ver=open(f"{root}/VERSION",encoding="utf-8").read().strip()
    cl=open(f"{root}/CHANGELOG.md",encoding="utf-8").read()
    top=re.search(r'^## v([\d.]+)',cl,re.M).group(1)
    if ver!=top:E(f"版本不一致 SKILL={ver} CHANGELOG={top}")
    _bn=os.path.basename(os.path.abspath(root))
    if not re.match(r"^[A-Za-z0-9_-]+$",_bn):E(f"顶层目录名须纯ASCII〔Claude.ai上传要求〕:{_bn}")
    _vu="v"+ver.replace(".","_")
    if _vu not in _bn and ("v"+ver) not in _bn:W(f"目录名未含版本 {_vu}(建议 <name>_{_vu},便于解压后溯源)")
    for _dp,_dns,_fns in os.walk(root):
        for _n in _dns+_fns:
            if not all(ord(_c)<128 for _c in _n):E(f"非ASCII文件/目录名〔Claude.ai上传拒收〕:{_n}")
    for f in glob.glob(f"{root}/references/**/*.md",recursive=True)+glob.glob(f"{root}/assets/**/*.css",recursive=True)+glob.glob(f"{root}/assets/components/*.html"):
        s=open(f,encoding="utf-8").read();b=os.path.relpath(f,root)
        if re.search(r'CL2@71%|71%/2px(?!.*已更正)',s) and "已更正" not in s:E(f"{b}: 71% 旧值残留")
        for _m in re.finditer(r'÷\s*2',s):  # ÷2 逐处判定(v3.7.6:豁免红线表述与胶囊几何,只揪真750缩放)
            _pre=s[max(0,_m.start()-4):_m.start()]; _win=s[max(0,_m.start()-14):_m.end()+10]
            if "不" in _pre: continue                      # 「不÷2」= 750红线表述本身,豁免
            if re.search(r'高度|胶囊|半径|曾假设|已废|已更正|历史',_win): continue   # 胶囊几何(圆角=高度÷2)/历史说明(曾假设÷2已废),与现行750红线无关,豁免
            W(f"{b}: 含÷2表述(疑750缩放),核对是否违反唯一基准红线: …{_win.strip()}…")
        for tk in ["--r-xl","--r-lg"]:
            if tk+":" in s or tk+")" in s:E(f"{b}: 引用已删圆角档 {tk}(v3.7.0 删除)")
        if re.search(r'#[0-9a-fA-F]{6}',s) and "design-tokens" not in b and b.endswith(".html"):
            pass # 参考实现允许内联hex(带token注释),不卡
    for f in glob.glob(f"{root}/assets/**/*",recursive=True):
        if os.path.isfile(f) and not all(ord(c)<128 for c in os.path.basename(f)):W(f"assets 非ASCII文件名: {os.path.basename(f)}")
    # 涨跌反检查:CS1 必须红 CS2 必须绿
    tok=open(f"{root}/assets/design-tokens.css",encoding="utf-8").read()
    if not re.search(r'--CS1:\s*var\(--R6\)|--CS1:\s*#?F93838',tok,re.I):E("CS1(涨)未绑红")
    if not re.search(r'--CS2:\s*var\(--G6\)|--CS2:\s*#?05B063',tok,re.I):E("CS2(跌)未绑绿")
    # Canonical SP/RD values, all current asset uses and hardcoded matching values.
    from spatial_tokens import EXPECTED, LEGACY, audit
    from pathlib import Path
    expected = {"--"+k: str(v) for k,v in EXPECTED.items()}
    for name, value in expected.items():
        found = re.findall(re.escape(name)+r"\s*:\s*([^;{}]+)", tok)
        if found != [value+"px"]: E(f"{name} 定义必须唯一且为 {value}px: {found}")
    for path in Path(root).rglob("*"):
        if not path.is_file() or path.suffix not in (".html", ".css", ".md", ".json"): continue
        if "fonts" in path.parts or "case-studies" in path.parts or path.name == "CHANGELOG.md": continue
        body = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(root))
        for old in LEGACY:
            if re.search(re.escape(old)+r"(?![\w-])",body): E(f"{rel}: 旧间距/圆角引用 {old}")
        if path.suffix in (".html", ".css"):
            for line, prop, value in audit(body,path.suffix == ".html"):
                E(f"{rel}:{line}: 标准值须用SP/RD: {prop}: {value}")
            _copy = re.findall(r"(--(?:SP|RD)\d+)\s*:\s*([^;{}]+)", body)
            for name, value in _copy:
                if name not in expected or value.strip() != expected[name]+"px": E(f"{rel}: token副本不一致 {name}: {value}")
            # 副本须齐全:只要定义了任一 SP/RD,就必须 22 个全有(防 sandbox-header 漏档 → var() 失效算成 0)
            _missing = sorted(set(expected) - {n for n, _ in _copy}, key=lambda k: (k[:4], int(k[4:])))
            if _copy and _missing: E(f"{rel}: token副本不全,缺 {' '.join(_missing)}")
            for name in re.findall(r"var\(\s*(--(?:SP|RD)\d+)",body):
                if name not in expected: E(f"{rel}: 未定义token {name}")
    # 参考实现自包含:用到的 token 必须在本文件定义(注释里的不算);片段 status-bar 由宿主页提供
    for path in Path(root, "assets").rglob("*.html"):
        if path.name in ("status-bar.html",): continue
        body = path.read_text(encoding="utf-8")
        if re.search(r"<link[^>]+design-tokens\.css", body): continue
        body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
        used = set(re.findall(r"var\(\s*(--[\w-]+)\s*\)", body))
        defined = set(re.findall(r"(--[\w-]+)\s*:", body)) | set(re.findall(r"setProperty\(\s*'(--[\w-]+)'", body))
        miss = sorted(n for n in used - defined if re.match(r"--(?:[A-Z]{1,2}\d+|s-\d+)$", n))
        if miss: E(f"{path.relative_to(root)}: 引用了未定义的 token {' '.join(miss)}(var() 会失效)")
    # 可靠性三层:索引/脚本存在 + 索引新鲜度
    import json as _j
    for need in ["assets/library-index.json","scripts/build-index.py","scripts/check-page.py","assets/icons/icon-palette.html"]:
        if not os.path.exists(f"{root}/{need}"):E(f"可靠性三层缺文件: {need}")
    _idx=f"{root}/assets/library-index.json"
    if os.path.exists(_idx):
        _d=_j.load(open(_idx,encoding="utf-8"))
        _ncss=len(re.findall(r'\.icon-[a-z0-9-]+:before',open(f"{root}/assets/icons/fonts/iconfont.css",encoding="utf-8").read()))
        _nidx=len(_d.get("icons",{}).get("iconfont",{}))
        if _ncss!=_nidx:E(f"library-index 过期:iconfont 类 css={_ncss} 索引={_nidx},请重跑 build-index.py")
        # 组件登记表 ↔ 索引 Cxx 一致性(防 C14 那类漏登)
        _m=re.search(r'## 组件登记表.*?(?=\n## )', sk, re.S)
        _reg=set(re.findall(r'\bC\d\d\b', _m.group(0))) if _m else set()
        _idxC=set(re.findall(r'\bC\d\d\b', " ".join(_d.get("components",{}).keys())))
        if _reg and _idxC and _reg!=_idxC:E(f"组件登记表↔索引 Cxx 不一致 SKILL={sorted(_reg)} 索引={sorted(_idxC)}")
        # 组件参考实现文件必须存在(防索引指向已删/改名的 html)
        for _ck,_cv in _d.get("components",{}).items():
            _ch=_cv.get("html")
            if _ch and not os.path.exists(f"{root}/{_ch}"):E(f"组件 {_ck} 参考实现缺失: {_ch}")
    # 参考实现 750 守卫(精准):注释文档化的尺寸 NN 若 CSS 改用 NN/2,即 375 ÷2 残留(组件本体被改坏,非 demo 文字误报)
    import glob as _g
    _resid=[]
    for _f in sorted(set(_g.glob(f"{root}/assets/components/*.html")+_g.glob(f"{root}/assets/components/**/*.html",recursive=True))):
        _txt=open(_f,encoding="utf-8").read()
        _cmt=" ".join(re.findall(r'<!--(.*?)-->',_txt,re.S))
        _doc={int(x) for x in re.findall(r'(?:高度?|宽|图标|icon)\s*(\d{2,3})',_cmt)}|{int(a) for a,b in re.findall(r'(\d{2,3})\s*[×x]\s*(\d{2,3})',_cmt)}|{int(b) for a,b in re.findall(r'(\d{2,3})\s*[×x]\s*(\d{2,3})',_cmt)}
        _css={int(x) for x in re.findall(r'(?:height|width|font-size):\s*(\d+)px',_txt)}
        # d 写成「d = a + b」的组合总值(如 整体高176=88+88)不是减半残留,跳过;真减半(如"高度88(实现44)")无此加号,仍会报
        _hit=sorted(d for d in _doc if d>=40 and d%2==0 and d not in _css and d//2 in _css
                    and not re.search(rf'{d}\s*[=＝][^。;\n]*[＋+]', _cmt))
        if _hit:_resid.append(f"{os.path.relpath(_f,root)}(注释 {','.join(map(str,_hit))} 但 CSS 用了 {','.join(str(d//2) for d in _hit)})")
    if _resid:
        E("参考实现 375 ÷2 残留(组件本体尺寸被减半):"+" / ".join(_resid)+" → 改回 750 标注值")

def check_site(root):
    pages=glob.glob(f"{root}/*.html")
    for p in pages:
        s=open(p,encoding="utf-8").read();b=os.path.basename(p)
        if not all(ord(c)<128 for c in b):E(f"页面非ASCII名 {b}")
        if re.findall(r'[\s](src|href)="assets/[^"]*\.(js|css)"',s):E(f"{b}: 真外链js/css(自包含违例)")
        if not re.search(r'v\d+\.\d+\.\d+',s):W(f"{b}: 未见版本徽标")
    for z in glob.glob(f"{root}/assets/*.zip"):
        import zipfile
        n=zipfile.ZipFile(z).namelist()[0]
        m1=re.search(r'v([\d.]+)\.zip',z);m2=re.search(r'v([\d.]+)',n)
        if m1 and m2 and m1.group(1)!=m2.group(1):E(f"下载包名实不符 文件名v{m1.group(1)} 内容v{m2.group(1)}")
if __name__=="__main__":
    a=sys.argv[1:]
    if a and a[0]=="--site":check_site(a[1] if len(a)>1 else ".")
    else:check_skill(a[0] if a else ".")
    for m in errs+warn:print(m)
    print(f"结果: {len(errs)} P0 / {len(warn)} P1")
    sys.exit(1 if errs else 0)
