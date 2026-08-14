import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
'''
求解因子收益率
'''

def calc_circu_mkt_ind_sum(data_df):
    circu_mkt_ind_sum_df = data_df.groupby('sw_industry_code_1')['Circu_Mkt'].sum()
    # circu_mkt_ind_sum_df = circu_mkt_ind_sum_df.reindex(industry_factors, fill_value=0)
    circu_mkt_ind_sum_df = circu_mkt_ind_sum_df.sort_index()
    return circu_mkt_ind_sum_df

def create_constrained_matrix(S_day,P,Q):
    S = S_day.values
    constrained_row = [-S[p] / S[P-1] for p in range(P-1)]
    industry_block = np.vstack((np.eye(P-1), constrained_row))
    country_block = np.eye(1)
    style_block = np.eye(Q)
    return np.block([[country_block,np.zeros((1,P-1)),np.zeros((1,Q))],[np.zeros((P,1)),industry_block,np.zeros((P,Q))],[np.zeros((Q,1)),np.zeros((Q,P-1)),style_block]])

def solve_constrained_wls(R, X, s, C):
    sqrt_w = np.sqrt(s)
    sqrt_w /= sqrt_w.sum()
    W = np.diag(sqrt_w)
    beta = C @ np.linalg.inv(C.T @ X.T @ W @ X @ C) @ C.T @ X.T @ W @ R
    return beta

def single_day_factor_return(args):
    dt, r_day, x_day, s_day, factor_names, C = args
    try:
        r = r_day.values # (N,)
        X = x_day.values # (N,K)
        s = s_day.values # (N,)

        beta = solve_constrained_wls(r, X, s, C)
        return pd.Series(beta, index = factor_names, name = dt)
    except Exception as e:
        print(f'Error on {dt}: {e}')
        return None

# 求解因子收益率
def estimate_factor_returns_parallel(data_df, max_workers=30, style_factors=None, industry_factors=None, country_factors=None):
    if style_factors is None:
        style_factors = ['VALUE','SIZE','MOMENTUM','QUALITY','YIELD','VOLATILITY','GROWTH','LIQUIDITY']
    if industry_factors is None:
        industry_factors = sorted(list(data_df['sw_industry_code_1'].unique()))
    if country_factors is None:
        country_factors = ['COUNTRY']
    barra_factors = country_factors + industry_factors + style_factors
    dates = data_df.index.get_level_values('dt').unique()
    task_args = []
    for dt in dates:
        try:
            ret_day = data_df.loc[dt]['label_t2o30d1']
            barra_day = data_df.loc[dt][barra_factors]
            s_day = data_df.loc[dt]['Circu_Mkt']
            S_day = calc_circu_mkt_ind_sum(data_df.loc[dt])
            C = create_constrained_matrix(S_day,P=len(industry_factors), Q=len(style_factors))
            task_args.append((dt, ret_day, barra_day, s_day, barra_factors, C))
        except KeyError:
            continue

    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(single_day_factor_return, args) for args in task_args]
        for fut in as_completed(futures):
            res = fut.result()
            if res is not None:
                results.append(res)

    return pd.DataFrame(results).sort_index()

data_sft = pd.read_hdf('/data/user/023859/factor_zooZZ/factor_lib/initial_files/sft_basic_formal_931_20160101_20201231.h5')
data_df = pd.read_pickle('/dfs/user/023859/Neptune/df_neptune_basic_barra_20160101_20201231.pkl')
data_df['COUNTRY'] = 1
data_df = data_sft[['label_t2o30d1']].join(data_df)
factor_returns = estimate_factor_returns_parallel(data_df)

factor_returns.to_pickle('/dfs/user/023859/Neptune/df_neptune_sft_barra_returns_20160101_20201231.pkl')