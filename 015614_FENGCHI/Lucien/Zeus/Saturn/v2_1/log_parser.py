# coding: utf-8
# Author：fengchi863
# Date ：2022/7/18 15:08

from Zeus.Saturn.v2_1.path_conf import *
from LucienUtil.FileUtil import FileUtil
import pandas as pd
import numpy as np

def log_parse(log_fpath=None,
              save_path=multi_path):
    key_df = pd.DataFrame()
    value_df = pd.DataFrame()
    params_list = list()
    with open(log_fpath, 'r') as log_file:
        log_lines = log_file.readlines()
        for log_line in log_lines:
            if not '收益风险比' in log_line:     # 判断该行是否存在超参数
                continue
            _key = log_line.split('}: {')[0].split(' - ')[-1]
            _value = log_line.split('}: {')[1][:-1]
            params_list.append('{' + _value)
            if 'nan' in _key:
                _key = _key.replace('nan', 'np.nan')
            key_df = key_df.append(pd.DataFrame(pd.Series(eval(_key + '}'))).T)
            value_df = value_df.append(pd.DataFrame(pd.Series(eval('{' + _value))).T)
    key_df = key_df.reset_index(drop=True)
    value_df = value_df.reset_index(drop=True)
    multi = pd.concat([key_df, value_df], axis=1, join_axes=[value_df.index])
    multi['整体参数'] = params_list
    FileUtil.save_df2xls(multi, save_path, '2022-07-20 19：17：26_SaturnS1_v2_1_xgb_reg_model.xlsx')

if __name__ == '__main__':
    # log_parse('/data/user/015614/Zeus/logs/SaturnS1/v2/xgb_clf_model/' + '2022-07-18 20：01：25_SaturnS1_v2_xgb_clf_model.log')
    log_parse('/data/user/015614/Zeus/logs/SaturnS1/v2_1/xgb_reg_model/' + '2022-07-20 19：17：26_SaturnS1_v2_1_xgb_reg_model.log',
              save_path='/data/user/015614/Zeus/logs/SaturnS1/v2_1/xgb_reg_model/')