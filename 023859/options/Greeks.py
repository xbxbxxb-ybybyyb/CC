import math
import pandas as pd
import numpy as np
from tqdm import tqdm
import os
assert os.system('pip install pulp') == 0
import pulp
from collections import defaultdict, Counter
from xquant.factordata import FactorData
fd = FactorData()

# ---------- 常用工具 ----------
SQRT2PI = math.sqrt(2.0 * math.pi)

# ==================== 工具函数 ====================

def _unit_theta_per_abs_delta(theta, delta):
    ad = abs(delta) + 1e-12
    return abs(theta) / ad  # 每对冲1单位|delta|的日度Theta损耗（越小越好）

def _unit_abs_delta(delta):
    return abs(delta)  # 每手能贡献的|delta|

def _theta_budget(v_stock, theta_budget_ratio):
    return theta_budget_ratio * v_stock  # 负值，越远离0表示越宽松

def _apply_caps(ask_qty, remain_mat_cap, remain_total_cap):
    """裁剪下单量到【单到期额度、全局额度】允许范围内"""
    return int(max(0, min(int(ask_qty), int(remain_mat_cap), int(remain_total_cap))))

def _drop_missing_or_expired_holdings(holdings, day_df_all, total_cap_left):
    """不在当日盘口（到期/下市）的持仓全部平掉"""
    today_ids = set(day_df_all.index)
    closes = {}
    for oid, q in list(holdings.items()):
        if oid not in today_ids:
            closes[oid] = closes.get(oid,0) + int(q)
            mat = day_df_all.loc[oid, 'maturity']
            total_cap_left[mat] += int(q)
            holdings.pop(oid, None)
    return closes, holdings, total_cap_left

# ==================== 跨日预调仓（先卖后买） ====================
def _pretrim_overhedge_holdings(day_df_all, holdings, delta_star, total_cap_left):
    flag = False
    if not holdings:
        return {}, total_cap_left, 0.0, 0.0, 0.0, 0.0, flag

    ref = day_df_all[['delta','gamma','vega','theta','maturity','IV','moneyness']]
    rows = []
    for oid, q in holdings.items():
        if oid not in ref.index:
            continue
        r = ref.loc[oid]
        rows.append(dict(opt_id=oid, qty=q, delta=r['delta'], gamma=r['gamma'],
                         vega=r['vega'], theta=r['theta'], maturity=r['maturity'], IV=r['IV'], moneyness=r['moneyness']))
    if not rows:
        return {}, total_cap_left, 0.0, 0.0, 0.0, 0.0, flag

    pos = pd.DataFrame(rows).set_index('opt_id')
    delta_hold = float((pos['qty'] * pos['delta']).sum())

    overhedged = (abs(delta_hold) >= abs(delta_star))
    if not overhedged:
        # 汇总greeks
        g = float((pos['qty'] * pos['gamma']).sum())
        v = float((pos['qty'] * pos['vega']).sum())
        t = float((pos['qty'] * pos['theta']).sum())
        return holdings, total_cap_left, delta_hold, g, v, t, flag

    # 如超额对冲，设计算法进行平仓
    flag = True
    pos['var'] = pos.index
    pos_call = pos[pos['delta'] > 0]
    pos_put = pos[pos['delta'] <= 0]
    prob = pulp.LpProblem('Determine_Pos', pulp.LpMaximize)  # 最大化对冲效率

    close_vars = pulp.LpVariable.dicts('Close', pos_put['var'], upBound=0, cat='Continuous')
    close_vars.update(pulp.LpVariable.dicts('Close', pos_call['var'], lowBound=0, cat='Continuous'))

    # 设置目标函数
    prob += pulp.lpSum([pos.loc[i,'theta'] * (holdings.get(i,0) + close_vars[i]) for i in pos['var']]), 'Theta_Max'

    # 添加约束条件
    for i in pos['var']:
        if holdings[i] >= 0:
            prob += holdings[i] + close_vars[i] >= 0, f'Close_limit_{i}'
        else:
            prob += holdings[i] + close_vars[i] <= 0, f'Close_limit_{i}'

    # 风险管理
    prob += pulp.lpSum([pos.loc[i,'delta'] * close_vars[i] for i in pos['var']]) == delta_star - delta_hold, 'Delta_Neutral'
    # prob += pulp.lpSum([pos.loc[i,'vega'] * (holdings.get(i,0)+close_vars[i]) for i in pos['var']]) == 0, 'Vega_Neutral'
    # prob += pulp.lpSum([pos.loc[i,'gamma'] * (holdings.get(i,0)+close_vars[i]) for i in pos['var']]) == 0, 'Gamma_Neutral'

    prob.solve()
    if pulp.LpStatus[prob.status] != 'Optimal':
        raise Exception('线性规划问题未能找到最优解')
        # del prob.constraints['Delta_Neutral']
        # prob += pulp.lpSum([pos.loc[i,'delta'] * close_vars[i] for i in pos['var']]), 'Delta_Max'
        # prob.solve()
        # if pulp.LpStatus[prob.status] != 'Optimal':
        #     raise Exception('线性规划问题未能找到最优解')

    # 更新持仓
    pos['Close'] = [pulp.value(close_vars[i]) for i in pos['var']]
    for _, row in pos.iterrows():
        oid = row.name
        q = int(row['Close'])
        holdings[oid] = holdings.get(oid, 0) + q
        mat = row['maturity']
        total_cap_left[mat] += (q if q>0 else -q)
    # 新汇总
    d = g = v = t = 0.0
    for oid, q in holdings.items():
        if oid in ref.index:
            rr = ref.loc[oid]
            d += q * rr['delta']; g += q * rr['gamma']; v += q * rr['vega']; t += q * rr['theta']

    return holdings, total_cap_left, d, g, v, t, flag


# ==================== 跨日预调仓（先卖后买） ====================
def pretrim_overhedge_holdings(day_df, holdings, delta_star, total_cap_left, delta_band_pct=0.05):
    """
    若持仓Δ超出容忍带（|Δ_hold| > |Δ*|），在持仓内先卖：
      1) 单位|Δ|的Theta成本最高优先
      2) 同等时，单位|Δ|更大优先
    卖到回到容忍带，或无票可卖为止。
    """
    if not holdings:
        return {}, total_cap_left, 0.0, 0.0, 0.0, 0.0

    ref = day_df.set_index('opt_id')[['delta','gamma','vega','theta','maturity','IV','moneyness']]
    rows = []
    for oid, q in holdings.items():
        if q <= 0 or oid not in ref.index:
            continue
        r = ref.loc[oid]
        rows.append(dict(opt_id=oid, qty=q, delta=r['delta'], gamma=r['gamma'],
                         vega=r['vega'], theta=r['theta'], maturity=r['maturity'], IV=r['IV'], moneyness=r['moneyness']))
    if not rows:
        return {}, total_cap_left, 0.0, 0.0, 0.0, 0.0

    pos = pd.DataFrame(rows)
    delta_hold = float((pos['qty'] * pos['delta']).sum())

    overhedged = (delta_star < 0 and delta_hold < (1 + delta_band_pct) * delta_star)
    if not overhedged:
        # 汇总greeks
        g = float((pos['qty'] * pos['gamma']).sum())
        v = float((pos['qty'] * pos['vega']).sum())
        t = float((pos['qty'] * pos['theta']).sum())
        return [], total_cap_left, delta_hold, g, v, t

    pos['u_theta_per_abs_delta'] = pos.apply(lambda r: _unit_theta_per_abs_delta(r['theta'], r['delta']), axis=1)
    pos['u_abs_delta'] = pos['delta'].abs()

    # if pos.loc[(pos['moneyness'] - 1.0).abs().idxmin(),'IV'] > 0.25:
    #     pos = pos.sort_values(['vega', 'u_abs_delta'], ascending=[False, False])
    # else:
    #     pos = pos.sort_values(['theta', 'u_abs_delta'], ascending=[True, False])
    pos = pos.sort_values(['theta', 'u_abs_delta'], ascending=[True, False])

    sells = {}
    for _, r in pos.iterrows():
        if (delta_star < 0 and delta_hold >= delta_star) or (delta_star > 0 and delta_hold <= delta_star):
            break
        max_sell = int(r['qty'])
        for _ in range(max_sell):
            # 卖一手
            sells[r['opt_id']] = sells.get(r['opt_id'],0)+1
            delta_hold -= r['delta']
            r['qty'] -= 1
            if (delta_star < 0 and delta_hold >= delta_star) or (delta_star > 0 and delta_hold <= delta_star):
                break

    # 应用到 holdings
    for oid, q in sells.items():
        holdings[oid] = holdings.get(oid, 0) - q
        mat = day_df.loc[day_df['opt_id']==oid,'maturity']
        total_cap_left[mat] += q
        if holdings[oid] <= 0:
            holdings.pop(oid, None)

    # 新汇总
    g = v = t = 0.0
    for oid, q in holdings.items():
        if q > 0 and oid in ref.index:
            rr = ref.loc[oid]
            g += q * rr['gamma']; v += q * rr['vega']; t += q * rr['theta']
    return sells, total_cap_left, delta_hold, g, v, t

# ==================== Stage 1：核心对冲（带开仓上限） ====================

def stage1_core_hedge_with_caps(day_df, target_core,
                                per_mat_cap_left, total_cap_left,
                                prefer_next_month=True, min_lot=1):
    """
    用“单位|Δ|的Theta成本最低”的基桶（每到期ATM+轻虚值）完成 ~core_ratio 的目标；遵守开仓上限。
    """
    # base = []
    # for _, dfm in day_df.groupby('maturity'):
    #     d2 = dfm.copy()
    #     # ATM ~ 1.0； 轻虚值 ~ 0.97
    #     atm_idx = (d2['moneyness'] - 1.01).abs().idxmin()
    #     otm_idx = (d2['moneyness'] - 0.99).abs().idxmin()
    #     d2.loc[:, 'bucket'] = None
    #     d2.loc[atm_idx, 'bucket'] = 'ATM'
    #     d2.loc[otm_idx, 'bucket'] = 'OTM1'
    #     base.append(d2[d2['bucket'].notna()])
    # base = pd.concat(base) if base else pd.DataFrame(columns=day_df.columns)
    base = day_df[(day_df['moneyness']>=0.97)].copy()
    base = base[base['delta']*target_core > 0]
    if base.empty:
        return {}, 0.0, 0.0, 0.0, 0.0, per_mat_cap_left, total_cap_left

    base['mat_rank'] = base['maturity'].rank(method='dense', ascending=False) if prefer_next_month else 1.0
    base['u_theta'] = base.apply(lambda r: _unit_theta_per_abs_delta(r['theta'], r['delta']), axis=1)
    base['u_abs_delta'] = base['delta'].abs()
    # base = base.sort_values(['mat_rank', 'gamma', 'u_abs_delta'], ascending=[True, False, False])
    base = base.sort_values(['mat_rank', 'u_theta', 'u_abs_delta'], ascending=[True, True, False])

    buys = {}
    d_now = g_now = v_now = t_now = 0.0

    for _, r in base.iterrows():
        if abs(d_now) >= abs(target_core) or total_cap_left <= 0:
            break
        mat = r['maturity']
        if per_mat_cap_left[mat] <= 0:
            continue
        unit_d = abs(r['delta'])
        if unit_d <= 0:
            continue
        # 需要手数（向下取整），至少1手试探
        need = (abs(target_core) - abs(d_now)) / unit_d
        ask = int(np.ceil(need)) if need > 0 else 0
        ask = max(ask, 1)
        can = _apply_caps(ask, per_mat_cap_left.get(mat, 0), total_cap_left)
        if can <= 0:
            continue

        buys[r['opt_id']] = buys.get(r['opt_id'], 0) + can
        d_now += can * r['delta']; g_now += can * r['gamma']
        v_now += can * r['vega'];  t_now += can * r['theta']

        per_mat_cap_left[mat] -= can
        total_cap_left -= can

    return buys, d_now, g_now, v_now, t_now, per_mat_cap_left, total_cap_left

# ==================== Stage 2：保护强化（带开仓上限） ====================

def stage2_optimize_with_caps(day_df, delta_target, delta_now, theta_now, theta_budget_total,
                              per_mat_cap_left, total_cap_left,
                              delta_band_pct=0.05, min_lot=1, max_steps=200,
                              S_ref=None, eps_S=0.01, vega_tiebreak='high'):
    """
    在剩余额度内，按“单位Theta的Gamma产出”排序递增买入（每步1手），
    满足：Delta带内、Theta不超预算、开仓不超上限。
    """
    if S_ref is None:
        S_ref = float(day_df['S_ref'].iloc[0])

    cands = day_df[day_df['delta'] * delta_target > 0].copy()
    if cands.empty or total_cap_left <= 0:
        return {}, 0.0, 0.0, 0.0, per_mat_cap_left, total_cap_left

    dS = S_ref * eps_S
    cands['eff_gpt'] = (0.5 * cands['gamma'] * (dS**2)) / (np.maximum(1e-12, -cands['theta']))
    if vega_tiebreak == 'high':
        cands = cands.sort_values(['vega', 'eff_gpt'], ascending=[True, False])
    elif vega_tiebreak == 'low':
        cands = cands.sort_values(['vega', 'eff_gpt'], ascending=[False, False])
    else:
        cands = cands.sort_values(['eff_gpt'], ascending=False)

    lo = (1 - delta_band_pct) * delta_target
    hi = (1 + delta_band_pct) * delta_target

    buys = {}
    g_add = v_add = t_add = 0.0
    steps = 0

    while steps < max_steps and total_cap_left > 0:
        steps += 1
        chosen = None
        best_key = None
        for _, r in cands.iterrows():
            mat = r['maturity']
            if per_mat_cap_left[mat] <= 0:
                continue
            # 试买1手
            d_new = delta_now + r['delta']
            t_new = theta_now + t_add + r['theta']
            if abs(t_new) > abs(theta_budget_total) + 1e-12:
                continue
            # 不把Delta推进带外更差方向
            if delta_target < 0 and d_new <= delta_target:
                continue
            if delta_target > 0 and d_new >= delta_target:
                continue

            key = (r['eff_gpt'], r['vega'] if vega_tiebreak=='high' else (-r['vega'] if vega_tiebreak=='low' else 0.0))
            if (best_key is None) or (key > best_key):
                best_key = key
                chosen = r

        if chosen is None:
            break

        mat = chosen['maturity']
        can = _apply_caps(min_lot, per_mat_cap_left[mat], total_cap_left)
        if can <= 0:
            break

        oid = chosen['opt_id']
        buys[oid] = buys.get(oid, 0) + can
        per_mat_cap_left[mat] -= can
        total_cap_left -= can

        delta_now += can * chosen['delta']
        g_add     += can * chosen['gamma']
        v_add     += can * chosen['vega']
        t_add     += can * chosen['theta']

        if (delta_target < 0 and hi <= delta_now <= lo) or (delta_target > 0 and lo <= delta_now <= hi):
            break

    return buys, g_add, v_add, t_add, per_mat_cap_left, total_cap_left

# ==================== 主流程（严控Vega、Gamma敞口） ====================
def collar_strategy(
    df_chain, df_port, df_all, fee,
    colmap=dict(dt='dt', opt_id='Ticker', maturity='LastTradingDate',
                moneyness='moneyness', delta='Delta', gamma='Gamma', vega='Vega',
                theta='Theta', premium='twap', S_ref='index_pre_close'),
    # 对冲与预算
    hedge_ratio=1.0, delta_band_pct=0.0,
    # 交易粒度 & 上限
    per_mat_open_cap=100, per_mat_hold_cap=1200,
    prefer_next_month = False
):
    df = df_chain.reset_index(drop=False).rename(columns={
        colmap['dt']: 'dt', colmap['opt_id']: 'opt_id', colmap['maturity']: 'maturity',
        colmap['moneyness']: 'moneyness',
        colmap['delta']: 'delta', colmap['gamma']: 'gamma', colmap['vega']: 'vega',
        colmap['theta']: 'theta', colmap['premium']: 'premium', colmap['S_ref']: 'S_ref'
    }).set_index(['dt','opt_id']) # index为dt、opt_id的格式
    holdings = {}  # opt_id -> qty
    out = []
    total_cap_left = defaultdict(lambda: per_mat_hold_cap) # 每个月份合约持仓量上限为1200
    V_stock = df_port['策略股票持仓'].mean()
    for dt, day_df in tqdm(df.groupby('dt')):
        S_ref = float(day_df['S_ref'].iloc[0])
        delta_star = - hedge_ratio * (1e4 * V_stock / S_ref / 100) # 需要对冲掉的delta，领口策略比例设为1
        theta_exposure = -720000/100  # 监控Theta敞口72万
        # atm_idx = (day_df[day_df['delta']<0]['moneyness'] - 1.0).abs().idxmin()
        # IV = day_df.loc[atm_idx, 'IV']
        # if IV >= 0.5:
        #     day_df = day_df[((day_df['delta'] < 0) & (day_df['moneyness'] >= 0.915) & (day_df['moneyness'] <= 0.985))] #只做保护型认沽
        # elif IV <= 0.2:
        #     day_df = day_df[((day_df['delta'] >= 0) & (day_df['moneyness'] >= 1.025) & (day_df['moneyness'] <= 1.115))] #只做备兑开仓
        # else:
        day_df = day_df.loc[dt]
        day_df_all = df_all.loc[dt]
        day_df = day_df[((day_df['delta'] >= 0) & (day_df['moneyness'] >= 0.985) & (day_df['moneyness'] <= 1.085)) |
                        ((day_df['delta'] < 0) & (day_df['moneyness'] >= 0.915) & (day_df['moneyness'] <= 1.015))] # 可选交易合约
        # 先平掉已不在盘口的持仓
        closes, holdings, total_cap_left = _drop_missing_or_expired_holdings(holdings, day_df_all, total_cap_left)
        holdings, total_cap_left, d_hold, g_hold, v_hold, t_hold, flag = _pretrim_overhedge_holdings(
            day_df_all, holdings, delta_star, total_cap_left,
        ) # TODO
        d_hold = 0.0
        g_hold = 0.0
        v_hold = 0.0
        t_hold = 0.0
        for oid, q in holdings.items():
            if oid in day_df_all.index:
                rr = day_df_all.loc[oid]
                d_hold += q * rr['delta']
                g_hold += q * rr['gamma']
                v_hold += q * rr['vega']
                t_hold += q * rr['theta']
        # 预调仓后的组合greeks
        delta_now = d_hold
        gamma_now = g_hold
        vega_now = v_hold
        theta_now = t_hold
        if flag:
            pass
        else:
            day_df['var'] = day_df.index
            day_df_call = day_df[day_df['delta'] >= 0]
            day_df_put = day_df[day_df['delta'] < 0]
            # 初始化当日开仓额度
            per_mat_cap_left = defaultdict(lambda: per_mat_open_cap)

            prob = pulp.LpProblem('Determine_Pos', pulp.LpMaximize) # 最大化对冲效率

            open_vars = pulp.LpVariable.dicts('Open', day_df_put['var'], lowBound=0, upBound=per_mat_open_cap, cat='Continuous')
            open_vars.update(pulp.LpVariable.dicts('Open', day_df_call['var'], lowBound=-per_mat_open_cap, upBound=0, cat='Continuous'))

            # 设置目标函数
            prob += pulp.lpSum([day_df.loc[i,'theta']*(holdings.get(i,0)+open_vars[i]) for i in day_df['var']]), 'Theta_Max'

            # 添加约束条件
            for mat, day_df_mat in day_df.groupby('maturity'):
                day_df_mat_call = day_df_mat[day_df_mat['delta'] > 0]
                day_df_mat_put = day_df_mat[day_df_mat['delta'] < 0]
                # 不把put和call进行区分
                prob += pulp.lpSum([-open_vars[i] for i in day_df_mat_call['var']]+[open_vars[j] for j in day_df_mat_put['var']]) <= per_mat_cap_left[mat], f'Cons_open_{mat}'
                prob += pulp.lpSum([-open_vars[i]-holdings.get(i,0) for i in day_df_mat_call['var']]+[open_vars[j]+holdings.get(j,0) for j in day_df_mat_put['var']]) <= per_mat_hold_cap, f'Cons_hold_{mat}'

            # 风险管理
            prob += pulp.lpSum([day_df.loc[i,'delta'] * open_vars[i] for i in day_df['var']]) == delta_star - delta_now, 'Delta_Neutral'
            # if IV < 0.5 and IV > 0.2:
            prob += pulp.lpSum([day_df.loc[i,'vega'] * (holdings.get(i, 0)+open_vars[i]) for i in day_df['var']]) == 0, 'Vega_Neutral'
            prob += pulp.lpSum([day_df.loc[i,'gamma'] * (holdings.get(i, 0)+open_vars[i]) for i in day_df['var']]) == 0, 'Gamma_Neutral'

            prob.solve()

            Neutrals = ['Delta_Neutral','Vega_Neutral','Gamma_Neutral']
            N = 0
            prob += pulp.lpSum([day_df.loc[i, 'theta'] * (holdings.get(i, 0) + open_vars[i]) for i in day_df['var']]) >= theta_exposure, 'Theta_Expo'
            while pulp.LpStatus[prob.status] != 'Optimal':
                # 优先delta建仓
                del prob.constraints[Neutrals[N]]
                prob += pulp.lpSum([-day_df.loc[i,'delta']*open_vars[i] for i in day_df['var']]), 'Delta_Max'
                prob.solve()
                N += 1
                if N > 2:
                    raise Exception('线性规划问题未能找到最优解')

            # 更新持仓
            day_df['Open'] = [pulp.value(open_vars[i]) for i in day_df['var']]
            for _,row in day_df.iterrows():
                if row['Open'] < 0:
                    oid = row.name
                    q = int(row['Open'])
                    # trade_vol -= q
                    # cost += -q * row['premium'] * 100 / 10000 * fee
                    holdings[oid] = holdings.get(oid, 0) + q
                elif row['Open'] > 0:
                    oid = row.name
                    q = int(row['Open'])
                    # trade_vol += q
                    # cost += q * row['premium'] * 100 / 10000 * fee
                    holdings[oid] = holdings.get(oid, 0) + q

            # cost += 15 * trade_vol / 10000

        # 计算收益
        cost = 0
        profit = 0
        for oid in holdings.keys():
            row = day_df_all.loc[oid]
            profit += row.premium * holdings[oid] * 100 / 10000 * row.pct

        out.append({
            'dt': dt,
            'holdings': holdings.copy(),
            'profit': profit - cost,
            'delta': delta_now, 'gamma': gamma_now, 'vega': vega_now, 'theta': theta_now,
        })

    return pd.DataFrame(out).set_index('dt')



# ==================== 主流程（含“带内跳过开仓”） ====================

def rebalance_two_stage_with_caps_over_time(
    df_chain, df_port, df_all, fee,
    colmap=dict(dt='dt', opt_id='Ticker', maturity='LastTradingDate',
                moneyness='moneyness', delta='Delta', gamma='Gamma', vega='Vega',
                theta='Theta', premium='twap', S_ref='index_pre_close'),
    # 对冲与预算
    hedge_ratio=0.4, theta_budget_ratio=-0.005, delta_band_pct=0.05,
    # 两阶段参数
    core_ratio=0.85, prefer_next_month=False, eps_S=0.01, vega_tiebreak=None,
    # 交易粒度 & 上限
    min_lot=1, per_maturity_cap=100, total_daily_cap=1200,
    # 跨日
    carry_positions=True,
    # 若跨日预调仓后Δ已在带内 → 跳过当日开仓
    skip_open_if_within_band=True
):
    d = df_chain.reset_index(drop=False).rename(columns={
        colmap['dt']:'dt', colmap['opt_id']:'opt_id', colmap['maturity']:'maturity',
        colmap['moneyness']:'moneyness',
        colmap['delta']:'delta', colmap['gamma']:'gamma', colmap['vega']:'vega',
        colmap['theta']:'theta', colmap['premium']:'premium', colmap['S_ref']:'S_ref'
    })
    d = d.copy()
    out = []
    holdings = {}  # opt_id -> qty
    total_cap_left = total_daily_cap
    for dt, day_df in tqdm(d.groupby('dt')):
        day_df = day_df[(day_df['moneyness'] >= 0.895)&(day_df['moneyness'] <= 1.015)]
        # 初始化当日开仓额度
        per_mat_cap_left = defaultdict(lambda: per_maturity_cap)

        if dt not in df_port.index:
            out.append({'dt':dt, 'buy_list':[], 'sell_list':[], 'holdings':holdings.copy(),
                        'delta_star':np.nan, 'theta_budget':np.nan,
                        'delta':np.nan, 'gamma':np.nan, 'vega':np.nan, 'theta':np.nan})
            continue

        V_stock = df_port['策略股票持仓'].mean()
        S_ref   = float(day_df['S_ref'].iloc[0])

        delta_star = - hedge_ratio * (1e4 * V_stock / S_ref / 100)
        theta_budget_total = _theta_budget(1e4*V_stock/100, theta_budget_ratio) # 按手数记
        lo = (1 - delta_band_pct) * delta_star
        hi = (1 + delta_band_pct) * delta_star

        # 先平掉已不在盘口的持仓
        sells_missing, total_cap_left = _drop_missing_or_expired_holdings(holdings, day_df, total_cap_left) # TODO

        # 跨日预调仓：若超额对冲，先在持仓中卖
        sells_trim, total_cap_left, d_hold, g_hold, v_hold, t_hold = pretrim_overhedge_holdings( # TODO
            day_df, holdings, delta_star, total_cap_left, delta_band_pct=delta_band_pct
        )
        sells = Counter(); sells.update(sells_missing); sells.update(sells_trim)

        # 预调仓后的组合greeks
        delta_now = d_hold
        gamma_now = g_hold
        vega_now  = v_hold
        theta_now = t_hold

        buys = Counter()
        # ============= 带内跳过开仓：核心逻辑 =============
        if skip_open_if_within_band and delta_star < 0 and hi <= delta_now <= lo:
            # 不再开仓，直接输出
            pass
        # ================================================
        else:
            # Stage 1：核心对冲（带开仓上限）
            target_core = min(0, core_ratio * delta_star - delta_now)
            buys1, d1, g1, v1, t1, per_mat_cap_left, total_cap_left = stage1_core_hedge_with_caps(
                day_df, target_core,
                per_mat_cap_left, total_cap_left,
                prefer_next_month=prefer_next_month, min_lot=min_lot
            )
            delta_now += d1; gamma_now += g1; vega_now += v1; theta_now += t1

            # Stage 2：保护强化（带开仓上限）
            # vega_tiebreak = None #'high' if day_df.loc[(day_df['moneyness'] - 1.0).abs().idxmin(),'IV'] >= 0.25 else 'low'

            buys2, g2, v2, t2, per_mat_cap_left, total_cap_left = stage2_optimize_with_caps(
                day_df, delta_star, delta_now, theta_now, theta_budget_total,
                per_mat_cap_left, total_cap_left,
                delta_band_pct=delta_band_pct, min_lot=min_lot, max_steps=200,
                S_ref=S_ref, eps_S=eps_S, vega_tiebreak=vega_tiebreak
            )
            gamma_now += g2; vega_now += v2; theta_now += t2

            # 合并买卖 & 持仓
            buys.update(buys1)
            buys.update(buys2)

        # 更新持仓
        trade_vol = cost = profit = 0
        for oid, q in sells.items():
            row = df_all.loc[(dt, oid)]
            trade_price = row.twap
            trade_vol += q
            cost += q * trade_price * 100 / 10000 * fee

        for oid, q in buys.items():
            holdings[oid] = holdings.get(oid, 0) + int(q)
            row = day_df[day_df['opt_id'] == oid].iloc[0]
            trade_price = row.premium
            trade_vol += q
            cost += q * trade_price * 100 / 10000 * fee

        holdings = {k: v for k, v in holdings.items() if v != 0}

        # 计算收益
        for oid in holdings.keys():
            row = day_df[day_df['opt_id'] == oid].iloc[0]
            trade_price = row.premium
            pct = row.pct
            hold_vol = holdings[oid]
            trade_amt = trade_price*hold_vol*100/10000
            profit += trade_amt * pct

        cost += 15*trade_vol/10000

        out.append({
            'dt': dt,
            'buy_list': [(k,int(v)) for k,v in buys.items() if v>0],
            'sell_list': [(k,int(v)) for k,v in sells.items() if v>0],
            'holdings': holdings.copy(),
            'profit': profit - cost,
            'delta_star': delta_star,
            'theta_budget': theta_budget_total,
            'delta': delta_now, 'gamma': gamma_now, 'vega': vega_now, 'theta': theta_now,
            'caps_left': {'total': total_cap_left, **{m:int(c) for m,c in per_mat_cap_left.items()}}
        })

    return pd.DataFrame(out).set_index('dt')

def n_pdf(x):  # 标准正态密度
    return math.exp(-0.5 * x * x) / SQRT2PI

def n_cdf(x):  # 标准正态分布函数（误差函数近似）
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def year_fraction(t_start, t_end):
    t_start = t_start.strftime('%Y%m%d')
    t_end = t_end.strftime('%Y%m%d')
    num_trading_days = len(fd.tradingday(t_start, t_end)) - 1
    return max(num_trading_days / 252.0, 0.0)

# ---------- Black-76 定价 ----------
def black76_price(F, K, r, T, sigma, is_call):
    if T <= 0 or sigma <= 0 or F <= 0 or K <= 0:
        return max((F - K) if is_call else (K - F), 0.0) * math.exp(-r*T)
    vol = sigma * math.sqrt(T)
    d1 = (math.log(F / K) + 0.5 * vol * vol) / vol
    d2 = d1 - vol
    df = math.exp(-r * T)
    if is_call:
        return df * (F * n_cdf(d1) - K * n_cdf(d2))
    else:
        return df * (K * n_cdf(-d2) - F * n_cdf(-d1))

def implied_vol_b76(price, F, K, r, T, is_call, lo=1e-4, hi=5.0, tol=1e-7, maxit=80):
    # 单调二分：价格对sigma单调
    if T <= 0 or F <= 0 or K <= 0 or price <= 0:
        return float("nan")
    p_lo = black76_price(F, K, r, T, lo, is_call)
    p_hi = black76_price(F, K, r, T, hi, is_call)
    # 超界则裁剪
    if price <= p_lo: return lo
    if price >= p_hi: return hi
    a, b = lo, hi
    for _ in range(maxit):
        m = 0.5 * (a + b)
        p = black76_price(F, K, r, T, m, is_call)
        if abs(p - price) < tol:
            return m
        if p > price:
            b = m
        else:
            a = m
    return 0.5 * (a + b)

# ---------- BS Greeks（现货S；可由F与r,q互换） ----------
def bs_greeks_spot(S, K, r, q, T, sigma, is_call):
    """
    返回 (delta, gamma, vega, theta)，theta按“每天”的数量（自然日或交易日）
    vega单位为 “对绝对波动率(1.0)” 的敏感度；若要每1%波动率，除以100
    """
    if any([S <= 0, K <= 0, T <= 0, sigma <= 0]) or math.isnan(sigma):
        return (float("nan"),) * 4
    vol = sigma * math.sqrt(T)
    F = S * math.exp((r - q) * T)
    d1 = (math.log(F / K) + 0.5 * vol * vol) / vol
    d2 = d1 - vol
    dq = math.exp(-q * T)
    df = math.exp(-r * T)
    if is_call:
        delta = dq * n_cdf(d1)
        theta = - (S * dq * n_pdf(d1) * sigma) / (2.0 * math.sqrt(T)) \
                - r * K * df * n_cdf(d2) + q * S * dq * n_cdf(d1)
    else:
        delta = - dq * n_cdf(-d1)
        theta = - (S * dq * n_pdf(d1) * sigma) / (2.0 * math.sqrt(T)) \
                + r * K * df * n_cdf(-d2) - q * S * dq * n_cdf(-d1)

    gamma = dq * n_pdf(d1) / (S * sigma * math.sqrt(T))
    vega  = S * dq * n_pdf(d1) * math.sqrt(T)
    # theta按“每天”尺度
    theta = theta * (1.0 / 252.0)  # 粗略，把年化衰减分到每个交易日
    return float(delta), float(gamma), float(vega), float(theta)

# ---------- 选桶 ----------
def pick_atm(df, win=(0.985, 1.015)): # 大约是虚四到实一
    pool = df[(df.moneyness>=win[0]) & (df.moneyness<=win[1])]
    if pool.empty: pool = df.iloc[(df.moneyness-1.0).abs().argsort()].head(3)
    return pool.iloc[(pool.moneyness-1.0).abs().argsort()].iloc[0]

def pick_otm2(df, target=0.97, tol=0.01):
    pool = df[(df.moneyness>=target-tol) & (df.moneyness<=target+tol)]
    if pool.empty: pool = df.iloc[(df.moneyness-target).abs().argsort()].head(3)
    return pool.iloc[(pool.moneyness-target).abs().argsort()].iloc[0]

# ---------- 单位Δ指标 ----------
def unit_metrics(row):
    d = abs(row.Delta) + 1e-12
    return {
        'u_theta': (-row.Theta)/d,      # 每单位Δ的每日Theta“消耗”
        'u_cost' : (row.PreSettlePrice)/d,     # 每单位Δ的权利金
        'u_gamma': (row.Gamma)/d,       # 每单位Δ的凸性
        'u_vega' : (row.Vega)/d         # 每单位Δ的vega
    }

# 货币化
def monetized_increments(row, S_ref, eps_S=0.01, eps_sigma=0.01, alpha=0.75):
    dS = S_ref * eps_S
    pv_gamma = 0.5 * row['Gamma'] * (dS**2)
    pv_vega  = row['Vega'] * eps_sigma
    pv_delta = abs(row['Delta']) * dS
    protect_value = pv_delta + pv_gamma + pv_vega
    net_cost = max(0.0, row['PreSettlePrice'] - alpha * protect_value)
    return protect_value, pv_gamma, pv_vega, net_cost

def greedy_allocate(cands_df, delta_target_resid, theta_budget_resid,
                     S_ref, eps_S=0.01, eps_sigma=0.01, alpha=0.75,
                     lam=dict(w_delta=1.0,w_theta=1.0,w_cost=0.0,w_gamma=0.6,w_vega=0.4),
                     min_lot=1, max_steps=200, delta_tol=0.0,
                     hard_theta=True, hard_cost=False, cost_budget_resid=None):
    buys = {}
    delta_now = gamma_now = vega_now = theta_now = cost_now = 0.0
    resid = delta_target_resid
    step = 0

    cands = cands_df.copy()
    cands = cands.T
    cands = cands[cands['Delta'] * resid > 0]

    while abs(resid) > delta_tol and step < max_steps and not cands.empty:
        step += 1
        best = None
        for _, r in cands.iterrows():
            if sum([buys.get(oid, 0) for oid in cands[cands['tag'] == r['tag']].index.get_level_values(1).unique()]) >= 100:
                continue
            delta_new = delta_now + r['Delta']
            gamma_new = gamma_now + r['Gamma']
            vega_new  = vega_now  + r['Vega']
            theta_new = theta_now + r['Theta']
            cost_new  = cost_now  + r['PreSettlePrice']

            if hard_theta and (theta_budget_resid is not None) and (theta_new < theta_budget_resid - 1e-12):
                continue
            if hard_cost and (cost_budget_resid is not None) and (cost_new > cost_budget_resid + 1e-12):
                continue

            pv, pv_gam, pv_veg, net_cost = monetized_increments(r, S_ref, eps_S, eps_sigma, alpha)
            delta_err_new = (delta_target_resid - delta_new)
            theta_excess_new = min(0.0, theta_new - (theta_budget_resid if theta_budget_resid is not None else 0.0))
            # 核心修改
            score = (lam['w_delta'] * abs(delta_err_new)
                     + lam['w_cost'] * net_cost
                     - lam['w_theta'] * theta_excess_new
                     - lam['w_gamma'] * pv_gam
                     - lam['w_vega']  * pv_veg)

            key = (score, r.name[1], delta_new, gamma_new, vega_new, theta_new, cost_new)
            if best is None or key[0] < best[0]:
                best = key

        if best is None:
            break

        score, oid, delta_now, gamma_now, vega_now, theta_now, cost_now = best
        buys[oid] = buys.get(oid, 0) + min_lot
        resid = delta_target_resid - delta_now

    return buys, dict(delta=delta_now, gamma=gamma_now, vega=vega_now, theta=theta_now, cost=cost_now)

# --------- 主流程（当月+次月，多桶） ----------
def rebalance_daily_multi_buckets(df_chain, df_port, df_all,
                                band=(0.85,1.05), atm_win=(0.965,0.975), otm_target=0.945, otm_tol=0.01, fee=0.0025, # atm_win=(0.935,0.955),
                                hedge_ratio=0.4, min_lot=10, max_new_lots=100, grid_cap=100,
                                theta_budget_ratio=-0.001/100,
                                # roll_params=dict(theta_improve_thresh=0.2, cost_improve_thresh=0.2),
                                ):
    """
    输入:
      df_chain: 多行/日（index=dt），当月PUT链，列至少含:
                ['opt_id','right','moneyness','delta','gamma','vega','theta','premium','S_ref'(或S_twap),'dte']
      df_port : 一行/日，列: ['V_stock','beta']（beta缺省=1）
    输出:
      DataFrame（index=dt），列:
        buy_list, sell_list, holdings(当日收盘), chosen_atm, chosen_otm,
        Delta_star, Theta_budget, Delta, Gamma, Vega, Theta, Cost
    """
    # delta_star_std = (hedge_ratio*1e4*df_port['策略股票持仓']/df_port['index_pre_close']/100).std()
    # df_port['策略股票持仓'] = df_port['策略股票持仓'].shift(1).fillna(0)
    holdings = {}  # {opt_id: qty}
    out = []

    for dt, chain_t_ in df_chain.groupby(level=0):  # dt为日期
        print(dt)
        chain_t = chain_t_.copy()
        chain_t = chain_t[chain_t.moneyness.between(band[0], band[1])] # 可选合约范围
        if chain_t.empty:
            out.append({'dt':dt, 'buy_list':[], 'sell_list':[], 'holdings':holdings.copy()})
            continue

        S_ref   = float(chain_t['index_pre_close'].iloc[0]) # 标的资产价格
        V_stock = df_port['策略股票持仓'].mean()# float(port['策略股票持仓'])
        Delta_star = - hedge_ratio * (1e4 * V_stock / S_ref / 100) # 负数, 相当于持有的delta（若干手）
        Theta_budget_total = 1e4 * theta_budget_ratio * V_stock  # 负数，股票持仓2亿则theta额度为10万

        # 选四桶（近月、远月各两桶）
        tag_list = sorted(list(set(chain_t['tag'])))
        atm_row_near = pick_atm(chain_t[chain_t['tag']==tag_list[0]], win=atm_win)
        atm_row_far = pick_atm(chain_t[chain_t['tag']==tag_list[1]], win=atm_win)
        otm_row_near = pick_otm2(chain_t[chain_t['tag']==tag_list[0]], target=otm_target, tol=otm_tol)
        otm_row_far = pick_otm2(chain_t[chain_t['tag']==tag_list[1]], target=otm_target, tol=otm_tol)

        # --- 处理“保留 or 换出”旧仓 ---
        keep_ids, close_ids = [], []
        for oid, qty in list(holdings.items()):
            cur_row = chain_t[chain_t.index.get_level_values(1)==oid]
            if cur_row.empty:
                close_ids.append(oid)  # 今天池里没有，必须平
                continue
            # cur_row = cur_row.iloc[0]
            # if should_roll(cur_row, atm_row, otm_row, **roll_params):
            #     close_ids.append(oid)  # 换到桶里更划算/到期近
            # else:
            keep_ids.append(oid)   # 继续持有

        # 先计算“保留仓位”的Greeks贡献（保持原数量）
        Delta_keep = Gamma_keep = Vega_keep = Theta_keep = Cost_keep = 0.0
        for oid in keep_ids:
            row = chain_t[chain_t.index.get_level_values(1)==oid].iloc[0]
            q   = int(holdings.get(oid,0))
            Delta_keep += q*row.Delta; Gamma_keep += q*row.Gamma
            Vega_keep  += q*row.Vega;  Theta_keep += q*row.Theta
            Cost_keep  += 0.0  # 已有仓位不计当日新增权利金

        # 剩余Δ目标（给两桶去补）
        Delta_resid = Delta_star - Delta_keep
        if Delta_resid >= 0:
            tgt_add = {}
            for oid in sorted(keep_ids, reverse=True): # 先卖远月平值
                row = chain_t[chain_t.index.get_level_values(1) == oid].iloc[0]
                q = int(holdings.get(oid, 0))
                if q * row.Delta + Delta_resid > 0:
                    Delta_resid += q * row.Delta
                    Delta_keep -= q * row.Delta; Gamma_keep -= q*row.Gamma
                    Vega_keep -= q * row.Vega; Theta_keep -= q * row.Theta
                    tgt_add[oid] = -q
                    continue
                else:
                    q_ = -np.ceil(Delta_resid / row.Delta)
                    Delta_keep -= q_ * row.Delta; Gamma_keep -= q_*row.Gamma
                    Vega_keep -= q_ * row.Vega; Theta_keep -= q_ * row.Theta
                    tgt_add[oid] = -q_
                    break
        # elif Delta_resid >= 0 or Delta_resid >= -0.5*delta_star_std:
        #     tgt_add = {}
        else:
            # Delta_resid += delta_star_std
            # 给两桶的θ预算（总预算减去保留仓的θ）
            Theta_budget_resid = None
            if Theta_budget_total is not None:
                Theta_budget_resid = Theta_budget_total - Theta_keep

            # --- 离散求解在两桶上的新增手数 ---
            cand_df = pd.concat([atm_row_near, otm_row_near, atm_row_far, otm_row_far], axis=1)
            best_rec = greedy_allocate(cand_df,
                Delta_resid,
                Theta_budget_resid,
                S_ref,
                lam=dict(w_delta=1.0,w_theta=1.0,w_cost=0.0,w_gamma=0.6,w_vega=0.4),
                min_lot=1, max_steps=200, delta_tol=0.0,
                hard_theta=True, hard_cost=False, cost_budget_resid=None)

            # 多桶目标新增
            tgt_add = {atm_row_near.name[1]: best_rec[0].get(atm_row_near.name[1],0),
                       otm_row_near.name[1]: best_rec[0].get(otm_row_near.name[1],0),
                       atm_row_far.name[1]: best_rec[0].get(atm_row_far.name[1],0),
                       otm_row_far.name[1]: best_rec[0].get(otm_row_near.name[1],0)}

        # 目标总持仓 = 保留仓 + 新增两桶；被close_ids的目标设为0
        tgt_holdings = {}
        # 保留仓原数量不动（如需允许“在原票上加减”，可自行扩展）
        for oid in keep_ids:
            tgt_holdings[oid] = int(holdings.get(oid,0))
        # 新增两桶数量“覆盖”同名旧仓（若旧仓本来就是其中之一）
        for oid, q in tgt_add.items():
            tgt_holdings[oid] = tgt_holdings.get(oid, 0) + int(q)
        # 需要平掉的仓位
        for oid in close_ids:
            if oid not in tgt_holdings.keys():
                tgt_holdings[oid] = 0

        # 生成买卖指令
        buys, sells = [], []
        all_ids = set(holdings.keys()) | set(tgt_holdings.keys())
        for oid in all_ids:
            q_now = int(holdings.get(oid, 0))
            q_tgt = int(tgt_holdings.get(oid, 0))
            diff  = q_tgt - q_now
            if diff == 0: continue
            if diff > 0: buys.append((oid, diff))
            else:        sells.append((oid, -diff))

        # 更新持仓
        trade_vol = cost = profit = 0
        for oid, q in buys:
            holdings[oid] = holdings.get(oid, 0) + q
            row = chain_t_[chain_t_.index.get_level_values(1) == oid].iloc[0]
            trade_price = row.twap
            trade_vol += q
            cost += q*trade_price*100/10000 * fee
        for oid, q in sells:
            holdings[oid] = holdings.get(oid, 0) - q
            row = df_all.loc[(dt,oid)]
            trade_price = row.twap
            trade_vol += q
            cost += q*trade_price*100/10000 * fee
        holdings = {k:v for k,v in holdings.items() if v!=0}
        # 计算收益
        for oid in holdings.keys():
            row = chain_t_[chain_t_.index.get_level_values(1) == oid].iloc[0]
            trade_price = row.twap
            pct = row.pct
            hold_vol = holdings[oid]
            trade_amt = trade_price*hold_vol*100/10000
            profit += trade_amt * pct

        cost += 15*trade_vol/10000

        # 当日组合汇总（保留 + 新增两桶）
        # Delta  = Delta_keep  + best_rec['Delta']
        # Gamma  = Gamma_keep  + best_rec['Gamma']
        # Vega   = Vega_keep   + best_rec['Vega']
        # Theta  = Theta_keep  + best_rec['Theta']
        # Cost   = Cost_keep   + best_rec['Cost']

        out.append({
            'dt': dt,
            'buy_list': buys,
            'sell_list': sells,
            'holdings': holdings.copy(),
            'profit': profit - cost,
            'chosen_atm_near': atm_row_near.name[1],
            'chosen_otm_near': otm_row_near.name[1],
            'chosen_atm_far': atm_row_far.name[1],
            'chosen_otm_far': otm_row_far.name[1],
            'Delta_star': Delta_star,
            'Theta_budget': Theta_budget_total,
            # 'Delta': Delta, 'Gamma': Gamma, 'Vega': Vega, 'Theta': Theta, 'Cost': Cost
        })

    return pd.DataFrame(out).set_index('dt')

# ---------- 离散求解“剩余Δ”的桶配比（直接在整数手数上最小化） ----------
def solve_residual_integer(dt, holdings, atm_row_near, otm_row_near, atm_row_far, otm_row_far,
                           delta_star_resid,  # 负值
                           theta_budget_resid=None,             # 对剩余部分的θ预算（元/日；负数）
                           shock_price_ratio = 0.01, # 指数波动1%
                           shock_vol_abs = 0.01,
                           S_ref = None,
                           weights=dict(w_delta=0.25, w_theta=0.25, w_gamma=0.25, w_vega=0.25, w_cost=0.0),
                           min_lot=10, max_new_lots=100, grid_cap=100):
    # atm_t = len(fd.tradingday(dt.strftime('%Y%m%d'), (atm_row.ExtentionDate).strftime('%Y%m%d')))
    # otm_t = len(fd.tradingday(dt.strftime('%Y%m%d'), (otm_row.ExtentionDate).strftime('%Y%m%d')))

    # 预估边界
    unit_delta_max = max(abs(atm_row_near.Delta),abs(otm_row_near.Delta),abs(atm_row_far.Delta),abs(otm_row_far.Delta)) + 1e-9
    N_hint = int(np.ceil(abs(delta_star_resid)/unit_delta_max)*2)
    N_bound = max(min(grid_cap, max(min_lot, N_hint)), min_lot)

    best, best_rec = None, None
    for n_atm_near in range(0, N_bound+1, min_lot):
        for n_otm_near in range(0, N_bound+1, min_lot):
            for n_atm_far in range(0, N_bound + 1, min_lot):
                for n_otm_far in range(0, N_bound + 1, min_lot):
                    if n_atm_near+n_otm_near > max_new_lots or n_atm_far+n_otm_far > max_new_lots:
                        continue
                    # 组合贡献（仅针对“新增在两桶”的部分）
                    Delta = n_atm_near*atm_row_near.Delta + n_otm_near*otm_row_near.Delta + n_atm_far*atm_row_far.Delta + n_otm_far*otm_row_far.Delta
                    Gamma = n_atm_near*atm_row_near.Gamma + n_otm_near*otm_row_near.Gamma + n_atm_far*atm_row_far.Gamma + n_otm_far*otm_row_far.Gamma
                    Vega  = n_atm_near*atm_row_near.Vega  + n_otm_near*otm_row_near.Vega + n_atm_far*atm_row_far.Vega  + n_otm_far*otm_row_far.Vega
                    Theta = n_atm_near*atm_row_near.Theta + n_otm_near*otm_row_near.Theta + n_atm_far*atm_row_far.Theta + n_otm_far*otm_row_far.Theta
                    Cost  = n_atm_near*atm_row_near.PreSettlePrice+n_otm_near*otm_row_near.PreSettlePrice+n_atm_far*atm_row_far.PreSettlePrice+n_otm_far*otm_row_far.PreSettlePrice

                    # 货币化
                    pnl_delta = (Delta - delta_star_resid) * S_ref * shock_price_ratio
                    pnl_gamma = 0.5*Gamma*(S_ref*shock_price_ratio)**2
                    pnl_vega = Vega * shock_vol_abs

                    theta_excess = min(0.0, Theta - (theta_budget_resid if theta_budget_resid is not None else 0.0))

                    loss = (weights['w_delta'] * abs(pnl_delta)
                    + weights['w_theta'] * abs(theta_excess)
                    - weights['w_gamma'] * pnl_gamma
                    - weights['w_vega'] * pnl_vega
                    + weights['w_cost'] * Cost
                    )

                    if (best is None) or (loss < best):
                        best = loss
                        best_rec = dict(n_atm_near=int(n_atm_near), n_otm_near=int(n_otm_near),
                                        n_atm_far=int(n_atm_far), n_otm_far=int(n_otm_far),
                                        Delta=Delta, Gamma=Gamma, Vega=Vega, Theta=Theta, Cost=Cost)
    # if best_rec is None:
    #     # 退化：只用最省Δ成本的一只来逼近
    #     if abs(atm_row.delta) >= abs(otm_row.delta):
    #         n_atm = int(np.ceil(abs(delta_star_resid)/ (abs(atm_row.delta)+1e-9)))
    #         return dict(n_atm=n_atm, n_otm=0, Delta=n_atm*atm_row.delta, Gamma=n_atm*atm_row.gamma,
    #                     Vega=n_atm*atm_row.vega, Theta=n_atm*atm_row.theta, Cost=n_atm*atm_row.PreSettlePrice)
    #     else:
    #         n_otm = int(np.ceil(abs(delta_star_resid)/ (abs(otm_row.delta)+1e-9)))
    #         return dict(n_atm=0, n_otm=n_otm, Delta=n_otm*otm_row.delta, Gamma=n_otm*otm_row.gamma,
    #                     Vega=n_otm*otm_row.vega, Theta=n_otm*otm_row.theta, Cost=n_otm*otm_row.PreSettlePrice)
    print(best)
    return best_rec

# ---------- 主流程 ----------
def rebalance_daily_two_buckets(df_chain, df_port, df_all,
                                band=(0.85,1.05), atm_win=(0.945,0.955), otm_target=0.925, otm_tol=0.01, fee=0.0025, # atm_win=(0.935,0.955),
                                hedge_ratio=0.4, min_lot=10, max_new_lots=100, grid_cap=100,
                                theta_budget_ratio=-0.001/100,
                                # roll_params=dict(theta_improve_thresh=0.2, cost_improve_thresh=0.2),
                                ):
    """
    输入:
      df_chain: 多行/日（index=dt），当月PUT链，列至少含:
                ['opt_id','right','moneyness','delta','gamma','vega','theta','premium','S_ref'(或S_twap),'dte']
      df_port : 一行/日，列: ['V_stock','beta']（beta缺省=1）
    输出:
      DataFrame（index=dt），列:
        buy_list, sell_list, holdings(当日收盘), chosen_atm, chosen_otm,
        Delta_star, Theta_budget, Delta, Gamma, Vega, Theta, Cost
    """
    # delta_star_std = (hedge_ratio*1e4*df_port['策略股票持仓']/df_port['index_pre_close']/100).std()
    # df_port['策略股票持仓'] = df_port['策略股票持仓'].shift(1).fillna(0)
    holdings = {}  # {opt_id: qty}
    out = []
    shock_price_ratio = 0.01#df_port['index_pre_close'].pct_change().abs().median()
    shock_vol_abs = 0.01#df_chain[(df_chain['option_type'] == '平值')&(df_chain['tag'] == 1)]['IV'].pct_change().abs().median()
    for dt, chain_t_ in df_chain.groupby(level=0):  # dt为日期
        print(dt)
        chain_t = chain_t_.copy()
        chain_t = chain_t[chain_t.moneyness.between(band[0], band[1])] # 可选合约范围
        if chain_t.empty:
            out.append({'dt':dt, 'buy_list':[], 'sell_list':[], 'holdings':holdings.copy()})
            continue

        port = df_port.loc[dt]
        S_ref   = float(chain_t['index_pre_close'].iloc[0]) # 标的资产价格
        V_stock = df_port['策略股票持仓'].mean()# float(port['策略股票持仓'])
        Delta_star = - hedge_ratio * (1e4 * V_stock / S_ref / 100) # 负数, 相当于持有的delta（若干手）
        Theta_budget_total = 1e4 * theta_budget_ratio * V_stock  # 负数，股票持仓2亿则theta额度为10万

        # 选四桶（近月、远月各两桶）
        tag_list = sorted(list(set(chain_t['tag'])))
        atm_row_near = pick_atm(chain_t[chain_t['tag']==tag_list[0]], win=atm_win)
        atm_row_far = pick_atm(chain_t[chain_t['tag']==tag_list[1]], win=atm_win)
        otm_row_near = pick_otm2(chain_t[chain_t['tag']==tag_list[0]], target=otm_target, tol=otm_tol)
        otm_row_far = pick_otm2(chain_t[chain_t['tag']==tag_list[1]], target=otm_target, tol=otm_tol)

        # weights = dict(w_delta=0.25, w_theta=0.25, w_gamma=0.25, w_vega=0.25, w_cost=0.0)
        # 隐波判断权重
        if (atm_row_near.IV+otm_row_near.IV+atm_row_far.IV+otm_row_far.IV)/4 >= 0.25:
            weights = dict(w_delta=1.5, w_theta=0.2, w_gamma=1, w_vega=1, w_cost=0.0)
        else:
            weights = dict(w_delta=1, w_theta=1.5, w_gamma=0.5, w_vega=0.5, w_cost=0.0)
        # --- 处理“保留 or 换出”旧仓 ---
        keep_ids, close_ids = [], []
        for oid, qty in list(holdings.items()):
            cur_row = chain_t[chain_t.index.get_level_values(1)==oid]
            if cur_row.empty:
                close_ids.append(oid)  # 今天池里没有，必须平
                continue
            # cur_row = cur_row.iloc[0]
            # if should_roll(cur_row, atm_row, otm_row, **roll_params):
            #     close_ids.append(oid)  # 换到桶里更划算/到期近
            # else:
            keep_ids.append(oid)   # 继续持有

        # 先计算“保留仓位”的Greeks贡献（保持原数量）
        Delta_keep = Gamma_keep = Vega_keep = Theta_keep = Cost_keep = 0.0
        for oid in keep_ids:
            row = chain_t[chain_t.index.get_level_values(1)==oid].iloc[0]
            q   = int(holdings.get(oid,0))
            Delta_keep += q*row.Delta; Gamma_keep += q*row.Gamma
            Vega_keep  += q*row.Vega;  Theta_keep += q*row.Theta
            Cost_keep  += 0.0  # 已有仓位不计当日新增权利金

        # 剩余Δ目标（给两桶去补）
        Delta_resid = Delta_star - Delta_keep
        if Delta_resid >= 0:#0.5*delta_star_std: # 超过1倍标准差再换仓
            # Delta_resid -= 0.5*delta_star_std
            tgt_add = {}
            for oid in sorted(keep_ids, reverse=True):
                row = chain_t[chain_t.index.get_level_values(1) == oid].iloc[0]
                q = int(holdings.get(oid, 0))
                if q * row.Delta + Delta_resid > 0:
                    Delta_resid += q * row.Delta
                    Delta_keep -= q * row.Delta; Gamma_keep -= q*row.Gamma
                    Vega_keep -= q * row.Vega; Theta_keep -= q * row.Theta
                    tgt_add[oid] = -q
                    continue
                else:
                    q_ = -np.ceil(Delta_resid / row.Delta)
                    Delta_keep -= q_ * row.Delta; Gamma_keep -= q_*row.Gamma
                    Vega_keep -= q_ * row.Vega; Theta_keep -= q_ * row.Theta
                    tgt_add[oid] = -q_
                    break
        # elif Delta_resid >= 0 or Delta_resid >= -0.5*delta_star_std:
        #     tgt_add = {}
        else:
            # Delta_resid += delta_star_std
            # 给两桶的θ预算（总预算减去保留仓的θ）
            Theta_budget_resid = None
            if Theta_budget_total is not None:
                Theta_budget_resid = Theta_budget_total - Theta_keep

            # --- 离散求解在两桶上的新增手数 ---
            best_rec = solve_residual_integer(
                dt, holdings, atm_row_near, otm_row_near, atm_row_far, otm_row_far,
                delta_star_resid=Delta_resid,
                theta_budget_resid=Theta_budget_resid,
                shock_price_ratio = shock_price_ratio,
                shock_vol_abs = shock_vol_abs,
                S_ref = S_ref,
                weights=weights, min_lot=min_lot, max_new_lots=max_new_lots, grid_cap=grid_cap
            )

            # 目标新增：只在两桶
            tgt_add = {atm_row_near.name[1]: best_rec['n_atm_near'], otm_row_near.name[1]: best_rec['n_otm_near'],
                       atm_row_far.name[1]: best_rec['n_atm_far'], otm_row_far.name[1]: best_rec['n_otm_far']}

        # 目标总持仓 = 保留仓 + 新增两桶；被close_ids的目标设为0
        tgt_holdings = {}
        # 保留仓原数量不动（如需允许“在原票上加减”，可自行扩展）
        for oid in keep_ids:
            tgt_holdings[oid] = int(holdings.get(oid,0))
        # 新增两桶数量“覆盖”同名旧仓（若旧仓本来就是其中之一）
        for oid, q in tgt_add.items():
            tgt_holdings[oid] = tgt_holdings.get(oid, 0) + int(q)
        # 需要平掉的仓位
        for oid in close_ids:
            if oid not in tgt_holdings.keys():
                tgt_holdings[oid] = 0

        # 生成买卖指令
        buys, sells = [], []
        all_ids = set(holdings.keys()) | set(tgt_holdings.keys())
        for oid in all_ids:
            q_now = int(holdings.get(oid, 0))
            q_tgt = int(tgt_holdings.get(oid, 0))
            diff  = q_tgt - q_now
            if diff == 0: continue
            if diff > 0: buys.append((oid, diff))
            else:        sells.append((oid, -diff))

        # 更新持仓
        trade_vol = cost = profit = 0
        for oid, q in buys:
            holdings[oid] = holdings.get(oid, 0) + q
            row = chain_t_[chain_t_.index.get_level_values(1) == oid].iloc[0]
            trade_price = row.twap
            trade_vol += q
            cost += q*trade_price*100/10000 * fee
        for oid, q in sells:
            holdings[oid] = holdings.get(oid, 0) - q
            row = df_all.loc[(dt,oid)]
            trade_price = row.twap
            trade_vol += q
            cost += q*trade_price*100/10000 * fee
        holdings = {k:v for k,v in holdings.items() if v!=0}
        # 计算收益
        for oid in holdings.keys():
            row = chain_t_[chain_t_.index.get_level_values(1) == oid].iloc[0]
            trade_price = row.twap
            pct = row.pct
            hold_vol = holdings[oid]
            trade_amt = trade_price*hold_vol*100/10000
            profit += trade_amt * pct

        cost += 15*trade_vol/10000

        # 当日组合汇总（保留 + 新增两桶）
        # Delta  = Delta_keep  + best_rec['Delta']
        # Gamma  = Gamma_keep  + best_rec['Gamma']
        # Vega   = Vega_keep   + best_rec['Vega']
        # Theta  = Theta_keep  + best_rec['Theta']
        # Cost   = Cost_keep   + best_rec['Cost']

        out.append({
            'dt': dt,
            'buy_list': buys,
            'sell_list': sells,
            'holdings': holdings.copy(),
            'profit': profit - cost,
            'chosen_atm_near': atm_row_near.name[1],
            'chosen_otm_near': otm_row_near.name[1],
            'chosen_atm_far': atm_row_far.name[1],
            'chosen_otm_far': otm_row_far.name[1],
            'Delta_star': Delta_star,
            'Theta_budget': Theta_budget_total,
            # 'Delta': Delta, 'Gamma': Gamma, 'Vega': Vega, 'Theta': Theta, 'Cost': Cost
        })

    return pd.DataFrame(out).set_index('dt')