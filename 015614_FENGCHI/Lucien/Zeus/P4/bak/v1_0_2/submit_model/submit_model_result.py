# coding: utf-8
# Author：fengchi863
# Date ：2023/11/6 9:09

import pandas as pd
import shutil
import os
from Zeus.P4.v1_0_2.config.path_conf import *
from Zeus.P4.v1_0_2.config.strat_conf import *

PERIOD = 'period4'
date_dict = DATE_CONFIG[PERIOD]
test_start_date = date_dict['test_start_date']
test_end_date = date_dict['test_end_date']
fit_start_date = date_dict['fit_start_date']
fit_end_date = date_dict['fit_end_date']

# 实际上传的model_name
# 整体是一个fsv8，一个fsv10，一个fsv11，一个rffs
# period1: fsv8 fsci(config4)      fsv11 fsv10(config3)
# period1: fsci fsv10 fsv11 fsv8 (config1)
# period1: fsci fsv10 fsv11 fsv8 (config2)

# period2: fsv11 fsci(config3)      rffs fsv10(config4)
# period2: fsci fsv10 rffs fsrs (config1)
# period2: fsci fsv10 rffs fsv8 (config2)
_model_name = {
   # 'fsrs_s1_Xgb': 'FSRSXgb',
   'rffs_s1_Xgb': 'FcXgb',
   'fsv11_s1_Xgb': 'FSV11Xgb',
   'fsv10_s1_Xgb': 'FSV10Xgb',
   # 'fsci_s1_Xgb': 'FSCIXgb',
   'fsv8_s1_Xgb': 'FSV8Xgb',
               }
model_name_list = list(_model_name.keys())
config = 'config2'


dept_path = f'/data/user/015614/Zeus/pred/P4/v1_0_2/'   # label
# dest_path = f'/data/user/015614/shared/for_wj/strategy_model/P4s1_label3/fac_20241225/区间{PERIOD[-1]}/'    # TODO：根据period修改这里的值
# dest_path = f'/data/user/015614/shared/for_wj/strategy_model/P4/fac_20240807/区间{PERIOD[-1]}/'    # TODO：根据period修改这里的值
dest_path = f'/data/user/015614/shared/for_wj/strategy_model/P4/fac_20250225/区间{PERIOD[-1]}/'    # TODO：根据period修改这里的值

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