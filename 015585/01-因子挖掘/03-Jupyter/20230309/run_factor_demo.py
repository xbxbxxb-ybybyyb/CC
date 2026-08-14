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
               emotion_data = {'Basic_zt':None, 'Label_zt':None},
               data_path_dic= {'TTransaction': '/data/group/800463/data/project1_prod/transaction_test_001_ezt/',
                                'LastTouchTTick':'/data/group/800463/data/project1_prod/last_touch_t_tick/',
                                'MarketTTick':'/data/group/800463/data/project1_prod/market_t_tick/',
                                'Market1TTick':'/data/group/800463/data/project1_prod/market_t_tick/',
                                'MarketIndTTick':'/data/group/800463/data/project1_prod/market_t_tick/',
                               'TOrder':'/data/group/800463/data/project1_prod/order_zt/'}):
    # 因子代码执行函数
    # func: function, 所需执行的因子计算函数
    # factor_name: string, 计算的因子名称
    # factor_type: string, 计算的因子类别，Todo:目前主要开发T-1_factor(T-1日类因子)/TTransaction(逐笔成交类因子)
    # start_date: int, 因子数据计算开始日期
    # end_date: int, 因子数据计算结束日期
    # basic_file_path: string, 样本数据的路径
    # result_path: string, 因子输出的路径
    # append_next_tradingday: 默认False, 是否要增加最新的日期，对于实盘的T-1日因子需要设为True, 其余则为False
    # interval_res：文件名是否需要加上时间区间
    # emotion_data: dict, 为emotion类因子计算所需的数据路径来源的字典查询文件
    # data_path_dic: dict, 为高频类因子计算所需的数据路径来源的字典查询文件

    if factor_type in ['TTransaction', 'T-1_factor','TOrder','LastTouchTTick','MarketTTick','Market1TTick','MarketIndTTick','T-1_Emotion', 'TEmotion']:
        # 个股因子
        basic_df = IO.read_data([start_date, end_date], alt=basic_file_path)
        if factor_type in ['TTransaction', 'TOrder']:
            tradingday_list = s.tradingday(start_date, end_date)
            factor_df_list = []
            for tradingday, num in zip(tradingday_list, range(len(tradingday_list))):
                view_bar(num, len(tradingday_list), tradingday)
                data = pd.read_pickle('%s%s.pkl'%(data_path_dic[factor_type], tradingday))
                tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x))
                factor_df_list.append(pd.concat([tmp_df], axis=1))
            factor_df = pd.concat(factor_df_list, axis=0)
            if factor_type in ['TTransaction']:
                factor_df = factor_df.reindex(basic_df.index)
            elif factor_type in ['TOrder']:
                factor_df = factor_df.reindex(basic_df[basic_df['Flag_SH_SZ']==1].index)
            # 使用因子计算函数中的fillna进行异常值填充, inf的填充则在计算函数内部进行处理
            fill_dic = func(None, return_fillna_dic=True)
            result_df = factor_df.fillna(fill_dic)
        elif factor_type in ['LastTouchTTick', 'MarketTTick','Market1TTick','MarketIndTTick']:
            if factor_type in ['MarketIndTTick']:  # 读取一级行业
                start_date_ = int(s.tradingday(str(start_date), - 5)[0])
                ind_data = IO.read_data([start_date_, end_date], columns=['amt'],
                                        alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
                ind_data['Industry'] = IO.read_data([start_date_, end_date], columns=['Industry'],
                                                    alt='/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')
                ind_data['Industry'] = ind_data['Industry'].unstack().shift(1).stack()

            tradingday_list = s.tradingday(start_date, end_date)
            factor_df_list = []
            basic_list = list(basic_df.groupby(level=0))
            basic_dic = {sample[0].strftime('%Y%m%d'):sample[1] for sample in basic_list}
            for tradingday, num in zip(tradingday_list, range(len(tradingday_list))):
                view_bar(num, len(tradingday_list), tradingday)
                if os.path.exists('%s%s.pkl' % (data_path_dic[factor_type], tradingday)) == False:
                    print(tradingday, 'tradingday not exist!')
                    continue
                else:
                    data = pd.read_pickle('%s%s.pkl' % (data_path_dic[factor_type], tradingday))
                tmp_df_list = []
                for index, inf in basic_dic[tradingday].iterrows():
                    zt_time = inf['ZT_Time']
                    zt_time = max(fun_get_time(int(zt_time), -3), 93000000)
                    filter_data = data[data['MDTime']<zt_time].copy()
                    if factor_type in ['Market1TTick']:
                        #过滤单市场
                        Ticker=index[1]
                        if '.SH' in Ticker:
                            filter_data = filter_data[filter_data['is_SH']]
                        else:
                            filter_data = filter_data[~filter_data['is_SH']]
                    if factor_type in ['MarketIndTTick']:
                        # 过滤一级行业
                        try:
                            Industry=ind_data.loc[index,'Industry']
                            filter_data = filter_data[filter_data['Industry']==Industry]
                        except Exception as e:
                            print(index,e,'!'*10)
                    if factor_type in ['MarketTTick','Market1TTick','MarketIndTTick']:
                        filter_data=filter_data.groupby(['dt','Ticker']).nth([0,-1]) #目前只使用开盘和最后一个tick
                    tmp_df_list.append(pd.Series(func(filter_data), name=index))
                tmp_df = pd.concat(tmp_df_list, axis=1).T
                factor_df_list.append(tmp_df)
            result_df = pd.concat(factor_df_list, axis=0)
            result_df = result_df.reindex(basic_df.index)
            fill_dic = func(None, return_fillna_dic=True)
            result_df = result_df.fillna(fill_dic)
        elif factor_type in ['T-1_factor', 'other']:
            factor_df = func(start_date, end_date, IO)
            start_date_ = int(s.tradingday(str(start_date), - 5)[0])
            if append_next_tradingday:
                last_date = int(s.tradingday(str(end_date), - 2)[0])
                # 获取md_data用来对齐样本，防止factor_df里缺少某些样本，因此T-1日因子必须要先等MD更新完之后才能更新
                md_data = IO.read_data([start_date_, last_date], columns=['amt'],alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
                factor_df = factor_df.reindex(md_data.index)
                factor_df = fun_append_next_tradingday(factor_df)
                result_df = pd.DataFrame(index=factor_df.index)
            else:
                result_df = pd.DataFrame(index=basic_df.index)
            for factor_col in factor_df.columns:
                result_df[factor_col] = factor_df[factor_col].unstack().shift(1).stack()
            # 使用因子计算函数中的fillna进行异常值填充, inf的填充则在计算函数内部进行处理
            fill_dic = func(None, None, None, return_fillna_dic=True)
            result_df = result_df.fillna(fill_dic)
        if interval_res:
            data_output([start_date, end_date], result_df, result_path, factor_name=factor_name)
        else:
            second_data_output([start_date, end_date], result_df, result_path, factor_name=factor_name)
        return result_df
    elif factor_type in ['T-1_Emotion', 'TEmotion']:
        #日频情绪因子
        basic_df = pd.read_hdf(emotion_data['Basic_zt'])
        label_df = pd.read_hdf(emotion_data['Label_zt'])
        for data_name, data in zip(['Basic_zt', 'Label_zt'], [basic_df, label_df]):
            date_list = list(pd.Series(data.index.get_level_values(0)).apply(lambda x:x.strftime('%Y%m%d')))
            first_date, last_date = min(date_list), max(date_list)
            end_date_ = s.tradingday(str(end_date-10000), str(end_date))[-1]
            if factor_type == 'T-1_Emotion':
                if ((last_date < str(end_date)) and (len(s.tradingday(last_date, str(end_date)))>2)) or \
                    (len(s.tradingday(first_date, str(start_date)))<10):
                    print('%s-%s data interval error!!!!factor interval:%s, data interval:%s'%(factor_name, data_name, [start_date, end_date], [int(first_date), int(last_date)]))
                    return
                else:
                    date_df = func(start_date, end_date, emotion_data['Basic_zt'], emotion_data['Label_zt'])
                    date_df = date_df.fillna(func(None, None, None, None, return_fillna_dic=True))
            elif factor_type == 'TEmotion':
                if (last_date < str(end_date_)) or (len(s.tradingday(first_date, str(start_date))) < 10):
                    print('%s-%s data interval error!!!!factor interval:%s, data interval:%s' % (factor_name, data_name, [start_date, end_date], [int(first_date), int(last_date)]))
                    return
                else:
                    date_df = func(start_date, end_date, emotion_data['Basic_zt'], emotion_data['Label_zt'])
                    date_df = date_df.fillna(func(None, None, None, None, return_fillna_dic=True))
        if not os.path.exists(result_path):
            os.makedirs(result_path)
        if interval_res:
            date_df.to_pickle(result_path + '%s_%d_%d.pkl' % (factor_name, start_date, end_date))
        else:
            second_output(result_path + '%s.pkl'%(factor_name), date_df)
        return date_df

if __name__ == '__main__':
    start_date, end_date = 20160101, 20181231#因子的样本内区间：16-18年
    basic_file_path = '/data/user/018107/factor_zoo1/public/Basic_zt.h5'
    result_path = '/data/user/018107/tmp/'
    import project1_public.factor_test_last_factor as func_tmp
    factor_df0 = run_factor(func_tmp.factor_test_last_factor, 'test_last_factor', 'T-1_factor',
                           start_date, end_date, basic_file_path, result_path,interval_res=False)

    import project1_public.factor_test_trade_factor as func_tmp
    factor_df1 = run_factor(func_tmp.factor_test_trade_factor, 'test_trade_factor', 'TTransaction',
                           start_date, end_date, basic_file_path, result_path,interval_res=False)
