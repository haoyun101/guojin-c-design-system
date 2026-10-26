# -*- coding: utf-8 -*-
"""SP/RD coverage guard. CSS definitions remain authoritative in design-tokens.css.

v4.0.2 范围收窄(只管「间距/圆角」,不管几何):
- 0 / 0px 不要求写成 SP0/RD0(写了也合法);
- 定位偏移 top/right/bottom/left/inset 不属间距,不检查;
- 胶囊/正圆几何圆角(同一规则块内 height 或 width = 2×圆角)不检查,须写像素值;
- 同一处不重复报(变量本身已直查命中,追链不再报)。
"""
import re
from html.parser import HTMLParser
from pathlib import Path

SP = {v: 'SP'+str(i) for i, v in enumerate((0,4,8,12,16,20,24,32,40,60,80))}
RD = {v: 'RD'+str(i) for i, v in enumerate((0,4,8,12,16,20,24,32,40,999,6))}
EXPECTED = {**{k:v for v,k in SP.items()}, **{k:v for v,k in RD.items()}}
LEGACY = {**{'--s-'+str(v):'--'+k for v,k in SP.items()},
          **{'--r-'+str(v):'--'+k for v,k in RD.items()}, '--r-pill':'--RD9'}
# --s-48 / --s-64 remain existing exceptions.
PROPERTY = re.compile(r'(?<![\w-])(--[\w-]+|[a-zA-Z][\w-]*)\s*:\s*([^;{}]+)')
NUMBER = re.compile(r'(?<![\w.#-])(-?\d+(?:\.\d+)?)(px)?(?![\w.%])')
# 几何尺寸:height / width 及常见尺寸变量(--btn-h / --xx-height / --xx-size / --xx-w)
GEOMETRY = re.compile(r'(?<![\w-])(?:height|width|min-height|--[\w-]*-(?:h|height|w|width|size))\s*:\s*(\d+(?:\.\d+)?)px')

def family(prop):
    if prop.startswith('--'):
        if re.search(r'radius|^--r-',prop): return RD
        if re.search(r'gap|pad|space|^--s-',prop): return SP
        return None
    if re.fullmatch(r'border(?:-[\w-]+)?-radius|border-radius',prop): return RD
    # top/right/bottom/left/inset 是定位偏移,不是间距,不纳入 SP。
    if re.fullmatch(r'(?:padding|margin)(?:-[\w-]+)?|(?:grid-)?(?:row-|column-)?gap|border-spacing|scroll-(?:padding|margin)(?:-[\w-]+)?',prop): return SP
    return None

def literals(value, mapping, pill=()):
    # var fallback values are scanned, custom property identifiers are not.
    masked = re.sub(r'--[\w-]+',lambda m:'_'*len(m.group()),value)
    result=[]
    for m in NUMBER.finditer(masked):
        n=float(m.group(1))
        if n == 0:
            continue  # 0 不要求引用 SP0/RD0
        if mapping is RD and n in pill:
            continue  # 胶囊/正圆几何圆角,保留像素值
        if n in mapping and m.group(2)=='px':
            # Percentages and arbitrary units are deliberately excluded.
            result.append((m.start(),m.end(),mapping[n]))
    return result

def pill_radii(block):
    """同一规则块里由 height/width 推出的胶囊圆角集合(= 尺寸 ÷ 2)。"""
    return {float(x)/2 for x in GEOMETRY.findall(block)}

def block_of(css, pos):
    a = css.rfind('{', 0, pos); b = css.find('}', pos)
    a = 0 if a < 0 else a + 1; b = len(css) if b < 0 else b
    return css[a:b]

class Regions(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text=text;self.parts=[];self.instyle=False
        self.starts=[0]+[m.end() for m in re.finditer('\n',text)]
    def source_offset(self):
        row,col=self.getpos();return self.starts[row-1]+col
    def handle_starttag(self, tag, attrs):
        if tag=='style':self.instyle=True
        raw=self.get_starttag_text();base=self.source_offset()
        for m in re.finditer(r'\bstyle\s*=\s*([\"\'])(.*?)\1',raw,re.S|re.I):
            self.parts.append((base+m.start(2),m.group(2)))
    def handle_endtag(self, tag):
        if tag=='style':self.instyle=False
    def handle_data(self, data):
        if self.instyle:self.parts.append((self.source_offset(),data))

def _parts(text, html):
    if html:
        parser=Regions(text);parser.feed(text);return parser.parts
    return [(0,text)]

def _clean(css):
    return re.sub(r'/\*.*?\*/',lambda m:re.sub(r'[^\n]',' ',m.group()),css,flags=re.S)

def declarations(text, html=True):
    for base,css in _parts(text, html):
        clean=_clean(css)
        for m in PROPERTY.finditer(clean):
            prop,value=m.groups();mapping=family(prop)
            if mapping is not None:
                # Global canonical and retained exception definitions are values, not uses.
                if re.fullmatch(r'--(?:SP\d+|RD\d+|s-(?:48|64))',prop):continue
                pill = pill_radii(block_of(clean, m.start()))
                yield base+m.start(),base+m.start(2),prop,value,mapping,pill

def rewrite(text, html=True):
    edits=[]
    for _,start,prop,value,mapping,pill in declarations(text,html):
        for a,b,token in literals(value,mapping,pill):edits.append((start+a,start+b,'var(--'+token+')'))
    for a,b,v in sorted(edits,reverse=True):text=text[:a]+v+text[b:]
    return text,len(edits)

def alias_audit(text, html=True):
    """Follow custom-property chains from spacing/radius consumers, irrespective of alias name.

    This is a conservative static check across definitions in one file. Unitless
    coefficients (e.g. progress * 1%) are not pixel distances.
    """
    definitions = {}; consumers = []
    for base, css in _parts(text, html):
        clean = _clean(css)
        for match in PROPERTY.finditer(clean):
            prop, value = match.groups()
            line = text.count('\n', 0, base + match.start()) + 1
            pill = pill_radii(block_of(clean, match.start()))
            if prop.startswith('--'):
                definitions.setdefault(prop, []).append((value.strip(), line, pill))
            elif family(prop) is not None:
                consumers.append((prop, value, line, pill))

    def follow(value, mapping, pill, seen=()):
        findings = []
        for name in re.findall(r'var\(\s*(--[\w-]+)', value):
            if name in seen or name in {'--'+v for v in mapping.values()}:
                continue
            # 变量名本身已属同一族 → 直查已覆盖,追链不重复报
            direct = family(name) is mapping
            for defined, line, dpill in definitions.get(name, []):
                # Only explicit pixel dimensions establish a spatial value;
                # zero without a unit can be a dimensionless coefficient.
                raw = re.sub(r'var\(\s*--[\w-]+', 'var(ALIAS', defined)
                if not direct:
                    for number in re.finditer(r'(?<![\w.#-])(-?\d+(?:\.\d+)?)px\b', raw):
                        n = float(number.group(1))
                        if n == 0 or (mapping is RD and (n in pill or n in dpill)):
                            continue
                        if n in mapping:
                            findings.append((name, defined, line))
                findings.extend(follow(defined, mapping, pill | dpill, seen + (name,)))
        return findings

    results = []
    for prop, value, line, pill in consumers:
        for name, defined, definition_line in follow(value, family(prop), pill):
            entry = (line, prop, value.strip() + ' -> ' + name +
                     ' (line ' + str(definition_line) + '): ' + defined)
            if entry not in results:
                results.append(entry)
    return results

def audit(text, html=True):
    result=[]
    for start,_,prop,value,mapping,pill in declarations(text,html):
        hits=literals(value,mapping,pill)
        if hits:result.append((text.count('\n',0,start)+1,prop,value.strip()))
    result.extend(alias_audit(text, html))
    return result

def definition_block():
    return '\n  /* SP/RD · 750px */\n  '+' '.join('--%s:%spx;'%(k,v) for k,v in EXPECTED.items())+'\n'

if __name__=='__main__':
    import sys
    root=Path(sys.argv[1]);bad=[]
    for p in sorted(root.rglob('*')):
        if p.suffix not in ('.html','.css') or 'fonts' in p.parts:continue
        for line,prop,value in audit(p.read_text(),p.suffix=='.html'):
            bad.append('%s:%s %s: %s'%(p.relative_to(root),line,prop,value))
    print('\n'.join(bad));print('SP/RD hardcoded candidates:',len(bad))
    sys.exit(bool(bad))
