# coding: utf-8
# Author：fengchi863
# Date ：2022/5/20 11:20

from xquant.factordata import FactorData
import numpy as np
import pandas as pd
from SimiStock.dataApi import getData, tradeDate, indName
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *

pd.options.display.float_format = '{:.2%}'.format

fd = FactorData()

resample_date = {'行业更换前一年': [20200730, 20210730]}

N = 21
start_date = 20200531
end_date = 20210730
date_list = tradeDate.get_date_range(start_date, end_date)
sw1 = getData.get_daily_1factor('SW1', date_list)
sw20211 = getData.get_daily_1factor('SW20211', date_list)
sw20211 = sw20211.fillna(method='bfill')
close_badj = getData.get_daily_1factor('close_badj', date_list)
pre_close_badj = getData.get_daily_1factor('pre_close_badj', date_list)
pctchg21d = close_badj / pre_close_badj.shift(N)

# 申万一级成分股21天波动率情况
yearly_stk_std = pd.DataFrame(index=resample_date.keys(), columns=pctchg21d.columns)
ln_pctchg = np.log(pctchg21d)
for stats_year in resample_date.keys():
    _start, _end = resample_date[stats_year][0], resample_date[stats_year][1]
    if _start not in pctchg21d.index:
        _start = tradeDate.get_pre_trade_date(_start, -1)
    if _end not in pctchg21d.index:
        _end = tradeDate.get_pre_trade_date(_end, 1)
    std_value = ln_pctchg.loc[_start: _end].std()
    yearly_stk_std.loc[stats_year] = std_value

yearly_ind_std = pd.DataFrame(index=pd.MultiIndex.from_product([['mean', 'count', '10%分位数', '30%分位数', '50%分位数', '70%分位数', '90%分位数'], list(resample_date.keys())]), columns=indName.sw2021_level1.keys())
for sw1_code in indName.sw2021_level1.keys():
    for stats_year in resample_date.keys():
        # _end = tradeDate.get_pre_trade_date(resample_date[stats_year][1], 1)
        _sw1 = sw20211.loc[resample_date[stats_year][1]]
        _stk_list = _sw1[_sw1 == sw1_code].index.tolist()
        yearly_ind_std.loc[('mean', stats_year), sw1_code] = yearly_stk_std.loc[stats_year, _stk_list].mean()
        yearly_ind_std.loc[('count', stats_year), sw1_code] = len(_stk_list)
        yearly_ind_std.loc[('10%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 10)
        yearly_ind_std.loc[('30%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 30)
        yearly_ind_std.loc[('50%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 50)
        yearly_ind_std.loc[('70%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 70)
        yearly_ind_std.loc[('90%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 90)
yearly_ind_std = yearly_ind_std.rename(columns=indName.sw2021_level1)
yearly_ind_std = yearly_ind_std.swaplevel(0, 1)

yearly_ind_std2 = pd.DataFrame(index=pd.MultiIndex.from_product([['mean', 'count', '10%分位数', '30%分位数', '50%分位数', '70%分位数', '90%分位数'], list(resample_date.keys())]), columns=indName.sw_level1.keys())
for sw1_code in indName.sw_level1.keys():
    for stats_year in resample_date.keys():
        _end = tradeDate.get_pre_trade_date(resample_date[stats_year][1], 1)
        _sw1 = sw1.loc[_end]
        _stk_list = _sw1[_sw1 == sw1_code].index.tolist()
        yearly_ind_std2.loc[('mean', stats_year), sw1_code] = yearly_stk_std.loc[stats_year, _stk_list].mean()
        yearly_ind_std2.loc[('count', stats_year), sw1_code] = len(_stk_list)
        yearly_ind_std2.loc[('10%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 10)
        yearly_ind_std2.loc[('30%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 30)
        yearly_ind_std2.loc[('50%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 50)
        yearly_ind_std2.loc[('70%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 70)
        yearly_ind_std2.loc[('90%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 90)
yearly_ind_std2 = yearly_ind_std2.rename(columns=indName.sw_level1)
yearly_ind_std2 = yearly_ind_std2.swaplevel(0, 1)

# 重合的部分
common_ind = sorted(list(set(list(indName.sw_level1.values())).intersection(set(list(indName.sw2021_level1.values())))))
a = yearly_ind_std[common_ind].T.reset_index()
b = yearly_ind_std2[common_ind].T.reset_index()
res = pd.merge(a, b, on='index').T
res = res.T.set_index('index', drop=True).T

other_ind2 = list(set(indName.sw_level1.values()).difference(set(common_ind)))
other_ind1 = list(set(indName.sw2021_level1.values()).difference(set(common_ind)))
old_ind_std = yearly_ind_std2[other_ind2]
new_ind_std = yearly_ind_std[other_ind1]

output_dict = {'重合的申万一级行业指数21天波动率': res,
               '新申万一级成分股21天波动率情况': new_ind_std,
               '旧申万一级成分股21天波动率情况': old_ind_std}

util.save_dict2xls(output_dict, other_stats_path, '2021新申万行业波动率统计结果2.xlsx')
util.send_file(other_stats_path, '2021新申万行业波动率统计结果2.xlsx')