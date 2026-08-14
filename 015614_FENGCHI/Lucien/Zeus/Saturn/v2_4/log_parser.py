# coding: utf-8
# Author：fengchi863
# Date ：2022/7/18 15:08

from Zeus.Saturn.v2_4.path_conf import *
from LucienUtil.FileUtil import FileUtil
import pandas as pd
import numpy as np

def log_parse(log_path=None,
              log_fname=None,
              note=None):
    key_df = pd.DataFrame()
    value_df = pd.DataFrame()
    params_list = list()
    with open(log_path + log_fname, 'r') as log_file:
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

    # 最后一列移动到第一列
    col = multi.iloc[:, [-1]].columns.tolist()
    other_col = multi.iloc[:, :-1].columns.tolist()
    multi = multi[col + other_col]

    FileUtil.save_df2xls(multi, log_path, f'{log_fname[:-4]}{note}.xlsx')

if __name__ == '__main__':
    log_parse(log_path='/data/user/015614/Zeus/logs/Saturn/v2_4/xgb_clf_model/',
              log_fname='2022-07-24 23：10：12_Saturn_v2_4_xgb_clf_model.log',
              note='debug使用')