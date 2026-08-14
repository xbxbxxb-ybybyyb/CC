import json
import numpy as np
import pandas as pd
import copy
import IO as IO
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

def run_factor(func, factor_name, factor_type, start_date, end_date, basic_file_path, result_path, append_next_tradingday=False, interval_res=True,
               t=None, last_factor_dic = None,
               data_path_dic={'TTransaction': '/data/group/800463/data/project2_prod/everyday_Data/transaction/',
                              'TTickab':'/data/group/800463/data/project2_prod/everyday_Data/tick/',
                              'TOrder':'/data/group/800463/data/project2_prod/everyday_Data/order_cs/',

                              'LastZtLastTick':'/data/group/800463/data/project2_prod/everyday_Data/last_zt_tick/',
                              'LastZtLastTick_cs':'/data/group/800463/data/project2_prod/everyday_Data/last_zt_tick/',
                              'LastZtLastTrans':'/data/group/800463/data/project2_prod/everyday_Data/last_zt_trans/',
                              'LastZtLastTrans_cs':'/data/group/800463/data/project2_prod/everyday_Data/last_zt_trans/',
                              'LastZtLastOrder':'/data/group/800463/data/project2_prod/everyday_Data/last_zt_order/',
                              'LastZtLastOrder_cs':'/data/group/800463/data/project2_prod/everyday_Data/last_zt_order/',
                              'LastZtLastTrans_BeforeZt':'/data/group/800463/data/project2_prod/everyday_Data/last_zt_trans/',

                              'T1mTransaction':'/data/group/800463/data/project2_prod/everyday_Data_931/transaction/',
                              'T1mTickab':'/data/group/800463/data/project2_prod/everyday_Data_931/tick/',
                              'T1mOrder': '/data/group/800463/data/project2_prod/everyday_Data_931/order_cs/',

                              'T10mTransaction':'/data/group/800463/data/project2_prod/everyday_Data_940/transaction/',
                              'T10mTickab':'/data/group/800463/data/project2_prod/everyday_Data_940/tick/',

                              'TTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data/transaction_cs/',
                              'TTickab_cs':'/data/group/800463/data/project2_prod/everyday_Data/tick_cs/',
                              'TOrder_cs':'/data/group/800463/data/project2_prod/everyday_Data/order_cs/',

                              'T1mTransaction_cs':'/data/group/800463/data/project2_prod/everyday_Data_931/transaction_cs/',
                              'T1mTickab_cs':'/data/group/800463/data/project2_prod/everyday_Data_931/tick_cs/',
                              'T1mOrder_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/order_cs/',
                              'T10mTransaction_cs':'/data/group/800463/data/project2_prod/everyday_Data_940/transaction_cs/',
                              'T10mTickab_cs':'/data/group/800463/data/project2_prod/everyday_Data_940/tick_cs/',}):
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
    basic_df = IO.read_data([start_date, end_date], alt=basic_file_path)
    if factor_type in  ['TTransaction', 'TTickab','T1mTransaction','T1mTickab','T10mTransaction','T10mTickab',
                        'TTransaction_cs', 'TTickab_cs', 'T1mTransaction_cs','T1mTickab_cs','T10mTransaction_cs','T10mTickab_cs',
                        'TOrder', 'T1mOrder', 'T10mOrder', 'TOrder_cs', 'T1mOrder_cs', 'T10mTickab_cs']:
        tradingday_list = list(map(lambda x: x.strftime('%Y%m%d'),basic_df.index.get_level_values(0).drop_duplicates()))
        # factor_df_list = []
        # for i in range(len(tradingday_list)):
        def cal_T_factors(i):
            tradingday = tradingday_list[i]
            view_bar(i,len(tradingday_list),tradingday)
            data = pd.read_pickle('%s%s.pkl'%(data_path_dic[factor_type], tradingday))
            if factor_type[-2:] == 'cs':
                tem0=data.groupby(level=[0, 1]).agg('first') #先保留日期股票列表
                data=data[data['lzt_label_pattern'].isin([3,4])]#再进行策略样本筛选
                data = data[data['after_not_ul_len'] > 10]
                tmp_df = data.groupby(level=[0]).apply(lambda x: func(x))
                if len(tmp_df)==0:
                    tmp_df = pd.DataFrame(columns=[factor_name])
                tmp_df=tmp_df.reindex(tem0.index)
            else:
                if (t=='t') and (last_factor_dic is not  None):
                    tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x, last_value=last_factor_dic[x.iloc[0].name]))
                else:
                    tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x))
            return tmp_df
        from joblib import Parallel, delayed
        factor_df_list = Parallel(n_jobs=16)(delayed(cal_T_factors)(i) for i in range(len(tradingday_list)))
            # factor_df_list.append(pd.concat([tmp_df], axis=1))
        factor_df = pd.concat(factor_df_list, axis=0)
        # 使用样本数据进行reindex，防止计算出的因子中样本缺失
        factor_df = factor_df.reindex(basic_df.index)
        # 使用因子计算函数中的fillna进行异常值填充, inf的填充则在计算函数内部进行处理
        fill_dic = func(None, return_fillna_dic=True)
        result_df = factor_df.fillna(fill_dic)
        if t == 't':
            return result_df
    elif factor_type in ['T-1_factor','other']:
        factor_df = func(start_date, end_date, IO)
        factor_df = fun_append_next_tradingday(factor_df)
        result_df = pd.DataFrame(index=basic_df.index)
        for factor_col in factor_df.columns:
            result_df[factor_col] = factor_df[factor_col].unstack().shift(1).stack()
        # 使用因子计算函数中的fillna进行异常值填充, inf的填充则在计算函数内部进行处理
        fill_dic = func(None, None, None, return_fillna_dic=True)
        result_df = result_df.fillna(fill_dic)
    elif factor_type in ['LastZtLastTick', 'LastZtLastTrans', 'LastZtLastTick_cs', 'LastZtLastTrans_cs', 'LastZtLastOrder', 'LastZtLastOrder_cs',
                         'LastZtLastTrans_BeforeZt']:
        # 更改逻辑，获取last_zt_date_list然后进行计算然后reindex：
        last_zt_list = list(np.unique(basic_df['dt_last_zt_1'].apply(lambda x: str(int(x)))))
        factor_df_list = []
        # for i in range(len(last_zt_list)):
        def cal_T_factors(i):
            tradingday = last_zt_list[i]
            view_bar(i,len(last_zt_list),tradingday)
            if os.path.exists('%s%s.pkl' % (data_path_dic[factor_type], tradingday)) == False:
                print(tradingday, 'last tradingday not exist!')  # 在2016年之前复牌的就不计算了
                return None
                # continue
            else:
                data = pd.read_pickle('%s%s.pkl' % (data_path_dic[factor_type], tradingday))
            if factor_type[-2:] == 'cs':
                tem0 = data.groupby(level=[0, 1]).agg('first')  # 先保留日期股票列表
                data = data[data['pattern'].isin([3, 4])]  # 再进行策略样本筛选
                data = data[data['after_not_ul_len'] > 10]
                tmp_df = data.groupby(level=[0]).apply(lambda x: func(x))
                if len(tmp_df) == 0:
                    tmp_df = pd.DataFrame(columns=[factor_name])
                tmp_df = tmp_df.reindex(tem0.index)
            else:
                if t=='last':
                    tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x, t='last')) # 计算跨日因子的前日数据
                else:
                    if factor_type=='LastZtLastTrans_BeforeZt':
                        tem0 = data.groupby(level=[0, 1]).agg('first')  # 先保留日期股票列表
                        data =data[(data['pattern'].isin([3, 4]))&(data['TradeType']!=10)]  # 去除开盘涨停
                        data['zt_price'] = data.groupby(['dt', 'Ticker'])['TradePrice'].max()
                        data['cummax'] = data.groupby(['dt', 'Ticker'])['TradePrice'].cummax()
                        data['cummax_shift'] = data.groupby(['dt', 'Ticker'])['cummax'].shift(1).fillna(0)
                        data = data[data['cummax_shift']<data['zt_price']]#首次涨停前的数据
                        tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x))
                        if len(tmp_df) == 0:
                            tmp_df = pd.DataFrame(columns=[factor_name])
                        tmp_df = tmp_df.reindex(tem0.index)
                    else:
                        tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x))
            fill_dic = func(None, return_fillna_dic=True)
            if t != 'last':
                tmp_df = tmp_df.fillna(fill_dic)
            return tmp_df
            # factor_df_list.append(pd.concat([tmp_df], axis=1))
        from joblib import Parallel,delayed
        factor_df_list = Parallel(n_jobs=16)(delayed(cal_T_factors)(i) for i in range(len(last_zt_list)))

        factor_df = pd.concat(factor_df_list, axis=0)
        factor_df = fun_append_next_tradingday(factor_df)  # last_zt_tick类因子一定要加一个交易日到后面
        result_df = pd.DataFrame()
        # 这一步进行进行shift
        for factor_col in factor_df.columns:
            if t=='last':
                result_df['last_'+factor_col] = factor_df[factor_col].unstack().fillna(method='ffill').shift(1).stack()  # fillna为了让停牌的股票有因子值
            else:
                result_df[factor_col] = factor_df[factor_col].unstack().fillna(method='ffill').shift(1).stack()
        # 使用样本数据进行reindex，防止计算出的因子中样本缺失
        result_df = result_df.reindex(basic_df.index)  # 这里与常规的不一样
        fill_dic = func(None, return_fillna_dic=True)
        if t!='last':
            result_df = result_df.fillna(fill_dic)
        if (t=='last') and (append_next_tradingday==False):
            return result_df
    elif factor_type in ['T_factor','T_factor_931','T_factor_940']:
        factor_df = func(start_date, end_date, IO)
        result_df = factor_df.reindex(basic_df.index)
        # 使用因子计算函数中的fillna进行异常值填充, inf的填充则在计算函数内部进行处理
        fill_dic = func(None, None, None, return_fillna_dic=True)
        result_df = result_df.fillna(fill_dic)
    elif factor_type in ['CrossTT', 'CrossTK', 'CrossKK', 'CrossKT', 'CrossTT1', 'CrossTK1', 'CrossKK1', 'CrossKT1']:
        trans_dic = {'last':{'T':'LastZtLastTrans', 'K':'LastZtLastTick'},
                     't':{'T':'TTransaction', 'K':'TTickab', 'T1':'T1mTransaction', 'K1':'T1mTickab'}}
        last_data_type, t_data_type = trans_dic['last'][factor_type[5]], trans_dic['t'][factor_type[6:]]
        last_factor_df = run_factor(func, 'last_'+factor_name, last_data_type, start_date, end_date, basic_file_path, result_path, append_next_tradingday, interval_res, t='last')
        if append_next_tradingday == False: #非日常更新的情况
            last_factor_dic = dict(last_factor_df['last_'+factor_name])
            result_df = run_factor(func, factor_name, t_data_type, start_date, end_date, basic_file_path, result_path, append_next_tradingday, interval_res, t='t', last_factor_dic=last_factor_dic)
        else:
            result_df = last_factor_df
            factor_name = 'last_'+factor_name
    if interval_res:
        data_output([start_date, end_date], result_df, result_path, factor_name=factor_name)
    else:
        second_data_output([start_date, end_date], result_df, result_path, factor_name=factor_name)
    return result_df

if __name__ == '__main__':
    start_date, end_date = 20160101, 20191231
    basic_file_path = '/data/group/800463/data/project2_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5'
    result_path = '/data/user/018107/tmp/'
    import project2_lib.public.factor_test_last_factor as func_tmp
    factor_df0 = run_factor(func_tmp.factor_test_last_factor, 'test_last_factor', 'T-1_factor',
                           start_date, end_date, basic_file_path, result_path,interval_res=False)
