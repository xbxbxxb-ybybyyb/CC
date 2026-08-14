# @Time : 2022/5/10 9:12
# @Author : Zhichen Lu
# @File : ByCategory.py

from StrongStockModel.Factor.FeatureEngineering.FactorCategory import perfect_distr,OK_distr,to_diff,trend_dirift,drop,kind_of_prob
import pandas as pd
import numpy as np
from dataApi.tradeDate import get_date_range
from dataApi.getData import trans_int2windcode,trans_windcode2int
from dataApi.stockList import get_stock_list
from operators import dt_delay,ds_delay

def get_factor_mv(factor,standardize_days = 40,test_drop_days=40,freq = 7):
    # factor = factor_df.copy()
    factor_finite = np.isfinite(factor)
    factor[~ factor_finite] = 0
    factor2 = factor ** 2

    d_cf = factor.sum(axis=1)
    d_cf2 = factor2.sum(axis=1)
    d_cn = factor_finite.sum(axis=1)

    rd_cf = np.lib.stride_tricks.as_strided(d_cf, shape=(
        d_cf.shape[0] - standardize_days + 1, standardize_days, d_cf.shape[1]), strides=(
        d_cf.strides[0], d_cf.strides[0], d_cf.strides[1])).sum(axis=1)

    rd_cf2 = np.lib.stride_tricks.as_strided(d_cf2, shape=(
        d_cf2.shape[0] - standardize_days + 1, standardize_days, d_cf2.shape[1]), strides=(
        d_cf2.strides[0], d_cf2.strides[0], d_cf2.strides[1])).sum(axis=1)

    rd_cn = np.lib.stride_tricks.as_strided(d_cn, shape=(
        d_cn.shape[0] - standardize_days + 1, standardize_days, d_cn.shape[1]), strides=(
        d_cn.strides[0], d_cn.strides[0], d_cn.strides[1])).sum(axis=1).astype(float)

    rd_cn[rd_cn < standardize_days * freq / 2] = np.nan
    factor[~ factor_finite] = np.nan

    rd_mean = (rd_cf / rd_cn)[test_drop_days - standardize_days: -1]
    rd_std = (((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5)[test_drop_days - standardize_days: -1]
    rd_std[rd_std == 0] = np.nan
    return rd_mean,rd_std

bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]

def _load_pickle_frame(file_name, date_list, code_list):

    factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'

    df_dic = {}
    for time in bar_list:
        df = pd.read_pickle(factor_address + 'Fix%s_' % time + file_name + '.pkl')
        df.index = df.index.map(int)
        df.columns = df.columns.map(trans_windcode2int)
        df = df.loc[date_list[0]: date_list[-1]]
        df = df.reindex(columns=code_list)
        df_dic[time] = df
    return np.r_['0,3', tuple(df_dic[x].values for x in bar_list)].transpose(1, 0, 2)

def OK_distr_process(factor_3d,window =40):
    r_mean, r_std = get_factor_mv(factor_3d, window, window, factor_3d.shape[1])
    factor_3d_norm = (factor_3d[window:] - r_mean[:, None]) / r_std[:, None]
    factor_smooth = np.where(abs(factor_3d_norm) > 3,
                             factor_3d_norm.clip(-3, 3) * r_std[:, None] + r_mean[:, None],
                             factor_3d[window:])
    smooth_mean, smooth_std = get_factor_mv(factor_smooth, window, window, 7)
    factor_smooth_norm = (factor_smooth[window:] - smooth_mean[:, None]) / smooth_std[:, None]
    return factor_smooth_norm

# factor_name = OK_distr[0]
Window = 40
d_list = get_date_range(20170101,20181231)
c_list = get_stock_list(20170101)
factor_3d = _load_pickle_frame('FactorMin76_mean',d_list,c_list)
factor_3d_dt_diff = factor_3d - dt_delay(factor_3d,1)
# factor_3d_ds_diff = factor_3d - ds_delay(factor_3d,1)

f_diff_mean,f_diff_std = get_factor_mv(factor_3d_dt_diff,Window,Window,7)
factor_diff_norm = (factor_3d_dt_diff[Window:] - f_diff_mean[:,None])/f_diff_std[:,None]




