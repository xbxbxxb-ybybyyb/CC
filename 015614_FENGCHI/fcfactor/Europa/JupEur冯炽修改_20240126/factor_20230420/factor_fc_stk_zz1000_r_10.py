# coding: utf-8
# Author：fengchi863
# Date ：2023/4/20 15:55

import pandas as pd
import numpy as np
import decimal
from xquant.factordata import FactorData
s = FactorData()

def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    cov = np.nanmean(d_x * d_y, axis=0)
    var = (np.nanvar(x, axis=0) * np.nanvar(y, axis=0)) ** 0.5
    return cov / var

def factor_fc_stk_zz1000_r_10(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='fc_stk_zz1000_r_10'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD','AIndexEODPrices']}

    start_date_ = int(s.tradingday(str(start_date), -20)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['open', 'close', 'pre_close', 'adjfactor']
                           , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    opn = md_data['open'] * md_data['adjfactor']
    close = md_data['close'] * md_data['adjfactor']
    pre_close = md_data['pre_close'] * md_data['adjfactor']

    index_data = IO.read_data([start_date_, end_date], columns=['S_DQ_CLOSE', 'S_DQ_OPEN']
                              , alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
    index_data = index_data.query('Ticker == "000852.SH"')
    index_opn = index_data['S_DQ_OPEN']
    index_close = index_data['S_DQ_CLOSE']
    ret = (close - opn) / pre_close

    # 注册制调整
    mask = ret.index.map(lambda x: (x[1][0] == '3' and x[0].strftime('%Y%m%d') >= '20200824') or x[1][:2] == '68')
    ret[mask] = ret[mask] / 2

    ret_market = (index_close - index_opn) / index_opn.shift(1)
    ret = ret.unstack().stack(dropna=False)  # 保证所有天的股票数量一致

    # 播放式计算
    factor = pd.DataFrame(index=opn.unstack().columns)
    start_date = s.tradingday(start_date, -2)[0]
    for dat in s.tradingday(start_date, end_date):
        format_dat = pd.to_datetime(dat)
        tmp_ret = ret.loc[:format_dat].unstack()
        tmp_market = ret_market.loc[:format_dat].unstack()
        cov_ret = array_corr_np(tmp_ret.values[-10:], tmp_market.values.repeat(tmp_ret.shape[1], -1)[-10:])
        factor[format_dat] = cov_ret

    ret = factor.T.stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = ret

    return factor_df