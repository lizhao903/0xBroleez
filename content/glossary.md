---
title: "术语"
url: "/glossary/"
ShowToc: true
TocOpen: true
hidemeta: true
hideSummary: true
disableShare: true
hiddenInHomeList: true
---

> 实施策略和因子验证过程中常用的术语速查。`Ctrl-F` 搜索最快。

## 策略与组合管理

### DCA · Dollar-Cost Averaging · 定额定投
按固定时间间隔（通常是月）从现金池投入固定金额到风险资产池，**不择时**。
平滑入场成本，避免一次性高位入场的择时焦虑。是被动投资者最常用基线。

### Buy-and-Hold (BH) · 买入并持有
最朴素的基线：一次性满仓买入持有到回测结束，期间不做任何操作。
所有主动策略都至少要跑得过 BH 才算「创造 alpha」。

### Rebalance · 再平衡
按预设规则把组合权重调回目标权重。常见频率：
- **定时再平衡**：每月/每季度执行一次（不管偏离多少）
- **阈值再平衡**：权重偏离目标超过 ±X% 才触发

### Equal-Weight · 等权
所有标的占组合相同比例（如 6 只 ETF 各 1/6）。最朴素的分散方式。

### Tilt · 因子倾斜
在等权基线上，按某个因子（动量、趋势、价值…）的强弱**线性**加减权重。
公式通常类似 `weight_i = base_weight * (1 + α * z_score_i)`，再 clip 到 [min, max]。

### Value Averaging (VA) · 价值平均法
DCA 的进阶版：不固定**投入金额**，而固定**目标净值增长**。市场跌了多投，市场涨了少投甚至赎回。
理论上比 DCA 多一层 mean-reversion 信号。

### Threshold Swing · 阈值做T
DCA + 阈值再平衡的组合：每天检查权重，超阈值上沿（高估）卖出超额的一部分（高抛），
低于阈值下沿（低估）从现金池补买（低吸）。冷却期防抖。

### Risk-on / Risk-off
市场状态二元判定。常见判据：大盘指数 > MA200 → risk-on（满仓风险池）；< MA200 → risk-off（撤回现金/债券）。

---

## 业绩与风险指标

### NAV · Net Asset Value · 净值
组合当前市值。回测起始 NAV = 初始资金（如 100,000）。

### Total Return · 总收益
`NAV_end / NAV_start - 1`，整段回测的累计收益。

### CAGR · Compound Annual Growth Rate · 年化收益
`(NAV_end / NAV_start) ^ (1/years) - 1`。把总收益换算成年化，方便跨周期比较。

### Annualized Volatility · 年化波动
日收益率标准差 × √252（A股交易日数）。

### Sharpe Ratio · 夏普比率
`(annual_return - rf) / annual_vol`，单位风险换来的超额收益。
通常 > 1 算优秀，> 2 罕见，< 0 是负预期。

### MaxDD · Maximum Drawdown · 最大回撤
从历史最高净值跌到的最低点的跌幅。-30% 表示组合一度亏掉本金的 30%。
**比 Sharpe 更直观体现"扛得住吗"**。

### Calmar Ratio · 卡玛比率
`CAGR / |MaxDD|`。每承担 1% 的回撤换来多少收益。MaxDD 视角下的 Sharpe。

### Excess Return · 超额收益
策略收益 - 基准收益。基准通常是 510300 BH。

### Alpha · 超额收益（年化）
通常等于年化的 excess return（vs 基准）。S2 v1 vs BH 的 +1.89%/yr 就是 alpha。

### Beta · β
策略收益对基准收益的敏感度（回归系数）。β=1 跟基准同步，β>1 放大波动。

### IR · Information Ratio · 信息比率
`Alpha / Tracking Error`。每单位"主动暴露的风险"换来多少 alpha。
跨策略横向比较 alpha 含金量的最公允指标。

### Tracking Error · 跟踪误差
策略 vs 基准超额收益序列的年化标准差。"主动管理偏离基准的程度"。

### Turnover · 换手率
年化交易额 / 平均组合规模。100% = 平均每年把组合卖一遍买一遍。
高换手意味着费用蚕食 alpha。

---

## 因子与信号

### Factor · 因子
对资产做出区分的可观测量：动量、价值、低波、规模、质量…
策略通过买入因子值高的、卖出因子值低的资产来获取 alpha。

### IC · Information Coefficient · 信息系数
某日所有标的的因子值 vs 它们次日（或 N 日后）收益的截面相关系数。
- IC 长期均值显著 ≠ 0 → 因子有预测力
- |IC 均值| > 0.05 通常算可用，> 0.10 罕见且珍贵

### IC IR
IC 序列均值 / IC 序列标准差。因子稳定性指标。

### Z-score · 标准化分数
`(x - cross_section_mean) / cross_section_std`。截面标准化，让因子值"无量纲"，
方便跨标的比较和做线性 tilt。

### Lookback · 回看窗口
计算因子时使用的历史天数，如 `momentum_60d` = 过去 60 个交易日的累计收益。
窗口越长越平滑、越短越敏感，是关键超参。

### Vol-adjust · 波动率调整
把因子除以滚动波动率，让低波资产权重更高、高波资产权重更低，等价于 risk parity tilt。

### Vol-target · 目标波动率
反向调整仓位让组合年化波动率接近某个目标值（如 12%）。
高波时降仓位，低波时加仓位。

### Time-Series Momentum (TSM)
单标的的"自身动量"：过去 N 天累计收益 > 0 才持有。S5 趋势倾斜本质就是 TSM。

### Cross-Sectional Momentum
同一截面上"标的之间的动量排序"，按 z-score 倾斜。S4 动量倾斜用的就是这个。

### MA · Moving Average · 移动平均
价格的移动均值。常用 MA60 / MA120 / MA200 判断趋势。
价格 > MA → 上升趋势；价格 < MA → 下行趋势。

### Donchian Channel · 唐奇安通道
N 日最高价 / 最低价构成的通道。突破上轨 = 多头信号，跌破下轨 = 空头信号。

---

## 验证方法

### Smoke Test · 烟雾测试
**用合成数据**跑一遍策略代码，验证机械正确性（接口对、字段全、无 NaN、无未来函数）。
不验证 alpha，只验证"代码跑得通"。

### Real-data Backtest · 真实数据回测
用真实历史数据跑回测，输出 NAV / Sharpe / MaxDD 等核心指标。

### Lookahead Bias · 未来函数
用了"未来才能知道"的信息做今天的决策（典型 bug：用当日收盘价决定当日开盘买入）。
**任何策略代码都必须严格无前瞻**。常见 fix：信号 `shift(1)` 一日。

### Sample / Out-of-sample (IS / OOS) · 样本内 / 样本外
- **IS**：用来调参的数据段
- **OOS**：未参与调参、用来"打脸验证"的数据段
- 优秀策略的 OOS 表现应该和 IS 接近；OOS 显著退化 = 过拟合

### Walk-Forward
滑动窗口的 IS-OOS 框架：在前 N 年调参 → 用第 N+1 年验证 → 滑动一年重复。
最严格的稳健性测试。

### Ablation · 消融实验
逐个关闭策略的组件（如：只留 DCA、关闭再平衡、关闭因子倾斜）看哪部分真正贡献 alpha。
回答"alpha 来自哪里"的核心方法。

### Sensitivity · 参数敏感性
扫描超参（lookback、阈值、α）的取值，看绩效是否稳定。
"参数稍微一动就崩盘" = 过拟合，不能上线。

### Pool Ablation · 池子消融
固定策略、改变标的池（如 6 只 vs 11 只 ETF），分离"标的选择"和"策略本身"的贡献。
S4 v2 通过这个发现 alpha 主要来自扩池而非动量信号。

---

## 标的与数据

### A股 ETF · 中国 A 股 ETF
在 A 股市场（上交所/深交所）交易的指数 ETF。本博客策略主要在 6-11 只主流 A 股 ETF 池中做实验。

### 510300 · 沪深300 ETF
华泰柏瑞沪深 300，本博客所有策略的默认基准。

### 510500 · 中证 500 ETF
覆盖中盘股。

### 159915 · 创业板 ETF
易方达创业板，成长股代表。

### 512100 · 中证 1000 ETF
覆盖小盘股。

### 512880 · 证券 ETF
证券行业，β 高、波动大。

### 512170 · 医疗 ETF
医疗行业。

### 511990 · 华宝添益（场内货币 ETF）
T+0 货币基金 ETF。年化 ~2%，本博客的"现金池"载体。

### 跨资产 / 跨市场池
A 股 ETF + 海外 ETF（如 513100 纳指、513500 标普）+ 商品（如 518880 黄金）+ 债券（如 511260 国债）。
S4 v2 用 11 只跨资产 ETF 做轮动。

### qfq / hfq · 前复权 / 后复权
处理拆分/分红后的价格序列。回测必须用复权价，否则除权日会出现"虚假大跌"。

---

## 工程与实现

### Strategy-Lib
本博客内容的源仓库 [github.com/lizhao903/Strategy-Lib](https://github.com/lizhao903/Strategy-Lib)，
按 `ideas/Sn_xxx/vN/` + `summaries/Sn_xxx/vN/` 双目录维护策略全周期记录。

### Page Bundle
Hugo 中"一篇文章是一个文件夹"的组织方式：`index.md` + 同目录的图片资源。
本博客的 `content/posts/strategies/Sn_xxx_vN/` 都是 Page Bundles。

### Frontmatter
markdown 文件顶部三个 `---` 之间的 YAML 元数据块（title/date/tags/...）。

### Benchmark Suite
一组**共享数据窗口和成本假设**的对照策略集合，确保横向对比的公平性。
本博客的 V1 = S1-S5 在同一时段、同一池、同一手续费下跑出的对照组。

---

> 缺词条？直接在 `content/glossary.md` 文件里追加，文件结构是按主题分组 + 字母（或主题）排序的。
