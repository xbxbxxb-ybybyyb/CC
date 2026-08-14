import os

import xfactor.runner.BasicRunner as Runner
from settings import RunMode
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
from fast_factor.code.neptune.t1mtickab.function_factor_t1mtickab import *
from itertools import product

dic_property = {
    'rcleanb': f_pro_rcleanb,
    'cleanb2ttran': f_pro_cleanb2ttran,
    'cleanb2tran': f_pro_cleanb2tran,
    'b2tran': f_pro_b2tran,
    'b2ttran': f_pro_b2ttran,
    'b2transtd': f_pro_b2transtd,
    's2tran': f_pro_s2tran,
    's2ttran': f_pro_s2ttran,
    's2transtd': f_pro_s2transtd,
    'amt': f_pro_amt,
    'corrb2b1': f_pro_corrb2b1,
    'corrpv': f_pro_corrpv,
    'corrb12s1': f_pro_corrb12s1,
    'corrb2s': f_pro_corrb2s,
    'corrb2t': f_pro_corrb2t,
    'corrbp2bv': f_pro_corrbp2bv,
    'corrbp2t': f_pro_corrbp2t,
    'corrb2tp': f_pro_corrb2tp,
    'abspchange': f_pro_abspchange,
    'bp': f_pro_bp,
    'sp': f_pro_sp,
    'b12b': f_pro_b12b,
    's12s': f_pro_s12s,
    'b12s1': f_pro_b12s1,
    'b2s': f_pro_b2s,
     'tran2b': f_pro_tran2b,
     'vwap2p': f_pro_vwap2p,
     'syx1': f_pro_syx1,
     'xyx1': f_pro_xyx1,
     'tpmin': f_pro_tpmin,
     'tvwap2pmin': f_pro_tvwap2pmin,
     'ratiob': f_pro_ratiob,
     'ratiob2': f_pro_ratiob2,
     'diffb12tran': f_pro_diffb12tran,
     'b1': f_pro_b1,
     'pb1': f_pro_pb1,
     'b': f_pro_b,
     'ratiob1thans1': f_pro_ratiob1thans1,
     'amt2newamt': f_pro_amt2newamt,
     'pv': f_pro_pv,
     'pricev': f_pro_pricev,
     't': f_pro_t,
     'bdiff': f_pro_bdiff,
     'sdiff': f_pro_sdiff,
     'pdiff': f_pro_pdiff,
     'hp': f_pro_hp,
     'lpcummax': f_pro_lpcummax,
     'b1delb': f_pro_b1delb,
     'hlmid': f_pro_hlmid,
     'hlmid2lp': f_pro_hlmid2lp,
     'numtradesdiff': f_pro_numtradesdiff,
     'pa': f_pro_pa,
     'bias5': f_pro_bias5,
     'pctturn': f_pro_pctturn
               }
dic_time_kind = {
                 '930':f_t_kind_930,
                }
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
                'h15':f_len_h15,
                't15':f_len_t15,
                'half1':f_len_half1,
                'half2':f_len_half2
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
for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250806_t1mtickab/factor_value/neptune/'):
    list_del.append(file_name.replace('.h5',''))
print('已计算{}个因子'.format(len(list_del)))
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
strategy = 'neptune'
for time_kind_i,time_type_i,\
        tick_kind1_i,tick_kind2_i,tick_kind3_i,tick_type3_i,\
        len_type_i,property_i\
        in product(dic_time_kind,time_type,
                   dic_tick_kind1,dic_tick_kind2,dic_tick_kind3,tick_type3,
                   dic_len_type,dic_property):
    list_class = []
    for calc_i in dic_calc:
        if (time_kind_i == '1000') & (time_type_i == 'after'):
            continue
        if (time_kind_i == '1430') & (time_type_i == 'before'):
            continue
        if (time_kind_i == '930') & (time_type_i == 'before'): # 不考虑930之前
            continue
        if (tick_kind3_i == '0') & (tick_type3_i == 'smaller'):
            continue#剔除“小于全部价格”的因子
        if (tick_kind3_i == 'p25') & (tick_type3_i == 'bigger'):
            continue
        if (tick_kind3_i == 'p75') & (tick_type3_i == 'smaller'):
            continue
        if (time_type_i == 'before') & (len_type_i == 'h15'):
            continue#剔除在xx时间前的最初，此类会重复
        if (time_type_i == 'after') & (len_type_i == 't15'):
            continue#剔除在xx时间后的最后，此类会重复
        if (time_type_i == 'before') & (time_kind_i == '930') & (property_i not in list_b930):
            continue
        if (property_i not in list_series) & (calc_i != 'nocalc'):
            continue #目前只有series可以使用calc
        if (property_i in list_series) & (calc_i == 'nocalc'):
            continue #series，必须calc
        factor_name_final = time_kind_i + '_' + time_type_i + '_'\
                      + tick_kind1_i + '_' + tick_kind2_i + '_' + tick_kind3_i + '_' + tick_type3_i + '_' \
                      + len_type_i + '_' + property_i + '_' + calc_i
        if factor_name_final in list_del:
            print(factor_name_final)
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
        t_day_data = ['T1mTickab']
        xdb_data = []
        exec('factor_{}.t_day_data = t_day_data'.format(factor_name_final))
        exec('factor_{}.xdb_data = xdb_data'.format(factor_name_final))
        exec('factor_{}.calc_i = calc_i'.format(factor_name_final))
        def pre_calculate_T_N_data(self, database):
            if database["skip"] == True:
                return database
            else:
                return database
        def prepare_T_data(self, database):
            if database["skip"] == True:
                return database
            else:
                return database
        def calculate(self, database):
            if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
                return pd.Series({self.factor_name: np.nan})
            else:
                tick1m_df = database['T1mTickab']
                tick1m_df['MDTime_delta'] = tick1m_df['MDTime'].apply(
                    lambda x: get_time_delta(x) - 1800000)  # 距离930毫秒数
                # 新增tick成交额、成交量列
                tick1m_df['ValueTrade'] = tick1m_df['TotalValueTrade'] - tick1m_df['TotalValueTrade'].shift(1).fillna(0)
                tick1m_df['VolumeTrade'] = tick1m_df['TotalVolumeTrade'] - tick1m_df['TotalVolumeTrade'].shift(1).fillna(0)
                # 筛选时间
                t = dic_time_kind[time_kind_i](tick1m_df)
                tick1m_df_t = get_f_t_filter(tick1m_df, time_type_i, t)
                # 筛选amt
                tick1m_df_t_1 = dic_tick_kind1[tick_kind1_i](tick1m_df_t)
                # 筛选up&down
                tick1m_df_t_2 = dic_tick_kind2[tick_kind2_i](tick1m_df_t_1)
                # 筛选tick价格
                p = dic_tick_kind3[tick_kind3_i](tick1m_df_t)  # 注意是用筛选过时间的tick
                if p > 0:
                    tick1m_df_t_3 = get_f_p_filter(tick1m_df_t_2, tick_type3_i, p)
                else:
                    tick1m_df_t_3 = tick1m_df_t_2.copy()
                # 筛选长度
                tick1m_df_t_len = dic_len_type[len_type_i](tick1m_df_t_3)
                # 因子属性
                factor_origin = dic_property[property_i](tick1m_df_t_len)
                # 计算最终结果
                if type(factor_origin) == pd.Series:
                    res = dic_calc[self.calc_i](factor_origin)
                else:
                    res = factor_origin
                factor_dict = {self.factor_name: res}
                return pd.Series(factor_dict)
        exec('factor_{}.pre_calculate_T_N_data = pre_calculate_T_N_data'.format(factor_name_final))
        exec('factor_{}.prepare_T_data = prepare_T_data'.format(factor_name_final))
        exec('factor_{}.calculate = calculate'.format(factor_name_final))
        exec('list_class.append(factor_{})'.format(factor_name_final))
    if len(list_class) > 0:
        res, check_res = Runner.run(start_date=20170110, end_date=20201231, strategy=strategy,
                         output_dir="/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/neptune/20250820_t1mtickab/",
                         options={
                             "calc.num_cpus": 30,
                             "local_evaluator": "",
                             'precheck': False,
                             "factor_test": True,
                             'report':False,
                             'mode': RunMode.research},class_list_out=list_class)
        for factor_class in list_class:
            i = factor_class.factor_name
            print(i)
            # print('score:', check_res[i + '_' + strategy].result_dic['check_score_res'].loc['score','tot_score'])
            # print('IC:',check_res[i + '_' + strategy].result_dic['corr_sta'].loc['corr_tot', 'value'])

