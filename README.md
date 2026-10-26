# 国金证券 C 端客户端设计组件系统

> 面向 AI 的设计系统 skill —— 把 Figma 里的设计真值固化成可复用、可校验的规则包,供大模型据此产出符合规范的客户端原型页面。

本仓是**阶段性对外发布面**,有阶段性成果时才更新。日常迭代不在这里。

---

## 仓里有什么

| 目录 | 是什么 | 当前版本 |
|---|---|---|
| [`design-system/`](./design-system) | **DS skill** —— 设计系统本体:基础规范(token / 字体 / 间距)、通用组件、业务场景、图标库、参考实现、页面骨架、校验脚本 | **v4.1.1** |
| [`workflow/`](./workflow) | **WF 工作流包** —— 维护这套 skill 的过程规则:谁做什么、文件怎么流转、组件怎么推进、版本如何贯穿 | **v6.9** |

**两者的关系**:`design-system/` 是**操作对象**(真值在里面),`workflow/` 是**怎么维护它的规则**(不含任何真值)。
用 skill 产出页面的人**只需要 `design-system/`**;参与维护的人两个都要。

---

## 怎么用

### 产出页面(多数人只需要这个)

1. 下载 [最新 Release](../../releases/latest) 或直接取 `design-system/` 整个目录。
2. 入口是 `design-system/SKILL.md` —— 它是**路由表**,按触发词指向该读哪一份。
   **不要预读全量**:这套包按「用到哪份读哪份」设计,整包读完既慢又会稀释上下文。
3. 动手前先出《用料清单》(BOM):每个图标 / 组件 / token 写明库内确切引用。**填不出 = 没查库。**
4. 交付前必跑 `design-system/scripts/check-page.py 你的页面.html`,**P0 = 0 才算过**。

> 详细安装与接入方式见 [`design-system/INSTALL.md`](./design-system/INSTALL.md);术语见 [`GLOSSARY.md`](./design-system/GLOSSARY.md)。

### 参与维护

读 [`workflow/SKILL.md`](./workflow/SKILL.md) —— 操作卡 + 七律 + 角色通道 + 路由表都在那一份里。

---

## 设计真值来自哪里

**Figma 是设计真值的唯一来源**(《佣金宝组件库 V2.0》)。`design-system/` 是由它**固化而来的 AI 执行载体**,除数值外还装着专为 AI 生成写的规则(场景、限制、组合约束)。

改动顺序 **Figma → skill → 站**,不反向。两者数值不一致时**以 Figma 为准**。
skill 里有、Figma 里没有的内容属正常 —— 那是为 AI 补的规则,不算冲突。

---

## 版本与校验

- 两条版本线**各自独立签发**,互不牵动:`design-system/VERSION` 与 `workflow/VERSION`。
- 每次阶段性发布打一个 tag,下载地址固定指向 [`releases/latest`](../../releases/latest)。
- 逐版改了什么:[`design-system/CHANGELOG.md`](./design-system/CHANGELOG.md) · [`workflow/CHANGELOG.md`](./workflow/CHANGELOG.md)。

**核对手上这份是不是完整的**,在对应目录内执行(macOS 用 `md5 -q`,Linux 用 `md5sum`):

```bash
find . -type f ! -name '.DS_Store' ! -name '._*' ! -path './__MACOSX/*' \
  | sed 's|^\./||' | LC_ALL=C sort \
  | while IFS= read -r f; do echo "$f  $(md5 -q "$f" 2>/dev/null || md5sum "$f" | cut -d' ' -f1)"; done \
  | md5 -q 2>/dev/null || md5sum | cut -d' ' -f1
```

算出来的值与该版 Release 说明里的**内容指纹**比对。
**这个值与压缩方式无关** —— zip 被重新压缩过(比如 macOS 解开再压回去会塞进 `__MACOSX/`)不影响它,而 zip 自身的 MD5 会变。

---

## 可视化站

<https://gjzqdesign.netlify.app> —— 对外橱窗,**非事实源**。站上的「下载 Skill 包」即指向本仓。
