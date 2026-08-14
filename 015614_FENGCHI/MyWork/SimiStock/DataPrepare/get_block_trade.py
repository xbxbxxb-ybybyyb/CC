# coding: utf-8
# Author：fengchi863
# Date ：2022/3/8 9:28

import os

import numpy as np
import pandas as pd
from xquant.factordata import FactorData

from SimiStock.config.path_config import *
from SimiStock.dataApi import stockList, getData, tradeDate

"""
运行此文件前要先运行get_clean_stock()
20220421：更新为剔除上证50个股
"""
os.system("python3 get_clean_stock.py")
os.system("python3 get_rong_data.py")


def filter_stock(stk_id):
    if len(str(stk_id)) == 6 and (stk_id // 100000 == 8 or stk_id // 100000 == 4):    # 北交所
        return False
    else:
        return True


fd = FactorData()
sz50_df = fd.get_factor_value('WIND_AIndexMembers',
                              S_INFO_WINDCODE='000016.SH')
sz50_df = sz50_df[['S_CON_WINDCODE', 'S_CON_INDATE', 'S_CON_OUTDATE']]

sz50_df = sz50_df.rename({'S_CON_WINDCODE': '股票代码',
                          'S_CON_INDATE': '生效日',
                          'S_CON_OUTDATE': '剔除日'}, axis=1)

sz50_df = sz50_df.drop(2)
sz50_df['股票代码'] = sz50_df['股票代码'].map(stockList.trans_windcode2int)
sz50_df = sz50_df.sort_values(['生效日'])

sz50_df['value'] = 1
sz50_entry = sz50_df.pivot('生效日', '股票代码', 'value')
sz50_remove = sz50_df[['剔除日', '股票代码', 'value']].dropna().pivot('剔除日', '股票代码', 'value')
sz50 = sz50_entry.sub(sz50_remove, fill_value=0).replace(0, np.nan).ffill() > 0.5
sz50.index = sz50.index.map(int)
sz50 = sz50.reindex(tradeDate.get_date_range(20131216)).ffill()


def inin_sz50(trade_date, stk_id):
    if stk_id not in sz50.columns.tolist():
        return False
    else:
        if sz50.loc[trade_date, stk_id]:
            return True
        else:
            return False


#%% 开始处理大宗历史样本
if __name__ == '__main__':
    fd = FactorData()
    block_trade_df = fd.get_factor_value('WIND_AShareBlockTrade',
                                         factor_names=['S_INFO_WINDCODE', 'TRADE_DT', 'S_BLOCK_PRICE', 'S_BLOCK_VOLUME',
                                                       'S_BLOCK_AMOUNT', 'S_BLOCK_BUYERNAME', 'S_BLOCK_SELLERNAME'],
                                         TRADE_DT=['>=20170101'])

    close = getData.get_daily_1factor('close', tradeDate.get_date_range(20170101, tradeDate.get_today()))
    clean_stock = pd.read_pickle(data_path + 'clean_stock.pkl')

    rename_dict = {
        'S_INFO_WINDCODE': '股票代码',
        'TRADE_DT': '交易日期',
        'S_BLOCK_PRICE': '成交价格',
        'S_BLOCK_VOLUME': '成交数量',   # 万
        'S_BLOCK_AMOUNT': '成交金额',   # 万
        'S_BLOCK_BUYERNAME': '买方名称',
        'S_BLOCK_SELLERNAME': '卖方名称'
    }
    block_trade_df = block_trade_df.rename(columns=rename_dict)
    block_trade_df['股票代码'] = block_trade_df['股票代码'].map(stockList.trans_windcode2int)
    block_trade_df['交易日期'] = block_trade_df['交易日期'].map(int)
    block_trade_df = block_trade_df.drop(['OBJECT_ID', 'CRNCY_CODE', 'S_BLOCK_FREQUENCY', 'OPDATE', 'OPMODE'], axis=1)
    block_trade_amt = block_trade_df.groupby(['交易日期', '股票代码'])['成交金额'].sum()
    block_trade_df['总成交金额'] = block_trade_df.apply(lambda x: block_trade_amt.loc[x['交易日期'], x['股票代码']], axis=1)
    block_trade_df = block_trade_df.drop_duplicates(['交易日期', '股票代码'])

    # 剔除京A股票
    block_trade_df = block_trade_df[block_trade_df['股票代码'].map(filter_stock)]

    # 剔除部分不满足要求的大宗
    block_trade_df = block_trade_df[block_trade_df[['交易日期', '股票代码']].apply(lambda x:
                                   clean_stock.loc[x['交易日期'], x['股票代码']], axis=1)]

    # 剔除个别股票 18
    block_trade_df = block_trade_df[block_trade_df['股票代码'] != 18]
    block_trade_df = block_trade_df[block_trade_df['股票代码'] != 600240]

    # 剔除上证50
    block_trade_df['isin_sz50'] = block_trade_df[['交易日期', '股票代码']].apply(lambda x: inin_sz50(x['交易日期'], x['股票代码']),
                                                                         axis=1)
    block_trade_df = block_trade_df.query('isin_sz50 == False')

    block_trade_df = block_trade_df[['交易日期', '股票代码', '成交价格', '总成交金额']]
    block_trade_df['折价比例'] = block_trade_df[['交易日期', '股票代码', '成交价格']].apply(lambda x: x['成交价格'] /
                                 close.loc[x['交易日期'], x['股票代码']], axis=1)
    block_trade_df = block_trade_df.sort_values(['交易日期', '股票代码'])

    block_trade_df.to_pickle(data_path + 'raw_block_data.pkl')
    print('已保存完成')

    tmp = block_trade_df[block_trade_df['折价比例'] <= 0.95]
    tmp.to_pickle(data_path + 'block_data_95.pkl')
    print('已保存完成')

    tmp = block_trade_df[block_trade_df['折价比例'] <= 0.93]
    tmp.to_pickle(data_path + 'block_data_93.pkl')
    print('已保存完成')

    # tmp = block_trade_df[block_trade_df['折价比例'] <= 1]
    # tmp.to_pickle('/data/group/800442/800319/Afengchi/SimiStock/block_data/block_data_100.pkl')
    # print('已保存完成')

    # # %% 测算当天不是一个价格成交的比例
    # a = block_trade_df.groupby(['交易日期', '股票代码'])['成交价格'].std()
    # a = a.fillna(0)
    # a[a>0].count()/len(a)
