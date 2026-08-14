# coding: utf-8
# Author：fengchi863
# Date ：2023/11/6 9:09

import pandas as pd
import shutil
import os

def _model_name(model_name):
    if 'fsv8' in model_name and 'Xgb' in model_name:
        ret = 'FSV8Xgb'
    elif 'fsv8' in model_name and 'Lgb' in model_name:
        ret = 'FSV8Lgb'
    elif 'fsv10' in model_name and 'Xgb' in model_name:
        ret = 'FSV10Xgb'
    elif 'fsv10' in model_name and 'Lgb' in model_name:
        ret = 'FSV10Lgb'
    elif 'fsv11' in model_name and 'Xgb' in model_name:
        ret = 'FSV11Xgb'
    elif 'fsv11' in model_name and 'Lgb' in model_name:
        ret = 'FSV11Lgb'
    elif 'fsrs' in model_name and 'Xgb' in model_name:
        ret = 'FSRSXgb'
    elif 'fsrs' in model_name and 'Lgb' in model_name:
        ret = 'FSRSLgb'
    elif 'rffs' in model_name and 'Xgb' in model_name:
        ret = 'FcXgb'
    elif 'rffs' in model_name and 'Lgb' in model_name:
        ret = 'FcLgb'
    else:
        ret = 'Error'

    return ret


model_name_list = ['fsv8_pct_AllXgbRegModel', 'fsv10_pct_AllXgbRegModel', 'fsv11_pct_AllXgbRegModel', 'fsrs_pct_AllXgbRegModel', 'rffs_pct_AllXgbRegModel',]

dept_path = '/data/user/015614/Zeus/pred/Europa/v4_0_6/'
dest_path = '/data/user/015614/shared/for_wj/strategy_model/Europa/fac_20231102/区间3/'    # TODO：根据period修改这里的值

for seed in range(31):
    for model_name in model_name_list:
        for roll_type in ['', 'roll_']:
            period = 'period3'
            if roll_type == 'roll_':
                period = f'{period}_roll'

            if 'Xgb' in model_name:
                model = 'XgbRegModel.pkl'
            else:
                model = 'LgbRegModel.pkl'

            new_model_name = _model_name(model_name)

            # 复制model文件
            model = dept_path + f'{model_name}/model/{period}/seed_{seed}/{model}'
            os.makedirs(dest_path + f'{new_model_name}', exist_ok=True)
            shutil.copy(model, dest_path + f'{new_model_name}/model_{roll_type}seed{seed}.pkl')

            if seed == 0:
                # 复制因子列表
                factor_list_fpath = dept_path + f'{model_name}/model/{period}/seed_{seed}/_factorName.json'
                shutil.copy(factor_list_fpath, dest_path + f'{new_model_name}/Model_{roll_type}factorName.json')

                # 复制预处理文件列表
                factor_scaler_fpath = dept_path + f'{model_name}/model/{period}/seed_{seed}/_factorScaler.json'
                shutil.copy(factor_scaler_fpath, dest_path + f'{new_model_name}/Model_{roll_type}factorScaler.json')

                # 复制pred文件
                pred_fpath = dept_path + f'{model_name}/model/{period}/seed_{seed}/20201201~20210531.csv'
                shutil.copy(pred_fpath, dest_path + f'{new_model_name}/20201201~20210531_{roll_type.replace("_", "")}.csv')

                threshold_fpath = dept_path + f'{model_name}/model/{period}/seed_{seed}/_score_threshold.json'
                shutil.copy(threshold_fpath, dest_path + f'{new_model_name}/Model_config.json')

                infer_fpath = dept_path + f'infer.py'
                shutil.copy(infer_fpath, dest_path + f'{new_model_name}/infer.py')



