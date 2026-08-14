# coding: utf-8
# Author：fengchi863
# Date ：2023/11/6 9:09

import pandas as pd
import shutil
import os
from Zeus.JupiterN.v2_0_3.config.path_conf import *
from Zeus.JupiterN.v2_0_3.config.strat_conf import *

PERIOD = 'period8'
date_dict = DATE_CONFIG[PERIOD]
test_start_date = date_dict['test_start_date']
test_end_date = date_dict['test_end_date']
fit_start_date = date_dict['fit_start_date']
fit_end_date = date_dict['fit_end_date']

# 实际上传的model_name   # NOTE: 20240606用于提交区间8模型
# model_name_list = ['fsv8_s1_Xgb', 'fsrs_s1_Xgb', 'rffs_s1_Xgb', 'fsv11_s1_Xgb', 'fsv10_s1_Xgb', 'fsci_s1_Xgb']
# model_name_list = ['rffs_s1_Xgb']
# model_name_list = ['rffs_s1_Xgb', 'fsv11_s1_Xgb']
# peirod4 config1-fsv11 config3-fsrs config4-fsv10-fsv8
# peirod5 config1-fsv11 config3-fsrs config4-fsv10-fsv8
# peirod6 config1-fsv11 config3-fsrs config4-fsv10-fsv8
# peirod7 config1-fsv11 config3-fsrs config4-fsv10-fsv8

"""
第八区间 上实盘
config1_fsv11 改名为p5_FSV11Xgb
config1_fsrs 改名为p5_FSRSXgb
config3_fsv11 改名为p5_FSV10Xgb
config3_fsci 改名为p5_FSV8Xgb
"""
_model_name = {
    # 'fsv8_s1_Xgb': 'FSV8Xgb',
   # 'fsrs_s1_Xgb': 'FSRSXgb',
   # 'rffs_s1_Xgb': 'RffsXgb',
   'fsv11_s1_Xgb': 'FSV11Xgb',
   # 'fsv10_s1_Xgb': 'FSV10Xgb',
   'fsci_s1_Xgb': 'FSCIXgb'
               }
model_name_list = list(_model_name.keys())
config = 'config3'


dept_path = f'/data/user/015614/Zeus/pred/JupiterN/v2_0_3/'   # label
dest_path = f'/data/user/015614/shared/for_skk/strategy_model/JupiterN/fac_20240911/区间{PERIOD[-1]}/'    # TODO：根据period修改这里的值

for seed in range(5):
    for model_name in model_name_list:
        for roll_type in ['', 'roll_']:
            if roll_type == 'roll_':
                period = PERIOD
                period = f'{period}_roll'
            else:
                period = PERIOD

            if 'Xgb' in model_name:
                model = 'XgbRegModel.pkl'
            else:
                model = 'LgbRegModel.pkl'

            new_model_name = _model_name[model_name]

            # 复制model文件
            model = dept_path + f'{config}/{model_name}/model/{period}/seed_{seed}/{model}'
            os.makedirs(dest_path + f'{new_model_name}', exist_ok=True)
            shutil.copy(model, dest_path + f'{new_model_name}/model_{roll_type}seed{seed}.pkl')

            if seed == 0:
                # 复制因子列表
                factor_list_fpath = dept_path + f'{config}/{model_name}/model/{period}/seed_{seed}/_factorName.json'
                shutil.copy(factor_list_fpath, dest_path + f'{new_model_name}/Model_{roll_type}factorName.json')

                # 复制预处理文件列表
                factor_scaler_fpath = dept_path + f'{config}/{model_name}/model/{period}/seed_{seed}/_factorScaler.json'
                shutil.copy(factor_scaler_fpath, dest_path + f'{new_model_name}/Model_{roll_type}factorScaler.json')

                # 复制pred文件
                pred_fpath = dept_path + f'{config}/{model_name}/model/{period}/seed_{seed}/{test_start_date}~{test_end_date}.csv'
                shutil.copy(pred_fpath, dest_path + f'{new_model_name}/{test_start_date}~{test_end_date}_{roll_type.replace("_", "")}.csv')

                threshold_fpath = dept_path + f'{config}/{model_name}/model/{period}/seed_{seed}/_score_threshold.json'
                shutil.copy(threshold_fpath, dest_path + f'{new_model_name}/Model_config.json')

                infer_fpath = f'./infer.py'
                shutil.copy(infer_fpath, dest_path + f'{new_model_name}/infer.py')

# 提交模型排名
model_rank_df = pd.DataFrame()