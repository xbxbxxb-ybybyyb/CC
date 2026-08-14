import os
from run_factor_demo_parallel_im import run_factor
from future_factor_test import FactorTest
import pandas as pd
import numpy as np
from function_factor_ttick30s import *
from itertools import product
# 参数设置
dic_property = {
                'rcleanb':f_pro_rcleanb,

               }
dic_time_kind = {
                 '930':f_t_kind_930,
                }
# time_type = ['before','after']
time_type = ['after']
dic_tick_kind1 = {'all':f_tick_kind1_all,
                   'amt25':f_tick_kind1_25,
                   'amt75':f_tick_kind1_75}# amt
dic_tick_kind2 = {'all':f_tick_kind2_all,
                   'up':f_tick_kind2_up,
                   'down':f_tick_kind2_down}# up&down
dic_tick_kind3 = {
                   '0':f_tick_kind3_all,
                   'p25':f_tick_kind3_25,
                   'p75':f_tick_kind3_75
                   }# 价格单
tick_type3 = ['bigger','smaller']
dic_len_type = {'all':f_len_all,
                'h500':f_len_h20,
                't500':f_len_t20,
                'half1':f_len_half1,
                'half2':f_len_half2
               }
dic_std = {'nostd':f_std_nostd,
           '2length':f_std_2length,
          }
dic_calc = {'nocalc':f_calc_nocalc,
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
            'tail':f_calc_tail,
            'm2m':f_calc_m2m,
            'std':f_calc_std
           }
dic_compare = [
               'nocompare',
              ]

# 计算
list_del = []
dic_done_factor = pd.read_pickle('/dfs/user/015585/01_factor_develop_store/fast_factor/saturnnext/done_factor/done_factor.pkl')
for factor_done in list(dic_done_factor['20230712talltick']['name']):
    list_del.append(factor_done)
list_series = ['rcleanb',
                'cleanb2ttran',
                'cleanb2tran',
                'b2tran',
                'b2ttran',
                'b2transtd',
                's2tran',
                's2ttran',
                's2transtd',
                'amt',
                'abspchange',
                'bp',
                'sp',
                'b12b',
                's12s',
                'b12s1',
                'b2s',
                'tran2b',
                'vwap2p',
                'ratiob',
                'ratiob2',
                'diffb12tran',
                'b1',
                'pb1',
                'b',
                'ratiob1thans1',
                'amt2newamt',
                'pv',
                't',
               'syx1',
               'xyx1',
               'bdiff',
               'pdiff',
               'sdiff',
               'hp',
               'lpcummax',
               'h2l',
               'h2l2',
               'b1delb',
               'hlmid2lp',
               'hlmid',
               'numtradesdiff',
               'pa',
               'bias5',
               'pctturn'
                ] # series格式的factor
list_b930 = []
#
for time_kind_i,time_type_i,\
        tick_kind1_i,tick_kind2_i,tick_kind3_i,tick_type3_i,\
        len_type_i,property_i,std_i,calc_i,compare_i\
        in product(dic_time_kind,time_type,
                   dic_tick_kind1,dic_tick_kind2,dic_tick_kind3,tick_type3,
                   dic_len_type,dic_property,dic_std,dic_calc,dic_compare):
        if (time_kind_i == '1000') & (time_type_i == 'after'):
            continue
        if (time_kind_i == '1430') & (time_type_i == 'before'):
            continue
        if (tick_kind3_i == '0') & (tick_type3_i == 'smaller'):
            continue#剔除“小于全部价格”的因子
        if (tick_kind3_i == 'p25') & (tick_type3_i == 'bigger'):
            continue
        if (tick_kind3_i == 'p75') & (tick_type3_i == 'smaller'):
            continue
        if (time_type_i == 'before') & (len_type_i == 'h500'):
            continue#剔除在xx时间前的最初500单，此类会重复
        if (time_type_i == 'after') & (len_type_i == 't500'):
            continue#剔除在xx时间后的最后500单，此类会重复
        if (len_type_i != 'all') & (property_i == 'rlength'):
            continue
        if (time_type_i == 'before') & (time_kind_i == '930') & (property_i not in list_b930):
            continue
        if (len_type_i == 'h500') & (property_i == 'avg'):
            continue
        if (property_i != 'rlength') & (std_i != 'nostd'):
            continue#非标准化因子，不需要标准化
        if (property_i not in list_series) & (calc_i != 'nocalc'):
            continue#目前只有series可以使用calc
        if (property_i in list_series) & (calc_i == 'nocalc'):
            continue#series，必须calc
        if (compare_i != 'nocompare') & \
           ((compare_i != 'compare_t') | (time_type_i != 'before')) & \
           ((compare_i != 'compare_1') | (tick_kind1_i != 'all')) &\
           ((compare_i != 'compare_2') | (tick_kind2_i != 'all')) &\
           ((compare_i != 'compare_3') | (tick_kind3_i == '0') | (tick_type3_i != 'bigger')) &\
           ((compare_i != 'compare_len_h2t') | (len_type_i != 'h500')) &\
           ((compare_i != 'compare_len_half12') | (len_type_i != 'half1')):
            continue
        factor_name = time_kind_i + '_' + time_type_i + '_'\
                      + tick_kind1_i + '_' + tick_kind2_i + '_' + tick_kind3_i + '_' + tick_type3_i + '_' \
                      + len_type_i + '_' + property_i + '_' + std_i + '_' + calc_i + '_'+ compare_i
        if factor_name in list_del:
            print(factor_name)
            continue
        def factor_func(tick_df, return_fillna_dic=False):
            if return_fillna_dic:
                # 返回因子为nan时的填充值
                return {factor_name: 0}
            value = generate_factor_addcompare(tick_df,
                                               property_i,time_kind_i,time_type_i,tick_kind1_i,tick_kind2_i,tick_kind3_i,tick_type3_i,
                                               len_type_i,std_i,calc_i,compare_i,
                                               dic_time_kind,dic_tick_kind1,dic_tick_kind2,dic_tick_kind3,dic_len_type,dic_property,dic_std,dic_calc
                                               )
            factor_dict = {factor_name: value}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
        print(factor_name)
        start_date, end_date = 20220801, 20250430
        factor_path = '/dfs/user/015585/01_factor_develop_store/fast_factor/future/h5' \
                      + '/20250527ttickab30s/' # 因子保存路径
        run_factor(func=factor_func,
                   factor_name=factor_name,
                   factor_type='TTickab30s',
                   start_date=start_date,
                   end_date=end_date,
                   basic_file_path='/dfs/user/015585/00_股指期货策略/Basic_future_20220801_20250430.h5',
                   result_path=factor_path)

        df = pd.read_hdf(factor_path + factor_name + '_20160101_20191231.h5')
        result_path = '/dfs/user/015585/01_factor_develop_store/fast_factor/future/factor_report' \
                      + '/20250527ttickab30s/' # report保存路径
        factor_test = FactorTest(start_date, end_date, cal_mi=False)
        for col in df.columns:
            print(col)
            factor_test.factor_test(df[[col]], result_path, factor_corr_test=False, generate_pdf=False)
            check_score = factor_test.result_dic['check_score_res']
            print('总分:',check_score.loc['score','tot_score'])
            print('CORR:',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])