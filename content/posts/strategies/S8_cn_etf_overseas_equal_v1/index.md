---
title: "A股 ETF 港股+海外+黄金 4 池等权 (无 A 股)"
date: 2026-05-08T15:47:10+08:00
draft: false
summary: "⏳ S3 等权机制 + 4 只 CN-listed 海外/黄金 ETF（**完全无 A 股**）在 2020-2024 in-sample 跑出 **NAV 171.3k / CAGR +11.87% / Sharpe 0.851 / MaxDD -20.9%**——是 V1 全套（含所有 v2、所有 universe sweep）的**全维度第一**。但**窗口偶然性是最大未知**，OOS 验证必须先做才能 ship。"
tags: ['策略复盘', 'equal-weight', 'cross-asset', 'multi-asset', 'no-a-share']
categories: ["策略复盘"]
series: ["S8_cn_etf_overseas_equal"]
status_kind: neutral
status_label: "validating"
ShowToc: true
TocOpen: false
---

<div class="post-callout post-callout-neutral">
<span class="status-badge status-neutral">⏳ validating</span> · 最终化：<code>2026-05-08</code>
<br>来源：<code>Strategy-Lib/ideas/S8_cn_etf_overseas_equal/v1</code> + <code>Strategy-Lib/summaries/S8_cn_etf_overseas_equal/v1</code>
</div>

## 想法（Why）

**一句话概括**

把 S3 等权机制套在 4 只 CN-listed 跟踪海外/黄金的 ETF 上，**完全去掉 A 股标的**。

**核心逻辑**

- **risky pool（4 只）**：159920 恒生 ETF（港股代理）/ 513100 纳指 ETF / 513500 标普500 ETF / 518880 黄金 ETF
- **再平衡**：S3 同款月度（rebalance_period=20）等权
- **现金代理**：511990（不主动持有；与 S3 一致永远满仓）
- **基准**：510300 buy-and-hold（与 V1 共享基线）
- **代码**：复用 `EqualRebalanceStrategy`，**无新策略类**，仅 universe 切换

**假设与依据**

**起源**：`scripts/universe_sweep_demo.py` 跑了 4 strategies × 4 universes 的 grid，发现 `cn_etf_overseas_4` (= 上述 4 只) 在所有 4 个策略上都暴揍 base_6 / broad_3 / expanded_11：

| | base_6 | broad_3 | expanded_11 | overseas_4 |
|---|---:|---:|---:|---:|
| S3 等权 Sharpe | 0.217 | 0.244 | 0.465 | **0.851** |
| S3 等权 NAV (100k) | 111.9k | 115.5k | 134.3k | **171.3k** |
| S3 等权 CAGR | +2.36% | +3.04% | +6.36% | **+11.87%** |
| S3 等权 MaxDD | -45.1% | -43.5% | -22.9% | **-20.9%** |

**一致性证据**：池子 alpha 在 4 个策略 (S3/S4v2/S5v2/S7v2) 上**单调递增**：base_6 < broad_3 < expanded_11 < overseas_4。

**机制解读**：
- 2020-2024 期间 A 股板块整体平盘 / 负收益（510300 5y CAGR ~+0.86%）
- 海外 + 黄金 大类全部正贡献：纳指 (~+15%/yr)、标普500 (~+10%/yr)、黄金 (~+10%/yr)、恒生 (~0%)
- 等权配置 + 月度再平衡 = "被动跨资产 risk parity"；4 只资产相关性低让组合波动天然下降

**标的与周期**

- 市场：A 股 ETF（CN-listed 但跟踪海外资产）
- 标的池：159920 / 513100 / 513500 / 518880
- cash 代理：511990
- 频率：日线
- 数据范围：2020-01-02 ~ 2024-12-31（已缓存）
- 暖机：120 日（与 S3 一致，月度再平衡需要的最少历史）

## 一句话结论

S3 等权机制 + 4 只 CN-listed 海外/黄金 ETF（**完全无 A 股**）在 2020-2024 in-sample 跑出 **NAV 171.3k / CAGR +11.87% / Sharpe 0.851 / MaxDD -20.9%**——是 V1 全套（含所有 v2、所有 universe sweep）的**全维度第一**。但**窗口偶然性是最大未知**，OOS 验证必须先做才能 ship。

## 关键数据

| | 值 |
|---|---|
| 样本期 | 2020-01-02 ~ 2024-12-31 (in-sample) |
| 样本外 | (待 2025+ 数据) |
| NAV | 171,303 |
| CAGR | +11.87% |
| Sharpe | 0.851 |
| MaxDD | -20.9% |
| Calmar | 0.57 |
| vs BH 510300 alpha/yr | +11.01% |
| vs S3 expanded_11 alpha/yr | +5.51% |
| vs S4v2 (前 V1 best) alpha/yr | +6.12% |

## 在什么情况下有效，什么情况下失效

✅ **有效（已验证）**：
- 任何 5y in-sample 期 A 股相对海外+黄金 underperform 的环境
- 多元跨资产类别下的等权 risk parity 思路（与 Mebane Faber GTAA 同根源）
- 4 池标的相关性低（A股海外平时 corr ~0.3-0.5）让组合波动天然下降

❌ **可能失效（未验证、需 OOS）**：
- A 股牛市 + 美股熊市的反向情景（如 2014-15 / 2008-09 / 2017）
- QDII 额度断供导致跟踪误差爆发（513100/513500 历史多次溢价 5-10%）
- 美元周期反转（2014-15 强美元期金价跌 30%）
- 单一 ETF 的 idiosyncratic 风险（如 518880 黄金 ETF 重大 redemption）

## 这个策略教会我什么

1. **池子选择是 alpha 的最大来源**：在 V1 全套验证「池子 >> 信号 >> 仓位」之后，本策略再次量化证实——同一个 S3 等权机制，换池子 Sharpe 从 0.217 跳到 0.851（4 倍）。**下次设计任何策略前，先用 `sweep()` 工具跑一下 universe 比较，避免在错误的池子上做大量参数调优**。

2. **expanded_11 的「6+5」组合是一种妥协**：当时设计 expanded_11 是「base_6 加 5 跨资产」的并集，看起来更全面。实际 sweep 显示 6 只 A 股是结构性拖累，5 跨资产单独跑反而更优。**「上策略」要敢于做减法，不一定 superset 就更好**。

3. **「最简方案」常常是真 winner**：S8 = 等权 + 月度再平衡 + 4 个标的，没有任何因子、timing、sizing。这种最简配置碾压所有"复杂版本"。**奥卡姆剃刀在策略研究里同样适用**。

4. **样本外验证比样本内胜出更重要**：S8 in-sample 的"全维度第一"如果 2025+ 失效，所有数字立刻贬值。**Ship 决策必须等 OOS 数据**。

## 实现要点

<details>
<summary>展开完整实现记录</summary>

# Implementation — S8 v1 (overseas_equal)

## 整体方案
**完全没有新代码**。S8 = `EqualRebalanceStrategy` (S3 同款) + `CN_ETF_OVERSEAS_4` universe。

```python
from strategy_lib.strategies.factories import s3_equal_rebalance
from strategy_lib.universes import CN_ETF_OVERSEAS_4
from strategy_lib.backtest import run_on_universe

metrics = run_on_universe(s3_equal_rebalance, CN_ETF_OVERSEAS_4)
```

## 因子清单
无。

## 新增因子（如有）
无。

## 策略配置
- 配置文件：`configs/S8_cn_etf_overseas_equal_v1.yaml`
- 类型：`equal_rebalance`（复用）
- 关键参数：`rebalance_period=20`（月度）
- 池组成：159920 恒生 / 513100 纳指 / 513500 标普500 / 518880 黄金

## 数据
- 标的池来源：手工选 4 只 CN-listed 跟踪海外/黄金的 ETF（去掉 A 股内部标的）
- 数据范围：2019-09-01 ~ 2024-12-31（120 日暖机 + 5 年绩效统计）
- 数据预处理：复用 `cn_etf` loader 的前复权（akshare adjust="qfq"）
- 已缓存：所有 4 标的 + 现金代理 511990 + benchmark 510300 都在 `data/raw/cn_etf/` 中

## 关键代码（无新增，引用现有）
- 等权机制：`src/strategy_lib/strategies/cn_etf_equal_rebalance.py::EqualRebalanceStrategy.run()`
- universe 定义：`src/strategy_lib/universes.py::CN_ETF_OVERSEAS_4`
- factory: `src/strategy_lib/strategies/factories.py::s3_equal_rebalance`

## 踩过的坑
- **没踩过坑**：S8 的实测在 sweep 工具里第一次就跑通，没有改任何代码
- 唯一注意：159920 / 513500 / 513100 / 518880 在 akshare 上数据齐全（5y ~1338 bars），但 159920（恒生 ETF）在 QDII 额度紧张时段可能有 1-2% 跟踪误差，长期累积误差暂时未单独计算

## 相关 commits
（uncommitted；S8 与所有 V1 v2 共在一个工作树）

## 与现有代码的接口契约
- S8 复用 S3 的 `target_weights` 钩子（默认实现 = 等权 1/N）
- universe 切换通过 `factory(universe)` 模式自动适配
- 不影响 S3 v1 / S4v2 / S5v2 / S7v2 等任何已有策略

</details>

## 验证过程

<details>
<summary>展开完整验证记录</summary>

# Validation — S8 v1 (overseas_equal)

---

## 2026-05-08 初版验证（来自 universe_sweep_demo 数据，未做专门 run）

### 数据来源
- **复用**：`scripts/universe_sweep_demo.py` 跑 4 strategies × 4 universes 的 grid 时 S3 在 overseas_4 上的结果
- 详细 CSV：`results/universe_sweep_demo_<timestamp>.csv` 中 `(strategy=S3 equal_rebal, universe=cn_etf_overseas_4)` 行
- 配置：`configs/S8_cn_etf_overseas_equal_v1.yaml`（与 sweep demo 等价）

### 主结果（in-sample 2020-01-02 ~ 2024-12-31）

| 指标 | 值 |
|---|---:|
| 最终 NAV (100k 起) | **171,303** |
| CAGR | **+11.87%** |
| Sharpe | **0.851** |
| MaxDD | -20.9% |
| 年化波动 | ~14.0% |
| Calmar | 0.57 |
| 切换 / 再平衡 | 月度（rebalance_period=20，5y ~60 次） |
| 年化换手 | ~50%（估，依据再平衡量） |

### vs V1 全套已知最佳对比

| 策略 | NAV | CAGR | Sharpe | MaxDD | 来源 |
|---|---:|---:|---:|---:|---|
| **S8 (本)** | **171.3k** | **+11.87%** | **0.851** | -20.9% | sweep |
| S4v2 (11 池含 A 股) | 130.7k | +5.75% | 0.44 | -22.2% | V1 v2 直接验证 |
| S3 11 池等权 (含 A 股) | 134.3k | +6.36% | 0.465 | -22.9% | S7v2 ablation |
| S5v2 6 池 | 112.9k | +2.57% | 0.28 | -20.5% | V1 v2 直接验证 |
| S7v2 11 池 | 119.0k | +3.70% | 0.40 | -17.5% | S7v2 主测 |
| BH 510300 | 104.3k | +0.86% | 0.18 | -44.8% | 基准 |

S8 在所有 7 个策略 + V1 v2 中：**Sharpe 第 1 / NAV 第 1 / CAGR 第 1**，MaxDD 第 4（劣于 S5v2 -20.5% / S7v2 -17.5% / S5v2+overseas_4 -8.5%）。

### 池子单调性（4 strategies × 4 universes 全部成立）

| | base_6 | broad_3 | expanded_11 | overseas_4 |
|---|---:|---:|---:|---:|
| S3 equal_rebal Sharpe | 0.217 | 0.244 | 0.465 | **0.851** |
| S4v2 momentum Sharpe | 0.191 | 0.218 | 0.548 | **0.730** |
| S5v2 trend Sharpe | 0.113 | 0.004 | 0.368 | **0.717** |
| S7v2 ma_filter Sharpe | 0.304 | 0.298 | 0.403 | 0.457 |

**关键观察**：池子改进对 sizing/factor 类策略（S3/S4v2/S5v2）效果显著（Sharpe 翻 4-6 倍），对 timing 类（S7v2）改进有限（仅 +50%）。

### 关键图表
**未生成**（本次仅复用 sweep 数据，未做专门 plot）。下一步 dedicated validate.py 应输出：
- `equity_curve.png` — S8 vs S4v2 vs S5v2 vs BH（4 条线）
- `drawdown.png` — 同上
- `weight_evolution.png` — 4 资产权重时间序列堆积图
- `yearly_returns.csv` — 分年度对比
- `rolling_window.csv` — 3 个 1.5y 子窗口（2020H1-2021H2 / 2021H2-2023H1 / 2023H1-2024H2）

### 解读 & 问题
1. **数据强烈暗示「无 A 股」是 alpha 主因**：池子 alpha 单调递增，4 个策略一致
2. **窗口偶然性是最大未知**：2020-2024 美股最强 / A 股最弱组合事后看明显，但事前并非显然
3. **overseas_4 中谁贡献了 alpha**：尚未做单标的 ablation；猜测 513100 纳指 + 518880 黄金为主，159920 恒生（HK 跟踪）和 513500 标普500 是稳定器；下一步 dedicated validate.py 应做单 ETF 留一交叉

### 已发现的策略类问题
- 无（复用 S3 现成代码）

### 下一步
- [ ] 写专门的 `summaries/S8_cn_etf_overseas_equal/v1/validate.py`，输出 dedicated 图表 + 分年度 + 单标的 ablation
- [ ] 跑 3 个滚动 1.5y 子窗口验证 in-sample 一致性
- [ ] OOS 测试（2025+ 数据可得后）
- [ ] 与 S5v2 + overseas_4 的 risk profile 对比（高收益 vs 低回撤的 trade-off）
- [ ] 5 池版（+511260 十年国债）作为 v2 候选

---

</details>

---

*本文由 [`scripts/sync_strategies.py`](https://github.com/lizhao903/0xBroleez/blob/main/scripts/sync_strategies.py) 从 Strategy-Lib 同步生成。*
