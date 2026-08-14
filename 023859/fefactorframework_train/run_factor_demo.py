import importlib
import json
import numpy as np
import pandas as pd
import copy
from h5data.IO import IO
from xquant.factordata import FactorData
s = FactorData()
import os

def check_dir(path):  # 路径生成函数
    if not os.path.exists(path):
        os.makedirs(path)

def fun_append_next_tradingday(factor_df):
    # 实盘中需要在T日开盘之前取到T-1日的因子，为了shift之后能有T日的时间戳，所以先把T日的时间戳加上去，取历史数据则没有该问题
    factor_df_unstack = factor_df.unstack()
    last_timestamp = factor_df_unstack.index[-1]
    next_tradingday_timestamp = pd.Timestamp(s.tradingday(last_timestamp.strftime('%Y%m%d'), 2)[-1])
    next_tradingday_df = pd.DataFrame(np.zeros((1,factor_df_unstack.shape[1])), columns=factor_df_unstack.columns,
                                      index=[next_tradingday_timestamp])
    factor_df = (factor_df_unstack.append(next_tradingday_df)).stack()
    factor_df.index.names = ['dt', 'Ticker']
    return factor_df

def data_output(date_interval, df, factor_path, factor_name, append=False, dataset=None):
    # 因子数据输出
    # date_interval:list, [20190101, 20191231], 因子数据输出的区间
    # df:DataFrame, index为['dt', 'Ticker']的双标签形式， column为因子列
    # factor_path: string, 因子数据输出路径
    # factor_name: string, 因子名称
    # append: bool, 默认False, 是否在已有数据上追加数据
    # dataset: string, 默认None, None则使用factor_name作为dataset
    if dataset is None:
        dataset = factor_name
    df_tradingday = pd.Series(df.index.get_level_values(0))
    start_timestamp, end_timestamp = pd.Timestamp(str(date_interval[0])), pd.Timestamp(str(date_interval[1]))
    df = df[np.array((start_timestamp<=df_tradingday) & (df_tradingday<=end_timestamp))]
    if not os.path.exists(factor_path):
        os.makedirs(factor_path)
    if append:
        IO.pd_hdf5_writer(df, hdf5='%s%s_%d_%d.h5' % (factor_path, factor_name, date_interval[0], date_interval[1]), dataset=dataset, append=True)
    elif not os.path.exists(factor_path + '%s_%d_%d.h5'%(factor_name, date_interval[0], date_interval[1])):
        IO.pd_hdf5_writer(df, hdf5='%s%s_%d_%d.h5'%(factor_path, factor_name, date_interval[0], date_interval[1]), dataset=dataset)
    else:
        IO.pd_hdf5_writer(df, hdf5='%s%s_%d_%d.h5' % (factor_path, factor_name, date_interval[0], date_interval[1]), dataset=dataset, override=True)
    return df


import sys


def view_bar(num, tot, s):
    rate = (num + 1) / (tot)
    rate_num = (int(rate * 100))
    n = rate_num // 3
    r = '\r[%s>%s]%d%%-%s' % ('=' * n, '-' * (33 - n), rate_num, s)
    sys.stdout.write(r)
    sys.stdout.flush()
    if rate == 1:
        print('\n')

def second_data_output(date_interval, df, factor_path, factor_name):
    dataset = factor_name

    df_tradingday = pd.Series(df.index.get_level_values(0))
    start_timestamp, end_timestamp = pd.Timestamp(str(date_interval[0])), pd.Timestamp(str(date_interval[1]))
    df = df[np.array((start_timestamp <= df_tradingday) & (df_tradingday <= end_timestamp))].astype(float)

    import os
    file_path = factor_path + '%s.h5'%(factor_name)
    if os.path.exists(file_path):
        IO.pd_hdf5_writer(df, file_path, dataset=dataset, append=True)
        df = pd.read_hdf(file_path).sort_index()
        IO.pd_hdf5_writer(df, file_path, dataset=dataset, override=True)
    else:
        IO.pd_hdf5_writer(df, file_path, dataset=dataset)

def update_xlsx(factor_list, upload_date):
    # df = pd.read_excel('/data/user/023859/factor_zooZZ/emotion_factor_inf.xlsx')
    new_factors = {
        "factor_name": [],
        "factor_type": [],
        "factor_owner": [],
        "提交时间": [],
        "emotion": [],
        "t": []
    }
    for factor in factor_list:
        new_factors['factor_name'].append(factor[7:])
        new_factors['factor_type'].append('IndexTTick')
        new_factors['factor_owner'].append('tsq')
        new_factors['提交时间'].append(int(upload_date))
        new_factors['emotion'].append(1)
        new_factors['t'].append('T')

    new_factors_df = pd.DataFrame(new_factors)
    df = new_factors_df
    # df = pd.concat([df, new_factors_df])
    df = df[['factor_name', 'factor_type', 'factor_owner', '提交时间', 'emotion', 't']]
    df.to_excel('/data/user/023859/factor_zooZZ/emotion_factor_inf_sa.xlsx', index=False)
    return

def run_factor(func, factor_name, factor_type, start_date, end_date, basic_file_path, result_path, append_next_tradingday=False, interval_res=True,
               t=None, last_factor_dic = None,
               data_path_dic={'IndexTTick': '/dfs/group/800463/data/index_data/ZZ1000/'}):
    # 因子代码执行函数
    # func: function, 所需执行的因子计算函数
    # factor_name: string, 计算的因子名称
    # factor_type: string, 计算的因子类别，目前包括:TTransaction(逐笔成交类因子)/TTickab(盘口行情类因子)/T-1_factor(T-1日类因子)
    # start_date: int, 因子数据计算开始日期
    # end_date: int, 因子数据计算结束日期
    # basic_file_path: string, 样本数据的路径
    # result_path: string, 因子输出的路径
    # append_next_tradingday: string, 默认False, 是否要增加最新的日期，对于实盘的T-1日因子需要设为True, 其余则为False
    # data_path_dic: dict, 为因子计算所需的高频数据路径来源的字典查询文件
    if basic_file_path.endswith('.h5'):
        basic_df = IO.read_data([start_date, end_date], alt=basic_file_path)
    else:
        basic_df = pd.read_pickle(basic_file_path).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    if factor_type in ['IndexTTick']:
        tradingday_list = list(map(lambda x: x.strftime('%Y%m%d'), basic_df.index.get_level_values(0).drop_duplicates()))
        factor_df_list = []
        for i in range(len(tradingday_list)):
            tradingday = tradingday_list[i]
            view_bar(i, len(tradingday_list), tradingday)
            data = pd.read_pickle('%s%s.pkl' % (data_path_dic[factor_type], tradingday))
            if 'TotalValueTrade' in data.columns:
                data['TotalValueTrade'] = data['TotalValueTrade'].apply(np.floor)

            tmp_df = pd.DataFrame(index=basic_df.loc[pd.to_datetime(tradingday):pd.to_datetime(tradingday)].index)
            tmp_df[factor_name] = func(data)[factor_name]
            factor_df_list.append(pd.concat([tmp_df], axis=1))
        factor_df = pd.concat(factor_df_list, axis=0)
        factor_df = factor_df.reindex(basic_df.index)
        fill_dic = func(None, return_fillna_dic=True)
        result_df = factor_df.fillna(fill_dic)

    if interval_res:
        data_output([start_date, end_date], result_df, result_path, factor_name=factor_name)
    else:
        second_data_output([start_date, end_date], result_df, result_path, factor_name=factor_name)


if __name__ == '__main__':
    start_date, end_date = 20170110, 20241231
    basic_file_path = '/dfs/user/023859/neptune/20250627/basic_file_zz1000_sa_20170110_20241231.pkl'
    result_path = f'/dfs/user/023859/neptune/20250627/index_emotion_factors/{start_date}_{end_date}/'
    os.makedirs(result_path, exist_ok=True)
    # import factor.factor_tsq_newneptune_index_emotion_5 as func_tmp
    # run_factor(func_tmp.factor_tsq_newneptune_index_emotion_5, 'tsq_newneptune_index_emotion_5', 'IndexTTick',
    #            start_date, end_date, basic_file_path, result_path, interval_res=False)
    factor_list = [f'factor_tsq_newneptune_sa_index_emotion_{i}' for i in range(1,15)]
    # 是否更新可用因子列表
    append_factor_inf = True
    upload_date = '20250627'
    if append_factor_inf:
        update_xlsx(factor_list, upload_date)
    for factor_name in factor_list:
        module = importlib.import_module(f'factor.{factor_name}')
        func_tmp = getattr(module, factor_name)
        run_factor(func_tmp, factor_name[7:], 'IndexTTick',
                   start_date, end_date, basic_file_path, result_path, interval_res=False)

