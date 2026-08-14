# coding: utf-8
# Author：fengchi863
# Date ：2023/8/2 11:18

"""
生成每周的未成交强势股
成交记录中这几天买入的个股，配合profit中的pct收益率，
"""

import pandas as pd
import numpy as np
from dataApi.stockList import trans_windcode2int as Wc2Int, trans_int2windcode as Int2Wc
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from xquant.factordata import FactorData
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil
from LucienUtil.StockUtil import StockUtil

week_start_date = 20230823
week_end_date = 20230829
date_list = get_date_range(week_start_date, week_end_date)
date_str_list = list(map(lambda x: str(x)[:4] + '-' + str(x)[4:6] + '-' + str(x)[6:8], date_list))

"""成交记录中的内容"""
# signal_fname = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/jupiter成交记录-20230801.xlsx'
# signal = pd.read_excel(signal_fname, sheet_name='累计买入明细')
# signal = signal.query('last_is_zt == False')    # 这个条件筛选得到jupiterN样本
# signal['trade_date'] = signal['发生日期'].map(lambda x: int(x.replace('-', ''))).tolist()
# signal['stk_id'] = signal['证券代码'].map(lambda x: Wc2Int(x))
# signal = signal.query('trade_date >= 20210101')
# signal['dt'] = signal['发生日期'].apply(lambda x: pd.to_datetime(x))
# signal = signal.set_index(['dt', '证券代码'])
# signal = signal.query(f'{week_start_date} <= trade_date <= {week_end_date}')

"""因子耗时中的内容"""
week_jup_trigger_df_list = list()
week_eur_trigger_df_list = list()
for date_str in date_str_list:
    factor_time_cost_df = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/' + f'因子耗时_{date_str}_prod.xlsx', index_col=0, sheet_name=None)

    factor_time_cost_df_jup = factor_time_cost_df['因子耗时']
    factor_time_cost_df_jup = factor_time_cost_df_jup.drop(factor_time_cost_df_jup.filter(regex='ZT.*?_probability').dropna(how='all', axis=0).index)
    factor_time_cost_df_jup['trade_date'] = int(date_str.replace('-', ''))
    factor_time_cost_df_jup['dt'] = pd.Timestamp(date_str)
    factor_time_cost_df_jup['Ticker'] = factor_time_cost_df_jup.index

    factor_time_cost_df_eur = factor_time_cost_df['因子耗时New']
    factor_time_cost_df_eur['trade_date'] = int(date_str.replace('-', ''))
    factor_time_cost_df_eur['dt'] = pd.Timestamp(date_str)
    factor_time_cost_df_eur['Ticker'] = factor_time_cost_df_eur.index

    # 统计黑名单
    tradeDatestr = date_str.replace('-', '')
    yesDatestr = str(get_pre_trade_date(int(tradeDatestr)))
    white_list_list = ['/data/group/800463/stock_list/white_list/%s.xlsx' % tradeDatestr]
    grey_list_list = ['/data/group/800463/stock_list/grey_list/grey_list_%s.xlsx' % tradeDatestr]
    black_list_list = [
        '/data/group/800463/stock_list/black_other_list/黑名单-20240415.xlsx',
        '/data/group/800463/stock_list/black_other_list/手动调整黑名单.xlsx',
        '/data/group/800463/stock_list/abnormal_notice_list/abnormal_notice_list_%s.xlsx' % tradeDatestr,
        '/data/group/800463/stock_list/pre_st_list/pre_st_list_%s.xlsx' % yesDatestr,
        '/data/group/800463/stock_list/after_dt_list/after_dt_list_%s.xlsx' % yesDatestr,
        '/data/group/800463/stock_list/defer_reply_list/defer_reply_list_%s.xlsx' % yesDatestr,
    ]
    all_black_list = []
    for black_list in black_list_list:
        black_df = pd.read_excel(black_list, dtype=str)
        if '出池时间' in black_df.columns.tolist():
            black_df = black_df[black_df['出池时间'].isnull()]
        if '证券代码' in black_df.columns.tolist():
            all_black_list = all_black_list + list(black_df['证券代码'])
        else:
            all_black_list = all_black_list + list(black_df['股票代码'])
    all_black_list = list(all_black_list)
    all_black_list = [x + '.SH' if x[0] == '6' else x + '.SZ' for x in all_black_list]

    all_grey_list = []
    for grey_list in grey_list_list:
        grey_df = pd.read_excel(grey_list, dtype=str)
        if '出池时间' in grey_df.columns.tolist():
            grey_df = grey_df[grey_df['出池时间'].isnull()]
        if '证券代码' in grey_df.columns.tolist():
            all_grey_list = all_grey_list + list(grey_df['证券代码'])
        else:
            all_grey_list = all_grey_list + list(grey_df['股票代码'])
    all_grey_list = list(all_grey_list)
    all_grey_list = [x + '.SH' if x[0] == '6' else x + '.SZ' for x in all_grey_list]

    factor_time_cost_df_jup['isin_grey_or_black'] = factor_time_cost_df_jup['Ticker'].apply(lambda x: True if x in all_grey_list or x in all_black_list else False)
    factor_time_cost_df_eur['isin_grey_or_black'] = factor_time_cost_df_eur['Ticker'].apply(lambda x: True if x in all_grey_list or x in all_black_list else False)

    factor_time_cost_df_jup = factor_time_cost_df_jup[['trade_date', 'shouldBuySignal', 'dt', 'Ticker', 'MRisk_info', 'isin_grey_or_black']].reset_index(drop=True)
    week_jup_trigger_df_list.append(factor_time_cost_df_jup)
    factor_time_cost_df_eur = factor_time_cost_df_eur[['trade_date', 'shouldBuySignal', 'dt', 'Ticker', 'MRisk_info', 'isin_grey_or_black']].reset_index(drop=True)
    week_eur_trigger_df_list.append(factor_time_cost_df_eur)

week_jup_trigger_df = pd.concat(week_jup_trigger_df_list, axis=0)
week_eur_trigger_df = pd.concat(week_eur_trigger_df_list, axis=0)
week_jup_trigger_df = week_jup_trigger_df.set_index(['dt', 'Ticker'])
week_eur_trigger_df = week_eur_trigger_df.set_index(['dt', 'Ticker'])

"""基础样本中的ZT_Time"""
basic_jup = pd.read_hdf('/data/group/800463/project/project1_prod/left_v2212/Basic_zt/Basic_zt.h5')
basic_eur = pd.read_hdf('/data/group/800463/project/project1_prod/left_v2212/Basic_zt_test/Basic_zt_001.h5')
week_jup_trigger_df = pd.merge(week_jup_trigger_df, basic_jup['ZT_Time'], on=['dt', 'Ticker'])
week_eur_trigger_df = pd.merge(week_eur_trigger_df, basic_jup['ZT_Time'], on=['dt', 'Ticker'])

jup_eur_trigger_list = list(set(week_jup_trigger_df.index.get_level_values(1).tolist()).union(week_eur_trigger_df.index.get_level_values(1).tolist()))

"""计算申万二级行业"""
fd = FactorData()
sw2_2021 = pd.DataFrame()
for _date in date_list:
    tmp = fd.hsi(jup_eur_trigger_list, _date, 'SW2021', 2)
    tmp['trade_date'] = _date
    sw2_2021 = pd.concat([sw2_2021, tmp], axis=0)
sw2_2021 = sw2_2021.pivot('trade_date', 'stock', 'industry_name')

"""拼凑周度成交样本和概念数据"""
sw2_2021 = sw2_2021.stack()
week_jup_trigger_df['stk_code'] = week_jup_trigger_df.index.get_level_values(1).tolist()
week_eur_trigger_df['stk_code'] = week_eur_trigger_df.index.get_level_values(1).tolist()
week_jup_trigger_df['concept'] = week_jup_trigger_df[['trade_date', 'stk_code']].apply(lambda x: sw2_2021.loc[x['trade_date'], x['stk_code']], axis=1)
week_eur_trigger_df['concept'] = week_eur_trigger_df[['trade_date', 'stk_code']].apply(lambda x: sw2_2021.loc[x['trade_date'], x['stk_code']], axis=1)

"""拼凑模拟收益文件"""
profit_jup_df = pd.read_hdf('/data/group/800463/project/project1_prod/LabelProfit_fix/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5')
profit_eur_df = pd.read_hdf('/data/group/800463/project/project1_prod/LabelProfit_fix/001/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5')
week_jup_trigger_df = pd.merge(week_jup_trigger_df, profit_jup_df['pct'], on=['dt', 'Ticker'])
week_eur_trigger_df = pd.merge(week_eur_trigger_df, profit_eur_df['pct'], on=['dt', 'Ticker'])

"""添加股票名称"""
name_dict = StockUtil.get_stock_name_dict()
week_jup_trigger_df['stk_name'] = week_jup_trigger_df['stk_code'].apply(lambda x: name_dict[x])
week_eur_trigger_df['stk_name'] = week_eur_trigger_df['stk_code'].apply(lambda x: name_dict[x])

week_jup_trigger_df = week_jup_trigger_df.sort_values(['trade_date', 'concept', 'ZT_Time'])
week_eur_trigger_df = week_eur_trigger_df.sort_values(['trade_date', 'concept', 'ZT_Time'])
output_dict = dict()
# output_dict = {'Jupiter': week_jup_trigger_df,
#                'Europa': week_eur_trigger_df}

"""进行筛选并保存"""
# jup_first1 = week_jup_trigger_df.groupby(['trade_date', 'concept']).head()
# eur_first1 = week_eur_trigger_df.groupby(['trade_date', 'concept']).head()
# jup_first1 = jup_first1.query('pct > 0.1')
# eur_first1 = eur_first1.query('pct > 0.1')

# output_dict['Jupiter_first1'] = jup_first1
# output_dict['Europa_first1'] = eur_first1

jup_first2 = week_jup_trigger_df.groupby(['trade_date', 'concept']).head(2)
eur_first2 = week_eur_trigger_df.groupby(['trade_date', 'concept']).head(2)
jup_first2 = jup_first2.query('pct > 0.05 & shouldBuySignal == 0')
eur_first2 = eur_first2.query('pct > 0.05 & shouldBuySignal == 0')
jup_first2 = jup_first2.reset_index()
eur_first2 = eur_first2.reset_index()

# jup_first3 = week_jup_trigger_df.groupby(['trade_date', 'concept']).head(3)
# eur_first3 = week_eur_trigger_df.groupby(['trade_date', 'concept']).head(3)
# jup_first3 = jup_first3.query('pct > 0.05')
# eur_first3 = eur_first3.query('pct > 0.05')

# output_dict['Jupiter_first1'] = jup_first1
# output_dict['Europa_first1'] = eur_first1
output_dict['Jupiter_first2'] = jup_first2
output_dict['Europa_first2'] = eur_first2
# output_dict['Jupiter_first3'] = jup_first3
# output_dict['Europa_first3'] = eur_first3

FileUtil.save_dict2xls(output_dict, '/data/group/800463/sunss/复盘/周度无信号强势股/', f'week_noBuy_strong_samples_{week_start_date}_{week_end_date}.xlsx')
send_file(f'/data/group/800463/sunss/复盘/周度无信号强势股/week_noBuy_strong_samples_{week_start_date}_{week_end_date}.xlsx')
check = pd.read_excel(f'/data/group/800463/sunss/复盘/周度无信号强势股/week_noBuy_strong_samples_{week_start_date}_{week_end_date}.xlsx', index_col=0)