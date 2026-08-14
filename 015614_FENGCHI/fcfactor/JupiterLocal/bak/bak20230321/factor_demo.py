# coding: utf-8
# Author：fengchi863
# Date ：2022/12/12 15:11

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
s = FactorData()

def cal_ul_price(pre_close_dataframe):
    pre_close_dataframe = pre_close_dataframe.reset_index()
    after_824 = pre_close_dataframe['dt']>=pd.Timestamp('20200824')
    cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='30')
    kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='68')
    pre_close_dataframe['ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * 1.1 + 0.5) / 100
    pre_close_dataframe.loc[(after_824 & cyb)| kcb, 'ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * 1.2 + 0.5) / 100
    return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']

def forward_fill(arr, axis, zero_fill=True):
    arr = arr.swapaxes(axis, -1)
    if zero_fill:
        mask = arr == 0
    else:
        mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[-1]), 0)
    np.maximum.accumulate(idx, axis=-1, out=idx)

    out = arr[tuple(np.arange(idx.shape[x])[(None,) * x + (slice(None),) + (None,) * (idx.ndim - x - 1)] for x in range(idx.ndim - 1)) + (idx,)]
    out = out.swapaxes(axis, -1)
    return out

def get_lb(zt_flag):
    zt_values_copy = zt_flag.values.copy()
    zt_values2 = zt_values_copy.cumsum(axis=1)
    breaks = zt_values2 * (zt_values_copy == 0)
    zt_values3 = forward_fill(breaks, axis=1)
    zt_values4 = zt_values2 - zt_values3
    return zt_values4

# T-1日类因子
def factor_demo(start_date, end_date, IO, return_fillna_dic=False):
    #函数名需要和代码名称保持一致
    import sys
    fname=sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {fname:2, 'data':['MD']}#填充值设置为因子值中位数，data为使用的800080相关数据表。

    start_date_ = int(s.tradingday(str(start_date), -50)[0]) #需要比开始时间超过使用数据长度
    #使用800080地址的行情数据
    md_data = IO.read_data([start_date_, end_date], columns=['close', 'pre_close','pct_chg'], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data = md_data[md_data.reset_index()['Ticker'].apply(lambda x: ('BJ' not in x)).values]  # 去除北交所股票
    zcz = (((md_data.reset_index()['Ticker'].apply(lambda x: x[0] == '3')) & (md_data.reset_index()['dt']>=pd.Timestamp('20200824'))) |
           (md_data.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    md_data.loc[zcz, 'pct_chg'] = md_data.loc[zcz, 'pct_chg'] / 2

    md_data['ul_price'] = cal_ul_price(md_data[['pre_close']])
    md_data['is_ul'] = md_data['close'] == md_data['ul_price']
    md_data['last_is_ul'] = md_data['is_ul'].unstack().shift(1).stack().astype(float)
    md_data['last_last_is_ul'] = md_data['is_ul'].unstack().shift(2).stack().astype(float)
    by_day = md_data[(md_data['last_is_ul']==1)&(md_data['last_last_is_ul']==0)]['pct_chg'].groupby(level=0).mean()
    by_day.name = fname
    factor_df = pd.DataFrame(index=md_data.index)
    factor_df = factor_df.join(by_day)
    return factor_df