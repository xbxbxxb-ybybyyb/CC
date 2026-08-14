# coding: utf-8
# Author：fengchi863
# Date ：2022/7/18 15:08

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
            # FIXME：这是一个衍生版本，卖出策略不包含
            if not 'sum_label_diff' in log_line:     # 判断该行是否存在超参数
                continue
            _key = log_line.split('}: {')[0].split(' - ')[-1]
            _value = log_line.split('}: {')[1][:-1]
            params_list.append('{' + _value)
            if 'nan' in _key:
                _key = _key.replace('nan', 'np.nan')
            if 'inf' in _key:
                _key = _key.replace('inf', 'np.inf')
            key_df = key_df.append(pd.DataFrame(pd.Series(eval(_key + '}'))).T)
            value_df = value_df.append(pd.DataFrame(pd.Series(eval('{' + _value))).T)
    key_df = key_df.reset_index(drop=True)
    value_df = value_df.reset_index(drop=True)
    multi = pd.concat([key_df, value_df], axis=1, join_axes=[value_df.index])
    multi['整体参数'] = params_list

    col = [
        '整体参数',
        'sum_label_diff',
        'sum_label_diff2'
    ]
    multi = multi[col]

    FileUtil.save_df2xls(multi, log_path, f'{log_fname[:-4]}_{note}.xlsx')

if __name__ == '__main__':
    log_parse(log_path='/data/user/015614/Zeus/logs/ProjectSell/v1_0_1/LgbRegModel/',
              log_fname='ProjectSell_v1_0_1_LgbRegModel_v1.log',
              note='test')
    # log_parse(log_path='/data/user/015614/Zeus/logs/JupiterN/v1_0_1/XgbRegModel/',
    #           log_fname='JupiterN_v1_0_1_XgbRegModel_v4.log',
    #           note='test')
    # log_parse(log_path='/data/user/015614/Zeus/logs/JupiterN/v1_0_1/LrRegModel/',
    #           log_fname='JupiterN_v1_0_1_LrRegModel_v4.log',
    #           note='test')
    # log_parse(log_path='/data/user/015614/Zeus/logs/JupiterN/v1_0_1/CatRegModel/',
    #           log_fname='JupiterN_v1_0_1_CatRegModel_v3.log',
    #           note='test')