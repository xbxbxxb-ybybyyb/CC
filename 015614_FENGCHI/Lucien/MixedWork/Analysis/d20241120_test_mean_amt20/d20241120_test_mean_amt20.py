# coding: utf-8
# Author：fengchi863
# Date ：2024/11/20 13:34

from xquant.factordata import FactorData
import pandas as pd
import numpy as np
from dataApi.stockList import get_all_stock_ever_appear, trans_int2windcode, trans_windcode2int
from dataApi.tradeDate import get_date_range
from dataApi.getData import get_daily_1factor

strat_list = ['Jupiter', 'Europa', 'Metis', 'Leda', 'Saturn']
stats_dict = dict()

fd = FactorData()

stock_list = get_all_stock_ever_appear(20241118)
stock_list = list(map(lambda x: trans_int2windcode(x), stock_list))
date_list = get_date_range(20200101, 20241118)
date_list = list(map(str, date_list))

live_days = get_daily_1factor('live_days', date_list=date_list)

amt_df = fd.get_factor_value('Basic_factor', stock=stock_list, mddate=date_list, factor_names = ['amt'])
amt_df = amt_df['amt'].unstack()

mean_amt_df = amt_df.rolling(20).mean().stack() / 10

for idx, strat in enumerate(['日内强势股总买入记录',
                              '日内强势股总买入记录New',
                              '日内强势股总买入记录Metis',
                              '日内强势股总买入记录Leda',
                              '项目二总买入记录']):
    deal_df = pd.read_excel(f'/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/{strat}-20241118.xlsx')
    deal_df['发生日期'] = deal_df['发生日期'].map(lambda x: x[:4] + x[5:7] + x[8:10])
    deal_df = deal_df.set_index(['发生日期', '证券代码'])
    deal_df_list = deal_df.index.tolist()

    sort_amt = mean_amt_df.loc[deal_df_list].sort_values(ascending=True)
    sort_amt = pd.DataFrame(sort_amt, columns=['过去20日平均成交额'])
    sort_amt['live_days'] = sort_amt.index.map(lambda x: live_days.loc[int(x[0]), trans_windcode2int(x[1])])

    stats_dict[strat_list[idx]] = sort_amt

from LucienUtil.FileUtil import FileUtil
from dataApi.sendInfo import send_file
FileUtil.save_dict2xls(stats_dict, '/data/user/015614/junkData/', 'stats_results.xlsx')
send_file('/data/user/015614/junkData/stats_results.xlsx')