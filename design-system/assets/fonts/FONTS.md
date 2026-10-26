# 字体资源登记

| 字体 | 用途 | 文件 | 字重 |
|---|---|---|---|
| GJType(数字字体) | 时间 / 涨跌幅 / 价格 / 总资产等**数字**专用(`--font-num` 首选) | assets/fonts/GJType-{Regular,Medium,Bold}.ttf | 400/500/700 |
| PingFang SC(系统/中文) | iOS 系统字、中文常规(`--font-sans` 首选) | 系统自带,不随包 | — |

> 仅 GJType(版权数字字体)随 skill 提供文件;中文/系统字走系统或替代栈(见 foundations 字体族)。
> 字体平台对应(切图/分发场景,Design「设计文件下载」页统一提供):PingFang=iOS系统、思源黑体=安卓、微软雅黑=Web、OPPO Sans=切图免费商用、GJType=数字。

@font-face 声明示例:
```css
@font-face{font-family:"GJType";font-weight:400;src:url("assets/fonts/GJType-Regular.ttf") format("truetype");}
@font-face{font-family:"GJType";font-weight:500;src:url("assets/fonts/GJType-Medium.ttf") format("truetype");}
@font-face{font-family:"GJType";font-weight:700;src:url("assets/fonts/GJType-Bold.ttf") format("truetype");}
```

## @font-face 用法(单文件原型)
```css
@font-face{font-family:"GJType";src:url("gjtype-regular.ttf") format("truetype");font-weight:400;}
```
单文件原型可 base64 内嵌;CJK 字体体积大,建议按需子集化(如 pyftsubset)后再内嵌。
