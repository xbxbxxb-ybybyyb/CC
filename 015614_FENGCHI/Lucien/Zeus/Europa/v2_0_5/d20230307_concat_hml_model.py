# coding: utf-8
# Author：fengchi863
# Date ：2023/3/7 11:07

import pandas as pd
from LucienUtil.FileUtil import FileUtil
PERIOD_LIST = ['period1', 'period2', 'period3']
SUB_VERSION = [[10, 11, 12], [20, 21, 22], [30, 31, 32]]

for model_name in ['LgbRegModelV2']:
    root_path = f'/data/user/015614/Zeus/pred/Europa/v2_0_5/{model_name}/'
    from Zeus.Europa.v2_0_5.path_conf import date_config
    for idx, PERIOD in enumerate(PERIOD_LIST):
        sub_versions = SUB_VERSION[idx]
        test_data = pd.DataFrame()
        date_dict = date_config[f'{PERIOD}']
        out_begin, out_end = date_dict['test_start_date'], date_dict['test_end_date']
        for sub_version in sub_versions:
            print(sub_version)
            test_fpath = root_path + f'{out_begin}~{out_end}_{model_name}_v{sub_version}.csv'
            tmp_test_data = pd.read_csv(test_fpath)
            test_data = test_data.append(tmp_test_data)

        test_data = test_data.set_index('Indexs')
        FileUtil.save_df2csv(test_data, root_path, f'{out_begin}~{out_end}_{model_name}_v{idx+1}_hml.csv')

        fit_data = pd.DataFrame()
        out_begin, out_end = date_dict['fit_start_date'], date_dict['fit_end_date']
        for sub_version in sub_versions:
            print(sub_version)
            fit_fpath = root_path + f'{out_begin}~{out_end}_{model_name}_v{sub_version}.csv'
            tmp_fit_data = pd.read_csv(fit_fpath)
            fit_data = fit_data.append(tmp_fit_data)

        fit_data = fit_data.set_index('Indexs')
        FileUtil.save_df2csv(fit_data, root_path, f'{out_begin}~{out_end}_{model_name}_v{idx+1}_hml.csv')