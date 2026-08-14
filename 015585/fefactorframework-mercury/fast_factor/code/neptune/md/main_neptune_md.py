import os

import xfactor.runner.BasicRunner as Runner
from settings import RunMode
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
from fast_factor.code.neptune.md.function_factor_md import *
from itertools import product
dic_property = {
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
                'corrpct2xyx20':f_pro_corrpct2xyx20,
                'pctnew1':f_pro_pctnew1,
                'pctnew2':f_pro_pctnew2,
                'o2a':f_pro_o2a,
                'c2a':f_pro_c2a,
                'pre2vol':f_pro_pre2vol
               }
# rolling范围
list_rolling_days = [1,5,10,20,60]
# list_rolling_days = [1,5]
# rolling时的筛选方式
dic_rolling_filter = {
                      'nofilter':f_roll_filter_nofilter,
                      'up1':f_roll_filter_up1,
                      'down1':f_roll_filter_down1,
                      'up2':f_roll_filter_up2,
                      'amtup201':f_roll_filter_amtup201,
                      'amtdown201':f_roll_filter_amtdown201,
                      'amtup202':f_roll_filter_amtup202
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
            'std':f_calc_std
           }
# 价格类指标是否成交量加权
list_price_pro = ['high','open','low','close','vwap',
                  'highori','openori','lowori','closeori','vwapori',
                  'pct','abspct','logabspct',
                  'syx1','syx2','xyx1','xyx2','syx2xyx1','syx2xyx2',
                  'c2v','h2v','l2v',
                  'amp','lengthk','pctnew1','pctnew2'
                  'generate'#生成式均为价格指标
                  ]
dic_amtstd = {
    'noamtstd':f_amtstd_no,
    'amtstd':f_amtstd_yes
              }# 如果需要，必须有指标2，指标2必须是amt
# ori系列最终要除以pre_close(除了偏度、峰度、集中度、cv)
list_ori = ['highori','lowori','openori','closeori','vwapori']
# 价格类指标可以和成交量做div，其他只能和自身
list_division = list_rolling_days.copy()
# 计算
list_del = []
# for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20241206tcancel/factor_value/neptune'):
#     list_del.append(file_name.replace('.h5',''))
print('已计算{}个因子'.format(len(list_del)))
list_series = ['amt','t','index','price','price1'] # series格式的factor
list_b930 = []
#
strategy = 'neptune'

for rolling_filter, rolling_days, division, factor_property, amtstd in \
    product(dic_rolling_filter, list_rolling_days,
            (['nodiv'] + list_division + ['amtdiv']), dic_property, dic_amtstd
                             ):
    list_class = []
    for calc_i in dic_calc:
        if (rolling_days == 1) & \
                (division == 'nodiv') & (calc_i != 'max'):  # 回溯1天且非相除，不涉及calc
            continue
        if (division == 'amtdiv') & \
                ((factor_property not in list_price_pro)
                 | (calc_i in ['cv', 'm2m', 'skew', 'kurt', 'cct'])
                 | (amtstd != 'amtstd')):  # 非价格指标不允许amt加权
            continue
        if (amtstd == 'amtstd') & (division != 'amtdiv'):
            continue
        if (division == 'amtdiv') & (rolling_days == 1):
            continue
        factor_name_final = factor_property + '_' \
                                          + amtstd + '_' \
                                          + rolling_filter + '_' \
                                          + str(rolling_days) + '_' \
                                          + calc_i + '_' \
                                          + str(division)
        if factor_name_final in list_del:
            print(factor_name_final)
            continue
        print(factor_name_final)
        generate_class_code = '''
class factor_{}(BaseFactor):
    strategy_name = "neptune"
    factor_name = factor_name_final
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "test"  # 因子逻辑解释
    zcz_adjusted = "是"  # 是否针对注册制调整：是/否
    logic_type = "test"  # 逻辑类别
    low_cost = "是"  # 是否低耗时
        '''.format(factor_name_final)
        exec(generate_class_code)
        t_day_data = []
        xdb_data = []
        t_1_factor_data = [
            {'name': 'MD_CHINA_STOCK_DAILY_WIND',
             'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
             'lag': 80,
             'column': ['adjfactor', 'amt', 'close', 'free_float_shares', 'high', 'low',
                       'mkt_cap_ard', 'open', 'pct_chg', 'pre_close', 'total_shares', 'turn',
                       'volume', 'vwap']
             }]
        t_1_factor_data_types = ['MD']  # T-1的h5文件类型列表
        exec('factor_{}.t_day_data = t_day_data'.format(factor_name_final))
        exec('factor_{}.xdb_data = xdb_data'.format(factor_name_final))
        exec('factor_{}.t_1_factor_data = t_1_factor_data'.format(factor_name_final))
        exec('factor_{}.t_1_factor_data_types = t_1_factor_data_types'.format(factor_name_final))
        if calc_i == 'max':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    df_ori = database['MD_CHINA_STOCK_DAILY_WIND']
                    df_ori_f1 = dic_property[factor_property](df_ori.copy())
                    df_ori_f2 = dic_rolling_filter[rolling_filter](df_ori_f1.copy())
                    # rolling
                    if rolling_days > 1:
                        df_ori_f3 = pd.DataFrame(df_ori_f2['factor'].unstack() \
                                                 .rolling(rolling_days, 1).apply(lambda x: dic_calc['max'](x)).stack())
                        df_ori_f3.columns = ['factor']
                    else:
                        df_ori_f3 = df_ori_f2.copy()
                    # 是否ori
                    if (factor_property in list_ori) & ('max' not in ['skew', 'kurt', 'cv', 'std', 'm2m', 'cct']):
                        df_ori_f3['factor'] = df_ori_f3['factor'].div(df_ori['pre_close'], axis=0)
                    res = pd.DataFrame(df_ori_f3['factor'])
                    res.columns = [self.factor_name]
                    database['pre_T_N'] = res
                return database
        raise
        else:
            # print('calc_i不在枚举中')
            # raise TypeError
            continue
        def prepare_T_data(self, database):
            if database["skip"] == True:
                return database
            else:
                return database
        def calculate(self, database):
            if database["skip"] == True:
                return pd.Series({self.factor_name: np.nan})
            else:
                df_ori = database['pre_T_N']
                return df_ori  # 纯h5文件的T-1_Factor直接返回df

        exec('factor_{}.pre_calculate_T_N_data = pre_calculate_T_N_data'.format(factor_name_final))
        exec('factor_{}.prepare_T_data = prepare_T_data'.format(factor_name_final))
        exec('factor_{}.calculate = calculate'.format(factor_name_final))
        exec('list_class.append(factor_{})'.format(factor_name_final))
    if len(list_class) > 0:
        res, check_res = Runner.run(start_date=20160101, end_date=20191231, strategy=strategy,
                         output_dir="/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250317_md/",
                         options={
                             "calc.num_cpus": 24,
                             "local_evaluator": "",
                             'precheck': False,
                             "factor_test": True,
                             'report':False,
                             'mode': RunMode.research},class_list_out=list_class)
        for factor_class in list_class:
            i = factor_class.factor_name
            print(i)
#            print('score:', check_res[i + '_' + strategy].result_dic['check_score_res'].loc['score','tot_score'])
#            print('IC:',check_res[i + '_' + strategy].result_dic['corr_sta'].loc['corr_tot', 'value'])


