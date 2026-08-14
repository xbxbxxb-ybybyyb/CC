import os

import xfactor.runner.BasicRunner as Runner
from settings import RunMode
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
from fast_factor.code.europa.ttrade.function_factor import *
from itertools import product
'''
1、时间：930全局，最后0.5分钟，最后1分钟，最后3分钟
2、长度：全部，最后50，100，300 非930全局不涉及长度
3、属性：固定为序列值
4、bsflag：
5、price：全部，9以上，9以下
6、大小单：全部，200000以上，50000以下，阈值为聚合后的结果
7、计算模式1：直接计算、分bsflag计算后相减（相除）、按长度分别计算后相减（相除）、按价格分别计算后相减（相除）
8、计算模式2：直接计算、按buy求和后计算、按sell求和后计算
'''
dic_property = {
    'amt': f_pro_amt,
    'amt2mv': f_pro_amt2mv,
    'vol': f_pro_vol,
    'pct': f_pro_pct,
    'vwappct': f_pro_vwappct,
    'buypctdiff': f_pro_buypctdiff,
    'amt2buypctdiff': f_pro_amt2buypctdiff,
               }
dic_time_kind = {
                 '930':f_t_kind_930,
                 '30s':f_t_kind_30s,
                 '1m':f_t_kind_1m,
                 '3m':f_t_kind_3m,
                }
dic_bs = {
    'allbs':f_bs_allbs,
    'buy':f_bs_buy,
    'sell':f_bs_sell,
    }
dic_price = {
    'allp':f_price_allp,
    'up9':f_price_up9,
    'down9':f_price_down9,
    }
dic_amt = {
    'allamt':f_amt_allamt,
    'big':f_amt_big,
    'small':f_amt_small,
}
dic_len_type = {
                 'all':f_len_all,
                 't50':f_len_t50,
                 't100':f_len_t100,
                 't300':f_len_t300,
               }
dic_calc_mode1 = {
    'alldf': f_mode1_alldf,
    'bsdf': f_mode1_bsdf,
    'lendf1': f_mode1_lendf1,
    'lendf2': f_mode1_lendf2,
    'pricedf1': f_mode1_pricedf1,
}
dic_calc_mode2 = {
    'calc': f_mode2_calc,
    'calcbuybs': f_mode2_calcbuybs,
    'gbuy': f_mode2_gbuy,
    'gsell': f_mode2_gsell,
}
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
            'tail':f_calc_tail,
            'm2m':f_calc_m2m,
            'std':f_calc_std,
            'length':f_calc_length,
           }
# 计算
list_del = []
# for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/europa/test_TTrade/factor_value/europa/'):
#     list_del.append(file_name.replace('.h5',''))
for file_name in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/europa/test_TTrade_filter/factor_value/europa/'):
    list_del.append(file_name.replace('.h5',''))
print('已计算{}个因子'.format(len(list_del)))

list_in = ['930_allbs_allp_allamt_t100_alldf_gbuy_amt2mv_avg_minus',
 '930_allbs_allp_small_all_alldf_calc_pct_skew_minus',
 '930_allbs_allp_big_all_alldf_calc_pct_avg_minus',
 '930_allbs_up9_allamt_all_alldf_gbuy_amt2mv_max_minus',
 '930_allbs_allp_allamt_t300_bsdf_calc_vwappct_cct_div',
 '930_allbs_up9_allamt_t100_alldf_gbuy_pct_max_minus',
 '930_allbs_up9_allamt_t100_alldf_gbuy_amt2buypctdiff_avg_minus',
 '930_allbs_allp_big_all_lendf1_calc_vwappct_std_minus',
 '930_allbs_allp_allamt_t300_alldf_gbuy_vwappct_tail_minus',
 '930_allbs_allp_big_all_alldf_calc_pct_skew_minus',
 '930_allbs_allp_allamt_t300_alldf_calcbuybs_pct_sum_minus',
 '930_allbs_allp_allamt_t300_bsdf_calc_amt2mv_sum_minus',
 '930_allbs_allp_big_all_lendf2_calc_vwappct_change_div',
 '930_allbs_allp_big_all_alldf_gsell_vwappct_max_minus',
 '930_allbs_allp_big_all_lendf2_gbuy_pct_cct_div',
 '930_allbs_allp_big_all_bsdf_gbuy_vwappct_change_minus',
 '930_allbs_allp_allamt_t100_alldf_gsell_pct_avg_minus',
 '930_allbs_allp_allamt_t300_bsdf_gbuy_vwappct_sum_minus',
 '930_allbs_up9_allamt_t100_alldf_gbuy_pct_sum_minus',
 '930_allbs_allp_small_all_alldf_gsell_vwappct_cct_minus',
 '930_allbs_allp_big_all_lendf2_calc_vwappct_cct_minus',
 '930_allbs_allp_small_all_alldf_gbuy_vwappct_tail_minus',
 '930_allbs_allp_allamt_t300_bsdf_gbuy_amt2buypctdiff_tail_minus',
 '930_allbs_allp_big_t100_alldf_calc_pct_cct_minus',
 '930_allbs_allp_small_all_alldf_gsell_pct_cv_minus',
 '930_allbs_allp_small_all_alldf_gsell_vwappct_tail_minus',
 '930_allbs_allp_allamt_t300_bsdf_calc_amt2buypctdiff_sum_minus',
 '930_allbs_allp_big_all_lendf1_calc_vwappct_tail_div',
 '930_allbs_allp_big_all_lendf1_calc_vwappct_avg_div',
 '930_allbs_allp_allamt_t300_alldf_gsell_vwappct_tail_minus',
 '930_allbs_allp_big_all_lendf1_calc_pct_cv_minus'] #
print('list_in:',len(list_in))

#
strategy = 'europa'
for time_kind_i, bs_i, price_i, amt_i, len_type_i, mode1, mode2, property \
        in product(dic_time_kind, dic_bs, dic_price, dic_amt, dic_len_type, dic_calc_mode1, dic_calc_mode2, dic_property):
    list_class = []
    for calc_i in dic_calc:
        for combo in ['div', 'minus']:
        # if (time_kind_i == '1000') & (time_type_i == 'after'):
        #     continue
            factor_name_final = '_'.join([time_kind_i, bs_i, price_i, amt_i, len_type_i, mode1, mode2, property, calc_i, combo])
            if factor_name_final not in list_in:
                continue
            if factor_name_final in list_del:
                print('已存在：', factor_name_final)
                continue
            if bs_i != 'allbs' and mode1 == 'bsdf':
                continue
            if len_type_i != 'all' and mode1 in ['lendf1','lendf2']:
                continue
            if mode1 == 'alldf' and combo == 'div': # 默认减法，只有bsdf lendf才有除法
                continue
            if price_i != 'allp' and mode1 in ['pricedf1']:
                continue
            if mode1 != 'alldf' and mode2 in ['calcbuybs']:
                continue
            if amt_i != 'allamt' and mode2 in ['calcbuybs']:
                continue
            if time_kind_i != '930' and len_type_i in ['t50,t100,t300']:
                continue
            if time_kind_i != '930' and mode1 in ['lendf2']:
                continue
            print(factor_name_final)
            generate_class_code = '''
class factor_{}(BaseFactor):
    strategy_name = "europa"
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
            t_day_data = ['TTransaction']
            xdb_data = []
            exec('factor_{}.t_day_data = t_day_data'.format(factor_name_final))
            exec('factor_{}.xdb_data = xdb_data'.format(factor_name_final))
            exec('factor_{}.calc_i = calc_i'.format(factor_name_final))
            exec('factor_{}.combo = combo'.format(factor_name_final))
            def pre_calculate_T_N_data(self, database):
                if database["skip"] == True:
                    database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
                    return database
                return database
            def prepare_T_data(self, database):
                if database["skip"] == True:
                    return database
                else:
                    trade_df = database['TTransaction']
                    trade_df = trade_df[trade_df['TradePrice'] > 0]
                    trade_df = filter_930(trade_df)
                    trade_df['TradeAmt'] = (trade_df['TradePrice'] * trade_df['TradeQty']).apply(lambda x : round_(x,5))
                    database['TTransaction'] = trade_df
                    return database

            def calculate(self, database):
                if database["skip"] == True:
                    return pd.Series({self.factor_name: np.nan})
                else:
                    trade_df = database['TTransaction']
                    # 筛选时间
                    t = dic_time_kind[time_kind_i](trade_df)
                    trade_df_t = get_f_t_filter(trade_df, t)
                    # 筛选长度
                    trade_df_len = dic_len_type[len_type_i](trade_df_t)
                    # 筛选bs，price，amt
                    trade_df_bs = dic_bs[bs_i](trade_df_len)
                    trade_df_price = dic_price[price_i](trade_df_bs)
                    trade_df_amt = dic_amt[amt_i](trade_df_price)
                    # 计算属性
                    trade_df_pro = dic_property[property](trade_df_amt)
                    # 模式1
                    trade_df_list_mode1 = dic_calc_mode1[mode1](trade_df_pro)
                    # 模式2
                    trade_df_list_mode2 = dic_calc_mode2[mode2](trade_df_list_mode1)
                    # 算子运用
                    if len(trade_df_list_mode2) == 1:
                        res = dic_calc[self.calc_i](trade_df_list_mode2[0]['factor'])
                    else:
                        res1 = dic_calc[self.calc_i](trade_df_list_mode2[0]['factor'])
                        res2 = dic_calc[self.calc_i](trade_df_list_mode2[1]['factor'])
                        if self.combo == 'minus':
                            res = res1 - res2
                        elif self.combo == 'div':
                            res = res1 / res2 if abs(res2) > 1e-8 else np.nan
                        else:
                            res = np.nan
                    factor_dict = {self.factor_name: res}
                    return pd.Series(factor_dict)

            exec('factor_{}.pre_calculate_T_N_data = pre_calculate_T_N_data'.format(factor_name_final))
            exec('factor_{}.prepare_T_data = prepare_T_data'.format(factor_name_final))
            exec('factor_{}.calculate = calculate'.format(factor_name_final))
            exec('list_class.append(factor_{})'.format(factor_name_final))
    if len(list_class) > 0:
        res, check_res = Runner.run(start_date=20170101, end_date=20250630, strategy=strategy,
                         output_dir="/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/europa/test_TTrade_filter/",
                         options={
                             "calc.num_cpus": 28,
                             "local_evaluator": "",
                             'precheck': False,
                             "factor_test": False,
                             'report':False,
                             'mode': RunMode.research},class_list_out=list_class)
        for factor_class in list_class:
            i = factor_class.factor_name
            print(i)
            # print('score:', check_res[i + '_' + strategy]['check_score_res'].loc['score','tot_score'])
            # print('IC:',check_res[i + '_' + strategy]['corr_sta'].loc['corr_tot', 'value'])


