import os
import time

from run_factor_demo import run_factor
from project_2_factor_test_origin import FactorTest
import pandas as pd
import numpy as np
from function_factor_5min import *
from xquant.factordata import FactorData
import IO
from itertools import product

dic_property = {
    # 'high':f_pro_high,
    # 'open':f_pro_open,
    # 'close':f_pro_close,
    # 'low':f_pro_low,
    # 'amt':f_pro_amt,
    # 'volume':f_pro_volume,
    # 'h2p':f_pro_h2p,
    # 'l2p':f_pro_l2p,
    # 'c2p':f_pro_c2p,
    # 'h2c':f_pro_h2c,
    # 'l2c':f_pro_l2c,
    # 'hl2p':f_pro_hl2p,
    # 'vwap':f_pro_vwap,
    # 'c2v':f_pro_c2v,
    # 'h2v':f_pro_h2v,
    # 'l2v':f_pro_l2v,
    'abspct':f_pro_abspct,
    'logabspct':f_pro_logabspct,
    'abspctamt':f_pro_abspctamt,
    'syx2':f_pro_syx2,
    'xyx1':f_pro_xyx1,
    'xyx2':f_pro_xyx2,
    'lengthk':f_pro_lengthk,
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
                    factor_property,
                    df_filter,
                    day_div,
                    calc_day,
                    calc_day_fm,
                    rolling_day,
                    calc
                    ):
    # 根据因子属性获取基础df
    df_f1 = dic_property[factor_property](df_amt, df_volume, df_low, df_close, df_high, df_open)
    # 筛选
    df_f2 = dic_filter[df_filter](df_f1, df_amt, df_volume, df_low, df_close, df_high, df_open)
    # 横向加权
    df_f3 = dic_day_div[day_div](df_f2, df_amt, df_volume, df_low, df_close, df_high, df_open)
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
        df_fm = get_fm_df(day_div, df_amt, df_volume, df_low, df_close, df_high, df_open)
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
for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor/neptune/h5/20250327_T_1_Factor_5min/'):
    list_del.append(file_name.replace('.h5',''))
for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor/neptune/h5/20250513_T_1_Factor_5min/'):
    list_del.append(file_name.replace('.h5',''))
print('已计算{}个因子'.format(len(list_del)))
#预先准备好测试函数和基础数据
start_date = 20160101
end_date = 20191231
s = FactorData()
start_date = int(s.tradingday(str(start_date), -80)[0])
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
md_data = IO.read_data([start_date, end_date],columns=['adjfactor'],
                       alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
df_low = df_low.multiply(md_data['adjfactor'], axis=0)
df_high = df_high.multiply(md_data['adjfactor'], axis=0)
df_open = df_open.multiply(md_data['adjfactor'], axis=0)
df_close = df_close.multiply(md_data['adjfactor'], axis=0)
df_volume = df_volume.divide(md_data['adjfactor'], axis=0)
print('完成复权处理')
sft_basic_path = '/data/group/800463/data/projectZZ_public/factor_lib/sft_basic_formal_931_20160101_20191231.h5'  # 这个文件里有label和所有因子
df_sft = IO.read_data([start_date, end_date], alt=sft_basic_path)
print('get sft')
for df_filter,\
    day_div,calc_day,calc_day_fm,\
    rolling_day,factor_property,calc in \
        product(dic_filter,
                dic_day_div,dic_calc_day,dic_calc_day_fm,
                list_rolling_days,dic_property,dic_calc):
    if (rolling_day == 1) and (calc != 'max'): # 回溯1天，不涉及纵向calc
        continue
    if day_div == 'nodaydiv' and calc_day_fm != 'absmax':# nodaydiv只有一种calc_day_fm
        continue
    factor_name = f'{factor_property}_{df_filter}_{day_div}_{calc_day}_{calc_day_fm}_{rolling_day}_{calc}'
    if factor_name in list_del:
        continue
    print(factor_name)
    def factor_func(start_date, end_date, IO, return_fillna_dic=False,
                    df_amt=df_amt.copy(), df_volume=df_volume.copy(),
                    df_low=df_low.copy(), df_close=df_close.copy(), df_high=df_high.copy(), df_open=df_open.copy()):
        if return_fillna_dic:
            # 返回因子为nan时的填充值
            return {factor_name: 0, 'data': ['MD']}
        res = generate_factor(df_amt, df_volume, df_low, df_close, df_high, df_open,
                              factor_property, df_filter,
                              day_div, calc_day, calc_day_fm, rolling_day, calc
                    )
        res.columns = [factor_name]
        # ---------------------------------------------------------------------------------------------------------------
        return res
    basic_file_path = '/data/group/800463/data/projectZZ_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5'
    factor_path = '/dfs/user/015585/01_factor_develop_store/fast_factor/neptune/h5' + '/20250513_T_1_Factor_5min/' # 因子保存路径
    factor_df0 = run_factor(func=factor_func,
                            factor_name=factor_name,
                            factor_type='T-1_factor',
                            start_date=start_date,
                            end_date=end_date,
                            basic_file_path=basic_file_path,
                            result_path=factor_path,
                            interval_res=False)
    df = pd.read_hdf(factor_path + factor_name + '.h5')
    result_path = '/dfs/user/015585/01_factor_develop_store/fast_factor/neptune/factor_report' + '/20250513_T_1_Factor_5min/'  # report保存路径
    factor_test = FactorTest(start_date, end_date, df_sft, cal_mi=False)
    for col in df.columns:
        print(col)
        # print(time.localtime())
        factor_test.factor_test(df[[col]], result_path,
                                factor_corr_test=True, generate_pdf=False)
        check_score = factor_test.result_dic['check_score_res']
        print('总分:', check_score.loc['score', 'tot_score'])
        print('CORR:', factor_test.result_dic['corr_sta'].loc['corr_tot', 'value'])
