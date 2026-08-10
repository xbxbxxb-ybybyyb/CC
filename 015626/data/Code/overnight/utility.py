import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import os
import numpy as np
from overnight.naming_config import *
import functools
import dill
import re

def get_constituent_stock_list(date):
    wdf = IO.read_data(date, ftype=FType.INDEXWEIGHT, dsource=DSource.CSI)
    zz500_stock_list = wdf[wdf['index_weight_zz500'] > 0].index.get_level_values(1).tolist()
    hs300_stock_list = wdf[wdf['index_weight_hs300'] > 0].index.get_level_values(1).tolist()
    sh50_stock_list = wdf[wdf['index_weight_sh50'] > 0].index.get_level_values(1).tolist()
    zz800_stock_list = zz500_stock_list + hs300_stock_list
    zz800_stock_list.sort()
    return zz500_stock_list, hs300_stock_list, zz800_stock_list, sh50_stock_list


@functools.lru_cache(maxsize=None)
def ticker_match(ticker_num):
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker


def get_trade_contract(start_date, end_date, prod_id, exp_day_num=2):
    pd_data_daily = IO.read_data([start_date, end_date], dtype=DType.FUTURES, h5root=private_root)
    IC_daily = pd_data_daily[pd_data_daily.PROD_ID == prod_id]
    df00 = IC_daily.groupby('dt').apply(lambda x: x.iloc[0:1, :]).reset_index(level=0, drop=True).reset_index(level=1)[['Ticker','EXPIRATION_DAYS']]
    df01 = IC_daily.groupby('dt').apply(lambda x: x.iloc[1:2, :]).reset_index(level=0, drop=True).reset_index(level=1)[['Ticker','EXPIRATION_DAYS']]
    df00 = df00.rename(columns = {x:x+'_00' for x in df00.columns.tolist()})
    df01 = df01.rename(columns = {x:x+'_01' for x in df01.columns.tolist()})
    df = df00.join(df01)
    df.loc[df.EXPIRATION_DAYS_00 <= exp_day_num, 'Ticker_00'] = np.nan
    df['Ticker_00'].fillna(df['Ticker_01'], inplace = True)
    df['contract'] = df['Ticker_00'].apply(lambda x:re.sub("\D", "", x))
    df = df[['contract']]
    return df


def diller(file_name, payload=None):
    if payload is None:
        with open(file_name, 'rb') as fin:
            return dill.load(fin)
    else:
        with open(file_name, 'wb') as fout:
            dill.dump(payload, fout, protocol=4)

def pd_writer(sig, savepath):
        sig_name = sig.columns[0]
        file_name = os.path.join(savepath, sig_name + '.h5')
        if os.path.exists(file_name):
            #sigold = IO.read_data(alt = file_name)
            sigold = pd.read_hdf(file_name)
            sig = sig[~sig.index.isin(sigold.index)]
            signew = pd.concat([sigold,sig],axis=0).sort_index()
        else:
            signew = sig
        signew.to_hdf(file_name,key=sig_name)