# coding: utf-8
# Author：fengchi863
# Date ：2022/7/18 15:08

from LucienUtil.FileUtil import FileUtil
import pandas as pd
import numpy as np
import os

def log_parse(log_path=None,
              log_fname=None,
              note=None):
    key_df = pd.DataFrame()
    value_df = pd.DataFrame()
    params_list = list()
    with open(log_path + log_fname, 'r') as log_file:
        log_lines = log_file.readlines()
        for log_line in log_lines:
            if not 'valid_auc' in log_line:     # 判断该行是否存在超参数
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
        'valid_auc',
        'valid_auc_std',
        'valid_precision',
        'valid_recall',
        'valid_rmse',
        'valid_ic',
        'test_auc',
        'test_precision',
        'test_recall',
        'test_rmse',
        'test_ic',
        'fit_auc',
        'fit_precision',
        'fit_recall',
        'fit_rmse',
        'fit_ic',
        # 'test_收益夏普比率',
        # 'test_收益风险比',
        # 'fit_收益夏普比率',
        # 'fit_收益风险比'
    ]
    multi = multi[col]
    multi = multi.sort_values('valid_auc', ascending=False)
    # multi = multi.sort_values('test_收益夏普比率', ascending=False)
    output_dict = {'调参': multi,
                   '指标相关性': multi.drop('整体参数', axis=1).iloc[:10].corr(method='spearman')}

    FileUtil.save_dict2xls(output_dict, log_path, f'{log_fname[:-4]}_{note}.xlsx')

if __name__ == '__main__':
    log_root_path = '/data/user/015614/Zeus/logs/Europa/v4_0_18/'
    folder_name_list = os.listdir(log_root_path)
    # folder_name_list = ['rffs_XgbRegModel']
    for folder_name in folder_name_list:
        log_file_list = os.listdir(log_root_path + folder_name + '/')
        log_fname_list = list(filter(lambda x: x.endswith('.log'), log_file_list))
        for log_fname in log_fname_list:
            log_parse(log_path=log_root_path + folder_name + '/',
                      log_fname=log_fname,
                      note='')