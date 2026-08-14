# coding: utf-8
# Author：fengchi863
# Date ：2022/5/16 19:21

"""
统计申万一级行业内的股票走势波动率等情况
"""

from xquant.factordata import FactorData
import numpy as np
import pandas as pd
from SimiStock.dataApi import getData, tradeDate, indName
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *

pd.options.display.float_format = '{:.2%}'.format

fd = FactorData()

resample_date = {'行业更换后': [20210730, 20220518],
                 '最近三个月': [20220218, 20220518],
                 '最近一个月': [20220418, 20220518]}

sw1_code_dict = {'801010.SI': '农林牧渔',
                 '801020.SI': '采掘',
                 '801030.SI': '化工',
                 '801040.SI': '钢铁',
                 '801050.SI': '有色金属',
                 '801080.SI': '电子',
                 '801110.SI': '家用电器',
                 '801120.SI': '食品饮料',
                 '801130.SI': '纺织服装',
                 '801140.SI': '轻工制造',
                 '801150.SI': '医药生物',
                 '801160.SI': '公用事业',
                 '801170.SI': '交通运输',
                 '801180.SI': '房地产',
                 '801200.SI': '商业贸易',
                 '801210.SI': '休闲服务',
                 '801230.SI': '综合',
                 '801710.SI': '建筑材料',
                 '801720.SI': '建筑装饰',
                 '801730.SI': '电气设备',
                 '801740.SI': '国防军工',
                 '801750.SI': '计算机',
                 '801760.SI': '传媒',
                 '801770.SI': '通信',
                 '801780.SI': '银行',
                 '801790.SI': '非银金融',
                 '801880.SI': '汽车',
                 '801890.SI': '机械设备'}
sw20211_code_dict = {
        '801150.SI': '医药生物',
        '801780.SI': '银行',
        '801750.SI': '计算机',
        '801120.SI': '食品饮料',
        '801180.SI': '房地产',
        '801740.SI': '国防军工',
        '801040.SI': '钢铁',
        '801790.SI': '非银金融',
        '801080.SI': '电子',
        '801770.SI': '通信',
        '801110.SI': '家用电器',
        '801760.SI': '传媒',
        '801210.SI': '社会服务',
        '801720.SI': '建筑装饰',
        '801050.SI': '有色金属',
        '801010.SI': '农林牧渔',
        '801030.SI': '基础化工',
        '801710.SI': '建筑材料',
        '801880.SI': '汽车',
        '801890.SI': '机械设备',
        '801730.SI': '电力设备',
        '801130.SI': '纺织服饰',
        '801200.SI': '商贸零售',
        '801160.SI': '公用事业',
        '801140.SI': '轻工制造',
        '801170.SI': '交通运输',
        '801230.SI': '综合',
        '801980.SI': '美容护理',
        '801960.SI': '石油石化',
        '801970.SI': '环保',
        '801950.SI': '煤炭',
}
sw1_code_list = list(sw20211_code_dict.keys())

N = 21
start_date = 20210530
end_date = 20220518
date_list = tradeDate.get_date_range(start_date, end_date)
sw1 = getData.get_daily_1factor('SW20211', date_list)
a_mkt_cap = getData.get_daily_1factor('a_mkt_cap', date_list)
pctchg = getData.get_daily_1factor('pct_chg', date_list)
close_badj = getData.get_daily_1factor('close_badj', date_list)
pre_close_badj = getData.get_daily_1factor('pre_close_badj', date_list)
pctchg21d = close_badj / pre_close_badj.shift(N)

sw_factor = fd.get_factor_value('WIND_ASWSindexEOD', ['S_DQ_PRECLOSE', 'S_DQ_CLOSE'],
                                S_INFO_WINDCODE=list(sw20211_code_dict.keys()),
                                TRADE_DT=['>=20160101'])
sw_close = sw_factor.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_CLOSE')
sw_pre_close = sw_factor.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_PRECLOSE')
sw_pctchg = sw_close / sw_close.shift(N)  # 月涨跌幅
sw_ln_pctchg = np.log(sw_pctchg)
sw_ln_pctchg.index = sw_ln_pctchg.index.map(int)

# 申万一级行业指数21天波动率
yearly_sw_std = pd.DataFrame(index=resample_date.keys(), columns=sw20211_code_dict)
for stats_year in resample_date.keys():
    _start, _end = resample_date[stats_year][0], resample_date[stats_year][1]
    if _start not in sw_ln_pctchg.index:
        _start = tradeDate.get_pre_trade_date(_start, -1)
    if _end not in sw_ln_pctchg.index:
        _end = tradeDate.get_pre_trade_date(_end, 1)
    std_value = sw_ln_pctchg.loc[_start: _end].std()
    yearly_sw_std.loc[stats_year] = std_value
yearly_sw_std = yearly_sw_std.rename(columns=sw20211_code_dict)

# 申万一级成分股21天波动率情况
yearly_stk_std = pd.DataFrame(index=resample_date.keys(), columns=pctchg21d.columns)
ln_pctchg = np.log(pctchg21d)
for stats_year in resample_date.keys():
    _start, _end = resample_date[stats_year][0], resample_date[stats_year][1]
    if _start not in sw_ln_pctchg.index:
        _start = tradeDate.get_pre_trade_date(_start, -1)
    if _end not in sw_ln_pctchg.index:
        _end = tradeDate.get_pre_trade_date(_end, 1)
    std_value = ln_pctchg.loc[_start: _end].std()
    yearly_stk_std.loc[stats_year] = std_value

yearly_ind_std = pd.DataFrame(index=pd.MultiIndex.from_product([['mean', 'count', '10%分位数', '30%分位数', '50%分位数', '70%分位数', '90%分位数'], list(resample_date.keys())]), columns=indName.sw2021_level1.keys())
for sw1_code in indName.sw2021_level1.keys():
    for stats_year in resample_date.keys():
        _end = tradeDate.get_pre_trade_date(resample_date[stats_year][1], 1)
        _sw1 = sw1.loc[_end]
        _stk_list = _sw1[_sw1 == sw1_code].index.tolist()
        yearly_ind_std.loc[('mean', stats_year), sw1_code] = yearly_stk_std.loc[stats_year, _stk_list].mean()
        yearly_ind_std.loc[('count', stats_year), sw1_code] = yearly_stk_std.loc[stats_year, _stk_list].count()
        yearly_ind_std.loc[('10%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 10)
        yearly_ind_std.loc[('30%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 30)
        yearly_ind_std.loc[('50%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 50)
        yearly_ind_std.loc[('70%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 70)
        yearly_ind_std.loc[('90%分位数', stats_year), sw1_code] = np.percentile(yearly_stk_std.loc[stats_year, _stk_list].dropna().tolist(), 90)
yearly_ind_std = yearly_ind_std.rename(columns=indName.sw2021_level1)
yearly_ind_std = yearly_ind_std.swaplevel(0, 1)

output_dict = {'申万一级行业指数21天波动率': yearly_sw_std.T,
               '申万一级成分股21天波动率情况': yearly_ind_std}

util.save_dict2xls(output_dict, other_stats_path, '2021新申万行业波动率统计结果.xlsx')
util.send_file(other_stats_path, '2021新申万行业波动率统计结果.xlsx')

# for ind_code in indName.sw_level1:

