# coding: utf-8
# Author：fengchi863
# Date ：2023/11/6 9:09

import pandas as pd
import shutil
import os
from Zeus.Neptune.v1_0_6.config.path_conf import *
from Zeus.Neptune.v1_0_6.config.strat_conf import *

PERIOD = 'period8'
date_dict = DATE_CONFIG[PERIOD]
test_start_date = date_dict['test_start_date']
test_end_date = date_dict['test_end_date']
fit_start_date = date_dict['fit_start_date']
fit_end_date = date_dict['fit_end_date']

dept_path = f'/data/user/015614/Zeus/pred/Neptune/v1_0_6/'

# 正式提交
_send_dict =[
{'dest_path': f'/data/user/015614/shared/for_wj/strategy_model/Neptune/fac_20250609_sc_filter_mid/区间{PERIOD[-1]}/',
     'model_name': {'config1_fsv11_s1_Xgb': 'mid_FSV11Xgb',}},
{'dest_path': f'/data/user/015614/shared/for_wj/strategy_model/Neptune/fac_20250609_sc_filter_mid/区间{PERIOD[-1]}/',
     'model_name': {'config1_fsv10_s1_Xgb': 'mid_FSV10Xgb',}},
    {'dest_path': f'/data/user/015614/shared/for_wj/strategy_model/Neptune/fac_20250609_sc_filter_mid/区间{PERIOD[-1]}/',
     'model_name': {'config2_fsv11_s1_Xgb': 'mid_sw_high_FSV11Xgb',}},
    {'dest_path': f'/data/user/015614/shared/for_wj/strategy_model/Neptune/fac_20250609_sc_filter_mid/区间{PERIOD[-1]}/',
     'model_name': {'config3_fsv11_s1_Xgb': 'mid_sw_low_FSV11Xgb', }},
    {'dest_path': f'/data/user/015614/shared/for_wj/strategy_model/Neptune/fac_20250609_sc_filter_mid/区间{PERIOD[-1]}/',
     'model_name': {'config2_fsv8_s1_Xgb': 'mid_sw_high_FSV8Xgb', }},
    {'dest_path': f'/data/user/015614/shared/for_wj/strategy_model/Neptune/fac_20250609_sc_filter_mid/区间{PERIOD[-1]}/',
     'model_name': {'config3_fsv8_s1_Xgb': 'mid_sw_low_FSV8Xgb', }},

    # {'dest_path': f'/data/user/015614/shared/for_skk/strategy_model/Neptune/fac_20250609_s1_filter_short/区间{PERIOD[-1]}/',
    #  'model_name': {'config6_fsv8_s1_Xgb': 'short_FSV8Xgb',}},
    # {'dest_path': f'/data/user/015614/shared/for_skk/strategy_model/Neptune/fac_20250609_s1_filter_short/区间{PERIOD[-1]}/',
    #  'model_name': {'config6_fsv10_s1_Xgb': 'short_FSV10Xgb',}},
    # {'dest_path': f'/data/user/015614/shared/for_skk/strategy_model/Neptune/fac_20250609_s1_filter_short/区间{PERIOD[-1]}/',
    #  'model_name': {'config7_fsv10_s1_Xgb': 'short_sw_high_FSV10Xgb',}},
    # {'dest_path': f'/data/user/015614/shared/for_skk/strategy_model/Neptune/fac_20250609_s1_filter_short/区间{PERIOD[-1]}/',
    #  'model_name': {'config8_fsv10_s1_Xgb': 'short_sw_low_FSV10Xgb', }},
    # {'dest_path': f'/data/user/015614/shared/for_skk/strategy_model/Neptune/fac_20250609_s1_filter_short/区间{PERIOD[-1]}/',
    #  'model_name': {'config9_fsv10_s1_Xgb': 'short_vol_low_FSV10Xgb', }},
    # {'dest_path': f'/data/user/015614/shared/for_skk/strategy_model/Neptune/fac_20250609_s1_filter_short/区间{PERIOD[-1]}/',
    #  'model_name': {'config10_fsv10_s1_Xgb': 'short_vol_high_FSV10Xgb', }},
]

for idx in range(6): # send_dict中两个组合
    now_send = _send_dict[idx]
    dest_path = now_send['dest_path']
    model_name_list = list(now_send['model_name'].keys())
    _model_name = now_send['model_name']
    for seed in range(2):   # 每个模型提交三个seed的结果
        for config_model_name in model_name_list:
            print(f'提交{config_model_name}')
            config = config_model_name.split('_')[0]
            model_name = '_'.join(config_model_name.split('_')[1:])
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

                new_model_name = _model_name[config_model_name]

                # 复制model文件
                model = dept_path + f'{config}/{model_name}/{period}/model/seed_{seed}/{model}'
                os.makedirs(dest_path + f'{new_model_name}', exist_ok=True)
                shutil.copy(model, dest_path + f'{new_model_name}/model_{roll_type}seed{seed}.pkl')

                if seed == 0:
                    # 复制因子列表
                    factor_list_fpath = dept_path + f'{config}/{model_name}/{period}/model/seed_{seed}/_factorName.json'
                    shutil.copy(factor_list_fpath, dest_path + f'{new_model_name}/Model_{roll_type}factorName.json')

                    # 复制预处理文件列表
                    factor_scaler_fpath = dept_path + f'{config}/{model_name}/{period}/model/seed_{seed}/_factorScaler.json'
                    shutil.copy(factor_scaler_fpath, dest_path + f'{new_model_name}/Model_{roll_type}factorScaler.json')

                    # 复制pred文件
                    pred_fpath = dept_path + f'{config}/{model_name}/{period}/model/seed_{seed}/{test_start_date}~{test_end_date}.csv'
                    shutil.copy(pred_fpath, dest_path + f'{new_model_name}/{test_start_date}~{test_end_date}_{roll_type.replace("_", "")}.csv')

                    threshold_fpath = dept_path + f'{config}/{model_name}/{period}/model/seed_{seed}/_score_threshold.json'
                    shutil.copy(threshold_fpath, dest_path + f'{new_model_name}/Model_config.json')

                    infer_fpath = f'./infer.py'
                    shutil.copy(infer_fpath, dest_path + f'{new_model_name}/infer.py')

# 提交模型排名
model_rank_df = pd.DataFrame()