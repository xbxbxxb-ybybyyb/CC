#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
import IO
s = FactorData()
factor_name = 'qyh_sat_md_20240201_10'
def factor_qyh_sat_md_20240201_10(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def f_calc_skew(factor_series):
        factor_series = factor_series[~np.isnan(factor_series)]
        mean = factor_series.mean()
        std = factor_series.std(ddof=1)
        n = len(factor_series)
        if n > 3:
            skew = sum(((factor_series - mean) / std) ** 3) * n / (n - 1) / (n - 2)
        else:
            skew = np.nan
        return skew
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori[factor_name] = df_ori['amt'] / df_ori['amt'].unstack().rolling(5,1).apply(lambda x : f_calc_skew(x)).stack()
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
def factor_check(func,factor_name,result_path):
    long_interval = [20160101, 20211231]
    short_interval_list = s.tradingday(20160101, 20160107)
    # short_interval_list += s.tradingday(20191225, 20191231)
    short_interval_list += s.tradingday(20211227, 20211231)
    short_interval_list = [int(tradingday) for tradingday in short_interval_list]
    try:
        if os.path.exists('%s%s_%d_%d.pkl'%(result_path, factor_name, long_interval[0], long_interval[1])):
            long_df = pd.read_pickle('%s%s_%d_%d.pkl'%(result_path, factor_name, long_interval[0], long_interval[1]))
        else:
            long_df = func(long_interval[0], long_interval[1], IO)
            long_df = long_df.fillna(func(None, None, None, return_fillna_dic=True))
            if not os.path.exists(result_path):
                os.makedirs(result_path)
            long_df.to_pickle('%s%s_%d_%d.pkl'%(result_path, factor_name, long_interval[0], long_interval[1]))
        if int(np.isinf(long_df).sum())>0:
            return '因子值存在inf'
    except Exception as e:
        return '函数测试出错-测试区间:%d-%d-%s'%(long_interval[0], long_interval[1], e)
    try:
        fill_dic = func(None, None, None, return_fillna_dic=True)
        for short_date in short_interval_list:
            if os.path.exists('%s%s_%d_%d.pkl'%(result_path, factor_name, short_date, short_date)):
                short_df = pd.read_pickle('%s%s_%d_%d.pkl'%(result_path, factor_name, short_date, short_date))
            else:
                short_df = func(short_date, short_date, IO).fillna(fill_dic)
                short_df.to_pickle('%s%s_%d_%d.pkl' % (result_path, factor_name, short_date, short_date))
            short_df = short_df.loc[pd.Timestamp(str(short_date))]
            tmp_long_df = long_df.loc[pd.Timestamp(str(short_date))]
            if np.nanmax((short_df - tmp_long_df).abs().values) > 1e-8:
                print('%s 因子值不一致1-计算区间:%d-%d和%d-%d'%(factor_name,long_interval[0], long_interval[1], short_date, short_date))
                print((short_df - tmp_long_df).abs().idxmax(),np.nanmax((short_df - tmp_long_df).abs().values))
                return '%s 因子值不一致1-计算区间:%d-%d和%d-%d'%(factor_name,long_interval[0], long_interval[1], short_date, short_date)
    except Exception as e:
        return '函数测试出错-测试区间:%d-%d-%s'%(short_date, short_date, e)

print(factor_check(factor_qyh_sat_md_20240201_10,
            factor_name,
            '/data/user/015585/01-因子挖掘/06-SaturnNext/factor_check/'))