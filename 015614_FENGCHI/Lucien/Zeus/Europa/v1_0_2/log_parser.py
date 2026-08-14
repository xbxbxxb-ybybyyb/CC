# coding: utf-8
# Author：fengchi863
# Date ：2022/7/18 15:08

from Zeus.Europa.v1_0_2.path_conf import *
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
        '预测值与标签IC',
        # '前50%IC',
        '夏普比率',
        '买入笔数',
        '总收益',
        '最大回撤',
        '扣费收益率胜率',
        '样本参与率',
        '最大收益风险比',
        '最大扣费收益率胜率',
        '最大累计盈利',
        '自适应风险收益比',
        '自适应扣费收益率胜率',
        '自适应参与率',
        '自适应夏普比率',
        '自适应累计盈利',
        '自适应阈值',
        '收益风险比2',
        '预测值与标签IC2',
        # '前50%IC2',
        '夏普比率2',
        '买入笔数2',
        '总收益2',
        '最大回撤2',
        '扣费收益率胜率2',
        '样本参与率2',
        '最大收益风险比2',
        '最大扣费收益率胜率2',
        '最大累计盈利2',
        '最大夏普比率2',
        '自适应风险收益比2',
        '自适应扣费收益率胜率2',
        '自适应参与率2',
        '自适应夏普比率2',
        '自适应累计盈利2',
        '自适应阈值2',
    ]
    multi = multi[col]

    # from scipy.stats import spearmanr
    # print('test, ic与风险收益比：', spearmanr(multi['预测值与标签IC'], multi['自适应风险收益比'])[0])
    # print('test, 50%ic与风险收益比：', spearmanr(multi['前50%IC'], multi['自适应风险收益比'])[0])
    # print('')
    # print('test, ic与扣费胜率：', spearmanr(multi['预测值与标签IC'], multi['自适应扣费收益率胜率'])[0])
    # print('test, 50%ic与扣费胜率：', spearmanr(multi['前50%IC'], multi['自适应扣费收益率胜率'])[0])
    # print('')
    # print('test, ic与扣费收益：', spearmanr(multi['预测值与标签IC'], multi['自适应累计盈利'])[0])
    # print('test, 50%ic与扣费收益：', spearmanr(multi['前50%IC'], multi['自适应累计盈利'])[0])
    # print('')
    # print('fit, ic与风险收益比：', spearmanr(multi['预测值与标签IC2'], multi['自适应风险收益比2'])[0])
    # print('fit, 50%ic与风险收益比：', spearmanr(multi['前50%IC2'], multi['自适应风险收益比2'])[0])
    # print('')
    # print('fit, ic与扣费胜率：', spearmanr(multi['预测值与标签IC2'], multi['自适应扣费收益率胜率2'])[0])
    # print('fit, 50%ic与扣费胜率：', spearmanr(multi['前50%IC2'], multi['自适应扣费收益率胜率2'])[0])
    # print('')
    # print('fit, ic与扣费收益：', spearmanr(multi['预测值与标签IC2'], multi['自适应累计盈利2'])[0])
    # print('fit, 50%ic与扣费收益：', spearmanr(multi['前50%IC2'], multi['自适应累计盈利2'])[0])

    FileUtil.save_df2xls(multi, log_path, f'{log_fname[:-4]}{note}.xlsx')

if __name__ == '__main__':
    # log_parse(log_path='/data/user/015614/Zeus/logs/Europa/v1_0_2/xgb_reg_model/',
    #           log_fname='2022-09-13 21：27：22_Europa_v1_0_2_xgb_reg_model.log',
    #           note='用全部因子进行测试20160101-20200630')
    log_parse(log_path='/data/user/015614/Zeus/logs/Europa/v1_0_2/lgb_reg_model/',
              log_fname='2022-10-28 17：17：04_Europa_v1_0_2_lgb_reg_model.log',
              note='_v2')