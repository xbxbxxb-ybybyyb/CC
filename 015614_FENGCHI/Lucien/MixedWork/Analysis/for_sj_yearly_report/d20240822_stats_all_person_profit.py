# coding: utf-8
# Author：fengchi863
# Date ：2023/8/14 10:07

"""
年中述职，统计大家半年度模型表现
根据半年内线上版本进行统计，比如jup 这半年内线上有v5和v6，那就统计这两个
"""

import pandas as pd

# track_path = '/data/user/015614/daily/复盘/策略模拟跟踪/20240731/'
#
# eur_fpath = track_path + 'Europa模型跟踪v3_20230101_20240731.xlsx'  # v1 v2 v3 v4
# sellv1_fpath = track_path + 'JupiterNSell模型跟踪v1_20230101_20240731.xlsx' # v1
# sellv3_fpath = track_path + 'JupiterNSell34模型跟踪v2_20230101_20240731.xlsx'   # v1
# jup_fpath = track_path + 'jupiter模型跟踪v2_20230101_20240731.xlsx' # v8 v9
# sat_fpath = track_path + 's1模型跟踪v6_20230101_20240731.xlsx' # v5 v6
# jupz_fpath = track_path + 'JupiterZ模型跟踪v1_20230101_20240731.xlsx'   # v1
# metis_fpath = track_path + 'Metis模型跟踪v1_20230101_20240731.xlsx' # v1
# leda_fpath = track_path + 'Leda模型跟踪v1_20230101_20240731.xlsx' # v1

track_path = '/data/user/015614/daily/复盘/策略模拟跟踪/20240628/'

eur_fpath = track_path + 'Europa模型跟踪v3_20230101_20240628.xlsx'  # v1 v2 v3 v4
sellv1_fpath = track_path + 'JupiterNSell模型跟踪v1_20230101_20240628.xlsx' # v1
sellv3_fpath = track_path + 'JupiterNSell34模型跟踪v2_20230101_20240628.xlsx'   # v1
jup_fpath = track_path + 'jupiter模型跟踪v2_20230101_20240628.xlsx' # v8 v9
sat_fpath = track_path + 's1模型跟踪v6_20230101_20240628.xlsx' # v5 v6
jupz_fpath = track_path + 'JupiterZ模型跟踪v1_20230101_20240628.xlsx'   # v1
metis_fpath = track_path + 'Metis模型跟踪v1_20230101_20240628.xlsx' # v1
leda_fpath = track_path + 'Leda模型跟踪v1_20230101_20240628.xlsx' # v1

strategy_list = [eur_fpath, jup_fpath, sat_fpath, jupz_fpath, sellv1_fpath, sellv3_fpath, metis_fpath, leda_fpath]
version_list = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9']
strategy_name_list = ['Europa', 'Jupiter', 'Saturn', 'JupiterZ', 'Sell_v1', 'Sell_v3', 'Metis', 'Leda']
model_idx_list = list(range(11))
need_cols = ['model', '开发人', '是否实盘', '信号次数', '参与率', '扣费收益率均值', '扣费总收益', '最大回撤', '收益风险比', '收益夏普比率']
res = pd.DataFrame(index=pd.MultiIndex.from_product([strategy_name_list, version_list, model_idx_list]), columns=need_cols)
for idx, strat_fpath in enumerate(strategy_list):
    strategy_name = strategy_name_list[idx]
    if strategy_name == 'Europa':
        v3 = pd.read_excel(strat_fpath, sheet_name='本地样本跟踪v3modelpool')
        for idx2 in range(len(v3)):
            res.loc[(strategy_name, 'v3', idx2), :] = v3.loc[idx2][need_cols].values
    elif strategy_name == 'Jupiter':
        v9 = pd.read_excel(strat_fpath, sheet_name='本地样本跟踪v9modelpool')
        for idx2 in range(len(v9)):
            res.loc[(strategy_name, 'v9', idx2), :] = v9.loc[idx2][need_cols].values
    elif strategy_name == 'Saturn':
        v6 = pd.read_excel(strat_fpath, sheet_name='本地样本跟踪v6modelpool')
        for idx2 in range(len(v6)):
            res.loc[(strategy_name, 'v6', idx2), :] = v6.loc[idx2][need_cols].values
    elif strategy_name == 'JupiterZ':
        v1 = pd.read_excel(strat_fpath, sheet_name='本地样本跟踪v1modelpool')
        for idx2 in range(len(v1)):
            res.loc[(strategy_name, 'v1', idx2), :] = v1.loc[idx2][need_cols].values
    elif strategy_name == 'Sell_v1':
        v1 = pd.read_excel(strat_fpath, sheet_name='本地样本跟踪v1modelpool')
        for idx2 in range(len(v1)):
            res.loc[(strategy_name, 'v1', idx2), :] = v1.loc[idx2][need_cols].values
    elif strategy_name == 'Sell_v3':
        v1 = pd.read_excel(strat_fpath, sheet_name='本地样本跟踪v1modelpool')
        for idx2 in range(len(v1)):
            res.loc[(strategy_name, 'v1', idx2), :] = v1.loc[idx2][need_cols].values
    elif strategy_name == 'Metis':
        v1 = pd.read_excel(strat_fpath, sheet_name='本地样本跟踪v1modelpool')
        for idx2 in range(len(v1)):
            res.loc[(strategy_name, 'v1', idx2), :] = v1.loc[idx2][need_cols].values
    elif strategy_name == 'Leda':
        v1 = pd.read_excel(strat_fpath, sheet_name='本地样本跟踪v1modelpool')
        for idx2 in range(len(v1)):
            res.loc[(strategy_name, 'v1', idx2), :] = v1.loc[idx2][need_cols].values

res = res.dropna(how='all', axis=0)
res.index.names = ['strategy', 'version', 'idx']
res_dict = dict()

"""汇总"""
res_dict['各模型各版本汇总'] = res
"""按模型|版本|开发人"""
res2 = pd.DataFrame()
res2['TOP10模型数量'] = res.groupby(['strategy', 'version', '开发人'])['扣费总收益'].count()
res2['实盘模型数量'] = res.query('是否实盘==1').groupby(['strategy', 'version', '开发人'])['扣费总收益'].count()
res2['模型收益'] = res.groupby(['strategy', 'version', '开发人'])['扣费总收益'].sum() / res.groupby(['strategy', 'version', '开发人'])['扣费总收益'].count()
res_dict['按模型|版本|开发人'] = res2
"""按版本|开发人"""
# res3 = pd.DataFrame()
# res3['实盘模型数量'] = res.query('是否实盘==1').groupby(['version', '开发人'])['扣费总收益'].count()
# res3['TOP10模型数量'] = res.groupby(['version', '开发人'])['扣费总收益'].count()
# res3['模型收益'] = res.query('是否实盘==1').groupby(['version', '开发人'])['扣费总收益'].sum()
# res_dict['按版本|开发人'] = res3

from LucienUtil.FileUtil import FileUtil
FileUtil.save_dict2xls(res_dict, '/data/user/015614/', '2024年中模型评估结果.xlsx')