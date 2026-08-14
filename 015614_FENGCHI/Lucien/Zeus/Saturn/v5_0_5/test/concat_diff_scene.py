# coding: utf-8
# Author：fengchi863
# Date ：2024/9/12 13:51

import importlib
import os
import pandas as pd
from Zeus.Saturn.v5_0_5.config.strat_conf import *

fs_version = ['fsv8', 'fsv10', 'fsv11', 'fsrs', 'fsci']
config_flag1 = 'config4'
config_flag2 = 'config6'

period = 'period5'
module_name = f'Zeus.Saturn.v5_0_5.config.path_conf'
module = importlib.import_module(module_name)

test_start_date, test_end_date = DATE_CONFIG[period]['test_start_date'], DATE_CONFIG[period]['test_end_date']
fit_start_date, fit_end_date = DATE_CONFIG[period]['fit_start_date'], DATE_CONFIG[period]['fit_end_date']

for factor_select in fs_version:
    for model in list(sorted(os.listdir(f'/data/user/015614/Zeus/pred/Saturn/v5_0_5/{config_flag1}/'))):
        signal1 = pd.read_csv(f'/data/user/015614/Zeus/pred/Saturn/v5_0_5/{config_flag1}/{model}/{test_start_date}~{test_end_date}.csv', index_col=0) # no2_industry
        signal2 = pd.read_csv(f'/data/user/015614/Zeus/pred/Saturn/v5_0_5/{config_flag2}/{model}/{test_start_date}~{test_end_date}.csv', index_col=0)
        signal1_index = signal1.index.tolist()
        signal2_index = signal2.index.tolist()
        cross_index = list(set(signal1_index).intersection(signal2.index))
        signal = pd.concat([signal1.loc[list(set(signal1_index).difference(cross_index))], signal2])
        signal = signal.sort_index()
        os.makedirs(f'/data/user/015614/Zeus/pred/Saturn/v5_0_5/config{config_flag1[-1]}{config_flag2[-1]}/{model}/', exist_ok=True)
        signal.to_csv(f'/data/user/015614/Zeus/pred/Saturn/v5_0_5/config{config_flag1[-1]}{config_flag2[-1]}/{model}/{test_start_date}~{test_end_date}.csv')

        signal1 = pd.read_csv(f'/data/user/015614/Zeus/pred/Saturn/v5_0_5/{config_flag1}/{model}/{fit_start_date}~{fit_end_date}.csv', index_col=0) # no2_industry
        signal2 = pd.read_csv(f'/data/user/015614/Zeus/pred/Saturn/v5_0_5/{config_flag2}/{model}/{fit_start_date}~{fit_end_date}.csv', index_col=0)
        signal1_index = signal1.index.tolist()
        signal2_index = signal2.index.tolist()
        cross_index = list(set(signal1_index).intersection(signal2.index))
        signal = pd.concat([signal1.loc[list(set(signal1_index).difference(cross_index))], signal2])
        signal = signal.sort_index()
        os.makedirs(f'/data/user/015614/Zeus/pred/Saturn/v5_0_5/config{config_flag1[-1]}{config_flag2[-1]}/{model}/', exist_ok=True)
        signal.to_csv(f'/data/user/015614/Zeus/pred/Saturn/v5_0_5/config{config_flag1[-1]}{config_flag2[-1]}/{model}/{fit_start_date}~{fit_end_date}.csv')
