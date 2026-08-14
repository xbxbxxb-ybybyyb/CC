import os

import xfactor.runner.BasicRunner as Runner
from settings import RunMode
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
from fast_factor.code.neptune.finance.function_factor_xdb_finance import *
from itertools import product

dic_property = {
    'amt': f_pro_amt,
               }
dic_season = {
    'cum':f_t_kind_cum, # 累计值，直接取原始值
    # 'single':f_t_kind_single, # 单季度值，先全部变为单季度值
    # 'ratiocum':f_t_kind_ratiocum, # 累计值同比
    # 'ratiosingle':f_t_kind_ratiosingle, # 单季度同比
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
# 计算
list_del = []
# for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/saturn/20250206xdb_cancel/factor_value/saturn/'):
#     list_del.append(file_name.replace('.h5',''))
print('已计算{}个因子'.format(len(list_del)))
#
strategy = 'neptune'
for
        in product(dic_time_kind,time_type,
                   dic_cancel_kind1,dic_cancel_kind2,dic_cancel_kind3,cancel_type3,
                   dic_len_type,dic_property,dic_std):
    list_class = []
    for calc_i in dic_calc:
        if (cancel_kind3_i == '0') & (cancel_type3_i == 'smaller'):
            continue  # 剔除“小于全部价格”的因子
        factor_name_final = time_kind_i + '_' + time_type_i + '_'\
                          + cancel_kind1_i + '_' + cancel_kind2_i + '_' + cancel_kind3_i + '_' \
                          + cancel_type3_i + '_' \
                          + len_type_i + '_' \
                          + property_i + '_' \
                          + std_i + '_' \
                          + calc_i
        if factor_name_final in list_del:
            # print(factor_name_final)
            continue
        print(factor_name_final)
        generate_class_code = '''
class factor_{}(BaseFactor):
    strategy_name = "saturn"
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
        xdb_data = [
            {
       'name': 'xdb_cancel', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 1 # 回看日期，N为往前回看1~N天
            }
        ]
        exec('factor_{}.t_day_data = t_day_data'.format(factor_name_final))
        exec('factor_{}.xdb_data = xdb_data'.format(factor_name_final))
        if calc_i == 'nocalc':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['nocalc'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'max':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['max'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'min':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['min'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'avg':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['avg'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'med':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['med'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'cv':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['cv'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'sum':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['sum'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'cct':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['cct'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'skew':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['skew'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'kurt':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['kurt'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'change':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['change'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'tail':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['tail'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'm2m':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['m2m'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        elif calc_i == 'std':
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                else:
                    cancel_df = database['xdb_cancel']
                    cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                        lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](cancel_df)
                    cancel_df_t = get_f_t_filter(cancel_df, time_type_i, t)
                    # 筛选买卖单
                    cancel_df_t_1 = dic_cancel_kind1[cancel_kind1_i](cancel_df_t)
                    # 筛选大小单
                    cancel_df_t_2 = dic_cancel_kind2[cancel_kind2_i](cancel_df_t_1)
                    # 筛选cancel价格
                    p = dic_cancel_kind3[cancel_kind3_i](cancel_df_t)
                    if p > 0:
                        cancel_df_t_3 = get_f_p_filter(cancel_df_t_2, cancel_type3_i, p)
                    else:
                        cancel_df_t_3 = cancel_df_t_2.copy()
                    # 筛选长度
                    cancel_df_t_len = dic_len_type[len_type_i](cancel_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](cancel_df_t_len)
                    # 如果是amt,尝试标准化
                    if (property_i == 'amt'):
                        factor_origin = dic_std[std_i](cancel_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['std'](factor_origin)
                    else:
                        res = factor_origin
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
                    return database
        else:
            print('calc_i不在枚举中')
            raise TypeError
        def prepare_T_data(self, database):
            if database["skip"] == True:
                return database
            else:
                return database
        def calculate(self, database):
            if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
                return pd.Series({self.factor_name: np.nan})
            else:
                res1 = database['pre_T_N'][self.factor_name].values[0]
                factor_dict = {self.factor_name: res1}
                return pd.Series(factor_dict)
        exec('factor_{}.pre_calculate_T_N_data = pre_calculate_T_N_data'.format(factor_name_final))
        exec('factor_{}.prepare_T_data = prepare_T_data'.format(factor_name_final))
        exec('factor_{}.calculate = calculate'.format(factor_name_final))
        exec('list_class.append(factor_{})'.format(factor_name_final))
    if len(list_class) > 0:
        res, check_res = Runner.run(start_date=20170101, end_date=20191231, strategy=strategy,
                         output_dir="/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/saturn/20250210xdb_cancel/",
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
            print('score:', check_res[i + '_' + strategy].result_dic['check_score_res'].loc['score','tot_score'])
            print('IC:',check_res[i + '_' + strategy].result_dic['corr_sta'].loc['corr_tot', 'value'])


