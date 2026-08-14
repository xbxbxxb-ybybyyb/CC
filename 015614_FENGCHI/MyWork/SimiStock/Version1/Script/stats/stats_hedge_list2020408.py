# coding: utf-8
# Author：fengchi863
# Date ：2022/4/8 13:14
"""
丽姐要求计算的0.8的部分
"""

from SimiStock.config.path_config import *
import pandas as pd
import numpy as np
from SimiStock.SimiStockGenerator.util import util

def get_quater(date):
    year = date // 10000
    month = date // 100 % 100
    if month in [1, 2, 3]:
        return f'{year}Q1'
    elif month in [4, 5, 6]:
        return f'{year}Q2'
    elif month in [7, 8, 9]:
        return f'{year}Q3'
    else:
        return f'{year}Q4'

def get_half(date):
    year = date // 10000
    month = date // 100 % 100
    if month in [1, 2, 3, 4, 5, 6]:
        return f'{year}H1'
    else:
        return f'{year}H2'

if __name__ == '__main__':
    data_file_list = ['叠加风格5_14_0.8_v3_95_20180101_20200630_result.pkl',
                      '叠加风格5_14_0.8_v3_100_20180101_20200630_result.pkl',
                      '叠加风格5_14_0.8_v3_95_20200701_20210630_result.pkl',
                      '叠加风格5_14_0.8_v3_100_20200701_20210630_result.pkl']
    df_list = list()
    for data_file in data_file_list:
        ret_list = list()
        hedge_list = pd.read_pickle(hedge_path + data_file)
        for idx, hedge in enumerate(hedge_list):
            ret_list.append([hedge['stk_id'], hedge['date'], hedge['discount'], len(hedge['hedge_list'])])
        df = pd.DataFrame(ret_list, columns=['stk_id', 'date', 'discount', '对冲标的可选数量'])
        df['discount'] = 1 - df['discount']
        df['month'] = df['date'] // 100
        df['quater'] = df['date'].apply(lambda x: get_quater(x))
        df['half'] = df['date'].apply(lambda x: get_half(x))

        ret_df = pd.DataFrame(index=['1', '2', '3', '>=4'])
        for i in [1, 2, 3, 4]:
            if i <= 3:
                ret_df.loc[f'{i}', '项目数量'] = (df['对冲标的可选数量'] == i).sum()
                ret_df.loc[f'{i}', '项目比例'] = (df['对冲标的可选数量'] == i).sum() / len(df)

                ret_df.loc[f'{i}', '1个月股票数量'] = len(df[df['对冲标的可选数量'] == i].groupby(['month', 'stk_id']).agg(
                    'count'))
                ret_df.loc[f'{i}', '3个月股票数量'] = len(df[df['对冲标的可选数量'] == i].groupby(['quater', 'stk_id']).agg(
                    'count'))
                ret_df.loc[f'{i}', '6个月股票数量'] = len(df[df['对冲标的可选数量'] == i].groupby(['half', 'stk_id']).agg(
                    'count'))
                ret_df.loc[f'{i}', '折价10%分位数'] = np.percentile(df[df['对冲标的可选数量'] == i]['discount'].values, 10)
                ret_df.loc[f'{i}', '折价30%分位数'] = np.percentile(df[df['对冲标的可选数量'] == i]['discount'].values, 30)
                ret_df.loc[f'{i}', '折价50%分位数'] = np.percentile(df[df['对冲标的可选数量'] == i]['discount'].values, 50)
                ret_df.loc[f'{i}', '折价70%分位数'] = np.percentile(df[df['对冲标的可选数量'] == i]['discount'].values, 70)
                ret_df.loc[f'{i}', '折价90%分位数'] = np.percentile(df[df['对冲标的可选数量'] == i]['discount'].values, 90)

            if i == 4:
                ret_df.loc[f'>={i}', '项目数量'] = (df['对冲标的可选数量'] >= i).sum()
                ret_df.loc[f'>={i}', '项目比例'] = (df['对冲标的可选数量'] >= i).sum() / len(df)

                ret_df.loc[f'>={i}', '1个月股票数量'] = len(df[df['对冲标的可选数量'] >= i].groupby(['month', 'stk_id']).agg(
                    'count'))
                ret_df.loc[f'>={i}', '3个月股票数量'] = len(df[df['对冲标的可选数量'] >= i].groupby(['quater', 'stk_id']).agg(
                    'count'))
                ret_df.loc[f'>={i}', '6个月股票数量'] = len(df[df['对冲标的可选数量'] >= i].groupby(['half', 'stk_id']).agg(
                    'count'))
                ret_df.loc[f'>={i}', '折价10%分位数'] = np.percentile(df[df['对冲标的可选数量'] >= i]['discount'].values, 10)
                ret_df.loc[f'>={i}', '折价30%分位数'] = np.percentile(df[df['对冲标的可选数量'] >= i]['discount'].values, 30)
                ret_df.loc[f'>={i}', '折价50%分位数'] = np.percentile(df[df['对冲标的可选数量'] >= i]['discount'].values, 50)
                ret_df.loc[f'>={i}', '折价70%分位数'] = np.percentile(df[df['对冲标的可选数量'] >= i]['discount'].values, 70)
                ret_df.loc[f'>={i}', '折价90%分位数'] = np.percentile(df[df['对冲标的可选数量'] >= i]['discount'].values, 90)

        df_list.append(ret_df.T)
    ret_dict = {'95折-样本内': df_list[0],
                '全部-样本内': df_list[1],
                '95折-样本外': df_list[2],
                '全部-样本外': df_list[3]}
    util.save_dict2xls(ret_dict, other_stats_path, '样本内外统计.xlsx')
