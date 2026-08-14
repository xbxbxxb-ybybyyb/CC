# coding: utf-8
# Author：fengchi863
# Date ：2022/7/18 15:08

from LucienUtil.FileUtil import FileUtil
import pandas as pd

def log_parse(log_path=None,
              log_fname=None,
              note=None):
    key_df = pd.DataFrame()
    value_df = pd.DataFrame()
    params_list = list()
    with open(log_path + log_fname, 'r') as log_file:
        log_lines = log_file.readlines()
        for log_line in log_lines:
            if not '自适应风险收益比' in log_line:     # 判断该行是否存在超参数
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
        '预测值与标签IC',
        '自适应风险收益比',
        '自适应扣费收益率胜率',
        '自适应参与率',
        '自适应夏普比率',
        '自适应累计盈利',
        '自适应阈值',
        'R自适应风险收益比',
        'R自适应扣费收益率胜率',
        'R自适应参与率',
        'R自适应夏普比率',
        'R自适应累计盈利',
        'R自适应阈值',
        # '预测值与标签IC2',
        # '自适应风险收益比2',
        # '自适应扣费收益率胜率2',
        # '自适应参与率2',
        # '自适应夏普比率2',
        # '自适应累计盈利2',
        # '自适应阈值2',
        # 'R自适应风险收益比2',
        # 'R自适应扣费收益率胜率2',
        # 'R自适应参与率2',
        # 'R自适应夏普比率2',
        # 'R自适应累计盈利2',
        # 'R自适应阈值2',
    ]
    multi = multi[col]

    FileUtil.save_df2xls(multi, log_path, f'{log_fname[:-4]}_{note}.xlsx')

if __name__ == '__main__':
    # log_parse(log_path='/data/user/015614/Zeus/logs/Europa/v1_0_32/LgbRegModel/',
    #           log_fname='Europa_v1_0_32_LgbRegModel_v5.log',
    #           note='test')
    log_parse(log_path='/data/user/015614/Zeus/logs/Europa/v1_0_32/XgbRegModel/',
              log_fname='Europa_v1_0_32_XgbRegModel_v5.log',
              note='test')
    # log_parse(log_path='/data/user/015614/Zeus/logs/Europa/v1_0_32/LrRegModel/',
    #           log_fname='Europa_v1_0_32_LrRegModel_v5.log',
    #           note='test')
    # log_parse(log_path='/data/user/015614/Zeus/logs/Europa/v1_0_32/CatRegModel/',
    #           log_fname='Europa_v1_0_32_CatRegModel_v3.log',
    #           note='test')
    # hml分场景 hml_factor
    # for ver in [10, 11, 12, 20, 21, 22, 30, 31, 32]:
    # for ver in [50, 51, 52]:
    #     log_parse(log_path='/data/user/015614/Zeus/logs/Europa/v1_0_32/XgbRegModel/',
    #               log_fname=f'Europa_v1_0_32_XgbRegModel_v{ver}.log',
    #               note='test')