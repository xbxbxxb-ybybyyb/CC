# coding: utf-8
# Author：fengchi863
# Date ：2023/3/29 14:31

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
s = FactorData()

def array_cov_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    cov = np.nanmean(d_x * d_y, axis=0)
    return cov

def factor_fc_stk_mar_corr_v2(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='fc_stk_mar_corr_v2'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD', 'AIndexEODPrices']}
    # 计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -60)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['open', 'close']
                           , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    opn = md_data['open']
    close = md_data['close']

    index_data = IO.read_data([start_date_, end_date], columns=['S_DQ_CLOSE', 'S_DQ_OPEN']
                           , alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
    index_data = index_data.query('Ticker == "000001.SH"')
    index_opn = index_data['S_DQ_OPEN']
    index_close = index_data['S_DQ_CLOSE']
    ret = (close - opn) / opn
    ret_market = (index_close - index_opn) / index_opn
    ret = ret.unstack().stack(dropna=False) # 保证所有天的股票数量一致

    # 播放式计算
    factor = pd.DataFrame(index=opn.unstack().columns)
    start_date = s.tradingday(start_date, -1)[0]    # 往前多算一天
    for dat in s.tradingday(start_date, end_date):
        format_dat = pd.to_datetime(dat)
        tmp_ret = ret.loc[:format_dat].unstack()
        tmp_market = ret_market.loc[:format_dat].unstack()
        cov_ret = array_cov_np(tmp_ret.values[-10:], tmp_market.values.repeat(tmp_ret.shape[1], -1)[-10:])
        ret_market_var = np.nanvar(ret_market.values[-40:], axis=0)
        daily_factor = cov_ret / ret_market_var
        factor[format_dat] = daily_factor

    ret = factor.T.stack()
    factor_df = pd.DataFrame()
    factor_df[factor_name] = ret
    return factor_df