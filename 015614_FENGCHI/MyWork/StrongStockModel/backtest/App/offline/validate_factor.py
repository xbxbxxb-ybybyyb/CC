# @Time : 2021/1/17 14:15
# @Author : Zhichen Lu
# @File : validate_factor.py

import pandas as pd
from dataApi.FixFactorRollPrepare import FixFactorRollPrepare

date = 20201026
factor_list = pd.read_pickle('/data/group/800319/strategy_local_path/using_fix_list.pkl')
# factor_direction = pd.read_pickle('/data/group/800319/strategy_local_path/factor_direction.pkl')
stk_list = pd.read_pickle('/data/group/800319/strategy_local_path/code_list/code_list20201023')
factor_mean = pd.read_pickle('/data/group/800319/strategy_local_path/factor_hyper_param2/mean20201023.pkl').T[factor_list]
factor_std = pd.read_pickle('/data/group/800319/strategy_local_path/factor_hyper_param2/std20201023.pkl').T[factor_list]
# def load_factor(time_point, factor_path):

time_point, factor_path = 1000, '/data/group/800002/realtime/alpha/x_day_lib/20201026/1000/'

factor = {}
for each in factor_list:
    temp_factor = pd.read_pickle('%s/Fix%d_%s.pkl' % (factor_path, time_point, each))
    factor[each] = temp_factor.T[str(date)]
factor = pd.DataFrame(factor)
factor = factor.reindex(stk_list, axis=0).reindex(factor_list, axis=1)
online_factor = (factor - factor_mean) / factor_std
online_factor.index = [int(x[:-3]) for x in online_factor.index]

dp = FixFactorRollPrepare(start_date=20201014, end_date=20201030, freq=7, model_time_len=1, factor_list=factor_list,
                          load_address='/data/group/800319/HFfactor/RealTimeFixRollMv/data/')

X, y, idx_date, idx_time, idx_code = dp.load_data(start_date=20201026, end_date=20201026, return_idx=True)
X, y, idx_date, idx_time, idx_code = dp.feature_engineering(X, y, idx_date, idx_time, idx_code)
offline_factor = pd.DataFrame(X[:, 0, :], index=pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code))), columns=factor_list)
offline_factor = offline_factor.loc[(20201026, 1000)]

offline_factor = offline_factor.reindex(online_factor.index)
online_factor = online_factor.clip(-5, 5)
corr_series = {}
mae_series = {}
for col in online_factor.columns:
    corr_series[col] = online_factor[col].corr(offline_factor[col])
    mae_series[col] = (online_factor[col] - offline_factor[col]).apply(abs).mean()

compare = pd.DataFrame({'corr': corr_series, 'mae': mae_series})
compare = compare.sort_values('mae', ascending=False)

factor_direction = compare['corr'] / compare['corr'].apply(abs)
pd.to_pickle(factor_direction, '/data/group/800319/strategy_local_path2/factor_direction.pkl')
