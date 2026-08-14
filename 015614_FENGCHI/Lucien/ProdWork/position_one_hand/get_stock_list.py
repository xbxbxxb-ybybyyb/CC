# coding: utf-8
# Author：fengchi863
# Date ：2025/8/8 14:12
from LucienUtil import IO
import pandas as pd
import datetime
from xquant.factordata import FactorData
s = FactorData()

def get_stock_list(today_date):
    today = s.tradingday(today_date, -1)[0]
    last_date = s.tradingday(today, -2)[0]  # 昨日

    # 读取白名单的股票列表
    white = pd.read_excel('/data/group/800463/stock_list/white_list/%s.xls' % today)
    white = white[(white['市场名称'].isin([1, 2])) & (white['证券代码'].str.startswith(('00', '30', '60', '68')))]
    white_list = list(white['证券代码'].unique())
    white_list = [x + '.SH' if x[0] == '6' else x + '.SZ' for x in white_list]

    # 已上市
    md = IO.read_data([last_date, last_date], columns=['after_not_ul_len'], alt='/data/group/800463/data/generalStrong/stock_detail/stock_detail.h5')
    not_new_list = md[md['after_not_ul_len'] > 5].reset_index()['Ticker'].to_list()
    white_list = [x for x in white_list if x in not_new_list]


    # 黑名单的股票
    black_list_list = [
        '/data/group/800463/stock_list/black_other_list/黑名单-20241223.xls',
        # '/data/group/800463/stock_list/black_other_list/黑名单-20240415.xlsx',
        '/data/group/800463/stock_list/black_other_list/手动调整黑名单.xlsx',
        '/data/group/800463/stock_list/pre_st_list/pre_st_list_%s.xlsx' % last_date,
        # '/data/group/800463/stock_list/after_dt_list/after_dt_list_%s.xlsx' % (last_date),
        '/data/group/800463/stock_list/defer_reply_list/defer_reply_list_%s.xlsx' % last_date,
        # '/data/group/800463/stock_list/share_comp_restrict_list/share_comp_restrict_list_%s.xlsx' % (today)
    ]
    # '/data/group/800463/stock_list/pre_dt_list/pre_dt_list_%s.xlsx' % (today)]

    all_black_list = []
    for black_list in black_list_list:
        black_df = pd.read_excel(black_list, dtype=str)
        if '出池时间' in black_df.columns:
            black_df = black_df[black_df['出池时间'].isnull()]
        if '证券代码' in black_df.columns:
            all_black_list = all_black_list + list(black_df['证券代码'])
        else:
            all_black_list = all_black_list + list(black_df['股票代码'])
    all_black_list = list(all_black_list)
    all_black_list = [x + '.SH' if x[0] == '6' else x.zfill(6) + '.SZ' for x in [x for x in all_black_list if '.S' not in x]] \
                     + [x for x in all_black_list if '.S' in x]

    # 中证800成分股
    llaste_date = s.tradingday(today, -3)[0]
    index = IO.read_data([llaste_date, llaste_date], columns=['index_300', 'index_500'],
                         alt='/data/group/800080/warehouseJG/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5')
    # index = IO.read_data([last_date, last_date], columns=['index_300', 'index_500'],
    #                      alt='/data/group/800080/warehouseJG/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5')
    zz800_list = index[index['index_300'] + index['index_500']].reset_index()['Ticker'].to_list()

    # #市值排名前1500
    # mkt_cap=IO.read_data([last_date,last_date],columns=['mkt_cap_ard'],
    #                 alt = '/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # mkt_cap['rank']=mkt_cap['mkt_cap_ard'].rank(ascending=False)
    # mkt_cap=mkt_cap.sort_values('mkt_cap_ard',ascending=False)
    # mkt1500_list=mkt_cap[mkt_cap['rank']<=1500].reset_index()['Ticker'].to_list()

    # 前收盘价较低的股票
    pre_close = pd.read_pickle('/data/group/800463/param/pre_close/%s.pkl' % today)
    pre_close_low_list = list(pre_close[pre_close['self_preclose'] < 2].index)

    # stpt
    stpt_df = s.get_factor_value('Basic_factor', stock=white_list, mddate=[today], factor_names=['stpt'])
    stpt_list = stpt_df[stpt_df['stpt'] == '1'].reset_index()['stock'].to_list()

    # 白名单中已上市的股票，减去手动调整黑名单、pre_st黑名单、一字跌停黑名单、延迟回复黑名单、限售解禁黑名单等，减去前收盘价较低的股票，减去stpt的股票
    # stock_list = [x for x in white_list if x not in all_black_list + zz800_list + pre_close_low_list + stpt_list]  # 白名单列表，不在黑名单，且不在中证800，且前收盘价不低，且不是ST
    stock_list = [x for x in white_list if x not in all_black_list + pre_close_low_list + stpt_list]  # 白名单列表，不在黑名单，且不在中证800，且前收盘价不低，且不是ST
    print(len(white_list), len(all_black_list), len(zz800_list), len(pre_close_low_list), len(stpt_list), len(stock_list))

    return white_list, zz800_list, stock_list