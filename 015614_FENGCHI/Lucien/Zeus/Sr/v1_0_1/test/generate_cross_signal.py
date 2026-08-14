# coding: utf-8
# Author：fengchi863
# Date ：2023/9/21 18:50

import pandas as pd
from Zeus.Sr.v1_0_1.config.strat_conf import DATE_CONFIG
import os

period = 'period1'
sel_model_names = ['fsrs_pct_XgbRegModel', 'fsrs_pct_LgbRegModel']
sel_all_model_names = ['fsrs_pct_AllXgbRegModel', 'fsrs_pct_AllLgbRegModel']
for period in ['period1', 'period2', 'period3']:
    for pred_type in ['test', 'fit']:
        date_dict = DATE_CONFIG[period]

        out_begin, out_end = date_dict[f'{pred_type}_start_date'], date_dict[f'{pred_type}_end_date']
        valid_path_list = [f'/data/user/015614/Zeus/pred/Sr/v1_0_1/{x}/{out_begin}~{out_end}.csv' for x in sel_model_names]
        all_valid_path_list = [f'/data/user/015614/Zeus/pred/Sr/v1_0_1/{x}/{out_begin}~{out_end}.csv' for x in sel_all_model_names]

        for idx, valid_path in enumerate(valid_path_list):
            signal = pd.read_csv(valid_path, index_col=0)
            all_valid_signal = pd.read_csv(all_valid_path_list[idx], index_col=0)
            cross_signal = all_valid_signal.loc[list(set(signal.index).intersection(set(all_valid_signal.index)))]
            cross_signal.to_csv('/data/user/015614/Zeus/pred/Sr/v1_0_1/' + f'{valid_path.split("/")[-2]}Cross/' + os.path.basename(valid_path))