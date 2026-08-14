import os
from run_factor_demo_parallel_new import run_factor
from test_factor_demo import strongFactorTest
import pandas as pd
import numpy as np
from function_factor import *
from xquant.factordata import FactorData
import IO
from itertools import product
# 因子属性函数 function_t-1_factor

dic_property = {
                # 'generate':0,
                'high':f_pro_high,
                'open':f_pro_open,
                'low':f_pro_low,
                'close':f_pro_close,
                'highori':f_pro_highori,
                'openori':f_pro_openori,
                'lowori':f_pro_lowori,
                'closeori':f_pro_closeori,
                'vwapori':f_pro_vwapori,
                'pct':f_pro_pct,
                'pctturn':f_pro_pctturn,
                'abspctturn':f_pro_abspctturn,
                'abspct':f_pro_abspct,
                'logabspct':f_pro_logabspct,
                'amt':f_pro_amt,
                'turn':f_pro_turn,
                'vwap':f_pro_vwap,
                'syx1':f_pro_syx1,
                'syx2':f_pro_syx2,
                'xyx1':f_pro_xyx1,
                'xyx2':f_pro_xyx2,
                'syx2xyx1':f_pro_syx2xyx1,
                'syx2xyx2':f_pro_syx2xyx2,
                'lengthk':f_pro_lengthk,
                'c2v':f_pro_c2v,
                'h2v':f_pro_h2v,
                'l2v':f_pro_l2v,
                'amp':f_pro_amp,
                'corrv2c20':f_pro_corrv2c20,
                'corramt2c20':f_pro_corramt2c20,
                'corramt2syx20':f_pro_corramt2syx20,
                'corramt2xyx20':f_pro_corramt2xyx20,
                'corrpct2syx20':f_pro_corrpct2syx20,
                'corrpct2xyx20':f_pro_corrpct2xyx20
               }
# rolling范围
list_rolling_days = [1,5,10,20,60,120,240]
# list_rolling_days = [1,5]
# rolling时的筛选方式
dic_rolling_filter = {
                      'nofilter':f_roll_filter_nofilter,
                      # 'up1':f_roll_filter_up1,
                      # 'down1':f_roll_filter_down1,
                      # 'up2':f_roll_filter_up2,
                      # 'amtup201':f_roll_filter_amtup201,
                      # 'amtdown201':f_roll_filter_amtdown201,
                      # 'amtup202':f_roll_filter_amtup202
                     }
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
            'std': f_calc_std
           }
# 价格类指标是否成交量加权
list_price_pro = ['high','open','low','close','vwap',
                  'highori','openori','lowori','closeori','vwapori',
                  'pct','abspct','logabspct',
                  'syx1','syx2','xyx1','xyx2','syx2xyx1','syx2xyx2',
                  'c2v','h2v','l2v',
                  'amp','lengthk',
                  'generate'#生成式均为价格指标
                  ]
dic_amtstd = {
    'noamtstd':f_amtstd_no,
    'amtstd':f_amtstd_yes
              }# 如果需要，必须有指标2，指标2必须是amt
# ori系列最终要除以pre_close(除了偏度、峰度、集中度、cv)
list_ori = ['highori','lowori','openori','closeori','vwapori']
# 双变量组合:仅考虑除以rolling_days大于他的情况
# 价格类指标可以和成交量做div，其他只能和自身
list_division = list_rolling_days.copy()

# 生成核心函数
dic_getA = {
    # 'ABC_high':f_ABC_high,
    # 'ABC_low':f_ABC_low,
    # 'ABC_open':f_ABC_open,
    # 'ABC_close':f_ABC_close,
    # 'ABC_hl':f_ABC_hl,
    # 'ABC_oc':f_ABC_oc,
    # 'ABC_vwap':f_ABC_vwap,
    # 'ABC_pre':f_ABC_pre
}
dic_getB ={
    # 'ABC_0':f_ABC_0,
    # 'ABC_high':f_ABC_high,
    # 'ABC_low':f_ABC_low,
    # 'ABC_open':f_ABC_open,
    # 'ABC_close':f_ABC_close,
    # 'ABC_hl':f_ABC_hl,
    # 'ABC_oc':f_ABC_oc,
    # 'ABC_vwap': f_ABC_vwap,
    # 'ABC_pre': f_ABC_pre
}
dic_getC = {
    # 'ABC_high':f_ABC_high,
    # 'ABC_low':f_ABC_low,
    # 'ABC_open':f_ABC_open,
    # 'ABC_close':f_ABC_close,
    # 'ABC_hl':f_ABC_hl,
    # 'ABC_oc':f_ABC_oc,
    # 'ABC_vwap': f_ABC_vwap,
    # 'ABC_pre': f_ABC_pre
}
list_rolling_days_kernal = [0,5,20,60]
def generate_kernal_factor(df_ori,
                           A,rollingA,
                           B,rollingB,
                           C,rollingC):
    df_oriA = dic_getA[A](df_ori,col = 'A')
    if rollingA != 0:
        df_oriA['A'] = df_oriA['A'].unstack().rolling(rollingA).mean().stack()
    df_oriB = dic_getB[B](df_oriA,col = 'B')
    if rollingB != 0:
        df_oriB['B'] = df_oriB['B'].unstack().rolling(rollingB).mean().stack()
    df_oriC = dic_getC[C](df_oriB,col = 'C')
    if rollingC != 0:
        df_oriB['C'] = df_oriB['C'].unstack().rolling(rollingC).mean().stack()
    df_oriC['factor'] = (df_oriC['A'] - df_oriC['B']) / df_oriC['C']
    return df_oriC
# 主体函数，在预先准备好df_ori的基础上
def generate_factor(df_ori,
                    factor_property,
                    amtstd,
                    rolling_filter,
                    rolling_days,
                    calc,
                    is_generate=0,
                    A="", rollingA=0,
                    B="", rollingB=0,
                    C="", rollingC=0
                    ):
    # 计算因子属性
    if ('amt' not in dic_property) & (factor_property=='amt'):
        df_ori_f1 = f_pro_amt(df_ori.copy())
    else:
        if not is_generate:
            df_ori_f1 = dic_property[factor_property](df_ori.copy())
        else: #生成大法
            df_ori_f1 = generate_kernal_factor(df_ori.copy(),
                                               A, rollingA,
                                               B, rollingB,
                                               C, rollingC)
    # 是否价格类指标做amtstd
    df_ori_f1 = dic_amtstd[amtstd](df_ori_f1.copy())
    # 是否rolling时筛选
    df_ori_f2 = dic_rolling_filter[rolling_filter](df_ori_f1.copy())
    # rolling
    if rolling_days>1:
        df_ori_f3 = pd.DataFrame(df_ori_f2['factor'].unstack()\
            .rolling(rolling_days,1).apply(lambda x : dic_calc[calc](x)).stack())
        df_ori_f3.columns = ['factor']
    else:
        df_ori_f3 = df_ori_f2.copy()
    # 是否ori
    if factor_property in list_ori:
        df_ori_f3['factor'] = df_ori_f3['factor'].div(df_ori['pre_close'],axis=0)
    res = pd.DataFrame(df_ori_f3['factor'])
    return res
def generate_factor_adddivision(df_ori,
                                factor_property,
                                amtstd,
                                rolling_filter,
                                rolling_days,
                                calc,
                                division,
                                is_generate=0,
                                A="", rollingA=0,
                                B="", rollingB=0,
                                C="", rollingC=0
                                ):
    if division == 'nodiv':
        res = generate_factor(df_ori.copy(),
                              factor_property,
                              'noamtstd',
                              rolling_filter,
                              rolling_days,
                              calc,
                              is_generate,
                              A, rollingA,
                              B, rollingB,
                              C, rollingC
                              )
    elif division == 'amtdiv':
        res1 = generate_factor(df_ori.copy(),
                              factor_property,
                              'amtstd',
                              rolling_filter,
                              rolling_days,
                              calc,
                               is_generate,
                               A, rollingA,
                               B, rollingB,
                               C, rollingC
                               )
        res1.columns = ['factor1']
        res2 = generate_factor(df_ori.copy(),
                              'amt',
                              'noamtstd',
                              rolling_filter,
                              rolling_days,
                              calc,
                               is_generate,
                               A, rollingA,
                               B, rollingB,
                               C, rollingC
                               )
        res2.columns = ['factor2']
        res = pd.concat([res1,res2],axis=1)
        res = pd.DataFrame(res['factor1']/res['factor2'])
        res.columns = [factor_name]
        res[factor_name] = res[factor_name].apply(lambda x : 100000000000 if x > 100000000000\
                                                  else -100000000000 if x <-100000000000\
                                                  else x)
    else:
        res1 = generate_factor(df_ori.copy(),
                              factor_property,
                              'noamtstd',
                              rolling_filter,
                              rolling_days,
                              calc,
                               is_generate,
                               A, rollingA,
                               B, rollingB,
                               C, rollingC
                               )
        res1.columns = ['factor1']
        res2 = generate_factor(df_ori.copy(),
                              factor_property,
                              'noamtstd',
                              rolling_filter,
                              division,
                              calc,
                               is_generate,
                               A, rollingA,
                               B, rollingB,
                               C, rollingC
                               )
        res2.columns = ['factor2']
        res = pd.concat([res1,res2],axis=1)
        res = pd.DataFrame(res['factor1']/res['factor2'])
        res.columns = [factor_name]
        res[factor_name] = res[factor_name].apply(lambda x : 100000000000 if x > 100000000000\
                                                  else -100000000000 if x <-100000000000\
                                                  else x)
    return res
# 剔除已经算过的因子
list_del = []
for  i in list(os.listdir('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhmd_filter/')):
    list_del.append(i[:-3])
# for  i in list(os.listdir('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20231020T-1/')):
#     list_del.append(i[:-3])
# for  i in list(os.listdir('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20231124T-1/')):
#     list_del.append(i[:-3])
# for  i in list(os.listdir('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20241017T-1_combination/')):
#     list_del.append(i[:-3])
print('list_del:', len(list_del))
list_in = [
     # 'syx1_amtstd_nofilter_20_sum_amtdiv',
     # 'syx1_noamtstd_nofilter_5_avg_nodiv',
     # 'syx1_noamtstd_nofilter_1_max_nodiv',
     # 'closeori_noamtstd_nofilter_1_avg_5',
     # 'pctturn_noamtstd_nofilter_20_std_nodiv',
     # 'syx1_noamtstd_nofilter_20_avg_nodiv',
     # 'c2v_noamtstd_nofilter_5_min_nodiv',
     # 'pctturn_noamtstd_nofilter_10_min_nodiv',
     # 'amp_amtstd_nofilter_20_avg_amtdiv',
     # 'pctturn_noamtstd_nofilter_5_min_nodiv',
     # 'low_amtstd_nofilter_60_avg_amtdiv',
     # 'syx1_amtstd_nofilter_60_avg_amtdiv',
     # 'syx1_noamtstd_nofilter_10_max_nodiv',
     # 'low_noamtstd_nofilter_20_sum_nodiv',
     # 'c2v_noamtstd_nofilter_1_max_nodiv',
     # 'syx1_noamtstd_nofilter_20_max_nodiv',
     # 'syx2_amtstd_nofilter_5_max_amtdiv',
     # 'syx2_amtstd_nofilter_20_sum_amtdiv',
     # 'h2v_noamtstd_nofilter_20_std_nodiv',
     # 'h2v_noamtstd_nofilter_60_cct_nodiv',
     # 'amp_amtstd_nofilter_5_max_amtdiv',
     # 'h2v_amtstd_nofilter_5_sum_amtdiv',
     # 'close_noamtstd_nofilter_20_min_nodiv',
     # 'low_amtstd_nofilter_20_sum_amtdiv',
     # 'syx1_amtstd_nofilter_5_med_amtdiv',
     # 'close_noamtstd_nofilter_20_cv_nodiv',
     # 'syx1_noamtstd_nofilter_5_std_nodiv',
     # 'syx1_amtstd_nofilter_5_std_amtdiv',
     # 'logabspct_amtstd_nofilter_60_sum_amtdiv',
     # 'close_noamtstd_nofilter_1_max_60',
     # 'syx2_amtstd_nofilter_20_std_amtdiv',
     # 'low_noamtstd_nofilter_20_med_nodiv',
     # 'vwapori_noamtstd_nofilter_1_std_20',
     # 'abspctturn_noamtstd_nofilter_20_med_nodiv',
     # 'close_noamtstd_nofilter_1_max_nodiv',
     # 'c2v_amtstd_nofilter_5_sum_amtdiv',
     # 'c2v_noamtstd_nofilter_1_std_20',
     # 'low_noamtstd_nofilter_1_std_10',
     # 'low_noamtstd_nofilter_5_sum_nodiv',
     # 'pct_noamtstd_nofilter_10_min_nodiv',
     # 'amp_amtstd_nofilter_20_std_amtdiv',
     # 'h2v_amtstd_nofilter_20_std_amtdiv',
     # 'syx1_noamtstd_nofilter_10_med_nodiv',
     # 'c2v_noamtstd_nofilter_1_max_60',
     # 'syx2xyx2_noamtstd_nofilter_20_max_nodiv',
     # 'syx1_noamtstd_nofilter_60_max_nodiv',
     # 'pct_noamtstd_nofilter_5_min_nodiv',
     # 'logabspct_amtstd_nofilter_20_avg_amtdiv',
     # 'amp_noamtstd_nofilter_20_std_nodiv',
     # 'syx1_amtstd_nofilter_20_std_amtdiv',
     # 'turn_noamtstd_nofilter_5_min_nodiv',
     # 'syx1_noamtstd_nofilter_10_avg_60',
     # 'logabspct_amtstd_nofilter_20_med_amtdiv',
     # 'open_noamtstd_nofilter_20_min_nodiv',
     # 'lowori_noamtstd_nofilter_60_std_nodiv',
     # 'syx2xyx2_noamtstd_nofilter_20_std_nodiv',
     # 'l2v_amtstd_nofilter_60_sum_amtdiv',
     # 'h2v_noamtstd_nofilter_1_std_10',
     # 'l2v_noamtstd_nofilter_5_med_nodiv',
     # 'syx1_noamtstd_nofilter_5_avg_60',
     # 'lowori_noamtstd_nofilter_1_max_nodiv',
     # 'syx2xyx2_noamtstd_nofilter_5_max_nodiv',
     # 'turn_noamtstd_nofilter_1_max_nodiv',
     # 'highori_noamtstd_nofilter_5_max_nodiv',
     # 'syx2_noamtstd_nofilter_60_std_nodiv',
     # 'syx1_noamtstd_nofilter_60_change_nodiv',
     # 'pctturn_noamtstd_nofilter_60_min_nodiv',
     # 'l2v_noamtstd_nofilter_1_std_60',
     # 'h2v_amtstd_nofilter_60_std_amtdiv',
     # 'vwapori_noamtstd_nofilter_60_max_nodiv',
     # 'abspct_noamtstd_nofilter_60_sum_nodiv',
     # 'syx2_amtstd_nofilter_60_max_amtdiv',
     # 'h2v_noamtstd_nofilter_60_max_nodiv',
     # 'vwap_noamtstd_nofilter_5_std_nodiv',
     # 'vwap_noamtstd_nofilter_20_std_nodiv',
     # 'h2v_noamtstd_nofilter_60_avg_nodiv',
     # 'vwapori_noamtstd_nofilter_1_sum_10',
     # 'pctturn_noamtstd_nofilter_5_sum_nodiv',
     # 'l2v_noamtstd_nofilter_20_sum_nodiv',
     # 'low_noamtstd_nofilter_60_pos_nodiv',
     # 'lowori_noamtstd_nofilter_1_std_10',
     # 'low_noamtstd_nofilter_60_sum_nodiv',
     # 'low_noamtstd_nofilter_60_change_nodiv',
     # 'h2v_amtstd_nofilter_5_med_amtdiv',
     # 'highori_noamtstd_nofilter_20_max_nodiv',
     # 'low_noamtstd_nofilter_1_std_5',
     # 'high_noamtstd_nofilter_60_min_nodiv',
     # 'close_noamtstd_nofilter_5_avg_60',
     # 'syx1_amtstd_nofilter_60_std_amtdiv',
     # 'lowori_noamtstd_nofilter_1_std_5',
     # 'open_noamtstd_nofilter_60_cv_nodiv',
     # 'close_noamtstd_nofilter_1_std_10',
     # 'h2v_noamtstd_nofilter_1_std_5',
     # 'open_noamtstd_nofilter_1_std_10',
     # 'c2v_noamtstd_nofilter_5_cv_nodiv',
     # 'syx1_noamtstd_nofilter_20_change_nodiv',
     # 'openori_amtstd_nofilter_60_max_amtdiv',
     # 'highori_amtstd_nofilter_5_max_amtdiv',
     # 'highori_amtstd_nofilter_20_max_amtdiv',
     # 'pct_noamtstd_nofilter_5_std_nodiv',
     # 'vwap_noamtstd_nofilter_5_change_nodiv',
     # 'abspct_amtstd_nofilter_60_med_amtdiv',
     # 'close_noamtstd_nofilter_60_change_nodiv',
     # 'open_noamtstd_nofilter_60_min_nodiv',
     # 'syx2xyx2_amtstd_nofilter_20_std_amtdiv',
     # 'amp_amtstd_nofilter_60_std_amtdiv',
     # 'low_noamtstd_nofilter_5_avg_60',
     # 'pctturn_noamtstd_nofilter_20_change_nodiv',
     # 'abspct_noamtstd_nofilter_5_sum_nodiv',
     # 'close_noamtstd_nofilter_1_sum_60',
     # 'xyx2_noamtstd_nofilter_20_std_nodiv',
     # 'pct_amtstd_nofilter_5_std_amtdiv',
     # 'l2v_amtstd_nofilter_20_std_amtdiv',
     # 'h2v_noamtstd_nofilter_5_sum_60',
     # 'h2v_amtstd_nofilter_5_max_amtdiv',
     # 'close_noamtstd_nofilter_60_min_nodiv',
     # 'syx1_noamtstd_nofilter_5_med_60',
     # 'l2v_noamtstd_nofilter_20_min_nodiv',
     # 'amp_amtstd_nofilter_5_min_amtdiv',
     # 'abspctturn_noamtstd_nofilter_60_skew_nodiv',
     # 'h2v_amtstd_nofilter_20_max_amtdiv',
     # 'open_noamtstd_nofilter_5_min_nodiv',
     # 'lengthk_amtstd_nofilter_5_sum_amtdiv',
     # 'highori_noamtstd_nofilter_1_std_5',
     # 'close_noamtstd_nofilter_20_m2m_nodiv',
     # 'syx1_noamtstd_nofilter_60_sum_nodiv',
     # 'corrv2c20_noamtstd_nofilter_60_max_nodiv',
     # 'h2v_amtstd_nofilter_20_med_amtdiv',
     # 'pct_amtstd_nofilter_60_std_amtdiv',
     # 'lengthk_noamtstd_nofilter_5_med_nodiv',
     # 'xyx2_amtstd_nofilter_60_avg_amtdiv',
     # 'high_noamtstd_nofilter_1_std_10',
     # 'lengthk_noamtstd_nofilter_20_med_nodiv',
     # 'h2v_noamtstd_nofilter_5_avg_60',
     # 'open_noamtstd_nofilter_5_m2m_nodiv',
     # 'open_amtstd_nofilter_20_sum_amtdiv',
     # 'amp_noamtstd_nofilter_1_max_nodiv',
     # 'pct_amtstd_nofilter_20_std_amtdiv',
     # 'syx2xyx1_amtstd_nofilter_20_std_amtdiv',
     # 'low_noamtstd_nofilter_5_med_60',
     # 'syx2_noamtstd_nofilter_20_med_nodiv',
     # 'l2v_amtstd_nofilter_5_min_amtdiv',
     # 'l2v_noamtstd_nofilter_1_std_10',
     # 'l2v_amtstd_nofilter_20_med_amtdiv',
     # 'logabspct_noamtstd_nofilter_20_avg_nodiv',
     # 'pct_amtstd_nofilter_10_min_amtdiv',
     # 'abspct_noamtstd_nofilter_60_kurt_nodiv',
     # 'vwap_noamtstd_nofilter_60_m2m_nodiv',
     # 'c2v_noamtstd_nofilter_5_sum_60',
     # 'syx2xyx1_noamtstd_nofilter_20_change_nodiv',
     # 'low_noamtstd_nofilter_1_avg_20',
     # 'closeori_noamtstd_nofilter_20_change_nodiv',
     # 'close_noamtstd_nofilter_5_sum_60',
     # 'c2v_noamtstd_nofilter_1_sum_60',
     # 'logabspct_noamtstd_nofilter_1_max_nodiv',
     # 'low_amtstd_nofilter_20_med_amtdiv',
     # 'lengthk_noamtstd_nofilter_60_max_nodiv',
     # 'lengthk_noamtstd_nofilter_20_max_nodiv',
     # 'openori_noamtstd_nofilter_5_max_nodiv',
     # 'low_amtstd_nofilter_60_med_amtdiv',
     # 'close_noamtstd_nofilter_5_med_60',
     # 'abspctturn_noamtstd_nofilter_1_max_nodiv',
     # 'xyx1_amtstd_nofilter_20_std_amtdiv',
     # 'close_noamtstd_nofilter_5_sum_20',
     # 'syx2xyx1_noamtstd_nofilter_5_med_nodiv',
     # 'h2v_noamtstd_nofilter_60_sum_nodiv',
     # 'high_noamtstd_nofilter_1_std_5',
     # 'low_noamtstd_nofilter_60_kurt_nodiv',
     # 'l2v_amtstd_nofilter_60_med_amtdiv',
     # 'vwap_amtstd_nofilter_60_std_amtdiv',
     # 'xyx2_noamtstd_nofilter_60_std_nodiv',
     # 'low_noamtstd_nofilter_20_change_nodiv',
     # 'syx2xyx2_amtstd_nofilter_20_sum_amtdiv',
     # 'openori_noamtstd_nofilter_1_avg_5',
     # 'c2v_noamtstd_nofilter_5_med_60',
     # 'c2v_noamtstd_nofilter_5_sum_20',
     # 'syx2xyx1_noamtstd_nofilter_60_pos_nodiv',
     # 'lowori_noamtstd_nofilter_1_avg_60',
     # 'xyx1_noamtstd_nofilter_1_std_20',
     # 'h2v_noamtstd_nofilter_1_min_60',
     # 'low_noamtstd_nofilter_5_sum_60',
     # 'c2v_noamtstd_nofilter_20_max_nodiv',
     # 'highori_noamtstd_nofilter_5_avg_nodiv',
     # 'high_noamtstd_nofilter_60_avg_nodiv',
     # 'c2v_noamtstd_nofilter_60_change_nodiv',
     # 'open_noamtstd_nofilter_5_avg_nodiv',
     # 'logabspct_noamtstd_nofilter_60_cct_nodiv',
     # 'high_amtstd_nofilter_20_sum_amtdiv',
     # 'open_noamtstd_nofilter_1_med_20',
     # 'logabspct_noamtstd_nofilter_60_avg_nodiv',
     # 'highori_amtstd_nofilter_5_med_amtdiv',
     # 'low_noamtstd_nofilter_5_avg_20',
     # 'l2v_amtstd_nofilter_5_max_amtdiv',
     # 'amp_noamtstd_nofilter_5_sum_60',
     # 'high_noamtstd_nofilter_1_med_20',
     # 'xyx1_noamtstd_nofilter_5_change_nodiv',
     # 'lengthk_amtstd_nofilter_20_max_amtdiv',
     # 'c2v_noamtstd_nofilter_20_avg_nodiv',
     # 'amt_noamtstd_nofilter_5_sum_nodiv',
     'syx1_noamtstd_nofilter_5_std_60',
     'low_amtstd_nofilter_5_min_amtdiv',
     'c2v_noamtstd_nofilter_60_m2m_nodiv',
     'high_noamtstd_nofilter_60_skew_nodiv',
     'amp_noamtstd_nofilter_5_med_60',
     'h2v_amtstd_nofilter_60_max_amtdiv',
     'syx2_noamtstd_nofilter_5_sum_60',
     'amp_noamtstd_nofilter_60_skew_nodiv',
     'c2v_noamtstd_nofilter_5_cv_60',
     'open_noamtstd_nofilter_20_sum_nodiv',
     'l2v_amtstd_nofilter_5_avg_amtdiv',
     'syx2xyx2_noamtstd_nofilter_5_avg_nodiv',
     'c2v_noamtstd_nofilter_5_avg_10',
     'lengthk_noamtstd_nofilter_5_med_60',
     'xyx2_noamtstd_nofilter_60_cct_nodiv',
     'logabspct_amtstd_nofilter_20_max_amtdiv',
     'highori_amtstd_nofilter_20_sum_amtdiv',
     'c2v_noamtstd_nofilter_60_sum_nodiv',
     'high_amtstd_nofilter_20_std_amtdiv',
     'pctturn_noamtstd_nofilter_5_std_60',
     'closeori_noamtstd_nofilter_1_sum_60',
     'abspct_noamtstd_nofilter_20_kurt_nodiv',
     'syx1_noamtstd_nofilter_5_avg_10',
     'syx1_noamtstd_nofilter_5_change_nodiv',
]

# factor_done1 = pd.read_excel('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/res/20230922T-1.xlsx')
# list_in = list_in + list(factor_done1[(abs(factor_done1['IC']) >= 0.03) & (factor_done1['score'] >= 12) & (factor_done1['same_ratio'] <= 0.2)]['factor_name'])
# factor_done2 = pd.read_excel('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/res/20231020T-1.xlsx')
# list_in = list_in + list(factor_done2[(abs(factor_done2['IC']) >= 0.03) & (factor_done2['score'] >= 12) & (factor_done2['same_ratio'] <= 0.2)]['factor_name'])
# print('len_list_in = {}'.format(len(list_in)))
#预先准备好测试函数和基础数据
start_date = 20150930
end_date = 20250630
s = FactorData()
start_date = int(s.tradingday(str(start_date), -300)[0])
df_ori = IO.read_data([start_date, end_date],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
for rolling_filter in dic_rolling_filter:
    for rolling_days in list_rolling_days:
        for calc in dic_calc:
            for division in (['nodiv'] +
                             list(np.array(list_division)[np.array(list_division)> rolling_days]) +
                             ['amtdiv']):
                for factor_property in dic_property:
                    for amtstd in dic_amtstd:
                        if (rolling_days == 1) & \
                                (division == 'nodiv') & (calc != 'max'): # 回溯1天且非相除，不涉及calc
                            continue
                        if (division == 'amtdiv') & \
                                ((factor_property not in list_price_pro)
                                 | (calc in ['cv','m2m','skew','kurt','cct'])
                                 |(amtstd != 'amtstd')): # 非价格指标不允许amt加权
                            continue
                        if (amtstd == 'amtstd') & (division != 'amtdiv'):
                            continue
                        if (division == 'amtdiv') & (rolling_days == 1):
                            continue
                        is_generate = 1 if factor_property == 'generate' else 0
                        if is_generate:
                            for A, B, C, rollingA, rollingB, rollingC in product(dic_getA, dic_getB, dic_getC,
                                                                                 list_rolling_days_kernal,
                                                                                 list_rolling_days_kernal,
                                                                                 list_rolling_days_kernal):
                                if (A==B):
                                    continue
                                if (A=='ABC_0') & (B==C):
                                    continue
                                if (B=='ABC_0') & (A==C):
                                    continue
                                if ((A=='ABC_0') & (rollingA > 0)) | ((B=='ABC_0') & (rollingB > 0)):
                                    continue
                                factor_property = 'generate' + '_' + A + "_" + str(rollingA) + "_" + B + "_" + str(
                                    rollingB) + "_" + C + "_" + str(rollingC)
                                factor_name = factor_property + '_' \
                                              + amtstd + '_' \
                                              + rolling_filter + '_' \
                                              + str(rolling_days) + '_'\
                                              + calc + '_'\
                                              + str(division)
                                print(factor_name)
                                if factor_name in list_del:
                                    continue
                                def factor_func(start_date, end_date, IO, return_fillna_dic=False, df_ori = df_ori.copy()):
                                    if return_fillna_dic:
                                        # 返回因子为nan时的填充值
                                        return {factor_name: 0,'data':['MD']}
                                    res = generate_factor_adddivision(df_ori,
                                                                      factor_property,
                                                                      amtstd,
                                                                      rolling_filter,
                                                                      rolling_days,
                                                                      calc,
                                                                      division,
                                                                      is_generate,
                                                                      A, rollingA,
                                                                      B, rollingB,
                                                                      C, rollingC
                                                                      )
                                    res.columns = [factor_name]
                                    # ---------------------------------------------------------------------------------------------------------------
                                    return res
                                basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'
                                factor_path = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20241017T-1_combination/'
                                factor_df0 = run_factor(func = factor_func,
                                                        factor_name = factor_name,
                                                        factor_type = 'T-1_factor',
                                                        start_date = start_date,
                                                        end_date = end_date,
                                                        basic_file_path = basic_file_path,
                                                        result_path = factor_path,
                                                        interval_res=False)
                                df = pd.read_hdf(factor_path + factor_name + '.h5')
                                result_path = '/data/user/015585/01-因子挖掘/' \
                                              '03-Jupyter/因子快速开发/回测报告/20231124T-1/'
                                factor_test = strongFactorTest(start_date, end_date,cal_mi=None)
                                for col in df.columns:
                                    print(col)
                                    factor_test.factor_test(df[[col]], result_path,
                                                            factor_corr_test=True, generate_pdf=False)
                                    check_score = factor_test.result_dic['check_score_res']
                                    print('总分:',check_score.loc['score','tot_score'])
                                    print('CORR:',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])
                        else:
                            factor_name = factor_property + '_' \
                                          + amtstd + '_' \
                                          + rolling_filter + '_' \
                                          + str(rolling_days) + '_' \
                                          + calc + '_' \
                                          + str(division)
                            if factor_name in list_del:
                                continue
                            if factor_name not in list_in:
                                continue
                            print(factor_name)
                            def factor_func(start_date, end_date, IO, return_fillna_dic=False, df_ori=df_ori.copy()):
                                if return_fillna_dic:
                                    # 返回因子为nan时的填充值
                                    return {factor_name: 0, 'data': ['MD']}
                                res = generate_factor_adddivision(df_ori,
                                                                  factor_property,
                                                                  amtstd,
                                                                  rolling_filter,
                                                                  rolling_days,
                                                                  calc,
                                                                  division,
                                                                  is_generate,
                                                                  )
                                res.columns = [factor_name]
                                # ---------------------------------------------------------------------------------------------------------------
                                return res
                            # basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'
                            basic_file_path = '/data/user/015585/01-因子挖掘/20240624 run/file/basic_europa_20150930_20250710.h5'
                            factor_path = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhmd_filter/'
                            factor_df0 = run_factor(func=factor_func,
                                                    factor_name=factor_name,
                                                    factor_type='T-1_factor',
                                                    start_date=start_date,
                                                    end_date=end_date,
                                                    basic_file_path=basic_file_path,
                                                    result_path=factor_path,
                                                    interval_res=False)
                            # df = pd.read_hdf(factor_path + factor_name + '.h5')
                            # result_path = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/factor_report/20250530_zwhmd/'
                            # factor_test = strongFactorTest(start_date, end_date, cal_mi=None)
                            # for col in df.columns:
                            #     print(col)
                            #     factor_test.factor_test(df[[col]], result_path,
                            #                             factor_corr_test=False, generate_pdf=False)
                            #     check_score = factor_test.result_dic['check_score_res']
                            #     print('总分:', check_score.loc['score', 'tot_score'])
                            #     print('CORR:', factor_test.result_dic['corr_sta'].loc['corr_tot', 'value'])
