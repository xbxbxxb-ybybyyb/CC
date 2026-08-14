# coding: utf-8
# Author：fengchi863
# Date ：2022/3/16 14:00

import numpy as np
import pandas as pd

from SimiStock.SimiBackTest.SimiBackTest import SimiBackTest
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *


def backtest_1method(filename, output_name=None, duration=120, hedge_num=None, start_date=20180101, end_date=20200631,
                     kernal_num=20, mode='multi', method_name=None):
    sbt = SimiBackTest(start_date, end_date, hedge_path + filename)

    filename_param = filename.split('_')
    method_name = method_name
    concept = filename_param[1]
    pre_days_num = filename_param[2]

    # 如要保存，可直接添加参数save_flag=True以及save_name, 默认参数save_path=hedge_path
    df1 = sbt.backtest(hedge_num=hedge_num, duration=duration, direction='history', kernal_num=kernal_num, mode=mode,
                       save_flag=True, save_name=f'history_{output_name}')
    print('history')

    df2 = sbt.backtest(hedge_num=hedge_num, duration=duration, direction='future', kernal_num=kernal_num, mode=mode,
                       save_flag=True, save_name=f'future_{output_name}', stats_flag=True,
                       stats_save_name=f'stats_{output_name}')
    print('future')

    df = df1.append(df2, ignore_index=True)
    groupby_columns = ['回测方向', '回测周期']

    summary = pd.DataFrame()
    summary['日均跟踪误差均值'] = df.groupby(groupby_columns).apply(lambda x: x['日均跟踪误差均值'].mean())
    summary['年化跟踪误差均值'] = df.groupby(groupby_columns).apply(lambda x: x['年化跟踪误差'].mean())
    summary['偏离70%分位数均值'] = df.groupby(groupby_columns).apply(lambda x: x['偏离70%分位数'].mean())
    summary['相关系数均值'] = df.groupby(groupby_columns).apply(lambda x: x['相关系数'].mean())
    summary['相关系数方差'] = df.groupby(groupby_columns).apply(lambda x: x['相关系数'].std())
    summary['最大回撤均值'] = df.groupby(groupby_columns).apply(lambda x: x['最大回撤'].mean())
    summary['最大收益均值'] = df.groupby(groupby_columns).apply(lambda x: x['最大收益'].mean())
    summary['累计最大偏离均值'] = df.groupby(groupby_columns).apply(lambda x: x['累计最大偏离'].mean())
    summary['相关系数大于0.8胜率'] = df.groupby(groupby_columns).apply(lambda x: (x['相关系数'] > 0.8).sum() /
                                                                         np.isfinite(x['相关系数']).sum())
    summary['相关系数大于0.7胜率'] = df.groupby(groupby_columns).apply(lambda x: (x['相关系数'] > 0.7).sum() /
                                                                         np.isfinite(x['相关系数']).sum())
    summary['相关系数大于0.6胜率'] = df.groupby(groupby_columns).apply(lambda x: (x['相关系数'] > 0.6).sum() /
                                                                         np.isfinite(x['相关系数']).sum())
    # summary['历史未来相关性的相关性'] = df1['相关系数'].corr(df2['相关系数']) # 这个指标没用
    # summary['历史未来秩相关性'] = df1['相关系数'].rank().corr(df2['相关系数'].rank())
    summary['历史未来相关性均值'] = df.groupby(groupby_columns).apply(lambda x: x['历史未来相关性'].mean())
    summary['历史未来秩相关性均值'] = df.groupby(groupby_columns).apply(lambda x: x['历史未来秩相关性'].mean())
    summary['method_name'] = method_name
    summary['hedge_num'] = hedge_num
    summary['concept'] = concept
    summary['pre_days_num'] = pre_days_num
    util.save_df2xls(summary, bt_path, output_name)


if __name__ == '__main__':
    filename = '日频pctchg皮尔逊相关性_SW1_120_result.pkl'
    backtest_1method(filename=filename,
                     output_name=f'tmp_test.xlsx',
                     duration=120,
                     hedge_num=12,
                     mode='serial',
                     kernal_num=12)

    # filename = '日频pctchg相关性_SW1_120_txTest_result.pkl'
    # for hedge_num in [1, 2, 3, 4, 5]:
    #     backtest_1method(filename=filename,
    #                      output_name=f'{hedge_num}_txTest.xlsx',
    #                      duration=120,
    #                      hedge_num=hedge_num,
    #                      mode='multi',
    #                      kernal_num=12)
