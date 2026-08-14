# coding: utf-8
# Author：fengchi863
# Date ：2023/4/24 13:36

"""
为了不重新进行训练，减少耗时，直接使用test中的参与率确定阈值，然后纳入fit中
这里要同时修改保存在model中的threshold文件！！！
"""
import pandas as pd

from Zeus.Europa.v4_0_64.path_conf import date_config
period_list = ['period1', 'period2', 'period3', 'period4']

attend_ratio = 45

for period in period_list:
    date_dict = date_config[period]
    pred_type = 'test'
    out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']
    test_out_begin, test_out_end = date_dict[f'test_start_date'], date_dict[f'test_end_date']

