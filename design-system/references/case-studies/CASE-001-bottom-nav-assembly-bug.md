# CASE-001 底部导航拼装翻车(2026.06 使用反馈)
现象:用 skill 搭 ETF 榜单页,前两版底导 tab 拼错(造了不存在的"行情/资产"tab)、图标颜色硬编码、字重误给500。
根因:缺成品参考实现,使用者凭规格表手拼。
正确:用 assets/components/bottom-nav.html;tab 集合=首页/自选/交易/理财/我的;字重 Regular 400(底导特例);图标 active+inactive 成对、inactive 用 currentColor。
沉淀:bottom-nav.html 已吸收(v3.7.0);"禁止未登记组件"硬规则(v3.7.1);icons README 两态约定。
