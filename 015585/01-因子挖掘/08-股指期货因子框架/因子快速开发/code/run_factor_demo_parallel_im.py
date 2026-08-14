# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
import IO as IO
import datetime as dt

s = FactorData()
def fun_get_time(time1,sec_delta):
    #计算给定时间戳time1在sec_delta秒后的时间戳
    tmp_time = dt.datetime.strptime(str(time1)[:-3],'%H%M%S')
    tmp_time2 = tmp_time+dt.timedelta(seconds=sec_delta)
    tmp_time2_str = tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
    if (int(tmp_time2_str)>113000000)&(time1<=113000000):
        adj_tmp_time2 = tmp_time2+dt.timedelta(seconds=1.5*3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str)<130000000)&(time1>=130000000):
        adj_tmp_time2 = tmp_time2-dt.timedelta(seconds=1.5*3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str)<93000000)&(time1>=93000000):
        adj_tmp_time2_str = '92500000'
        return int(adj_tmp_time2_str)
    elif (time1<93000000):
        adj_tmp_time2 = tmp_time2+dt.timedelta(seconds=4*60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)

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

def second_output(out_file_path, df):
    if not os.path.exists(out_file_path):
        df.to_pickle(out_file_path)
    else:
        old = pd.read_pickle(out_file_path)
        repeat_index = list(set(old.index) & set(df.index))
        repeat_index.sort()

        old = old[np.array(pd.Series(old.index).apply(lambda x:x not in repeat_index))]
        old = old.append(df).sort_index()
        old.to_pickle(out_file_path)

        repeat_index = [int(index.strftime('%Y%m%d')) for index in repeat_index]
        print('delete repeat index:', repeat_index)

        new_index = list(df.index)
        new_index = [int(index.strftime('%Y%m%d')) for index in new_index]
        print('append new index:', new_index)

def view_bar(num, tot, s):
    # 进度条函数
    import sys
    rate = (num+1) / tot
    rate_num = (int(rate * 100))
    n = rate_num // 3
    r = '\r[%s>%s]%d%%-%s' % ('=' * n, '-' * (33 - n), rate_num, s)
    sys.stdout.write(r)
    sys.stdout.flush()
    if rate == 1:
        print('\n')

def run_factor(func, factor_name, factor_type, start_date, end_date, basic_file_path, result_path, append_next_tradingday=False, interval_res=True,
               data_path_dic= {
                               'TTickab30s': '/dfs/group/800463/data/projectF_prod/IM_tick/',
                               }):
    if factor_type in ['TTickab30s']:
        # 期货因子
        end_date_ = (pd.Timestamp(str(end_date)) + pd.Timedelta(days=1)).strftime('%Y%m%d') # 带时分秒之后，end_date要后延一天，否则最后一天取不到，因为默认是到end_date的0时0分0秒
        basic_df = IO.read_data([int(start_date), int(end_date_)], alt=basic_file_path)
        tradingday_list = list(set(map(lambda x: x.strftime('%Y%m%d'),basic_df.index.get_level_values(0).drop_duplicates())))
        tradingday_list.sort()
        # print(tradingday_list)
        def calc_tmp_df(tradingday, num):
            view_bar(num, len(tradingday_list), tradingday)
            data_path = f'{data_path_dic[factor_type]}{tradingday}/'
            file_time_list = os.listdir(data_path)
            list_factor_value_date = []
            for file in file_time_list:
                data = pd.read_pickle(f'{data_path}{file}')
                factor_value_date_time = data.groupby(['cuttime','Ticker']).apply(lambda x: func(x))
                list_factor_value_date.append(factor_value_date_time)
            factor_value_date = pd.concat(list_factor_value_date).reset_index().sort_values(['cuttime','Ticker'])
            def trans_time(x): # x=94530000
                x = str(x).zfill(9)
                res = f'{x[:2]}:{x[2:4]}:{x[4:6]}'
                return res
            factor_value_date['dt'] = factor_value_date['cuttime'].apply(lambda x : pd.Timestamp(f'{tradingday} {trans_time(x)}'))
            factor_value_date = factor_value_date.set_index(['dt','Ticker'])[[factor_name]]
            return factor_value_date
        from joblib import Parallel, delayed
        factor_df_list = Parallel(n_jobs=30)(delayed(calc_tmp_df)(tradingday, num) for tradingday, num in
                                             zip(tradingday_list, range(len(tradingday_list))))
        factor_df = pd.concat(factor_df_list, axis=0)
        factor_df = factor_df.reindex(basic_df.index)
        # 使用因子计算函数中的fillna进行异常值填充, inf的填充则在计算函数内部进行处理
        fill_dic = func(None, return_fillna_dic=True)
        result_df = factor_df.fillna(fill_dic)
        if interval_res:
            data_output([start_date, end_date_], result_df, result_path, factor_name=factor_name) # 注意end_date要改写，向后延一天，避开时分秒导致的问题
        else:
            second_data_output([start_date, end_date_], result_df, result_path, factor_name=factor_name) # 注意end_date要改写，向后延一天，避开时分秒导致的问题
        return result_df

if __name__ == '__main__':
    start_date, end_date = 20220801, 20250430 #因子的样本内区间：
    basic_file_path = '/dfs/user/015585/00_股指期货策略/Basic_future_20220801_20250430.h5'
    result_path = '/data/user/015585/01-因子挖掘/08-neptune/future_factor_20250523/'
    from factor_qyh_future_sample10 import factor_qyh_future_sample10
    factor_df0 = run_factor(factor_qyh_future_sample10, 'qyh_future_sample10', 'TTickab30s',
                           start_date, end_date, basic_file_path, result_path,interval_res=False)






