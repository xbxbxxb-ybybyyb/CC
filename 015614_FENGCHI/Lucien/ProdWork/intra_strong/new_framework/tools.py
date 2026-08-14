# coding: utf-8
# Author：fengchi863
# Date ：2025/8/15 16:28

import numpy as np
import pandas as pd
from xquant.factordata import FactorData

s = FactorData()
import datetime

today_date = datetime.datetime.today().strftime('%Y%m%d')
md_data_wind_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/md_data_wind/'


def getExtraBuyInfo(df):
    floatColumns = ['成交数量', '成交金额', '成交均价']
    df[floatColumns] = df[floatColumns].astype(float)
    if len(df) != 0:
        Adate = str(df.iloc[0]['发生日期'])
        date = Adate[:4] + Adate[5:7] + Adate[8:10]
        start_date = s.tradingday(date, -20)[0]
        md_data = pd.read_pickle(md_data_wind_path + f'{start_date}-{date}.pkl')

        for index, row in df.iterrows():
            stockCode = row['证券代码']
            open_, pre_close, close, high = md_data.loc[date, stockCode][['raw_open', 'raw_pre_close', 'raw_close', 'raw_high']].values
            highLimitedPrice = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
            if ((stockCode[0] == '3') & (date >= '20200824')) or ((stockCode[:2] == '68') & (date >= '20100824')):
                highLimitedPrice = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
            if stockCode[-2:] == 'BJ':
                highLimitedPrice = np.floor(pre_close * 100 * 1.3 + 1e-8) / 100
            df.loc[index, '买入当天收盘价'] = close
            df.loc[index, '买入当天开盘价'] = open_
            df.loc[index, '买入当天前收价'] = pre_close
            df.loc[index, '买入当天开盘涨幅(%)'] = (open_ / pre_close - 1) * 100
            if close >= highLimitedPrice:
                df.loc[index, '买入当天是否收盘涨停'] = 1
            else:
                df.loc[index, '买入当天是否收盘涨停'] = 0
            df.loc[index, '买入当天涨停价'] = highLimitedPrice
            df.loc[index, '买入当日收益率(%)'] = (close - row['成交均价']) / row['成交均价'] * 100
    return df
