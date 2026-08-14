# coding: utf-8
# Author：fengchi863
# Date ：2024/5/15 15:33

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def gen_black_list(trade_date):
    tradeDatestr = str(trade_date)
    yesDatestr = s.tradingday(tradeDatestr, -2)[0]
    white_fpath = f'/data/group/800463/stock_list/white_list/{tradeDatestr}.xls'
    grey_fpath = f'/data/group/800463/stock_list/grey_list/grey_list_{tradeDatestr}.xlsx'
    black_list_list = [
        f'/data/group/800463/stock_list/black_other_list/黑名单-20240415.xlsx',
        f'/data/group/800463/stock_list/black_other_list/手动调整黑名单.xlsx',
        f'/data/group/800463/stock_list/pre_dt_list/pre_dt_list_{tradeDatestr}.xlsx',
        f'/data/group/800463/stock_list/pre_st_list/pre_st_list_{yesDatestr}.xlsx',
        f'/data/group/800463/stock_list/after_dt_list/after_dt_list_{yesDatestr}.xlsx',
        f'/data/group/800463/stock_list/share_comp_restrict_list/share_comp_restrict_list_{tradeDatestr}.xlsx',
        f'/data/group/800463/stock_list/defer_reply_list/defer_reply_list_{yesDatestr}.xlsx',
    ]
    all_black_list = []
    for black_list in black_list_list:
        black_df = pd.read_excel(black_list, dtype=str)
        if '出池时间' in black_df.columns.tolist():
            in_black_df = black_df[(black_df['出池时间'].isna()) & (black_df['入池时间'].apply(lambda x: pd.to_datetime(x)) <= pd.to_datetime(tradeDatestr))]
            black_df = black_df.query(f'出池时间 > "{pd.to_datetime(tradeDatestr)}" &'
                                      f'入池时间 <= "{pd.to_datetime(tradeDatestr)}"')
            black_df = pd.concat([in_black_df, black_df], axis=0)
        if '证券代码' in black_df.columns.tolist():
            all_black_list = all_black_list + list(black_df['证券代码'])
        else:
            all_black_list = all_black_list + list(black_df['股票代码'])
    all_black_list = list(map(lambda x: x if x[-1].isdigit() else x[:-3], all_black_list))
    all_black_list = [x +'.SH' if x[0] == '6' else x + '.SZ' for x in all_black_list]
    all_grey_list = []

    grey_df = pd.read_excel(grey_fpath, dtype=str)
    if '证券代码' in grey_df.columns.tolist():
        all_grey_list = all_grey_list + list(grey_df['证券代码'])
    else:
        all_grey_list = all_grey_list + list(grey_df['股票代码'])

    all_grey_list = list(all_grey_list)
    all_grey_list = [x + '.SH' if x[0] == '6' else x + '.SZ' for x in all_grey_list]

    filter_black_list = list(set(all_black_list)-set(all_grey_list))    # 只在黑名单

    white_df = pd.read_excel(white_fpath, dtype=str)
    white_list = white_df['证券代码'].tolist()

    return filter_black_list, all_grey_list, white_list

if __name__ == '__main__':
    gen_black_list(20240515)

