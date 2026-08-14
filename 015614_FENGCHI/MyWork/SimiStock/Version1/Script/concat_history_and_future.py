# coding: utf-8
# Author：fengchi863
# Date ：2022/3/15 11:18

from SimiStock.SimiBackTest.SimiBackTest import SimiBackTest
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
import numpy as np
import pandas as pd

if __name__ == '__main__':
    # 输入要回测的hedge_list文件名, filename中最好包含策略名，此处假设file_name即为策略名
    # hedge生成参数
    method_name = '日频close相关性'
    concept = 'SW2'
    pre_days_num = 120

    # 回测参数
    duration = 120
    hedge_num = 1

    hedge_param_list = [method_name, concept, str(pre_days_num)]
    bt_param_list = [method_name, concept, str(pre_days_num), str(duration), str(hedge_num)]
    file_name = '_'.join(hedge_param_list) + '_result.pkl'
    output_name = '_'.join(bt_param_list) + '_bt_summary.xlsx'

    sbt = SimiBackTest(20180101, 20200631, hedge_path + file_name)

    # 如要保存，可直接添加参数save_flag=True以及save_name, 默认参数save_path=hedge_path
    df1 = sbt.backtest(hedge_num=hedge_num, duration=duration, direction='history', kernal_num=12, mode='serial',
                       save_flag=True, save_name='tmp1.xlsx')
    print('history')

    sbt = SimiBackTest(20180101, 20200631, hedge_path + file_name)
    df2 = sbt.backtest(hedge_num=hedge_num, duration=duration, direction='future', kernal_num=12, mode='serial',
                       save_flag=True, save_name='tmp2.xlsx')
    print('future')

    df = df1.append(df2, ignore_index=True)
    groupby_columns = ['回测方向', '回测周期']
    # summary = df.groupby(['回测方向', '回测周期'])[['日均跟踪误差均值', '年化跟踪误差', '偏离70%分位数', '相关系数',
    #                                         '最大回撤', '最大收益', '累计最大偏离']].mean()
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

    util.save_df2xls(summary, bt_path, output_name)




