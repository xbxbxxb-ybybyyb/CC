# coding: utf-8
# Author：fengchi863
# Date ：2022/7/18 15:08

from Zeus.Saturn.v2_13.path_conf import *
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

    col = [
        '整体参数',
        '收益风险比',
        '夏普比率',
        '买入笔数',
        '总收益',
        '最大回撤',
        '扣费收益率胜率',
        '样本参与率',
        '收益风险比2',
        '夏普比率2',
        '买入笔数2',
        '总收益2',
        '最大回撤2',
        '扣费收益率胜率2',
        '样本参与率2',
        'train_acc',
        'valid_acc',
        'test_acc',
        'train_prec',
        'valid_prec',
        'test_prec',
        'train_rec',
        'valid_rec',
        'test_rec',
        'train_auc',
        'valid_auc',
        'test_auc',
        'train_f1',
        'valid_f1',
        'test_f1',
        'train_mse',
        'valid_mse',
        'test_mse',
        'train_mae',
        'valid_mae',
        'test_mae',
        'train_mae2',
        'valid_mae2',
        'test_mae2',
        'train_r2',
        'valid_r2',
        'test_r2',
        'train_evs',
        'valid_evs',
        'test_evs',
        'booster',
        'colsample_bytree',
        'factor_num',
        'gamma',
        'learning_rate',
        'len_test',
        'len_train',
        'max_depth',
        'min_child_weight',
        'n_estimators',
        'n_jobs',
        'pct_threshold',
        'random_state',
        'refer_num',
        'reg_alpha',
        'reg_lambda',
        'scale_pos_weight',
        'seed',
        'silent',
        'subsample',
        'tree_method'
    ]
    multi = multi[col]

    FileUtil.save_df2xls(multi, log_path, f'{log_fname[:-4]}{note}.xlsx')

if __name__ == '__main__':
    log_parse(log_path='/data/user/015614/Zeus/logs/Saturn_down/v2_13/xgb_reg_model/',
              log_fname='2022-08-12 17：40：10_Saturn_down_v2_13_xgb_reg_model.log',
              note='down版本修改版')