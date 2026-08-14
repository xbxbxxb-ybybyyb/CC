import os
import time

from run_factor_demo import run_factor
from project_2_factor_test_origin import FactorTest
import pandas as pd
import numpy as np
from function_factor_indicator import *
from xquant.factordata import FactorData
import IO
from itertools import product

dic_property = {
    # 'pe': f_pro_pe,
    # 'pb': f_pro_pb,
    # 'pettm': f_pro_pettm,
    # 'pcfocf': f_pro_pcfocf,
    # 'pcfocfttm': f_pro_pcfocfttm,
    # 'pcfncf': f_pro_pcfncf,
    # 'pcfncfttm': f_pro_pcfncfttm,
    # 'ps': f_pro_ps,
    # 'psttm': f_pro_psttm,
    # 'p2dps': f_pro_p2dps,
    # 'nppcttm': f_pro_nppcttm,
    # 'nppclyr': f_pro_nppclyr,
    # 'nassets': f_pro_nassets,
    # 'ncfoattm': f_pro_ncfoattm,
    # 'ncfoalyr': f_pro_ncfoalyr,
    'orttm': f_pro_orttm,
    'orlyr': f_pro_orlyr,
    'niccettm': f_pro_niccettm,
    'niccelyr': f_pro_niccelyr,
               }
dic_filter = {
    'nofilter':f_filter_nofilter,
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
# 和自身不同rolling的求比例
list_rolling_days_fm = ['nodiv', 5,10,20,60]
# 分母rolling计算函数
dic_calc_fm = {
    'max': f_calc_max,
    'min': f_calc_min,
    'avg': f_calc_avg,
    'med': f_calc_med,
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
# 主体函数，在预先准备好多个df的基础上
def generate_factor(df_ori,
                    factor_property,
                    df_filter,
                    rolling_day,
                    calc,
                    rolling_day_fm,
                    calc_fm
                    ):
    # 计算factor列
    df_f1 = dic_property[factor_property](df_ori)
    # 原始数据是否筛选
    df_f2 = dic_filter[df_filter](df_f1)
    # 纵向rolling
    if rolling_day > 1:
        df_f3 = df_f2['factor'].unstack().rolling(rolling_day,1).apply(dic_calc[calc]).stack().to_frame()
        df_f3.columns = ['factor']
    else:
        df_f3 = df_f2[['factor']]
    # 计算分母
    if rolling_day_fm != 'nodiv':
        df_fm = df_f2['factor'].unstack().rolling(rolling_day_fm,1).apply(dic_calc_fm[calc_fm]).stack()
        df_f4 = (df_f3['factor'] / df_fm.apply(lambda x : round_(x,5)).replace(0,np.nan)).to_frame()
        df_f4.columns = ['factor']
    else:
        df_f4 = df_f3.copy()
    res = pd.DataFrame(df_f4['factor'])
    return res

# 剔除已经算过的因子
list_del = []
for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor/neptune/h5/20250331_T_1_Factor_indicator/'):
    list_del.append(file_name.replace('.h5',''))
print('已计算{}个因子'.format(len(list_del)))
#预先准备好测试函数和基础数据
start_date = 20160101
end_date = 20191231
s = FactorData()
start_date = int(s.tradingday(str(start_date), -400)[0])
df_ori = IO.read_data([start_date, end_date],alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5')

for df_filter, rolling_day, factor_property, calc,\
    rolling_day_fm, calc_fm in \
        product(dic_filter, list_rolling_days, dic_property,dic_calc,
                list_rolling_days_fm, dic_calc_fm):
    if (rolling_day == 1) and (calc != 'max'): # 回溯1天，不需要calc
        continue
    if (rolling_day == 1) and (calc_fm in ['cv','cct','skew','kurt','m2m','pos']): # 回溯1天，不除以高维统计量
        continue
    if rolling_day_fm != 'nodiv' and rolling_day_fm <= rolling_day:
        continue
    if rolling_day_fm == 'nodiv' and calc_fm != 'max': # 不除以分母，不需要分母的运算
        continue
    factor_name = f'{factor_property}_{df_filter}_{rolling_day}_{calc}_{rolling_day_fm}_{calc_fm}'
    print(factor_name)
    if factor_name in list_del:
        continue
    def factor_func(start_date, end_date, IO, return_fillna_dic=False, df_ori = df_ori.copy()):
        if return_fillna_dic:
            # 返回因子为nan时的填充值
            return {factor_name: 0, 'data': ['MD']}
        res = generate_factor(df_ori,
                              factor_property, df_filter, rolling_day, calc, rolling_day_fm, calc_fm
                             )
        res.columns = [factor_name]
        # ---------------------------------------------------------------------------------------------------------------
        return res
    basic_file_path = '/data/group/800463/data/projectZZ_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5'
    factor_path = '/dfs/user/015585/01_factor_develop_store/fast_factor/neptune/h5/20250331_T_1_Factor_indicator/' # 因子保存路径
    factor_df0 = run_factor(func=factor_func,
                            factor_name=factor_name,
                            factor_type='T-1_factor',
                            start_date=start_date,
                            end_date=end_date,
                            basic_file_path=basic_file_path,
                            result_path=factor_path,
                            interval_res=False)
    df = pd.read_hdf(factor_path + factor_name + '.h5')
    result_path = '/dfs/user/015585/01_factor_develop_store/fast_factor/neptune/factor_report/20250331_T_1_Factor_indicator/'  # report保存路径
    factor_test = FactorTest(start_date, end_date, cal_mi=False)
    for col in df.columns:
        print(col)
        # print(time.localtime())
        factor_test.factor_test(df[[col]], result_path,
                                factor_corr_test=True, generate_pdf=False)
        check_score = factor_test.result_dic['check_score_res']
        print('总分:', check_score.loc['score', 'tot_score'])
        print('CORR:', factor_test.result_dic['corr_sta'].loc['corr_tot', 'value'])
