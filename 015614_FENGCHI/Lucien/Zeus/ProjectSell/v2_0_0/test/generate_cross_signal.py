# coding: utf-8
# Author：fengchi863
# Date ：2023/9/21 18:50

import pandas as pd
from Zeus.ProjectSell.v2_0_0.config.strat_conf import DATE_CONFIG
import os

period = 'period1'
model_name_list = ['fsv8_s1_Xgb', 'fsrs_s1_Xgb', 'rffs_s1_Xgb', 'fsv11_s1_Xgb', 'fsv10_s1_Xgb', 'fsci_s1_Xgb']
for period in ['period1', 'period2']:
    for pred_type in ['test', 'fit']:
        date_dict = DATE_CONFIG[period]

        out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']
        valid_path_list = [f'/data/user/015614/Zeus/pred/ProjectSell/v2_0_0/config1/{x}/{out_begin}~{out_end}.csv' for x in model_name_list]

        for idx, valid_path in enumerate(valid_path_list):
            signal = pd.read_csv(valid_path, index_col=0)
            all_valid_signal = pd.read_csv(valid_path_list[idx], index_col=0)
            cross_signal = all_valid_signal.loc[list(set(signal.index).intersection(set(all_valid_signal.index)))]
            os.makedirs('/data/user/015614/Zeus/pred/ProjectSell/v2_0_0/config1/' + f'{valid_path.split("/")[-2]}Cross/', exist_ok=True)
            cross_signal.to_csv('/data/user/015614/Zeus/pred/ProjectSell/v2_0_0/config1/' + f'{valid_path.split("/")[-2]}Cross/' + os.path.basename(valid_path))