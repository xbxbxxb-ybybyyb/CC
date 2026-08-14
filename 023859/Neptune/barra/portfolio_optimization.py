import pandas as pd
import numpy as np
import cvxpy as cp
import json

'''
求解二次规划问题
def optimization(alpha,Sigma,F,w_old,bounds,cons_dict=None, risk_aversion=1e-6):
    N = len(alpha)
    K = F.shape(1)

    w = cp.Variable(N)

    opt_object = cp.Maximize(alpha@w-0.5*risk_aversion*cp.quad_form(w,Sigma))
    # cap_neu_cons = cp.abs(port_cap.T @ w - bm_cap.T @ bm_weight)

    opt_cons = []

    # 权重之和为1
    opt_cons.append(cp.sum(w) == 1)

    # 权重为正数（禁止卖空限制）
    opt_cons.append(cp.min(w) >= 0)

    # 风险因子中性（Barra风格/行业中性）
    if cons_dict is not None and "factor_exposure" in cons_dict:
        for i in range(K):

    # 换手率约束
    if cons_dict is not None and "turnover_limit" in cons_dict:
        turnover_limit = cons_dict["turnover_limit"]
        z = cp.Variable(N)
        opt_cons += [z >= w - w_old, z >= -(w - w_old)]
        opt_cons.append(cp.sum(z) <= turnover_limit)

    # 权重上下限约束
    lb, ub = bounds
    opt_cons.append(w >= lb)
    opt_cons.append(w <= ub)

    # 求解优化
    prob_factor = cp.Problem(
        opt_object,
        opt_cons
    )

    prob_factor.solve(solver=cp.OSQP)

    return w.value, prob.status
'''

def build_constraints(w, alpha=None, exposure=None, target_expo=None, industry=None, industry_neutral=True):
    cons = [cp.sum(w) == 1, w >= 0]

    return cons

def two_stage_optimization(
        vote_sum_pred_vec, cov_mat,
        prev_weights = None,
        turnover_limit = None,
        exposure = None,
        industry = None,
        target_expo = None
):
    dt = vote_sum_pred_vec.index.get_level_values(0).unique()[0]
    tickers = vote_sum_pred_vec.index.get_level_values(1)
    n = len(tickers)
    v = vote_sum_pred_vec.values
    Q = cov_mat.loc[tickers, tickers].values

    if prev_weights is not None:
        prev_w = prev_weights.reindex(tickers).fillna(0).values
    else:
        prev_w = np.zeros(n) # 不能是0，应该是全复制

    # Step1: 最大化组合收益
    w1 = cp.Variable(n)
    obj1 = cp.Maximize(v @ w1)
    cons1 =build_constraints(w1)
    prob1 = cp.Problem(obj1, cons1)
    prob1.solve(solver = cp.OSQP)
    R_star = v @ w1.value

    # Step2: 最小化组合波动
    w2 = cp.Variable(n)
    obj2 = cp.Minimize(cp.quad_form(w2,Q))
    cons2 = build_constraints(w2)
    cons2 += [v @ w2 >= R_star]

    # 换手率约束
    if turnover_limit is not None:
        turnover_expr = cp.norm1(w2 - prev_w)
        cons2 += [turnover_expr <= turnover_limit]

    prob2 = cp.Problem(obj2, cons2)
    prob2.solve(solver = cp.OSQP, eps_abs=1e-6)
    if prob2.status != 'optimal':
        print(dt, prob2.status)

    return pd.Series(w2.value, index=tickers)

def run_portfolio_optimization(
        vote_df, asset_cov_dict,
        exposure_df = None,
        industry_df = None,
        target_expo = None,
        turnover_limit = None
):
    result = {}
    prev_w = None

    for dt, vote_day in vote_df.groupby(level=0):
        tickers = vote_day.index.get_level_values(1)
        vote_vec = vote_day.squeeze()

        if dt not in asset_cov_dict:
            continue
        cov = asset_cov_dict[dt].loc[tickers, tickers]
        cov = cov.fillna(0)
        expo = exposure_df.loc[dt].loc[tickers] if exposure_df is not None else None
        industry = industry_df.loc[dt].loc[tickers] if industry_df is not None else None

        w = two_stage_optimization(
            vote_vec, cov,
            prev_weights = prev_w,
            turnover_limit = turnover_limit,
            exposure = expo,
            industry = industry,
            target_expo = target_expo
        )

        result[dt] = w
        prev_w = w

    return pd.concat(result, names=['dt','Ticker'])

data_sft = pd.read_hdf('/data/user/023859/factor_zooZZ/factor_lib/initial_files/sft_basic_formal_931_20160101_20201231.h5')
data_sft['vote_sum_pred'] = np.random.randint(0,7,size=len(data_sft))
asset_cov_dict = pd.read_pickle('/dfs/user/023859/Neptune/dict_neptune_sft_asset_cov_20160101_20201231.pkl')
vote_df = data_sft[['vote_sum_pred']]

final_weights = run_portfolio_optimization(
    vote_df = vote_df,
    asset_cov_dict = asset_cov_dict,
    exposure_df = None,
    industry_df = None,
    target_expo = None,
    turnover_limit = None
)
print(final_weights)