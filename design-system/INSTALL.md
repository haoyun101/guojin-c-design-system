# INSTALL · 团队接入指南

## 它是什么
一份喂给 AI 的设计规则说明书。把它作为上下文/系统提示提供给 AI,生成的证券类页面就会遵守本设计系统。

## 三种接入方式

**A. 临时单次使用(最快)**
1. 新建 AI 对话(Claude / GPT / Gemini)。
2. 上传 `SKILL.md` + `assets/design-tokens.css`(需要细节时再补 `references/` 下文件)。
3. 描述要生成的页面,例如:「按本设计系统生成一个持仓列表页的移动端 HTML」。
4. 拿到代码存成 `.html` 用浏览器打开;不满意继续对话迭代。

**B. 长期挂载(推荐团队用)**
- Claude Projects:把整个 skill 文件夹作为「项目知识」上传,项目内每次对话自动遵守。
- 自定义 GPT:把 `SKILL.md` 内容写入系统提示,`design-tokens.css` 作为知识文件。

**C. 编码工具**
- Claude Code / Cursor:把 skill 文件夹放进仓库,让 AI 写界面时参照;`design-tokens.css` 可直接 import 进项目。

## 给 AI 的标准开场白(可复制)
```
请严格按照本设计系统 skill(见所附 SKILL.md 与 design-tokens.css)生成页面。
取色只用 var(--) 变量、涨红跌绿、尺寸用 750 基准原值(不 ÷2)、字号取 S1–S8;做业务场景页面先声明场景(首页/行情/交易/理财/AI智能体/微信小程序),按场景→通用→基础顺序取用。
完成后对照 SKILL.md 的自检清单逐条核对。
现在请生成:【在此描述你的页面需求】
```

## 验收
对照 `SKILL.md` 的自检清单逐条核对。不符合的条目,即本 skill 需要加强之处——反馈以迭代。

## 合规校验接入(让使用者稳定产出符合规范的页面)

写在文档里的规则,模型不一定执行。要稳定合规,靠"可靠性三层"(详见 SKILL「绘制原型」与工作流 4.8)。其中**唯一硬保证是确定性校验,它必须被"自动执行"才有效**——别指望谁记得手动跑。skill 已自带接入件:

**① 一键校验(本地/CI 通用)**

```bash
# skill 自检 + 扫当前目录所有页面;P0 即退出 1
bash 国金证券客户端设计系统-skill_v3.10.0/scripts/check-all.sh .
# 也可只校验指定页面/目录
bash .../scripts/check-all.sh path/to/页面.html src/pages/
```

**② git 提交钩子(提交前自动挡)** —— 推荐,零记忆成本

```bash
# 在你的项目仓库根执行(把 skill 目录路径按需调整):
export GJZQ_SKILL_DIR="$(pwd)/国金证券客户端设计系统-skill_v3.10.0"   # 可写进 shell profile
git config core.hooksPath .githooks
mkdir -p .githooks
cp "$GJZQ_SKILL_DIR/scripts/hooks/pre-commit" .githooks/pre-commit
chmod +x .githooks/pre-commit
# 之后每次 commit 自动对暂存的 .html 跑 check-page;有 P0 阻断提交。
```

**③ CI(PR/push 自动挡)**

```bash
# 复制 CI 模板到仓库根的 .github/workflows/,按注释改 skill 路径即可:
cp 国金证券客户端设计系统-skill_v3.10.0/scripts/ci-templates/github-actions-design-compliance.yml \
   .github/workflows/design-compliance.yml
```

**配套日常命令**
- 出图前:让模型按**闸门 A** 产出《用料清单 BOM》(图标/组件/token → `assets/library-index.json` 库内引用)。
- 资产(图标/组件)有增改:重跑 `python3 scripts/build-index.py` 刷新索引,再 `python3 scripts/validate.py` 自检。

> 三道接入任选其一即可达到"自动执行";**②或③ 至少接一个**,否则第三层形同虚设。check-page 的 P0 = 手画图标等硬违规;P1 = 需人工复核项(emoji/裸色/D-DIN 等)。

## 资产服务的 MIME 类型(分发链路提醒)
本 skill 以 zip 内嵌二进制资产(`.svg`/`.woff2`/`.ttf`)。**消费方解包后,静态服务器须按扩展名重设 content-type**,否则浏览器解码失败、图标/字体全空白:
- `.svg` → `image/svg+xml`(常见坑:被当 `image/png` 返回 → SVG 整片渲染失败)
- `.woff2` → `font/woff2`;`.ttf` → `font/ttf`

(widget / 沙盒场景不走 HTTP、改用 base64 内嵌,见 SKILL.md「第 0 步 · 判输出渠道」。)


## 从3.x迁移到4.0.0

间距和圆角改用SP/RD编号，编号不等于像素值。完整取值见 `assets/design-tokens.css`、用途见 `references/foundations.md` §4–§5。

| 原值名 | 新引用 |
|---|---|
| 间距4/8/12/16/20/24/32/40px | `--SP1` / `--SP2` / `--SP3` / `--SP4` / `--SP5` / `--SP6` / `--SP7` / `--SP8` |
| 圆角4/8/12/16/20/24/32px | `--RD1` / `--RD2` / `--RD3` / `--RD4` / `--RD5` / `--RD6` / `--RD7` |
| 圆角6px / 胶囊999px | `--RD10` / `--RD9` |

代码使用 `var(--SP4)` 等引用。既有非标准值保持原值；6px间距无对应SP，不能改成圆角RD10。更新嵌入的token定义与组件参考实现，不能只替换文档名称。
