# -*- coding: utf-8 -*-
"""
Protective Put + Short Call (Collar) 两步对冲策略（当月/次月）
— Step1: 核心对冲（桶A，买入ATM/轻OTM Put，拉回Δ容忍带）
— Step2: 跨日预调仓 + 结构优化（桶B，少量高Gamma Put微调 + 卖OTM Call缓冲Theta）
容量约束：当日≤200手；单到期月≤100手；仅当月/次月
作者：AA（示例）
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import math
import numpy as np
import pandas as pd

# ========= 配置 ========= #

@dataclass
class StrategyConfig:
    # 名义口径：用于把greeks换算到组合名义（例如股票市值或标准化单位）
    notional: float = 200_000_000.0   # 组合名义（示例：2亿）
    contract_multiplier_col: str = "multiplier"  # 合约乘数字段

    # 期限与窗口（仅当月/次月）
    dte_min: int = 10
    dte_max: int = 60

    # Delta容忍带（按名义百分比）
    delta_tol_pct: float = 0.02  # ±2%
    # Theta 目标区间（绝对值，以“每单位标的价格变动的名义”衡量；可按notional缩放）
    theta_target_low: float = -0.10    # -0.10 * (notional基准单位)
    theta_target_high: float = +0.10

    # IV regime 阈值（使用分位数或绝对阈值，二选一）
    iv_high_percentile: float = 0.80   # 高IV：≥80%分位
    iv_low_percentile: float = 0.30    # 低IV：≤30%分位

    # 卖Call比率（相对买Put手数）随IV regime调整
    call_sell_ratio_low_iv: float = 0.3   # 低IV：少卖
    call_sell_ratio_mid_iv: float = 0.5   # 中IV：中等
    call_sell_ratio_high_iv: float = 0.7  # 高IV：相对多卖（仍<1，避免过度封顶）

    # OTM 距离（相对现价）
    put_otm_moneyness_low: float = -0.02  # 轻OTM Put（-2%）
    call_otm_moneyness_high: float = +0.07  # OTM Call（+7%）

    # 风控限额（整体组合）
    max_total_gamma: float = np.inf        # 可设正/负范围，如不希望整体Gamma转负可设下限
    min_total_gamma: float = -np.inf
    max_total_vega: float = np.inf         # 避免过度正Vega
    min_total_vega: float = -np.inf

    # 容量约束
    day_capacity: int = 200
    month_capacity: int = 100  # 当月或次月各自的当日上限

    # 滚动与换档阈值
    dte_roll_threshold: int = 5           # 剩余<=5交易日开始展期
    moneyness_rebalance_band: float = 0.08 # 偏离±8%考虑换档

    # 仅交易这两类月份标记
    allowed_month_buckets: Tuple[str, str] = ("near", "next")

# ========= 数据接口与字段假设 ========= #
"""
合约快照DataFrame（按日）字段约定（index为日期 dt；也可两层index[dt, ticker]）：
- 'ticker': 合约代码
- 'cp':    'P'或'C'
- 'month_bucket': 'near'或'next'（当月/次月）
- 'dte':   剩余交易日（int）
- 'strike': 行权价
- 'spot':   标的现价
- 'moneyness': (spot - strike) / spot   （认沽为负、认购为正的直观口径）
- 'iv':     隐含波动率
- 'delta', 'gamma', 'vega', 'theta': 单份合约的希腊（按期权价格对标的/波动/时间的敏感度）
- 'multiplier': 合约乘数（与标的名义换算）
- 'liquidity_score': 流动性评分（越大越好）
"""

# 你可以把下面的函数替换为你的真实数据源
def load_daily_option_snapshot(dt: pd.Timestamp) -> pd.DataFrame:
    """返回当日当月/次月合约池（含Greeks/IV/DTE等）。此处仅定义接口。"""
    raise NotImplementedError("请对接你自己的数据源。")

def load_portfolio_greeks_without_options(dt: pd.Timestamp) -> Dict[str, float]:
    """返回当日组合剔除期权后的Greeks，例如仅现货/期货部分：{'delta': x}（按notional口径）"""
    raise NotImplementedError("请对接你自己的数据源。")

# ========= 工具函数 ========= #

def iv_percentiles(series: pd.Series, q_low: float, q_high: float) -> Tuple[float, float]:
    return series.quantile(q_low), series.quantile(q_high)

def month_key_from_bucket(bucket: str) -> str:
    # “当月”与“次月”分别以 bucket 做月度容量计数键
    if bucket not in ("near","next"):
        return "other"
    return bucket

def lots_needed(delta_gap_abs: float, unit_delta_abs: float, delta_tol_abs: float) -> int:
    """在允许误差内计算需要的手数（向上取整），避免欠对冲。"""
    if unit_delta_abs <= 0:
        return 0
    # 目标是把abs(delta_gap)降至<=delta_tol_abs
    need = max(0.0, delta_gap_abs - delta_tol_abs) / unit_delta_abs
    return int(math.ceil(need))

def unit_delta(contract_row: pd.Series, notional: float, multiplier_col: str) -> float:
    """把单份合约delta换算到组合名义口径（绝对值）。"""
    return abs(contract_row["delta"] * contract_row[multiplier_col] / notional)

def pick_put_candidates(df: pd.DataFrame, cfg: StrategyConfig, spot: float) -> pd.DataFrame:
    """Step1：优先 ATM/轻OTM Put；Step2：可允许更高Gamma（ATM附近）。"""
    is_allowed = df["cp"].eq("P") & df["month_bucket"].isin(cfg.allowed_month_buckets) \
                 & df["dte"].between(cfg.dte_min, cfg.dte_max)
    sub = df.loc[is_allowed].copy()
    # 距离ATM程度
    sub["atm_distance"] = sub["moneyness"].abs()
    # 成本/Delta（以绝对值计）与流动性排序
    # 避免0除
    eps = 1e-8
    sub["cost_per_delta"] = (sub["iv"].values + eps) / (sub["delta"].abs().values + eps)
    # 排序：成本/Delta 升序、atm距离升序、流动性降序、dte适中
    sub = sub.sort_values(by=["cost_per_delta","atm_distance","liquidity_score","dte"],
                          ascending=[True, True, False, True])
    return sub

def pick_call_candidates(df: pd.DataFrame, cfg: StrategyConfig, spot: float) -> pd.DataFrame:
    """为Collar挑选 OTM Call（+5%~+10%），当月/次月，流动性优先。"""
    is_allowed = df["cp"].eq("C") & df["month_bucket"].isin(cfg.allowed_month_buckets) \
                 & df["dte"].between(cfg.dte_min, cfg.dte_max)
    sub = df.loc[is_allowed].copy()
    # 目标moneyness在正侧（+7%±3%）
    lower = cfg.call_otm_moneyness_high - 0.03
    upper = cfg.call_otm_moneyness_high + 0.03
    sub = sub[(sub["moneyness"] >= lower) & (sub["moneyness"] <= upper)]
    # 排序：权利金/Delta（越大越好），流动性高，dte适中
    eps = 1e-8
    sub["premium_per_delta"] = (sub["iv"].values + eps) / (sub["delta"].abs().values + eps)
    sub = sub.sort_values(by=["premium_per_delta","liquidity_score","dte"],
                          ascending=[False, False, True])
    return sub

def apply_capacity(open_lots: int, day_left: Dict, month_left: Dict, month_key: str, cfg: StrategyConfig) -> int:
    """根据当日/当月剩余额度裁剪手数。"""
    open_lots = min(open_lots, day_left["day"])
    open_lots = min(open_lots, month_left.get(month_key, cfg.month_capacity))
    return max(0, open_lots)

def update_capacity(used: int, day_left: Dict, month_left: Dict, month_key: str):
    day_left["day"] = max(0, day_left["day"] - used)
    month_left[month_key] = max(0, month_left.get(month_key, 0) - used)

# ========= 主流程 ========= #

class CollarHedgeEngine:
    def __init__(self, cfg: StrategyConfig):
        self.cfg = cfg
        # 持仓记录：dict[ticker] = {"lots": +买入/-卖出, "bucket": "A"/"B", "cp": "P"/"C", "month_bucket": "..."}
        self.positions: Dict[str, Dict] = {}

    def _aggregate_option_greeks(self, df_today: pd.DataFrame) -> Dict[str, float]:
        """按持仓聚合Greeks（名义口径）。"""
        total = {"delta":0.0,"gamma":0.0,"vega":0.0,"theta":0.0}
        pos_df = df_today.set_index("ticker")
        for tkr, pos in self.positions.items():
            if tkr not in pos_df.index:
                continue
            row = pos_df.loc[tkr]
            lots = pos["lots"]
            sgn = np.sign(lots)
            qty = abs(lots)
            mul = row[self.cfg.contract_multiplier_col] / self.cfg.notional
            # 买入正、卖出负（lots带符号）
            total["delta"] += lots * row["delta"] * mul
            total["gamma"] += lots * row["gamma"] * mul
            total["vega"]  += lots * row["vega"]  * mul
            total["theta"] += lots * row["theta"] * mul
        return total

    def _place_order(self, ticker: str, lots: int, bucket: str, meta: Dict):
        """下单：更新本地持仓（示例为即时成交）。"""
        if lots == 0:
            return
        if ticker not in self.positions:
            self.positions[ticker] = {"lots": 0, "bucket": bucket,
                                      "cp": meta["cp"], "month_bucket": meta["month_bucket"]}
        self.positions[ticker]["lots"] += lots  # 买入用正，卖出用负
        # bucket 若不同，保持“更保守”的A优先
        if bucket == "A":
            self.positions[ticker]["bucket"] = "A"

    def step1_core_hedge(self, dt: pd.Timestamp, df_today: pd.DataFrame, portfolio_delta_wo_opt: float,
                         day_left: Dict, month_left: Dict) -> float:
        """
        Step1：核心对冲（桶A，买Put），目标把 Δ 拉回容忍带。
        返回：对冲后剩余delta_gap（名义口径）
        """
        cfg = self.cfg
        tol = cfg.delta_tol_pct
        delta_gap = portfolio_delta_wo_opt  # 先不含期权持仓（也可含既有期权，按你的需要）
        if abs(delta_gap) <= tol:
            return delta_gap

        # 仅当月/次月 Put，ATM/轻OTM优先
        spot = df_today["spot"].iloc[0]
        candidates = pick_put_candidates(df_today, cfg, spot)

        for _, c in candidates.iterrows():
            if day_left["day"] <= 0: break
            mkey = month_key_from_bucket(c["month_bucket"])
            if month_left.get(mkey, cfg.month_capacity) <= 0:
                continue

            # 单份合约Δ（名义口径）
            udelta = unit_delta(c, cfg.notional, cfg.contract_multiplier_col)
            need = lots_needed(abs(delta_gap), udelta, tol)
            if need <= 0:
                break

            # 容量约束
            open_lots = apply_capacity(need, day_left, month_left, mkey, cfg)
            if open_lots <= 0:
                continue

            # 买入PUT => lots为正
            self._place_order(c["ticker"], open_lots, bucket="A",
                              meta={"cp": c["cp"], "month_bucket": c["month_bucket"]})

            # 更新delta_gap（Put是负Delta：买入后组合Delta更负；这里用名义口径）
            delta_effect = open_lots * udelta * np.sign(-1.0) * np.sign(delta_gap)  # 顺势对冲
            # 更清晰：若 delta_gap>0（多头过多），买入Put的Δ≈-，应减少gap
            if delta_gap > 0:
                delta_gap -= open_lots * udelta
            else:
                delta_gap += open_lots * udelta  # 若delta_gap<0，一般不买put；此分支通常走不到

            update_capacity(open_lots, day_left, month_left, mkey)

            if abs(delta_gap) <= tol:
                break

        return delta_gap

    def _iv_regime(self, df_today: pd.DataFrame) -> str:
        """基于当日全样本IV分位判断IV regime：'low'/'mid'/'high'"""
        iv = df_today["iv"].dropna()
        if len(iv) < 10:
            return "mid"
        lo, hi = iv_percentiles(iv, self.cfg.iv_low_percentile, self.cfg.iv_high_percentile)
        iv_median = iv.median()
        # 这里用“当日中位数 vs 分位阈值”的简化判定
        if iv_median <= lo:
            return "low"
        if iv_median >= hi:
            return "high"
        return "mid"

    def step2_preadjust_and_collar(self, dt: pd.Timestamp, df_today: pd.DataFrame,
                                   portfolio_delta_after_step1: float,
                                   day_left: Dict, month_left: Dict) -> None:
        """
        Step2：预调仓 + 结构优化：
          1）若预测T+1 Δ越界：在桶B用少量“高Gamma Put(ATM附近)”微调（买入）；
          2）结合IV regime 卖出OTM Call获取权利金，缓解Theta，控制Vega；
          3）若Step2后预测Δ入带，且“当日开仓”尚未执行，可跳过额外开仓（由调用方掌控）。
        """
        cfg = self.cfg
        tol = cfg.delta_tol_pct
        spot = df_today["spot"].iloc[0]

        # —— 2.1 预测T+1 Delta（保守：价格持平 + 期限推进 + 伪保守系数）——
        # 简化：用当日对冲后Delta近似T+1（可接入你自己的预测器/夜盘场景）
        pred_delta_t1 = portfolio_delta_after_step1

        # —— 2.2 高Gamma Put微调（仅当|pred_delta_t1|>tol）——
        if abs(pred_delta_t1) > tol and day_left["day"] > 0:
            # 再挑ATM附近Put（Gamma更高）
            puts = pick_put_candidates(df_today, cfg, spot)
            # 进一步靠近ATM
            puts = puts.sort_values(by=["atm_distance","cost_per_delta","liquidity_score"],
                                    ascending=[True, True, False])
            for _, c in puts.iterrows():
                if day_left["day"] <= 0: break
                mkey = month_key_from_bucket(c["month_bucket"])
                if month_left.get(mkey, cfg.month_capacity) <= 0:
                    continue
                udelta = unit_delta(c, cfg.notional, cfg.contract_multiplier_col)
                need = lots_needed(abs(pred_delta_t1), udelta, tol)
                if need <= 0:
                    break
                open_lots = apply_capacity(min(need, 20), day_left, month_left, mkey, cfg)  # Step2微调设上限20
                if open_lots <= 0:
                    continue

                # 买入PUT（桶B）
                self._place_order(c["ticker"], open_lots, bucket="B",
                                  meta={"cp": c["cp"], "month_bucket": c["month_bucket"]})

                # 更新预测Δ
                if pred_delta_t1 > 0:
                    pred_delta_t1 -= open_lots * udelta
                else:
                    pred_delta_t1 += open_lots * udelta

                update_capacity(open_lots, day_left, month_left, mkey)

                if abs(pred_delta_t1) <= tol:
                    break

        # —— 2.3 Collar：根据IV regime 卖出OTM Call（备兑，桶B）——
        regime = self._iv_regime(df_today)
        if regime == "low":
            call_ratio = self.cfg.call_sell_ratio_low_iv
        elif regime == "high":
            call_ratio = self.cfg.call_sell_ratio_high_iv
        else:
            call_ratio = self.cfg.call_sell_ratio_mid_iv

        if day_left["day"] > 0 and call_ratio > 0:
            calls = pick_call_candidates(df_today, cfg, spot)
            # 卖出手数上限 = 已买入Put手数 * ratio （粗略估计：用“今日新增Put总手数”也行）
            # 这里用当前“桶A+桶B”的Put净手数估计
            put_lots_total = 0
            for tkr, pos in self.positions.items():
                if pos["cp"] == "P":
                    put_lots_total += max(0, pos["lots"])  # 买入Put为正
            target_call_sell = int(math.floor(put_lots_total * call_ratio))

            # 当前已卖Call手数
            current_call_sold = 0
            for tkr, pos in self.positions.items():
                if pos["cp"] == "C":
                    current_call_sold += max(0, -pos["lots"])  # 卖出为负lots

            to_sell = max(0, target_call_sell - current_call_sold)

            for _, c in calls.iterrows():
                if day_left["day"] <= 0 or to_sell <= 0:
                    break
                mkey = month_key_from_bucket(c["month_bucket"])
                if month_left.get(mkey, cfg.month_capacity) <= 0:
                    continue
                # 卖Call lots为负
                open_lots = apply_capacity(min(to_sell, 20), day_left, month_left, mkey, cfg)  # 分散成交
                if open_lots <= 0:
                    continue
                self._place_order(c["ticker"], -open_lots, bucket="B",
                                  meta={"cp": c["cp"], "month_bucket": c["month_bucket"]})
                update_capacity(open_lots, day_left, month_left, mkey)
                to_sell -= open_lots

    def roll_and_switch(self, dt: pd.Timestamp, df_today: pd.DataFrame,
                        day_left: Dict, month_left: Dict):
        """展期与换档：DTE过低、moneyness偏离、效率恶化时进行替换（受容量约束）"""
        cfg = self.cfg
        if day_left["day"] <= 0:
            return
        # 标记需要处理的持仓
        pos_df = df_today.set_index("ticker")
        to_close = []
        for tkr, pos in list(self.positions.items()):
            if tkr not in pos_df.index:
                continue
            row = pos_df.loc[tkr]
            lots = pos["lots"]
            if lots == 0:
                continue
            need_roll = (row["dte"] <= cfg.dte_roll_threshold)
            need_switch = (abs(row["moneyness"]) >= cfg.moneyness_rebalance_band)
            if need_roll or need_switch:
                to_close.append((tkr, pos, row))

        # 简化：将需要处理的持仓先平掉，再找等风险新券开回（容量允许的情况下）
        for tkr, pos, row in to_close:
            if day_left["day"] <= 0:
                break
            lots = pos["lots"]
            mkey = month_key_from_bucket(pos["month_bucket"])
            # 平仓占用容量（这里也计入，因为真实交易会吃容量/成交能力）
            close_lots = apply_capacity(abs(lots), day_left, month_left, mkey, self.cfg)
            if close_lots <= 0:
                continue
            # 平掉close_lots
            self._place_order(tkr, -np.sign(lots)*close_lots, bucket=pos["bucket"],
                              meta={"cp": pos["cp"], "month_bucket": pos["month_bucket"]})
            update_capacity(close_lots, day_left, month_left, mkey)

            # 重新开回（按当前规则再选一只）：
            # 认沽 -> 选ATM/轻OTM Put；认购 -> 选OTM Call
            spot = df_today["spot"].iloc[0]
            if pos["cp"] == "P":
                candidates = pick_put_candidates(df_today, self.cfg, spot)
                # 近似用等手数开回到更合适的券（如有余量）
                for _, c in candidates.iterrows():
                    if day_left["day"] <= 0:
                        break
                    mkey2 = month_key_from_bucket(c["month_bucket"])
                    open_back = apply_capacity(close_lots, day_left, month_left, mkey2, self.cfg)
                    if open_back <= 0:
                        continue
                    self._place_order(c["ticker"], open_back, bucket=pos["bucket"],
                                      meta={"cp": c["cp"], "month_bucket": c["month_bucket"]})
                    update_capacity(open_back, day_left, month_left, mkey2)
                    break
            else:  # Call
                candidates = pick_call_candidates(df_today, self.cfg, spot)
                for _, c in candidates.iterrows():
                    if day_left["day"] <= 0:
                        break
                    mkey2 = month_key_from_bucket(c["month_bucket"])
                    open_back = apply_capacity(close_lots, day_left, month_left, mkey2, self.cfg)
                    if open_back <= 0:
                        continue
                    # 卖出开回
                    self._place_order(c["ticker"], -open_back, bucket=pos["bucket"],
                                      meta={"cp": c["cp"], "month_bucket": c["month_bucket"]})
                    update_capacity(open_back, day_left, month_left, mkey2)
                    break

    # ====== 日度驱动 ====== #
    def run_one_day(self, dt: pd.Timestamp, df_today: pd.DataFrame, portfolio_delta_wo_opt: float):
        cfg = self.cfg
        # 每日容量重置
        day_left = {"day": cfg.day_capacity}
        month_left = {mb: cfg.month_capacity for mb in cfg.allowed_month_buckets}

        # Step 0: 计算现有期权持仓Greeks，更新组合Delta（如需）
        opt_greeks = self._aggregate_option_greeks(df_today)
        portfolio_delta_before = portfolio_delta_wo_opt + opt_greeks["delta"]

        # Step 1: 核心对冲（桶A，买Put）
        delta_gap_after_step1 = self.step1_core_hedge(
            dt, df_today, portfolio_delta_before, day_left, month_left
        )

        # Step 2: 预调仓 + Collar（桶B）
        self.step2_preadjust_and_collar(
            dt, df_today, delta_gap_after_step1, day_left, month_left
        )

        # 展期/换档
        self.roll_and_switch(dt, df_today, day_left, month_left)

        # 汇总
        opt_greeks_after = self._aggregate_option_greeks(df_today)
        result = {
            "dt": dt,
            "portfolio_delta_before": portfolio_delta_before,
            "portfolio_delta_after": portfolio_delta_wo_opt + opt_greeks_after["delta"],
            "opt_theta_after": opt_greeks_after["theta"],
            "opt_gamma_after": opt_greeks_after["gamma"],
            "opt_vega_after":  opt_greeks_after["vega"],
            "day_capacity_left": day_left["day"],
            "month_capacity_left_near": month_left.get("near", 0),
            "month_capacity_left_next": month_left.get("next", 0),
            "positions": self.positions.copy()
        }
        return result

# ========= 快速联调（可删除） ========= #

def mock_data_provider(dt: pd.Timestamp, spot: float = 100.0) -> Tuple[pd.DataFrame, Dict[str,float]]:
    """
    造一批当月/次月的P/C合约示例数据（用于联调）。
    注意：仅为示意，Greeks/IV等是随机生成。
    """
    rng = np.random.default_rng(abs(hash(str(dt))) % (1<<32))
    n = 80
    month_bucket = rng.choice(["near","next"], size=n, p=[0.6,0.4])
    cp = rng.choice(["P","C"], size=n)
    dte = np.where(month_bucket=="near", rng.integers(8,35,size=n), rng.integers(25,65,size=n))
    strike = np.round(spot * (1 + rng.normal(0, 0.08, size=n)), 2)
    moneyness = (spot - strike) / spot  # C为正、P为负的口径无所谓，排序用
    iv = np.clip(rng.normal(0.25, 0.05, size=n), 0.10, 0.60)
    delta = np.clip(rng.normal(0.5, 0.2, size=n), 0.05, 0.95)
    # 调整符号：P为负delta、C为正delta
    delta = np.where(cp=="P", -np.abs(delta), np.abs(delta))
    gamma = np.clip(rng.normal(0.02, 0.01, size=n), 0.005, 0.04)
    # P/C gamma同号（正），theta为负（多头），卖出后会变号
    theta = -np.clip(rng.normal(0.02, 0.01, size=n), 0.005, 0.05)
    vega = np.clip(rng.normal(0.10, 0.03, size=n), 0.02, 0.20)
    multiplier = np.full(n, 100.0)
    liq = rng.uniform(0,1,size=n)

    df = pd.DataFrame({
        "dt": dt, "ticker": [f"T{dt.strftime('%m%d')}{i:03d}" for i in range(n)],
        "cp": cp, "month_bucket": month_bucket, "dte": dte, "strike": strike,
        "spot": spot, "moneyness": (spot - strike)/spot, "iv": iv,
        "delta": delta, "gamma": gamma, "theta": theta, "vega": vega,
        "multiplier": multiplier, "liquidity_score": liq
    })
    # 组合（无期权）Delta：假设为正（多头）
    port_wo_opt = {"delta": +0.06}  # +6% 名义
    return df, port_wo_opt

if __name__ == "__main__":
    cfg = StrategyConfig()
    engine = CollarHedgeEngine(cfg)

    # 演示连续3天
    dates = pd.date_range("2025-09-18", periods=3, freq="B")
    for dt in dates:
        df_today, port_wo_opt = mock_data_provider(dt, spot=100.0)
        res = engine.run_one_day(dt, df_today, portfolio_delta_wo_opt=port_wo_opt["delta"])
        print(f"{dt.date()} 结果：")
        print(f"  Δ(前) = {res['portfolio_delta_before']:.4f},  Δ(后) = {res['portfolio_delta_after']:.4f}")
        print(f"  Θ(后) = {res['opt_theta_after']:.4f}, Γ(后) = {res['opt_gamma_after']:.4f}, 𝜈(后) = {res['opt_vega_after']:.4f}")
        print(f"  容量余量：当日={res['day_capacity_left']}, 当月={res['month_capacity_left_near']}, 次月={res['month_capacity_left_next']}")
        print(f"  持仓数：{len(res['positions'])}")
        print("-"*60)