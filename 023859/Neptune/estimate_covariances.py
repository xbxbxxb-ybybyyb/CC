import pandas as pd
import numpy as np
from collections import defaultdict
import pickle

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

def compute_residuals(data_df, factor_ret_df, return_col='label_t2o30d1'):
    resids_by_stock = defaultdict(list)

    # Step1 逐日计算残差
    for dt, df_day in data_df.groupby(level=0):
        if dt not in factor_ret_df.index:
            continue
        beta = df_day.drop(columns=[return_col]).values # N*K
        factor_ret = factor_ret_df.loc[dt].values.reshape(-1,1) # K*1

        # 回归预测收益
        pred_ret = beta @ factor_ret # N*1
        actual_ret = df_day[return_col].values.reshape(-1,1)
        residuals = (actual_ret - pred_ret).flatten()

        tickers = df_day.index.get_level_values(1)
        for ticker, resid in zip(tickers, residuals):
            if not np.isnan(resid):
                resids_by_stock[ticker].append((dt,resid))

    return resids_by_stock

def estimate_specific_variance_nw(resids_by_stock, halflife=20, min_obs=10):
    lam = np.exp(-np.log(2) / halflife)
    specific_var = defaultdict(dict)

    def ewma_weights(n):
        w = np.array([lam ** (n-1-i) for i in range(n)])
        return w / w.sum()

    for stock, data in resids_by_stock.items():
        if len(data) < min_obs:
            continue
        data = sorted(data, key=lambda x: x[0])
        dates, resids = zip(*data)
        resids = np.array(resids)

        for i in range(min_obs, len(resids)):
            window = resids[:i+1]
            weights = ewma_weights(len(window))
            mean = np.average(window, weights = weights)
            var = np.sum(weights * (window-mean)**2)
            specific_var[stock][dates[i]] = var

    return specific_var

'''
贝叶斯收缩

def shrink_specific_variance(specific_var, industry_map, shrink_strength=5):
    return specific_var
'''

def build_diagonal_cov_matrix(specific_var):
    dt_set = set()
    for stock in specific_var:
        dt_set.update(specific_var[stock].keys())

    cov_matrices = {}

    for dt in sorted(dt_set):
        stock_vars = {
            stock: var[dt]
            for stock, var in specific_var.items()
            if dt in var
        }
        vec = pd.Series(stock_vars).dropna()
        cov = pd.DataFrame(
            np.diag(vec.values),
            index = vec.index,
            columns = vec.index
        )
        cov_matrices[dt] = cov

    return cov_matrices

def estimate_specific_risk_pipline(data_df, factor_ret_df, industry_map=None,
                                   return_col='label_t2o30d1', halflife=20, shrinkage=True):
    resids = compute_residuals(data_df, factor_ret_df, return_col)
    spec_var = estimate_specific_variance_nw(resids, halflife)

    if shrinkage and industry_map is not None:
        pass
        # spec_var = shrink_specific_variance(spec_var, industry_map)

    cov_matrices = build_diagonal_cov_matrix(spec_var)

    return cov_matrices

def compute_total_asset_covariance(data_df, factor_cov_dict, specific_cov_dict):
    total_cov_dict = {}

    for dt, df_day in data_df.groupby(level=0):
        if dt not in factor_cov_dict or dt not in specific_cov_dict:
            continue
        tickers = df_day.index.get_level_values(1)
        B = df_day.values # N*K
        Sigma_factor = factor_cov_dict[dt].values # K*K
        Omega = specific_cov_dict[dt]

        systematic_cov = B @ Sigma_factor @ B.T
        systematic_df = pd.DataFrame(systematic_cov, index=tickers, columns=tickers)

        total_cov = systematic_df + Omega
        total_cov_dict[dt] = total_cov

    return total_cov_dict


factor_returns = pd.read_pickle('/dfs/user/023859/Neptune/df_neptune_sft_barra_returns_20160101_20201231.pkl')
data_df = pd.read_pickle('/dfs/user/023859/Neptune/df_neptune_basic_barra_20160101_20201231.pkl')
data_sft = pd.read_hdf('/data/user/023859/factor_zooZZ/factor_lib/initial_files/sft_basic_formal_931_20160101_20201231.h5')
data_df['COUNTRY'] = 1
data_df = data_sft[['label_t2o30d1']].join(data_df)

label = 'label_t2o30d1'
barra_factors = ['COUNTRY', '6101', '6102', '6103', '6104', '6105', '6108', '6111',
       '6112', '6113', '6114', '6115', '6116', '6117', '6118', '6120', '6121',
       '6123', '6124', '6125', '6126', '6127', '6128', '6129', '6130', '6131',
       '6132', '6133', '6134', 'VALUE', 'SIZE', 'MOMENTUM', 'QUALITY', 'YIELD',
       'VOLATILITY', 'GROWTH', 'LIQUIDITY']
data_df = data_df[barra_factors+[label]]
factor_returns = factor_returns[barra_factors]

# 股票特质性协方差矩阵估计
specific_cov_dict = estimate_specific_risk_pipline(
    data_df,
    factor_returns,
    industry_map = None,
    return_col = label,
    halflife = 20,
    shrinkage = True
)

# 因子协方差矩阵估计
factor_cov_dict = estimate_factor_covariance_matrices(factor_returns)

# 资产协方差矩阵
asset_cov_dict = compute_total_asset_covariance(data_df[barra_factors], factor_cov_dict, specific_cov_dict)
with open('/dfs/user/023859/Neptune/dict_neptune_sft_asset_cov_20160101_20201231.pkl', 'wb') as f:
    pickle.dump(asset_cov_dict, f)