# coding: utf-8
# Author：fengchi863
# Date ：2025/4/18 11:10


import importlib
import os

module_name = f'Zeus.Mimas.v1_0_18.config.path_conf'
module = importlib.import_module(module_name)


def check_path_is_ok(config_flag):
    PT = getattr(module, config_flag)
    data_fpath = PT['data_fpath']

    fsv8_fpath = PT['xgb_fsv8_fpath']
    fsv10_fpath = PT['xgb_fsv10_fpath']
    fsv11_fpath = PT['xgb_fsv11_fpath']
    fsrs_fpath = PT['fsrs_fpath']

    profit_data_fpath = PT['profit_data_fpath']

    check_list = [data_fpath, fsv8_fpath, fsv10_fpath, fsv11_fpath, fsrs_fpath, profit_data_fpath]

    for path in check_list:
        if os.path.exists(path):
            continue
        else:
            raise Exception(f'缺失{path}')
