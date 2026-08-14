# coding: utf-8
# Author：fengchi863
# Date ：2023/1/14 17:33

import pandas as pd
from LucienUtil.FileUtil import FileUtil
PERIOD_LIST = ['period1', 'period2', 'period3']
# SUB_VERSION = [[10, 11, 12], [20, 21, 22], [30, 31, 32]]
SUB_VERSION = [1, 2, 3]

# for model_name in ['XgbRegModel', 'LgbRegModel']:
#     root_path = f'/data/user/015614/Zeus/pred/Europa/v1_0_31/{model_name}/xbc_rolling/'
#     from Zeus.Europa.v1_0_31.path_conf import xbc_rolling_config as date_config
#     for idx, PERIOD in enumerate(PERIOD_LIST):
#         sub_versions = SUB_VERSION[idx]
#         test_data = pd.DataFrame()
#         pred_type = 'test'  # test fit
#         date_dict = date_config[f'{PERIOD}_{pred_type}']
#         out_begin, out_end = date_dict['train_start_date'], date_dict['train_end_date']
#         for sub_version in sub_versions:
#             print(sub_version)
#             test_fpath = root_path + f'{out_begin}~{out_end}_{model_name}_v{sub_version}.csv'
#             tmp_test_data = pd.read_csv(test_fpath)
#             test_data = test_data.append(tmp_test_data)
#
#         test_data = test_data.set_index('Indexs')
#         FileUtil.save_df2csv(test_data, root_path, f'{out_begin}~{out_end}_{model_name}_v{idx+1}_hml.csv')

"""拼接所有v1 v2 v3"""
# for model_name in ['XgbRegModel', 'LgbRegModel', 'LrRegModel']:
#     root_path = f'/data/group/800463/fengc/for_xbc/20230113_europa_ensemble/{model_name}/'
#     from Zeus.Europa.v1_0_31.path_conf import xbc_rolling_config as date_config
#
#     for idx, PERIOD in enumerate(PERIOD_LIST):
#         pred_data = pd.DataFrame()
#         pred_type = 'test'  # test fit
#         date_dict = date_config[f'{PERIOD}_{pred_type}']
#         out_begin, out_end = date_dict['train_start_date'], date_dict['train_end_date']
#         final_end = date_config[f'{PERIOD}_fit']['test_end_date']
#         import os
#
#         sub_version = SUB_VERSION[idx]
#         for tmp_path in os.listdir(root_path):
#             if f'v{sub_version}' in tmp_path:
#                 pred_fpath = root_path + tmp_path
#                 tmp_begin = int(tmp_path.split('~')[0])
#                 tmp_end = int(tmp_path.split('~')[1][:8])
#                 tmp_test_data = pd.read_csv(pred_fpath, index_col=0)
#                 tmp_test_data = tmp_test_data.query('datelist >= @tmp_begin & datelist <= @tmp_end')
#                 pred_data = pred_data.append(tmp_test_data)
#         pred_data = pred_data.sort_values(['datelist', 'stockID'])
#         FileUtil.save_df2csv(pred_data, root_path, f'total_{out_begin}~{final_end}_{model_name}_v{idx + 1}.csv')

for model_name in ['XgbRegModel', 'LgbRegModel']:
    root_path = f'/data/group/800463/fengc/for_xbc/20230113_europa_ensemble/Hml{model_name}/'
    from Zeus.Europa.v1_0_31.path_conf import xbc_rolling_config as date_config
    for idx, PERIOD in enumerate(PERIOD_LIST):
        pred_data = pd.DataFrame()
        pred_type = 'test'  # test fit
        date_dict = date_config[f'{PERIOD}_{pred_type}']
        out_begin, out_end = date_dict['train_start_date'], date_dict['train_end_date']
        final_end = date_config[f'{PERIOD}_fit']['test_end_date']
        import os
        sub_version = SUB_VERSION[idx]
        for tmp_path in os.listdir(root_path):
            if f'v{sub_version}' in tmp_path:
                pred_fpath = root_path + tmp_path
                tmp_begin = int(tmp_path.split('~')[0])
                tmp_end = int(tmp_path.split('~')[1][:8])
                tmp_test_data = pd.read_csv(pred_fpath, index_col=0)
                tmp_test_data = tmp_test_data.query('datelist >= @tmp_begin & datelist <= @tmp_end')
                pred_data = pred_data.append(tmp_test_data)
        pred_data = pred_data.sort_values(['datelist', 'stockID'])
        FileUtil.save_df2csv(pred_data, root_path, f'total_{out_begin}~{final_end}_{model_name}_v{idx+1}_hml.csv')