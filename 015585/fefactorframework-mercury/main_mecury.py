import xfactor.runner.BasicRunner as Runner
from settings import RunMode
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
from xfactor.function_factor import *
from itertools import product

dic_property = {
                'rcleanb':f_pro_rcleanb,
               }
dic_time_kind = {
                 '930':f_t_kind_930,
                }
time_type = ['before']
dic_tick_kind1 = {'all':f_tick_kind1_all,}
dic_tick_kind2 = {'all':f_tick_kind2_all,}
dic_tick_kind3 = {
                   '0':f_tick_kind3_all,
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
               # 'compare_t',
               # 'compare_1',
               # 'compare_2',
               # 'compare_3',
               # 'compare_len_h2t',
               # 'compare_len_half12'
              ]
# 计算
list_del = []
# dic_done_factor = pd.read_pickle('/dfs/user/015585/01_factor_develop_store/fast_factor/saturn/done_factor/done_factor.pkl')
# for factor_done in list(dic_done_factor['20240308lastztlasttick']['name']):
#     list_del.append(factor_done)
# print('已计算{}个因子'.format(len(list_del)))
list_series = [
                ] # series格式的factor
list_b930 = ['ratiob2',
            'b1',
            'pb1',
            't',]
#
strategy = 'mercury'
for time_kind_i,time_type_i,\
        tick_kind1_i,tick_kind2_i,tick_kind3_i,tick_type3_i,\
        len_type_i,property_i,std_i\
        in product(dic_time_kind,time_type,
                   dic_tick_kind1,dic_tick_kind2,dic_tick_kind3,tick_type3,
                   dic_len_type,dic_property,dic_std):
    list_class = []
    list_factor = []
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
        factor_name_final = time_kind_i + '_' + time_type_i + '_'\
                      + tick_kind1_i + '_' + tick_kind2_i + '_' + tick_kind3_i + '_' + tick_type3_i + '_' \
                      + len_type_i + '_' + property_i + '_' + std_i + '_' + calc_i
        if factor_name_final in list_del:
            # print(factor_name)
            continue
        class factor_qyh_fastfactor(BaseFactor):
            strategy_name = "mercury"
            factor_name = "qyh_fastfactor"
            factor_name_new = factor_name_final
            fill_na_value = 0
            need_pre_calculate_T_N = False
            owner = "qyh"  # 开发人员姓名
            factor_explain = "test"  # 因子逻辑解释
            zcz_adjusted = "是"  # 是否针对注册制调整：是/否
            logic_type = "test"  # 逻辑类别
            low_cost = "是"  # 是否低耗时
            #
            t_day_data = ['TTickab919']
            xdb_data = []
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                return database
            def prepare_T_data(self, database):
                if database["skip"] == True:
                    return database
                else:
                    return database
            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    tick_df = database['TTickab919']
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
                    # 筛选长度
                    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_3)
                    # 因子属性
                    factor_origin = dic_property[property_i](tick_df_t_len)
                    # rlength,尝试标准化
                    if (property_i == 'rlength'):
                        factor_origin = dic_std[std_i](tick_df, factor_origin)
                    # 计算最终结果
                    if type(factor_origin) == pd.Series:
                        res = dic_calc[calc_i](factor_origin)
                    else:
                        res = factor_origin
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)
        list_class.append(factor_qyh_fastfactor)
        list_factor.append(factor_qyh_fastfactor.factor_name_new)
    res, check_res = Runner.run(start_date=20160101, end_date=20201231, strategy=strategy,
                     output_dir="/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/mecury_20240522_919tick/",
                     options={
                         "calc.num_cpus": 2,
                         "local_evaluator": "",
                         'precheck': False,
                         "factor_test": True,
                         'report':False,
                         'mode': RunMode.research},class_list_out=list_class)
    for i in list_factor:
        print(i)
        print('score:', check_res[i[7:] + '_' + strategy].result_dic['check_score_res'].loc['score','tot_score'])
        print('IC:',check_res[i[7:] + '_' + strategy].result_dic['corr_sta'].loc['corr_tot', 'value'])


