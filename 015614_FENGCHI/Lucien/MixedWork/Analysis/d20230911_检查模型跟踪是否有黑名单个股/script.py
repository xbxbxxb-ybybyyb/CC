# coding: utf-8
# Author：fengchi863
# Date ：2023/9/11 8:58

import pandas as pd
from dataApi.tradeDate import get_date_range
from xquant.factordata import FactorData
s = FactorData()

model_track = '/data/group/800463/日内强势股/log_parse/模型差异/'
factor_cost = '/data/group/800463/日内强势股/log_parse/因子耗时/'

date_list = get_date_range(20230701, 20230908)

for dat in date_list:
    try:
        tradeDatestr = s.tradingday(dat, -1)[0]
        tradeDateStr2 = tradeDatestr[:4] + '-' + tradeDatestr[4:6] + '-' + tradeDatestr[6:]
        yesDatestr = s.tradingday(tradeDatestr, -1)[0]
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

        filter_black_list = list(set(all_black_list) - set(all_grey_list))

        # 读取Saturn策略中的标的列表
        # saturn = pd.read_excel(model_track + f'{dat}/模型差异_{dat}_UAT_pj2_931.xlsx', sheet_name='本地投票结果')
        # saturn_list = saturn['Ticker'].tolist()
        # 读取因子耗时中
        saturn = pd.read_excel(factor_cost + f'因子耗时_{tradeDateStr2}_prod.xlsx', sheet_name='项目二931样本', index_col=0)
        saturn_list = saturn.index.tolist()

        inter_list = set(saturn_list).intersection(set(filter_black_list))
        print(f'{dat}日：', len(inter_list), inter_list)
    except:
        print(f'{dat}日：读取出错')


