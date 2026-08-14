import os

import xfactor.runner.BasicRunner as Runner
from settings import RunMode
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
from fast_factor.code.neptune.ttickfull.function_factor import *
from itertools import product

dic_property = {
    'orderp2bp': f_pro_orderp2bp,
    'orderp2sp': f_pro_orderp2sp,
    'orderp2lp': f_pro_orderp2lp,
    'orderp2bp10': f_pro_orderp2bp10,
    'ordervol2bvol': f_pro_ordervol2bvol,
    'ordervol2svol': f_pro_ordervol2svol,
    'orderamt2bamt': f_pro_orderamt2bamt,
    'orderamt2samt': f_pro_orderamt2samt,
    'orderamt2bsamt': f_pro_orderamt2bsamt,
    'orderamt2trade': f_pro_orderamt2trade,
    'orderp2tradep': f_pro_orderp2tradep
               }
dic_time_kind = {
                 '930':f_t_kind_930,
                }
time_type = ['after']
dic_tick_kind1 = {'all':f_tick_kind1_all,}
dic_tick_kind2 = {
                  'all':f_tick_kind2_all,
                  'up100':f_tick_kind2_up100,
                  'down100':f_tick_kind2_down100}
dic_tick_kind3 = {
                   '0':f_tick_kind3_all,
                   }
dic_tick_kind4 = {
    'all':f_tick_kind4_all,
    'b1':f_tick_kind4_b1,
    'b2':f_tick_kind4_b2,
    'o1':f_tick_kind4_o1,
    'o2':f_tick_kind4_o2,
    'cb':f_tick_kind4_cb,
    'co':f_tick_kind4_co
}
dic_tick_kind5 = {
    'all':f_tick_kind5_all,
    'big':f_tick_kind5_big,
    'mid':f_tick_kind5_mid,
    'small':f_tick_kind5_small,
}
dic_tick_kind6 = {
    'all': f_tick_kind6_all,
    'upsell10': f_tick_kind6_upsell10,
    'downbuy10': f_tick_kind6_downbuy10,
    'up9': f_tick_kind6_up9,
    'up101':f_tick_kind6_up101,
    'down99':f_tick_kind6_down99,
}
tick_type3 = ['bigger','smaller']
dic_len_type = {
                 'all':f_len_all,
#                 'h500':f_len_h20,
#                 't500':f_len_t20,
#                   't100':f_len_t100,
#                't1min':f_len_t1min,
#                 'half1':f_len_half1,
#                 'half2':f_len_half2
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
               # 'compare_t',
               # 'compare_1',
               # 'compare_2',
               # 'compare_3',
               # 'compare_len_h2t',
               # 'compare_len_half12'
              ]
# 计算
list_del = []
for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250604_ttickfull/factor_value/neptune/'):
    list_del.append(file_name.replace('.h5',''))
for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250609_ttickfull/factor_value/neptune/'):
    list_del.append(file_name.replace('.h5',''))

# dic_done_factor = pd.read_pickle('/dfs/user/015585/01_factor_develop_store/fast_factor/saturn/done_factor/done_factor.pkl')
# for factor_done in list(dic_done_factor['20240308lastztlasttick']['name']):
#     list_del.append(factor_done)
print('已计算{}个因子'.format(len(list_del)))
list_series = [
    'orderp2bp',
    'orderp2sp',
    'orderp2lp',
    'orderp2bp10',
    'ordervol2bvol',
    'ordervol2svol',
    'orderamt2bamt',
    'orderamt2samt',
    'orderamt2bsamt',
    'orderamt2trade',
    'orderp2tradep',
                ] # series格式的factor
list_b930 = [
    'ratiob2',
    'b1',
    'pb1',
    'b22s22mv',
    'b12mv',
    'b1diff',
    'b1diff2mv',
    'b22s2diff',
    'b22s2diff2mv',
             ]
#
strategy = 'neptune'
for time_kind_i,time_type_i,\
        tick_kind1_i,tick_kind2_i,tick_kind3_i,tick_type3_i,\
        tick_kind4_i,tick_kind5_i,tick_kind6_i,\
        len_type_i,property_i,std_i\
        in product(dic_time_kind,time_type,
                   dic_tick_kind1,dic_tick_kind2,dic_tick_kind3,tick_type3,
                    dic_tick_kind4,dic_tick_kind5,dic_tick_kind6,
                   dic_len_type,dic_property,dic_std):
    list_class = []
    for calc_i in dic_calc:
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
#        if (time_type_i == 'after') & (len_type_i == 't500'):
#            continue#剔除在xx时间后的最后500单，此类会重复
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
        # if (tick_kind5_i=='all') & (tick_kind6_i=='all'):
        #     continue
        factor_name_final = time_kind_i + '_' + time_type_i + '_'\
                          + tick_kind1_i + '_' + tick_kind2_i + '_' + tick_kind3_i + '_' \
                          + tick_type3_i + '_' \
                          + tick_kind4_i + '_' \
                          + tick_kind5_i + '_' \
                          + tick_kind6_i + '_' \
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
    strategy_name = "neptune"
    factor_name = factor_name_final
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "test"  # 因子逻辑解释
    zcz_adjusted = "是"  # 是否针对注册制调整：是/否
    logic_type = "test"  # 逻辑类别
    low_cost = "是"  # 是否低耗时
        '''.format(factor_name_final)
        exec(generate_class_code)
        t_day_data = ['T1mTickfulladdorder']
        xdb_data = []
        exec('factor_{}.t_day_data = t_day_data'.format(factor_name_final))
        exec('factor_{}.xdb_data = xdb_data'.format(factor_name_final))
        def pre_calculate_T_N_data(self, database):
            if database["skip"] == True:
                database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                return database
            return database
        def prepare_T_data(self, database):
            if database["skip"] == True:
                return database
            else:
                tick_df = database['T1mTickfulladdorder']
                tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
                tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
                database['T1mTickfulladdorder'] = tick_df
                return database
        if calc_i == 'nocalc':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['nocalc'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'max':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['max'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'min':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['min'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'avg':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['avg'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'med':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['med'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'cv':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['cv'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'sum':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['sum'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'cct':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['cct'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'skew':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['skew'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'kurt':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['kurt'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'change':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['change'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'tail':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['tail'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'm2m':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['m2m'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        elif calc_i == 'std':
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['T1mTickfulladdorder']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](tick_df)
                    tick_df_t = get_f_t_filter(tick_df, time_type_i, t)
                    # 筛选amt
                    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
                    # 筛选up&down
                    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
                    # 筛选tick价格
                    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
                    if p > 0:
                        tick_df_t_3 = get_f_p_filter(tick_df_t_2, tick_type3_i, p)
                    else:
                        tick_df_t_3 = tick_df_t_2.copy()
                    # 筛选订单类型
                    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
                    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
                    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc['std'](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        else:
            print('calc_i不在枚举中')
            raise TypeError
        exec('factor_{}.pre_calculate_T_N_data = pre_calculate_T_N_data'.format(factor_name_final))
        exec('factor_{}.prepare_T_data = prepare_T_data'.format(factor_name_final))
        exec('factor_{}.calculate = calculate'.format(factor_name_final))
        exec('list_class.append(factor_{})'.format(factor_name_final))
    if len(list_class) > 0:
        res, check_res = Runner.run(start_date=20160101, end_date=20191231, strategy=strategy,
                         output_dir="/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250609_ttickfull/",
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


