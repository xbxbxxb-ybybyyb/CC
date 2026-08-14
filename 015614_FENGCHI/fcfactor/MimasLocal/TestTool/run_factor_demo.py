# coding: utf-8
# Author：fengchi863
# Date ：2023/7/4 20:11

import json
import numpy as np
import pandas as pd
import copy
import IO as IO
import datetime as dt
import gc
import time
import importlib
from datetime import datetime, timedelta
from joblib import Parallel, delayed

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

def wrapper(func, factor_type, basic_df, data_path_dic, tradingday, t, last_factor_dic, param_tuple):
    if factor_type in ['NextTickab','NextTickab_cs','NextTransaction','NextTransaction_cs',
                        'Next1mTickab','Next1mTickab_cs','Next1mTransaction','Next1mTransaction_cs']:
        data = pd.read_pickle('%s%s.pkl'%(data_path_dic[factor_type], tradingday))
        if factor_type[-2:] == 'cs':
            tem0 = data.groupby(level=[0, 1]).agg('first')  # 先保留日期股票列表
            data = data[data['lzt_label_pattern'].isin([3, 4])]  # 再进行策略样本筛选
            data = data[data['after_not_ul_len'] > 10]
            tmp_df = data.groupby(level=[0]).apply(lambda x: func(x, param_tuple=param_tuple))
            if len(tmp_df) == 0:
                tmp_df = pd.DataFrame(columns=[factor_name])
            tmp_df = tmp_df.reindex(tem0.index)
        else:
            if (t == 't') and (last_factor_dic is not None):
                tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x, param_tuple=param_tuple, last_value=last_factor_dic[x.iloc[0].name]))
            else:
                tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x, param_tuple=param_tuple))
    elif factor_type in ['TallTick','TallTick_cs','TallTrans','TallTrans_cs']:
        if not os.path.exists('%s%s.pkl' % (data_path_dic[factor_type], tradingday)):
            print(tradingday, 'last tradingday not exist!')  # 在2016年之前复牌的就不计算了
            return
        else:
            data = pd.read_pickle('%s%s.pkl' % (data_path_dic[factor_type], tradingday))
        if factor_type[-2:] == 'cs':
            tem0 = data.groupby(level=[0, 1]).agg('first')  # 先保留日期股票列表
            data = data[data['pattern'].isin([3, 4])]  # 再进行策略样本筛选
            data = data[data['after_not_ul_len'] > 10]
            tmp_df = data.groupby(level=[0]).apply(lambda x: func(x, param_tuple=param_tuple))
            if len(tmp_df) == 0:
                tmp_df = pd.DataFrame(columns=[factor_name])
            tmp_df = tmp_df.reindex(tem0.index)
        else:
            if t == 'last':
                tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x, param_tuple=param_tuple, t='last'))  # 计算跨日因子的前日数据
            else:
                tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x, param_tuple=param_tuple))
    return tmp_df

def run_factor(func, factor_name, factor_type, start_date, end_date, basic_file_path, result_path, append_next_tradingday=False, interval_res=True,
               t=None, last_factor_dic = None,
               data_path_dic={'NextTickab':'/data/group/800463/data/project2_prod/everyday_Data/next_tick_cs/',
                              'NextTickab_cs':'/data/group/800463/data/project2_prod/everyday_Data/next_tick_cs/',
                              'NextTransaction': '/data/group/800463/data/project2_prod/everyday_Data/next_transaction_cs/',
                              'NextTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data/next_transaction_cs/',

                              'Next1mTickab':'/data/group/800463/data/project2_prod/everyday_Data_931/next_tick_cs/',
                              'Next1mTickab_cs':'/data/group/800463/data/project2_prod/everyday_Data_931/next_tick_cs/',
                              'Next1mTransaction':'/data/group/800463/data/project2_prod/everyday_Data_931/next_transaction_cs/',
                              'Next1mTransaction_cs':'/data/group/800463/data/project2_prod/everyday_Data_931/next_transaction_cs/',

                              'TallTick':'/data/group/800463/data/project2_prod/everyday_Data/all_tick_cs/',
                              'TallTick_cs':'/data/group/800463/data/project2_prod/everyday_Data/all_tick_cs/',
                              'TallTrans':'/data/group/800463/data/project2_prod/everyday_Data/all_transaction_cs/',
                              'TallTrans_cs':'/data/group/800463/data/project2_prod/everyday_Data/all_transaction_cs/',}, param_tuple=(), multi=False):
    # 因子代码执行函数
    # func: function, 所需执行的因子计算函数
    # factor_name: string, 计算的因子名称
    # factor_type: string, 计算的因子类别
    # start_date: int, 因子数据计算开始日期
    # end_date: int, 因子数据计算结束日期
    # basic_file_path: string, 样本数据的路径
    # result_path: string, 因子输出的路径
    # append_next_tradingday: string, 默认False, 是否要增加最新的日期，对于实盘的T-1日因子需要设为True, 其余则为False
    # data_path_dic: dict, 为因子计算所需的高频数据路径来源的字典查询文件
    basic_df = IO.read_data([start_date, end_date], alt=basic_file_path)
    if factor_type in  ['NextTickab','NextTickab_cs','NextTransaction','NextTransaction_cs',
                        'Next1mTickab','Next1mTickab_cs','Next1mTransaction','Next1mTransaction_cs']:
        tradingday_list = list(map(lambda x: x.strftime('%Y%m%d'),basic_df.index.get_level_values(0).drop_duplicates()))
        factor_df_list = []
        if not multi:
            for i in range(len(tradingday_list)):
                tradingday = tradingday_list[i]
                # print(tradingday)
                view_bar(i,len(tradingday_list),tradingday)
                data = pd.read_pickle('%s%s.pkl'%(data_path_dic[factor_type], tradingday))
                if factor_type[-2:] == 'cs':
                    tem0=data.groupby(level=[0, 1]).agg('first') #先保留日期股票列表
                    data=data[data['lzt_label_pattern'].isin([3,4])]#再进行策略样本筛选
                    data = data[data['after_not_ul_len'] > 10]
                    tmp_df = data.groupby(level=[0]).apply(lambda x: func(x, param_tuple=param_tuple))
                    if len(tmp_df)==0:
                        tmp_df = pd.DataFrame(columns=[factor_name])
                    tmp_df=tmp_df.reindex(tem0.index)
                else:
                    if (t=='t') and (last_factor_dic is not  None):
                        tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x, param_tuple=param_tuple, last_value=last_factor_dic[x.iloc[0].name]))
                    else:
                        tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x, param_tuple=param_tuple))
                factor_df_list.append(pd.concat([tmp_df], axis=1))
        else:
            import time
            t1 = time.time()
            job_list = list()
            for tradingday, num in zip(tradingday_list, range(len(tradingday_list))):
                job_list.append(delayed(wrapper)(func, factor_type, basic_df, data_path_dic, tradingday, t, last_factor_dic, param_tuple))
            factor_df_list = Parallel(n_jobs=24, backend='multiprocessing')(job_list)
            print('因子计算耗时：', time.time() - t1)

        factor_df = pd.concat(factor_df_list, axis=0)
        # 使用样本数据进行reindex，防止计算出的因子中样本缺失
        factor_df = factor_df.reindex(basic_df.index)
        # 使用因子计算函数中的fillna进行异常值填充, inf的填充则在计算函数内部进行处理
        fill_dic = func(None, param_tuple=param_tuple, return_fillna_dic=True)
        result_df = factor_df.fillna(fill_dic)
        if t == 't':
            return result_df
    elif factor_type in ['Next_T-1_factor','other']:
        factor_df = func(start_date, end_date, IO, param_tuple)
        factor_df = fun_append_next_tradingday(factor_df)
        result_df = pd.DataFrame(index=basic_df.index)
        for factor_col in factor_df.columns:
            result_df[factor_col] = factor_df[factor_col].unstack().shift(1).stack()
        # 使用因子计算函数中的fillna进行异常值填充, inf的填充则在计算函数内部进行处理
        fill_dic = func(None, None, None, param_tuple=param_tuple, return_fillna_dic=True)
        result_df = result_df.fillna(fill_dic)
    elif factor_type in ['TallTick','TallTick_cs','TallTrans','TallTrans_cs']:
        # 更改逻辑，获取last_zt_date_list然后进行计算然后reindex：
        last_zt_list = list(np.unique(basic_df['dt_last_saturn'].apply(lambda x: str(int(x)))))
        factor_df_list = []
        if not multi:
            for i in range(len(last_zt_list)):
                tradingday = last_zt_list[i]
                view_bar(i,len(last_zt_list),tradingday)
                if os.path.exists('%s%s.pkl' % (data_path_dic[factor_type], tradingday)) == False:
                    print(tradingday, 'last tradingday not exist!')  # 在2016年之前复牌的就不计算了
                    continue
                else:
                    data = pd.read_pickle('%s%s.pkl' % (data_path_dic[factor_type], tradingday))
                if factor_type[-2:] == 'cs':
                    tem0 = data.groupby(level=[0, 1]).agg('first')  # 先保留日期股票列表
                    data = data[data['lzt_label_pattern'].isin([3, 4])]  # 再进行策略样本筛选
                    data = data[data['after_not_ul_len'] > 10]
                    tmp_df = data.groupby(level=[0]).apply(lambda x: func(x))
                    if len(tmp_df) == 0:
                        tmp_df = pd.DataFrame(columns=[factor_name])
                    tmp_df = tmp_df.reindex(tem0.index)
                else:
                    if t=='last':
                        tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x, param_tuple=param_tuple, t='last')) # 计算跨日因子的前日数据
                    else:
                        tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x, param_tuple=param_tuple))
                fill_dic = func(None, param_tuple=param_tuple, return_fillna_dic=True)
                if t != 'last':
                    tmp_df = tmp_df.fillna(fill_dic)
                factor_df_list.append(pd.concat([tmp_df], axis=1))
        else:
            import time
            t1 = time.time()
            job_list = list()
            for tradingday, num in zip(last_zt_list, range(len(last_zt_list))):
                tradingday = last_zt_list[num]
                job_list.append(delayed(wrapper)(func, factor_type, basic_df, data_path_dic, tradingday, t, last_factor_dic, param_tuple))
            factor_df_list = Parallel(n_jobs=24, backend='multiprocessing')(job_list)
            print('因子计算耗时：', time.time() - t1)

        factor_df = pd.concat(factor_df_list, axis=0)
        factor_df = fun_append_next_tradingday(factor_df)
        result_df = pd.DataFrame()
        # 这一步进行进行shift
        for factor_col in factor_df.columns:
            if t=='last':
                result_df['last_'+factor_col] = factor_df[factor_col].unstack().fillna(method='ffill').shift(1).stack()  # fillna为了让停牌的股票有因子值
            else:
                result_df[factor_col] = factor_df[factor_col].unstack().fillna(method='ffill').shift(1).stack()
        # 使用样本数据进行reindex，防止计算出的因子中样本缺失
        result_df = result_df.reindex(basic_df.index)  # 这里与常规的不一样
        fill_dic = func(None, param_tuple=param_tuple, return_fillna_dic=True)
        if t!='last':
            result_df = result_df.fillna(fill_dic)
        if (t=='last') and (append_next_tradingday==False):
            return result_df
    if interval_res:
        data_output([start_date, end_date], result_df, result_path, factor_name=factor_name)
    else:
        second_data_output([start_date, end_date], result_df, result_path, factor_name=factor_name)
    return result_df


if __name__ == '__main__':
    print('------------------开始跑因子-------------------')
    print('当前时间', dt.datetime.now().strftime('%H%M%S'))
    t1 = time.time()
    start_date, end_date = 20160101, 20191231
    basic_file_path = '/data/group/800463/data/project2_public/next_factor_lib/Basic_next_hf_finish_20160101_20191231.h5'
    result_path = '/data/user/015614/factor/'

    factor_df = pd.DataFrame()
    date = 20230803
    # TTransaction TOrder TTickab TTransaction_TOrder T-1_factor False True

    factor_type, no, multi = 'Next_T-1_factor', 1, False
    # factor_type, no, multi = 'Next1mTransaction', 1, True
    # factor_type, no, multi = 'TallTrans', 1, True
    # factor_type, no, multi = 'TallTick', 4, True
    print(factor_type, f'no=={no}')

    if factor_type == 'Next_T-1_factor':
        mod_name = f'MimasLocal.d{date}.factor_fc_nextT1_{no}'
        module = importlib.import_module(mod_name)
        func = getattr(module, f'factor_fc_nextT1_{no}')
        factor_name = f'fc_nextT1_{no}'
        factor_df = run_factor(func, factor_name, factor_type, start_date, end_date, basic_file_path, result_path, param_tuple=(), interval_res=False, multi=multi)
    elif factor_type in ['NextTickab','NextTickab_cs','NextTransaction','NextTransaction_cs',
                        'Next1mTickab','Next1mTickab_cs','Next1mTransaction','Next1mTransaction_cs',
                         'TallTick','TallTick_cs','TallTrans','TallTrans_cs']:
        mod_name = f'MimasLocal.d{date}.factor_fc_{factor_type}_{no}'
        module = importlib.import_module(mod_name)
        func = getattr(module, f'factor_fc_{factor_type}_{no}')
        factor_name = f'fc_{factor_type}_{no}'
        factor_df = run_factor(func, factor_name, factor_type, start_date, end_date, basic_file_path, result_path, param_tuple=(), interval_res=False, multi=multi)

    print('开始因子测试...')
    start_date, end_date = 20180101, 20191231
    factor_df2 = run_factor(func, factor_name, factor_type, start_date, end_date, basic_file_path, result_path, param_tuple=(), interval_res=False, multi=multi)
    check1 = factor_df.loc[pd.to_datetime('20180102')]
    check2 = factor_df2.loc[pd.to_datetime('20180102')]
    from MimasLocal.TestTool.project_2_factor_test_origin import pj2FactorTest
    # factor_test = pj2FactorTest(start_date, end_date)
    # factor_fpath = result_path + factor_name + '.h5'
    # factor_df = pd.read_hdf(factor_fpath)
    # factor_test.factor_test(factor_df, result_path, factor_corr_test=True)
    #
    # print('计算本地高相关：')
    # week_local_factors = list(filter(lambda x: str(x).endswith('.h5'), os.listdir('/data/user/015614/factor/')))
    # for factor_fname in week_local_factors:
    #     if factor_fpath.endswith(factor_fname):
    #         continue
    #     tmp_factor = pd.read_hdf('/data/user/015614/factor/' + factor_fname)
    #     corr = tmp_factor.iloc[:, 0].corr(factor_df.iloc[:, 0], method='spearman')
    #     if corr > 0.7:
    #         print(factor_fname, corr)
    #
    # print('回测耗时', time.time() - t1)
    # print(factor_df.describe())