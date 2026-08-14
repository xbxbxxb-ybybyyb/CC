#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
import IO
s = FactorData()
factor_name = 'qyh_sat_md_20240125_8'
def factor_qyh_sat_md_20240125_8(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:1,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','pct_chg','turn'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori = df_ori[(df_ori['amt'] > 0) & (df_ori['vwap'] > 0) & df_ori['close'] > 0]
    x = 'vwap'
    y = 'close'
    df_ori['xy'] = (df_ori[x] * df_ori[y])
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = ((df_ori['exy'] - df_ori['ex'] * df_ori['ey'])
                        /(df_ori['stdx'] * df_ori['stdy'] + 1e-4).apply(lambda x : round_(x,6)))
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)
    df_ori['med'] = df_ori['factor'].unstack().rolling(5,1).median().stack()
    df_ori = df_ori[abs(df_ori['med']) > 1e-6]
    df_ori[factor_name] = (df_ori['factor']) / df_ori['med']
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x :round_(x,3))
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

print(factor_check(factor_qyh_sat_md_20240125_8,
            'qyh_sat_md_20240125_8',
            '/data/user/015585/01-因子挖掘/06-SaturnNext/factor_check/'))