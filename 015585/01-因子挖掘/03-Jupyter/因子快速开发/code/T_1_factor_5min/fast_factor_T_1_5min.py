import os
import time

from run_factor_demo_parallel_new import run_factor
from test_factor_demo import strongFactorTest
import pandas as pd
import numpy as np
from function_factor_5min import *
from xquant.factordata import FactorData
import IO
from itertools import product

dic_property = {
    'high':f_pro_high,
    'open':f_pro_open,
    'close':f_pro_close,
    'low':f_pro_low,
    'amt':f_pro_amt,
    'volume':f_pro_volume,
    'h2p':f_pro_h2p,
    'l2p':f_pro_l2p,
    'c2p':f_pro_c2p,
    'h2c':f_pro_h2c,
    'l2c':f_pro_l2c,
    'hl2p':f_pro_hl2p,
    'vwap':f_pro_vwap,
    'c2v':f_pro_c2v,
    'h2v':f_pro_h2v,
    'l2v':f_pro_l2v,
    'abspct':f_pro_abspct,
    'logabspct':f_pro_logabspct,
    'abspctamt':f_pro_abspctamt,
    'syx2':f_pro_syx2,
    'xyx1':f_pro_xyx1,
    'xyx2':f_pro_xyx2,
    'lengthk':f_pro_lengthk,
    'closediff': f_pro_closediff,
    'absclosediff': f_pro_absclosediff,
    'voldiff': f_pro_voldiff,
    'absvoldiff': f_pro_absvoldiff,
    'bqty': f_pro_bqty,
    'bqtydiff2tvol': f_pro_bqtydiff2tvol,
    'sqty': f_pro_sqty,
    'sqtydiff2tvol': f_pro_sqtydiff2tvol,
    'bp': f_pro_bp,
    'sp': f_pro_sp,
    'bp2sp': f_pro_bp2sp,
    'bqtyratio': f_pro_bqtyratio,
    'bqty2sqty': f_pro_bqty2sqty,
    'absbqty2sqty': f_pro_absbqty2sqty,
    'c2bp': f_pro_c2bp,
    'c2sp': f_pro_c2sp,
    'v2bqty': f_pro_v2bqty,
    'v2sqty': f_pro_v2sqty,
    'v2bsqty': f_pro_v2bsqty,
    'amt2bamt': f_pro_amt2bamt,
    'amt2samt': f_pro_amt2samt,
               }
dic_filter = {
    'nofilter':f_filter_nofilter,
    'up':f_filter_up,
    'down':f_filter_down,
                     }
# 横向加权变量
dic_day_div = {
    'nodaydiv': f_day_div_no,
    'amt': f_day_div_amt,
    'volume': f_day_div_volume,
    'close': f_day_div_close,
}
# 横向计算函数(axis=1)
dic_calc_day = {
    'max': f_calc_max,
    'min': f_calc_min,
    'mean': f_calc_avg,
    'median': f_calc_med,
    'cv': f_calc_cv,
    'sum': f_calc_sum,
    'cct': f_calc_cct,
    'skew': f_calc_skew,
    'kurt': f_calc_kurt,
    'change': f_calc_change,
    'm2m': f_calc_m2m,
    'pos': f_calc_pos,
    'std': f_calc_std
}
# 横向分母计算函数
dic_calc_day_fm = {
    'absmax': f_calc_absmax,
    'mean': f_calc_avg,
    'sum': f_calc_sum,
    'std': f_calc_std
}
# 纵向rolling范围
list_rolling_days = [1,5,10,20,60]
# rolling计算函数
dic_calc = {
            'max':f_calc_max,
            'min':f_calc_min,
            'avg':f_calc_avg,
            'med':f_calc_med,
            'cv':f_calc_cv,
            'sum':f_calc_sum,
            'cct':f_calc_cct,
            'skew':f_calc_skew,
            'kurt':f_calc_kurt,
            'change':f_calc_change,
            'm2m':f_calc_m2m,
            'pos':f_calc_pos,
            'std':f_calc_std
           }
# 和自身不同rolling的求比例 这一步在目前先不考虑(202503)
list_division = list_rolling_days.copy()
# 自身rolling的计算函数
dic_calc_rolling_div = {
    'absmax': f_calc_absmax,
    'avg': f_calc_avg,
    'sum': f_calc_sum,
    'std': f_calc_std
}
# 主体函数，在预先准备好多个df的基础上
def generate_factor(df_amt, df_volume, df_low, df_close, df_high, df_open,
                    df_bqty, df_sqty, df_bp, df_sp,
                    factor_property,
                    df_filter,
                    day_div,
                    calc_day,
                    calc_day_fm,
                    rolling_day,
                    calc
                    ):
    # 根据因子属性获取基础df
    df_f1 = dic_property[factor_property](df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,)
    # 筛选
    df_f2 = dic_filter[df_filter](df_f1, df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,)
    # 横向加权
    df_f3 = dic_day_div[day_div](df_f2, df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,)
    # 横向计算
    if calc_day in ['max', 'min', 'mean', 'median', 'skew', 'kurt', 'std']:
        df_f4 = getattr(df_f3, calc_day)(axis=1)
    elif calc_day == 'cv':
        df_f4 = getattr(df_f3, 'std')(axis=1) / abs(getattr(df_f3, 'mean')(axis=1)).apply(lambda x : round_(x,5)).replace(0,np.nan)
    elif calc_day == 'm2m':
        df_f4 = (getattr(df_f3, 'max')(axis=1) - getattr(df_f3, 'min')(axis=1)) / (getattr(df_f3, 'mean')(axis=1) - getattr(df_f3, 'min')(axis=1)).apply(lambda x : round_(x,5)).replace(0,np.nan)
    elif calc_day == 'cct':
        df_f4 = getattr(df_f3 ** 2, 'sum')(axis=1) / (getattr(df_f3, 'sum')(axis=1) ** 2)
    else:
        df_f4 = df_f3.apply(dic_calc_day[calc_day],axis=1)
    # 获取横向分母
    if day_div != 'nodaydiv':
        df_fm = get_fm_df(day_div, df_amt, df_volume, df_low, df_close, df_high, df_open, df_bqty, df_sqty, df_bp, df_sp,)
        if calc_day_fm in ['mean', 'sum', 'std']:
            df_f5 = df_f4.divide(getattr(df_fm, calc_day_fm)(axis=1).replace(0,np.nan))
        elif calc_day_fm == 'absmax':
            df_f5 = df_f4.divide(getattr(abs(df_fm), 'max')(axis=1).replace(0, np.nan))
        else:
            df_f5 = df_f4.divide(df_fm.apply(dic_calc_day_fm[calc_day_fm], axis=1).replace(0, np.nan))
    else:
        df_f5 = df_f4.copy()
    # 纵向rolling
    if rolling_day > 1:
        df_f6 = df_f5.unstack().rolling(rolling_day,1).apply(dic_calc[calc]).stack()
    else:
        df_f6 = df_f5.copy()
    res = pd.DataFrame(df_f6)
    return res

# 剔除已经算过的因子
list_del = []
for file_name in os.listdir('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhmd5m_filter/'):
    list_del.append(file_name.replace('.h5',''))
print('已计算{}个因子'.format(len(list_del)))

list_in = [
    'c2p_nofilter_nodaydiv_mean_absmax_120_std',
    'logabspct_nofilter_nodaydiv_max_absmax_240_skew',
    'logabspct_nofilter_nodaydiv_max_absmax_120_kurt',
    'c2v_nofilter_nodaydiv_mean_absmax_20_cv',
    'c2bp_nofilter_nodaydiv_mean_absmax_60_avg',
    'close_nofilter_nodaydiv_max_absmax_120_cv',
    'closediff_nofilter_nodaydiv_min_absmax_10_med',
    'bp_nofilter_nodaydiv_max_absmax_240_cv',
    'h2p_nofilter_nodaydiv_mean_absmax_60_kurt',
    'bp2sp_nofilter_nodaydiv_mean_absmax_10_min',
    'bp_nofilter_nodaydiv_max_absmax_120_cct',
    'c2bp_nofilter_nodaydiv_mean_absmax_240_avg',
    'h2p_nofilter_nodaydiv_min_absmax_10_cv',
    'h2c_nofilter_nodaydiv_max_absmax_60_std',
    'amt2bamt_nofilter_nodaydiv_max_absmax_60_med',
    'c2sp_nofilter_nodaydiv_min_absmax_10_med',
    'bp2sp_nofilter_nodaydiv_mean_absmax_120_min',
    'bp_nofilter_nodaydiv_min_absmax_20_cct',
    'sqtydiff2tvol_nofilter_nodaydiv_mean_absmax_20_avg',
    'absclosediff_nofilter_nodaydiv_max_absmax_240_std',
    'closediff_nofilter_nodaydiv_mean_absmax_20_min',
    'xyx2_nofilter_nodaydiv_std_absmax_120_skew',
    'xyx1_nofilter_nodaydiv_max_absmax_5_min',
    'c2p_nofilter_nodaydiv_mean_absmax_60_min',
    'c2sp_nofilter_nodaydiv_mean_absmax_5_min',
    'bp2sp_nofilter_nodaydiv_min_absmax_5_avg',
    'amt2samt_nofilter_nodaydiv_max_absmax_5_avg',
    'bqtydiff2tvol_nofilter_nodaydiv_mean_absmax_60_sum',
    'c2v_nofilter_nodaydiv_std_absmax_10_max',
    'syx2_nofilter_nodaydiv_std_absmax_240_cv',
    'h2v_nofilter_nodaydiv_max_absmax_120_max',
    'bp2sp_nofilter_nodaydiv_min_absmax_1_max',
    'bp2sp_nofilter_nodaydiv_max_absmax_20_med',
    'absvoldiff_nofilter_nodaydiv_mean_absmax_240_pos',
    'absbqty2sqty_nofilter_nodaydiv_mean_absmax_240_std',
    'c2bp_nofilter_nodaydiv_std_absmax_10_min',
    'closediff_nofilter_nodaydiv_mean_absmax_60_min',
    'bqtyratio_nofilter_nodaydiv_mean_absmax_240_cct',
    'v2bsqty_nofilter_nodaydiv_std_absmax_20_min',
    'high_nofilter_nodaydiv_min_absmax_10_cv',
    'sqtydiff2tvol_nofilter_nodaydiv_mean_absmax_120_cct',
    'bqtydiff2tvol_nofilter_nodaydiv_mean_absmax_10_max',
    'c2bp_nofilter_nodaydiv_min_absmax_10_m2m',
    'bp2sp_nofilter_nodaydiv_min_absmax_60_min',
    'c2v_nofilter_nodaydiv_std_absmax_10_min',
    'bqtyratio_nofilter_nodaydiv_max_absmax_240_cv',
    'amt2bamt_nofilter_nodaydiv_max_absmax_20_max',
    'h2c_nofilter_nodaydiv_std_absmax_5_min',
    'c2bp_nofilter_nodaydiv_mean_absmax_240_cv',
    'bqtydiff2tvol_nofilter_nodaydiv_max_absmax_5_med',
    'h2v_nofilter_nodaydiv_std_absmax_5_std',
    'bp2sp_nofilter_nodaydiv_max_absmax_60_min',
    'v2sqty_nofilter_nodaydiv_max_absmax_60_min',
    'c2bp_nofilter_nodaydiv_mean_absmax_60_cct',
    'absbqty2sqty_nofilter_nodaydiv_max_absmax_240_m2m',
    'sp_nofilter_nodaydiv_min_absmax_5_m2m',
    'bp_nofilter_nodaydiv_mean_absmax_5_m2m',
    'abspct_nofilter_nodaydiv_std_absmax_120_skew',
    'closediff_nofilter_nodaydiv_mean_absmax_120_min',
    'h2c_nofilter_nodaydiv_mean_absmax_5_std',
    'sqtydiff2tvol_nofilter_nodaydiv_mean_absmax_10_std',
    'h2c_nofilter_nodaydiv_mean_absmax_240_pos',
    'amt2bamt_nofilter_nodaydiv_std_absmax_120_avg',
    'c2sp_nofilter_nodaydiv_std_absmax_10_avg',
    'sqtydiff2tvol_nofilter_nodaydiv_std_absmax_120_pos',
    'c2bp_nofilter_nodaydiv_max_absmax_20_min',
    'c2bp_nofilter_nodaydiv_min_absmax_5_std',
    'h2p_nofilter_nodaydiv_max_absmax_60_med',
    'c2bp_nofilter_nodaydiv_std_absmax_1_max',
    'syx2_nofilter_nodaydiv_max_absmax_20_std',
    'bqtydiff2tvol_nofilter_nodaydiv_std_absmax_120_cct',
    'bp_nofilter_nodaydiv_min_absmax_20_m2m',
    'abspctamt_nofilter_nodaydiv_mean_absmax_60_skew',
    'voldiff_nofilter_nodaydiv_max_absmax_120_cct',
    'sqtydiff2tvol_nofilter_nodaydiv_min_absmax_1_max',
    'absbqty2sqty_nofilter_nodaydiv_std_absmax_240_cv',
    'sp_nofilter_nodaydiv_std_absmax_240_skew',
    'c2v_nofilter_nodaydiv_max_absmax_240_m2m',
    'xyx2_nofilter_nodaydiv_max_absmax_20_max',
    'amt_nofilter_nodaydiv_min_absmax_10_cct',
    'hl2p_nofilter_nodaydiv_std_absmax_120_kurt',
    'abspct_nofilter_nodaydiv_max_absmax_240_m2m',
    'volume_nofilter_nodaydiv_std_absmax_5_min',
    'h2c_nofilter_nodaydiv_max_absmax_120_max',
    'absvoldiff_nofilter_nodaydiv_max_absmax_240_std',
    'c2bp_nofilter_nodaydiv_max_absmax_5_med',
    'c2v_nofilter_nodaydiv_mean_absmax_240_m2m',
    'h2v_nofilter_nodaydiv_max_absmax_5_cv',
    'c2sp_nofilter_nodaydiv_mean_absmax_20_std',
    'sqtydiff2tvol_nofilter_nodaydiv_min_absmax_10_sum',
    'absvoldiff_nofilter_nodaydiv_mean_absmax_60_sum',
    'closediff_nofilter_nodaydiv_mean_absmax_120_pos',
    'closediff_nofilter_nodaydiv_mean_absmax_120_kurt',
    'lengthk_nofilter_nodaydiv_mean_absmax_240_max',
    'sp_nofilter_nodaydiv_mean_absmax_240_kurt',
    'bp_nofilter_nodaydiv_min_absmax_5_std',
    'sqtydiff2tvol_nofilter_nodaydiv_mean_absmax_120_avg',
    'sqtydiff2tvol_nofilter_nodaydiv_mean_absmax_10_min',
    'xyx2_nofilter_nodaydiv_max_absmax_240_kurt'
]

# 预先准备好测试函数和基础数据
start_date = 20170101
end_date = 20250630
s = FactorData()
start_date = int(s.tradingday(str(start_date), -300)[0])
df_amt = IO.read_data([start_date, end_date],
                      alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
print('get amt')
df_volume = IO.read_data([start_date, end_date],
                      alt='/data/group/800463/data/generalStrong/minute5/volume.h5')
print('get volume')
df_low = IO.read_data([start_date, end_date],
                      alt='/data/group/800463/data/generalStrong/minute5/low.h5')
print('get low')
df_close = IO.read_data([start_date, end_date],
                      alt='/data/group/800463/data/generalStrong/minute5/close.h5')
print('get close')
df_high = IO.read_data([start_date, end_date],
                      alt='/data/group/800463/data/generalStrong/minute5/high.h5')
print('get high')
df_open = IO.read_data([start_date, end_date],
                      alt='/data/group/800463/data/generalStrong/minute5/open.h5')
print('get open')
df_bqty = IO.read_data([start_date, end_date],
                      alt='/data/group/800463/data/generalStrong/ordersheet5/TotalBidQty.h5')
print('get bqty')
df_sqty = IO.read_data([start_date, end_date],
                      alt='/data/group/800463/data/generalStrong/ordersheet5/TotalOfferQty.h5')
print('get sqty')
df_bp = IO.read_data([start_date, end_date],
                      alt='/data/group/800463/data/generalStrong/ordersheet5/WeightedAvgBidPx.h5')
print('get bp')
df_sp = IO.read_data([start_date, end_date],
                      alt='/data/group/800463/data/generalStrong/ordersheet5/WeightedAvgOfferPx.h5')
print('get sp')


md_data = IO.read_data([start_date, end_date],columns=['adjfactor'],
                       alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
df_low = df_low.multiply(md_data['adjfactor'], axis=0)
df_high = df_high.multiply(md_data['adjfactor'], axis=0)
df_open = df_open.multiply(md_data['adjfactor'], axis=0)
df_close = df_close.multiply(md_data['adjfactor'], axis=0)
df_volume = df_volume.divide(md_data['adjfactor'], axis=0)
df_bqty = df_bqty.divide(md_data['adjfactor'], axis=0)
df_sqty = df_sqty.divide(md_data['adjfactor'], axis=0)
df_bp = df_bp.multiply(md_data['adjfactor'], axis=0)
df_sp = df_sp.multiply(md_data['adjfactor'], axis=0)

print('完成复权处理')
sft_basic_path = '/data/group/800463/data/project1_public/factor_lib_v3/sft_update_europa.h5'  # 这个文件里有label和所有因子
df_sft = IO.read_data([start_date, end_date], alt=sft_basic_path)
print('get sft')
for df_filter,\
    day_div,calc_day,calc_day_fm,\
    rolling_day,factor_property,calc in \
        product(dic_filter,
                dic_day_div,dic_calc_day,dic_calc_day_fm,
                list_rolling_days,dic_property,dic_calc):
    if factor_property in ['syx1','syx2','xyx1','xyx2','lengthk','absclosediff',] and calc_day in ['min']: # 一些属性的日内最小值必然为0
        continue
    if (rolling_day == 1) and (calc != 'max'): # 回溯1天，不涉及纵向calc
        continue
    if day_div == 'nodaydiv' and calc_day_fm != 'absmax':# nodaydiv只有一种calc_day_fm
        continue
    factor_name = f'{factor_property}_{df_filter}_{day_div}_{calc_day}_{calc_day_fm}_{rolling_day}_{calc}'
    if factor_name in list_del:
        continue
    if factor_name not in list_in:
        continue
    print(factor_name)
    def factor_func(start_date, end_date, IO, return_fillna_dic=False,
                    df_amt=df_amt.copy(), df_volume=df_volume.copy(),
                    df_low=df_low.copy(), df_close=df_close.copy(), df_high=df_high.copy(), df_open=df_open.copy(),
                    df_bqty = df_bqty.copy(), df_sqty = df_sqty.copy(), df_bp = df_bp.copy(), df_sp = df_sp.copy()):
        if return_fillna_dic:
            # 返回因子为nan时的填充值
            return {factor_name: 0, 'data': ['5min']}
        res = generate_factor(df_amt, df_volume, df_low, df_close, df_high, df_open,
                              df_bqty, df_sqty, df_bp, df_sp,
                              factor_property, df_filter,
                              day_div, calc_day, calc_day_fm, rolling_day, calc)
        res.columns = [factor_name]
        # ---------------------------------------------------------------------------------------------------------------
        return res
    # basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'
    basic_file_path = '/data/user/015585/01-因子挖掘/20240624 xdb数据探索/file/basic_europa_20150930_20250710.h5'
    factor_path = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhmd5m_filter/' # 因子保存路径
    factor_df0 = run_factor(func=factor_func,
                            factor_name=factor_name,
                            factor_type='T-1_factor',
                            start_date=start_date,
                            end_date=end_date,
                            basic_file_path=basic_file_path,
                            result_path=factor_path,
                            interval_res=False)
    # df = pd.read_hdf(factor_path + factor_name + '.h5')
    # result_path = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/factor_report/20250530_zwhmd5m1/'  # report保存路径
    # factor_test = strongFactorTest(start_date, end_date, df_sft)
    # for col in df.columns:
    #     print(col)
    #     # print(time.localtime())
    #     factor_test.factor_test(df[[col]], result_path,
    #                             factor_corr_test=False, generate_pdf=False)
    #     check_score = factor_test.result_dic['check_score_res']
    #     print('总分:', check_score.loc['score', 'tot_score'])
    #     print('CORR:', factor_test.result_dic['corr_sta'].loc['corr_tot', 'value'])
