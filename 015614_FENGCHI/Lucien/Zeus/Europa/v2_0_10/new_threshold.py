# coding: utf-8
# Author：fengchi863
# Date ：2023/7/11 14:15

import pandas as pd
from Zeus.Europa.v2_0_10.path_conf import date_config

root_path = '/data/user/015614/Zeus/pred/Europa/v2_0_10/LgbRegModel/'

for PERIOD in ['period1', 'period2', 'period3']:
    SUB_VERSION = f'v{PERIOD[-1]}'
    date_dict = date_config[f'{PERIOD}']
    test_out_begin, test_out_end = date_dict[f'test_start_date'], date_dict[f'test_end_date']
    fit_out_begin, fit_out_end = date_dict[f'fit_start_date'], date_dict[f'fit_end_date']

    test_df = pd.read_csv(root_path + f'{test_out_begin}~{test_out_end}_LgbRegModel_{SUB_VERSION}.csv')
    fit_df = pd.read_csv(root_path + f'{fit_out_begin}~{fit_out_end}_LgbRegModel_{SUB_VERSION}.csv')

    threshold = test_df['pred_Reg'].quantile(0.6)
    test_df['prediction'] = test_df['pred_Reg'] >= threshold
    fit_df['prediction'] = fit_df['pred_Reg'] >= threshold

    test_df.to_csv(root_path + f'{test_out_begin}~{test_out_end}_LgbRegModel_{SUB_VERSION}.csv')
    fit_df.to_csv(root_path + f'{fit_out_begin}~{fit_out_end}_LgbRegModel_{SUB_VERSION}.csv')



