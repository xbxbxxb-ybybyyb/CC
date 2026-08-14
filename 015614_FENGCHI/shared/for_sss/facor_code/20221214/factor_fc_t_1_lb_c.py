# coding: utf-8
# Author：fengchi863
# Date ：2022/12/12 16:01

import numpy as np
import pandas as pd
from xquant.factordata import FactorData

from LucienUtil import IO

fd = FactorData()

def cal_stock_list(start_date, end_date, IO):
    MD_data = IO.read_data([fd.tradingday(str(start_date), -300)[0], end_date],
                           columns=['amt'],
                           alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    ipo_data = IO.read_data([20000101, 20990101],
                            alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5')
    ipo_data = ipo_data.rename(columns={'S_INFO_LISTDATE': 'list_date', 'S_INFO_CODE': 'code'})
    ipo_data = ipo_data.reset_index()
    ipo_data = ipo_data[ipo_data['code'].apply(lambda x: x[:2] in ['60', '30', '00'])]  # 筛选上交所和深交所股票，不包括科创板
    ipo_data = ipo_data[~ipo_data['list_date'].isnull()]  # 去掉没有上市日期的股票，包括IPO终止和还未上市的股票
    ipo_data['list_date'] = ipo_data['list_date'].apply(lambda x: pd.Timestamp(str(int(x))))
    ipo_data['dt'] = ipo_data['list_date']
    ipo_data['is_list_date'] = True
    ipo_data = ipo_data.set_index(['dt', 'Ticker'])[['is_list_date']]

    md_df = MD_data.copy()
    md_df = md_df.join(ipo_data)
    md_df['after_list'] = md_df['is_list_date'].unstack().fillna(method='ffill').stack()  # 上市后的标记
    md_df.loc[md_df['amt'] == 0]['after_list'] = np.nan
    md_df['list_len'] = md_df['after_list'].unstack().rolling(10000000, 1).sum().stack()
    md_df.loc[(md_df['list_len'].isnull() & (md_df['amt'] > 0)), 'list_len'] = 250  # sss：大部分股票上市日期小于md的起始日期，导致为空，直接填充250
    md_df['list_len'] = md_df['list_len'].unstack().fillna(method='ffill').stack()
    # list_len和after_not_ul_len要加1
    md_df['list_len'] = md_df['list_len'] + 1
    md_df.loc[(md_df['list_len'] > 250), 'list_len'] = 250

    stock_pool = md_df['list_len'].unstack() >= 30

    date_list = fd.tradingday(str(start_date), str(end_date))

    st_pool = pd.DataFrame(index=stock_pool.index, columns=stock_pool.columns)
    for _dat in date_list:
        index = pd.to_datetime(str(_dat))
        nost_stk_list = fd.stock_filter(stock_pool.columns.tolist(), _dat, 'STPT')['stock'].tolist()
        st_pool.loc[index, nost_stk_list] = True
    st_pool = st_pool.fillna(False)

    stock_pool = stock_pool & st_pool.astype(bool)
    return stock_pool

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
def factor_fc_t_1_lb_c(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    fname = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {fname:2, 'data':['MD']}

    start_date_ = int(fd.tradingday(str(start_date), -30)[0])

    md_data = IO.read_data([start_date_, end_date], columns=['close', 'pre_close','pct_chg'], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data = md_data[md_data.reset_index()['Ticker'].apply(lambda x: ('BJ' not in x)).values]
    zcz = (((md_data.reset_index()['Ticker'].apply(lambda x: x[0] == '3')) & (md_data.reset_index()['dt']>=pd.Timestamp('20200824'))) |
           (md_data.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    md_data.loc[zcz, 'pct_chg'] = md_data.loc[zcz, 'pct_chg'] / 2

    md_data['ul_price'] = cal_ul_price(md_data[['pre_close']])
    md_data['is_ul'] = md_data['close'] == md_data['ul_price']

    stock_pool = cal_stock_list(start_date=start_date,
                                end_date=end_date,
                                IO=IO)

    zt = md_data['is_ul'].unstack().fillna(False)
    zt = zt & stock_pool.reindex(index=zt.index, columns=zt.columns)
    lb = pd.DataFrame(get_lb(zt.T).T, index=zt.index, columns=zt.columns)
    daily_lb_num = pd.Series(np.nansum(lb.values >= 2, axis=1), index=lb.index)

    by_day = daily_lb_num
    by_day.name = fname
    factor_df = pd.DataFrame(index=md_data.index)
    factor_df = factor_df.join(by_day)
    return factor_df

if __name__ == '__main__':
    factor = factor_fc_t_1_lb_c(20221001, 20221211, IO=IO, return_fillna_dic=False)
    pass