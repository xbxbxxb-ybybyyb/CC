from xquant.thirdpartydata.factordata import FactorData
import pandas as pd
import datetime
import time
from joblib import Parallel, delayed
import os
import numpy as np

file_path = '/dfs/user/015585/20250417_飞笛媒体数据/'
file_list = os.listdir(file_path)
file_list.sort()

def data_process(file): # 数据预处理，计算业务指标每日均值、最大值、标准差
    columns = ['MEDIANEWSNUM', 'SOCIALNEWSNUM', 'MEDIANUM', 'BIGVSUM',
       'INTERACTSUM',]
    df = pd.read_pickle(f'{file_path}{file}')
    df = df.rename(columns = {'TRADINGCODE':'Ticker'})
    df['dt'] = df['RECORDTIME'].apply(lambda x : pd.Timestamp(x.split(' ')[0]))
    df = df.set_index(['dt','Ticker'])
    res1 = df.groupby(['dt','Ticker']).mean()[columns]
    res2 = df.groupby(['dt','Ticker']).max()[columns]
    res3 = df.groupby(['dt','Ticker']).std()[columns]
    return [res1, res2, res3]

res_mean = pd.DataFrame()
res_max = pd.DataFrame()
res_std = pd.DataFrame()
for file in file_list:
    print(file)
    res_file = data_process(file)
    res_mean = res_mean.append(res_file[0])
    res_max = res_max.append(res_file[1])
    res_std = res_std.append(res_file[2])
res_mean.to_pickle('data_mean.pkl')
res_max.to_pickle('data_max.pkl')
res_std.to_pickle('data_std.pkl')

# 计算全市场因子
res_mean = pd.read_pickle('data_mean.pkl')
res_max = pd.read_pickle('data_max.pkl')
res_std = pd.read_pickle('data_std.pkl')
dic_data = {
    'mean':res_mean,
    'max':res_max,
    'std':res_std
}
'''
分别对mean max std的基础数据，rolling取1，5，10，calc取mean和std计算因子值
最终要shift(1)
'''
def f_calc_avg(factor_series):
    return factor_series[~np.isnan(factor_series)].mean()
def f_calc_std(factor_series):
    factor_series = factor_series[~np.isnan(factor_series)]
    return np.std(factor_series,ddof=1)
rolling_days = [1,5,10]
dic_calc_func = {
    'mean':f_calc_avg,
    'std':f_calc_std
}
columns = [
    'MEDIANEWSNUM', 'SOCIALNEWSNUM', 'MEDIANUM', 'BIGVSUM',
    'INTERACTSUM',
]
factor_list = []
for data_type in dic_data:
    for col in columns:
        for rolling_day in rolling_days:
            for calc_func in dic_calc_func:
                factor_name = f'{data_type}_{col}_{rolling_day}_{calc_func}'
                print(factor_name)
                data_ori = dic_data[data_type]
                res = data_ori[col].unstack().rolling(rolling_day,1).apply(dic_calc_func[calc_func]).stack().to_frame(name = factor_name)
                res = res.reset_index()
                res['Ticker'] = res['Ticker'].apply(lambda x : x + '.SH' if x.startswith('6') \
                    else x + '.SZ' if x.startswith('3') or x.startswith('0') else x + '.BJ')
                res = res.set_index(['dt', 'Ticker'])
                res.to_pickle(f'/data/user/015585/01-因子挖掘/20250417_飞笛舆情/factors/{factor_name}.pkl')
                factor_list.append(res)
all_factor = pd.concat(factor_list,axis=1)
for col in all_factor.columns:
    print('shift1',col)
    all_factor[col] = all_factor[col].unstack().shift(1).stack().fillna(0)
all_factor.to_pickle('all_factor_df.pkl')