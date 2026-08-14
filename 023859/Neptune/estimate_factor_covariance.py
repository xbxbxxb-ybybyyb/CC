import pandas as pd
import numpy as np
from collections import defaultdict

def estimate_factor_covariance_matrices(factor_returns, halflife = 200):
    df = factor_returns.copy()
    factors = df.columns
    lam = np.exp(-np.log(2) / halflife)
    # 初始化
    cov = None
    cov_matrices_dict = {}
    for date, row in df.iterrows():
        x = row.values.reshape(-1, 1)  # K×1 向量
        if cov is None:
            # 第一天初始化为 outer product
            cov = np.dot(x, x.T)
        else:
            # EWMA更新
            cov = lam * cov + (1 - lam) * np.dot(x, x.T)
        cov_df = pd.DataFrame(cov, index=factors, columns=factors)
        cov_matrices_dict[date] = cov_df
    return cov_matrices_dict

def estimate_specific_risk_covariance(exposure_df, factor_ret_df, halflife=20, shrinkage=False, industry_series=None,min_obs=10):
    resids_dict = defaultdict(list)
    specific_var_dict = {}

    # Step1 逐日计算残差
    for dt, expo_today in exposure_df.groupby(level=0):
        if dt not in factor_ret_df.index:
            continue
        betas = expo_today.values # N*K
        factor_ret = factor_ret_df.loc[dt].values.reshape(-1,1) # K*1
        stocks = expo_today.index.get_level_values(1)

        # 回归预测收益
        pred_ret = betas @ factor_ret # N*1


factor_returns = pd.read_pickle('/dfs/user/023859/Neptune/df_neptune_sft_barra_returns_20160101_20201231.pkl')
