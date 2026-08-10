import datetime as dt
import pandas as pd
import os
import numpy as np
from utils import *
from multifactor.IO import IO
from multifactor.IO.IO_enums import *


def ticker_match(ticker_num):  # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num >= 600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num))) * '0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker


def fill_openNaN(dfminute0, dfprices0):
    dfminute0 = dfminute0.reset_index()
    dfminute0['Ticker'] = dfminute0.Ticker.apply(lambda x: ticker_match(x))

    open1300df = dfminute0[dfminute0.minute == 1300]
    open1300nanlist = open1300df[open1300df.open.isna()].Ticker.tolist()

    # 向前（上午）补close
    open1300nandf = dfminute0[dfminute0.Ticker.isin(open1300nanlist)]
    tempopen1300nandf = open1300nandf[['Ticker', 'minute', 'close']]
    tempopen1300nandf = tempopen1300nandf.groupby(['Ticker'], as_index=False).apply(lambda group: group.ffill())
    middle1 = pd.merge(open1300nandf, tempopen1300nandf, on=['Ticker', 'minute'])
    middle1['open'] = middle1.close_y
    middle1300nan = middle1[middle1.minute == 1300]

    # close无法填充的使用windA股日行情表open补
    openstillnanlist = middle1300nan[middle1300nan.open.isna()].Ticker.tolist()
    mddf = dfprices0[dfprices0.index.get_level_values(1).isin(openstillnanlist)]
    mddf = mddf.reset_index()
    mddf = mddf[['Ticker', 'S_DQ_OPEN']]
    fillnadf = pd.merge(middle1300nan, mddf, on='Ticker', how='left')
    fillnadf = fillnadf.fillna(0)
    fillnadf['open'] = fillnadf.open + fillnadf.S_DQ_OPEN
    fillnadf = fillnadf.set_index('Ticker')
    dftmin = dfminute0.set_index(['Ticker', 'minute'])
    for ticker in open1300nanlist:
        dftmin.loc[(ticker, 1300), 'open'] = fillnadf.loc[ticker].open
    dftmin = dftmin.reset_index()
    return dftmin


def fill_closeNaN(dfminute1, dfprices1):
    dfminute1 = dfminute1.reset_index()
    dfminute1['Ticker'] = dfminute1.Ticker.apply(lambda x: ticker_match(x))

    close1129df = dfminute1[dfminute1.minute == 1129]
    close1129nanlist = close1129df[close1129df.close.isna()].Ticker.tolist()

    # 向前（上午）补close
    close1129nandf = dfminute1[dfminute1.Ticker.isin(close1129nanlist)]
    middle1 = close1129nandf.groupby(['Ticker'], as_index=False).apply(lambda group: group.ffill())
    middle1129nan = middle1[middle1.minute == 1129]

    # close无法填充的使用windA股日行情表open补
    closestillnanlist = middle1129nan[middle1129nan.close.isna()].Ticker.tolist()
    mddf = dfprices1[dfprices1.index.get_level_values(1).isin(closestillnanlist)]
    mddf = mddf.reset_index()
    mddf = mddf[['Ticker', 'S_DQ_PRECLOSE']]
    fillnadf = pd.merge(middle1129nan, mddf, on='Ticker', how='left')
    fillnadf = fillnadf.fillna(0)
    fillnadf['close'] = fillnadf.close + fillnadf.S_DQ_PRECLOSE
    fillnadf = fillnadf.set_index('Ticker')
    dftmin = dfminute1.set_index(['Ticker', 'minute'])
    for ticker in close1129nanlist:
        dftmin.loc[(ticker, 1129), 'close'] = fillnadf.loc[ticker].close
    dftmin = dftmin.reset_index()
    return dftmin


def get_halfday_price(df):
    return df.groupby('Ticker').agg({
        'open': lambda x: x.head(1),
        'high': 'max',
        'low': 'min',
        'close': lambda x: x.tail(1),
        'volume': 'sum',
        'amt': 'sum'})


def fill_sigh_Nan(dfhalfday, sigh):
    highnanlist = dfhalfday[dfhalfday[sigh].isna()].index.tolist()

    if len(highnanlist) > 0:
        for ticker in highnanlist:
            if sigh == 'turn':
                dfhalfday.loc[ticker, sigh] = 0
            else:
                dfhalfday.loc[ticker, sigh] = dfhalfday.loc[ticker].open

    return dfhalfday

def get_data(day0, day1):
    dfindicator1 = IO.read_data(day1, columns=['S_DQ_TURN', 'TOT_SHR_TODAY', 'FREE_SHARES_TODAY', 'S_VAL_MV'],
                                alt=r'Z:/warehouse/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5')
    dfindicator0 = IO.read_data(day0, columns=['S_DQ_TURN', 'TOT_SHR_TODAY', 'FREE_SHARES_TODAY', 'S_VAL_MV'],
                                alt=r'Z:/warehouse/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5')
    dfprices1 = IO.read_data(day1, columns=['S_DQ_ADJFACTOR', 'S_DQ_OPEN', 'S_DQ_VOLUME','S_DQ_PRECLOSE'],
                             alt=r'Z:/warehouse/prod/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5')
    dfprices0 = IO.read_data(day0, columns=['S_DQ_ADJFACTOR', 'S_DQ_OPEN','S_DQ_PRECLOSE'],
                             alt=r'Z:/warehouse/prod/DATABASE/WIND/AShareEODPrices/AShareEODPrices.h5')

    dfminute1 = pd.read_pickle('Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\WIND\\MINUTE\\stock_perdate\\' + str(day1) + '.pkl',
                               compression='gzip')
    dfminute0 = pd.read_pickle('Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\WIND\\MINUTE\\stock_perdate\\' + str(day0) + '.pkl',
                               compression='gzip')

    return dfindicator1,dfindicator0,dfprices1,dfprices0,dfminute1,dfminute0

def data_prepare(dfminute0, dfminute1, dfprices0, dfprices1):
    dfminute_yesterday = fill_openNaN(dfminute0, dfprices0) # 补全 open
    dfminute_pre_close = fill_closeNaN(dfminute0, dfprices0) # 补全 pre_close
    dfminute_today = fill_closeNaN(dfminute1, dfprices1) # 补全 close

    dfminute_preclose = dfminute_pre_close[dfminute_pre_close.minute == 1129]
    dfminute0 = dfminute_yesterday[dfminute_yesterday.minute >= 1300]
    dfminute1 = dfminute_today[dfminute_today.minute <= 1129]

    dfhalfday0 = get_halfday_price(dfminute0).reset_index()
    dfhalfday1 = get_halfday_price(dfminute1).reset_index()

    return dfminute_preclose,dfhalfday0,dfhalfday1

def get_halfday_data(dfprices0,dfprices1,dfhalfday0,dfhalfday1,dfminute_preclose):
    dfprices0 = dfprices0.reset_index()
    dfprices1 = dfprices1.reset_index()

    dfhalfday0 = pd.merge(dfhalfday0, dfprices0, on='Ticker', how='left')
    dfhalfday0 = dfhalfday0.rename(columns={'S_DQ_ADJFACTOR': 'adjfactor0'})
    dfhalfday0 = pd.merge(dfhalfday0, dfprices1, on='Ticker', how='left')
    dfhalfday0['adjfac'] = dfhalfday0.S_DQ_ADJFACTOR / dfhalfday0.adjfactor0

    dfminute_preclose = dfminute_preclose.rename(columns={'close': 'pre_close'})
    dfminute_preclose = dfminute_preclose[['Ticker', 'pre_close']]
    dfhalfday0 = pd.merge(dfhalfday0, dfminute_preclose, on='Ticker', how='left')

    indicators = ['open', 'high', 'low', 'close', 'volume', 'pre_close']
    for indi in indicators:
        dfhalfday0.eval(indi + '=' + indi + '* adjfac', inplace=True)

    stock_list = list(set(dfhalfday0.Ticker.tolist()) & set(dfhalfday1.Ticker.tolist()))
    dfhalfday0 = dfhalfday0[dfhalfday0.Ticker.isin(stock_list)]
    dfhalfday1 = dfhalfday1[dfhalfday1.Ticker.isin(stock_list)]

    df_preclose = dfhalfday0[['Ticker', 'pre_close']]

    dfhalfday0 = dfhalfday0[['Ticker', 'open', 'high', 'low', 'close', 'volume', 'amt']]
    dfhalfday = dfhalfday0.append(dfhalfday1)
    dfhalfday = get_halfday_price(dfhalfday)

    dfhalfday = fill_sigh_Nan(dfhalfday, 'high')
    dfhalfday = fill_sigh_Nan(dfhalfday, 'low')

    return dfhalfday, df_preclose

def get_total_data(dfindicator1,dfprices1,dfhalfday,df_preclose,dfprices0,day):
    dfindicator1 = dfindicator1.reset_index()
    df_indi_price = pd.merge(dfindicator1, dfprices1, on=['dt', 'Ticker'])
    df_indi_price['turn_shares'] = df_indi_price.S_DQ_VOLUME * 100 / df_indi_price.S_DQ_TURN
    df_total = pd.merge(dfhalfday, df_indi_price, on='Ticker', how='left')
    df_total['turn'] = df_total.volume / df_total.turn_shares
    df_total['vwap'] = df_total.amt / df_total.volume

    df_total = fill_sigh_Nan(df_total, 'turn')
    df_total = fill_sigh_Nan(df_total, 'vwap')

    df_total = pd.merge(df_total, df_preclose, on='Ticker', how='left')

    df_total['pct_chg'] = 100 * (df_total.close - df_total.pre_close) / df_total.pre_close

    df_total = df_total.rename(
        columns={'S_VAL_MV': 'mkt_cap_ard', 'FREE_SHARES_TODAY': 'free_float_shares', 'TOT_SHR_TODAY': 'total_shares',
                 'S_DQ_ADJFACTOR': 'adjfactor'})
    # 单位换算
    df_total['volume'] = df_total.volume / 100
    df_total['amt'] = df_total.amt / 1000

    # df = pd.read_csv('Z://warehouse//prod//LOCAL_DATA//CSV//wind_data//wind_stock_list//' + str(day) + '.csv')
    # df_total = pd.merge(df, df_total, on='Ticker', how='left')

    df_total['dt'] = day
    df_total = df_total.set_index(['dt', 'Ticker'])
    md_list = ['adjfactor', 'amt', 'close', 'free_float_shares', 'high', 'low', 'mkt_cap_ard', 'open', 'pct_chg',
               'pre_close', 'total_shares', 'turn', 'volume', 'vwap']
    df_total = df_total[md_list]

    return df_total

def run(start = None, end = None):
    sdate, edate, cdate_list = check_update_date(start, end)
    for i in range(1,len(cdate_list)):
        day1 = cdate_list[i]
        print(day1)
        day0 = cdate_list[i-1]
        dfindicator1, dfindicator0, dfprices1, dfprices0, dfminute1, dfminute0 = get_data(day0, day1)
        dfminute_preclose,dfhalfday0,dfhalfday1 = data_prepare(dfminute0, dfminute1, dfprices0, dfprices1)
        dfhalfday, df_preclose = get_halfday_data(dfprices0, dfprices1, dfhalfday0, dfhalfday1, dfminute_preclose)
        df_total = get_total_data(dfindicator1, dfprices1, dfhalfday, df_preclose, dfprices0, day0)

        df_total.to_csv('Z://warehouse//test//LOCAL_DATA//CSV//hf_MD//' + str(day0) + '.csv')

run(20180101,20191106)