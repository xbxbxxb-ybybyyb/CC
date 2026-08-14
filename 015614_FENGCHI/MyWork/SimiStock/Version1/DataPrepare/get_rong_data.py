# coding: utf-8
# Author：fengchi863
# Date ：2022/3/14 17:30

from xquant.factordata import FactorData
from SimiStock.dataApi import stockList, tradeDate
import numpy as np
import pandas as pd
from SimiStock.config.path_config import data_path

if __name__ == '__main__':
    fd = FactorData()
    rong_df = fd.get_factor_value('WIND_AShareMarginSubject')
    rong_df = rong_df.query('S_MARGIN_SHARETYPE == 244000002')
    rong_df = rong_df[['S_INFO_WINDCODE', 'S_MARGIN_EFFECTDATE', 'S_MARGIN_ELIMINDATE']]

    rong_df = rong_df.rename({'S_INFO_WINDCODE': '股票代码',
                              'S_MARGIN_EFFECTDATE': '生效日',
                              'S_MARGIN_ELIMINDATE': '剔除日'}, axis=1)

    rong_df['股票代码'] = rong_df['股票代码'].map(stockList.trans_windcode2int)
    rong_df['生效日'] = rong_df['生效日'].map(int)
    # rong_df['剔除日'] = rong_df['剔除日'].map(lambda x: int(x) if np.isfinite(x) else np.nan)
    rong_df = rong_df.sort_values(['生效日'])

    rong_df['value'] = 1
    rong_entry = rong_df.drop_duplicates(['生效日', '股票代码']).pivot(
        '生效日', '股票代码', 'value').reindex(tradeDate.get_date_range(20100101)).ffill()
    rong_remove = rong_df[['剔除日', '股票代码', 'value']].dropna().drop_duplicates().pivot(
        '剔除日', '股票代码', 'value').reindex(tradeDate.get_date_range(20100101)).ffill()
    # rong_entry = rong_entry.sort_index()
    # rong_remove = rong_remove.sort_index()
    rong = rong_entry.sub(rong_remove, fill_value=0).replace(0, np.nan).ffill() > 0.5
    del rong.columns.name

    rong = rong[sorted(list(set(rong.columns.tolist())))]
    # tmp_rong = rong.reset_index()
    # tmp_rong = tmp_rong.drop_duplicates('index', keep='first')
    # rong = tmp_rong.set_index('index')
    del rong.index.name

    stock_list = pd.read_hdf('/data/group/800442/800319/junkData/daily/stock_list.h5', 'stock_list')
    rong = rong.reindex_like(stock_list) == 1
    rong = rong.applymap(int)

    rong.to_pickle(data_path + '2rong.pkl')