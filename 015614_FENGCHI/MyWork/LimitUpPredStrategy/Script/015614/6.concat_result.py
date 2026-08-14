# coding: utf-8
# Author：fengchi863
# Date ：2021/4/27 9:58

from LimitUpPredStrategy.conf.path_conf import bt_output_path
import pandas as pd, numpy as np

'''
拼接所有结果
可选全量结果：
all_bt_result_20210419191404.xlsx
all_strategy_board_bt_result_20210419165811.xlsx
compensate_board_bt_result_20210419165811.xlsx
dragon_board_bt_result_20210419165811.xlsx
low_board_bt_result_20210419165811.xlsx
virga2consis_board_bt_result_20210419165811.xlsx
'''

concat_xlsx_list = ['all_board_bt_result_20210419191404.xlsx', # 全量
                    'xgb_reg_trainPeriod60_predictPeriod10_factorNum80_signal_r2s1_bt_result.xlsx',
                    'xgb_reg_trainPeriod60_predictPeriod10_factorNum80_signal_r2s2_bt_result.xlsx',
                    ]

start_date = 20150407
end_date = 20191231

res_stats = pd.DataFrame()
res_curve = pd.DataFrame()
for xlsx_path in concat_xlsx_list:

    name = '_'.join(xlsx_path.split('_')[:2])

    tmp_res_stats = pd.Series()
    tmp_xlsx = pd.read_excel(bt_output_path + xlsx_path, sheet_name='统计结果')
    tmp_res_stats['胜率'] = tmp_xlsx.loc['胜率', '数值收益']
    tmp_res_stats['平均收益率'] = tmp_xlsx.loc['平均收益率', '数值收益']
    tmp_res_stats['盈亏比'] = tmp_xlsx.loc['盈亏比', '数值收益']

    tmp_res_curve = pd.DataFrame()
    tmp_xlsx = pd.read_excel(bt_output_path + xlsx_path, sheet_name='净值曲线')
    tmp_res_stats['日平均信号数'] = tmp_xlsx.loc[:, '日交易次数'].mean()
    tmp_res_stats['日平均胜率'] = tmp_xlsx.loc[:, '日胜率'].mean()
    tmp_res_curve[name] = tmp_xlsx['净盈利']

    # 拼接

