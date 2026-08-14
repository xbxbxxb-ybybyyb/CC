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
    # 'bjg': f_pro_bjg,
    # 'bjg2amt': f_pro_bjg2amt,
    # 'bjg2mv': f_pro_bjg2mv,
    # 'bjgratio': f_pro_bjgratio,
    # 'bjgdhratio': f_pro_bjgdhratio,
    # 'bshratio': f_pro_bshratio,
    # 'sjg': f_pro_sjg,
    # 'sjgratio': f_pro_sjgratio,
    # 'sjgdhratio': f_pro_sjgdhratio,
    # 'sshratio': f_pro_sshratio,
    # 'tradescount': f_pro_tradescount,
    # 'btradesjg': f_pro_btradesjg,
    # 'btradesjgratio': f_pro_btradesjgratio,
    # 'btradesjgdhratio': f_pro_btradesjgdhratio,
    # 'btradesshratio': f_pro_btradesshratio,
    # 'stradesjg': f_pro_stradesjg,
    # 'stradesjgratio': f_pro_stradesjgratio,
    # 'stradesjgdhratio': f_pro_stradesjgdhratio,
    # 'stradesshratio': f_pro_stradesshratio,
    # 'valuesh': f_pro_valuesh,
    # 'valuesh2amt': f_pro_valuesh2amt,
    # 'valuesh2mv': f_pro_valuesh2mv,
    # 'valueshact': f_pro_valueshact,
    # 'valueshact2amt': f_pro_valueshact2amt,
    # 'valueshact2mv': f_pro_valueshact2mv,
    # 'valuejg': f_pro_valuejg,
    # 'valuejg2amt': f_pro_valuejg2amt,
    # 'valuejg2mv': f_pro_valuejg2mv,
    # 'valuejgact': f_pro_valuejgact,
    # 'valuejgact2amt': f_pro_valuejgact2amt,
    # 'valuejgact2mv': f_pro_valuejgact2mv,
    # 'valuesh2jg': f_pro_valuesh2jg,
    # 'valuekplr': f_pro_valuekplr,
    # 'valuekplr2mv': f_pro_valuekplr2mv,
    # 'valuekplr2amt': f_pro_valuekplr2amt,
    # 'ratiokplr': f_pro_ratiokplr,
    # 'zjlxraio': f_pro_zjlxraio,
    # 'ddjlrraio': f_pro_ddjlrraio,
    # 'bjgact': f_pro_bjgact,
    # 'bjgact2amt': f_pro_bjgact2amt,
    # 'bjgact2mv': f_pro_bjgact2mv,
    # 'bjgactratio': f_pro_bjgactratio,
    # 'bjgactdhratio': f_pro_bjgactdhratio,
    # 'bshactratio': f_pro_bshactratio,
    # 'sjgact': f_pro_sjgact,
    'sjgactratio': f_pro_sjgactratio,
    'sjgactdhratio': f_pro_sjgactdhratio,
    'sshactratio': f_pro_sshactratio,
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
            # 'med':f_calc_med,
            'cv':f_calc_cv,
            'sum':f_calc_sum,
            'cct':f_calc_cct,
            'skew':f_calc_skew,
            'kurt':f_calc_kurt,
            # 'change':f_calc_change,
            'm2m':f_calc_m2m,
            'pos':f_calc_pos,
            'std': f_calc_std
           }
# 价格类指标是否成交量加权
list_price_pro = [
                  ]
dic_amtstd = {
    'noamtstd':f_amtstd_no,
    # 'amtstd':f_amtstd_yes
              }# 如果需要，必须有指标2，指标2必须是amt
# ori系列最终要除以pre_close(除了偏度、峰度、集中度、cv)
list_ori = ['highori','lowori','openori','closeori','vwapori']
# 双变量组合:仅考虑除以rolling_days大于他的情况
# 价格类指标可以和成交量做div，其他只能和自身
list_division = list_rolling_days.copy()

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
    df_ori_f1 = dic_property[factor_property](df_ori.copy())
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
for  i in list(os.listdir('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhmd_zjlx/')):
    list_del.append(i[:-3])
print('list_del:', len(list_del))
list_in = [
]

# factor_done1 = pd.read_excel('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/res/20230922T-1.xlsx')
# list_in = list_in + list(factor_done1[(abs(factor_done1['IC']) >= 0.03) & (factor_done1['score'] >= 12) & (factor_done1['same_ratio'] <= 0.2)]['factor_name'])
# factor_done2 = pd.read_excel('/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/res/20231020T-1.xlsx')
# list_in = list_in + list(factor_done2[(abs(factor_done2['IC']) >= 0.03) & (factor_done2['score'] >= 12) & (factor_done2['same_ratio'] <= 0.2)]['factor_name'])
# print('len_list_in = {}'.format(len(list_in)))
#预先准备好测试函数和基础数据
start_date = 20160101
end_date = 20191231
s = FactorData()
start_date = int(s.tradingday(str(start_date), -300)[0])
df_ori = IO.read_data([start_date, end_date],
                      alt='/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')
df_md = IO.read_data([start_date, end_date], columns=['amt','mkt_cap_ard'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
df_ori['amt'] = df_md['amt']
df_ori['mkt_cap_ard'] = df_md['mkt_cap_ard']
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
                        if division != 'nodiv': # 简化
                            continue
                        is_generate = 1 if factor_property == 'generate' else 0

                        factor_name = factor_property + '_' \
                                      + amtstd + '_' \
                                      + rolling_filter + '_' \
                                      + str(rolling_days) + '_' \
                                      + calc + '_' \
                                      + str(division)
                        if factor_name in list_del:
                            continue
                        # if factor_name not in list_in:
                        #     continue
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
                        basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'
                        # basic_file_path = '/data/user/015585/01-因子挖掘/20240624 run/file/basic_europa_20150930_20250710.h5'
                        factor_path = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhmd_zjlx/'
                        factor_df0 = run_factor(func=factor_func,
                                                factor_name=factor_name,
                                                factor_type='T-1_factor',
                                                start_date=start_date,
                                                end_date=end_date,
                                                basic_file_path=basic_file_path,
                                                result_path=factor_path,
                                                interval_res=False)
                        df = pd.read_hdf(factor_path + factor_name + '.h5')
                        result_path = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/factor_report/20250530_zwhmd_zjlx/'
                        factor_test = strongFactorTest(start_date, end_date, cal_mi=None)
                        for col in df.columns:
                            print(col)
                            factor_test.factor_test(df[[col]], result_path,
                                                    factor_corr_test=False, generate_pdf=False)
                            check_score = factor_test.result_dic['check_score_res']
                            print('总分:', check_score.loc['score', 'tot_score'])
                        #     print('CORR:', factor_test.result_dic['corr_sta'].loc['corr_tot', 'value'])
