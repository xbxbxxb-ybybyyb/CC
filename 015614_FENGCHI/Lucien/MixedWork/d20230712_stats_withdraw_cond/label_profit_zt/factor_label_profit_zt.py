# -*- coding: utf-8 -*-
import os
from LucienUtil import IO
import numpy as np
import pandas as pd
import datetime as dt
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()
import MixedWork.d20230712_stats_withdraw_cond.label_profit_zt.func_LabelProfit_zt_twap as func_twap # twap正常卖出

def change_param(basicDf, input_param_dic, sell_type):
    date_list = pd.Series(basicDf.index.get_level_values(0)).apply(lambda x: x.strftime('%Y%m%d'))
    start_date, end_date = min(date_list), max(date_list)
    md_data_path = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5'
    md_data = IO.read_data([start_date, s.tradingday(end_date, 40)[-1]], columns=['volume', 'pre_close', 'close'], alt=md_data_path)
    md_data['float_mv'] = IO.read_data([start_date, s.tradingday(end_date, 40)[-1]], columns=['S_DQ_MV'],
                                       alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5')['S_DQ_MV']
    basicDf['close'], basicDf['pre_close'] = md_data['close'], md_data['pre_close']
    basicDf['float_mv'] = md_data['float_mv']

    basicDf = basicDf.reset_index()
    basicDf['dt'] = basicDf['dt'].apply(lambda x: x.strftime('%Y%m%d'))
    basicDf['date'] = basicDf['dt'].copy()
    basicDf = basicDf.reset_index().set_index(['date', 'Ticker'])
    basicDf['sell_vol_pct'] = input_param_dic['sell_vol_pct']  # 0.2
    basicDf['max_amt'] = input_param_dic['max_amt']
    basicDf['max_vol'] = input_param_dic['max_vol']
    basicDf['lag_ms'] = list(pd.Series(basicDf.index.get_level_values(1)).apply(lambda x: input_param_dic['lag_ms_SH'] if x[-2:] == 'SH' else input_param_dic['lag_ms_SZ']))
    basicDf['cover_amt'] = input_param_dic['cover_amt']
    param_dic = {}
    for index, value in basicDf.iterrows():
        param_dic[index] = dict(value[['sell_vol_pct', 'max_amt', 'lag_ms', 'cover_amt', 'max_vol']])
        if sell_type[:14] == 'twap_interval_':
            start_minuter=int(sell_type[14:].split('_')[0])
            end_minute=int(sell_type[14:].split('_')[1])
            param_dic[index]['start_minute'] = start_minuter
            param_dic[index]['end_minute'] = end_minute
        if sell_type in ['twap_quickt', 'twap_v3quickt']:
            #param_dic[index]['quick_time']=value['next_ZT_Time']
            param_dic[index]['quick_time'] = value['next_pct_time']

    volume = md_data['volume'].unstack()
    date_list = np.array(pd.Series(volume.index).apply(lambda x: x.strftime('%Y%m%d')))
    for index, value in basicDf.iterrows():
        tradingday, code = index[0], index[1]
        ul_pct = 1.2 if ((code[:2] in ['30', '68']) and (tradingday>='20200824')) else 1.1
        param_dic[index]['date_list'] = list(date_list[(date_list>=index[0]) & (volume[index[1]]>0)])
        param_dic[index]['close_price'] = value['close']
        param_dic[index]['ul_price'] = np.floor(value['pre_close'] * 100 * ul_pct + 0.5) / 100
        if len(param_dic[index]['date_list'])>20:
            param_dic[index]['date_list'] = param_dic[index]['date_list'][:20]
    return param_dic

def pool_fun(i, basic_df, input_param, sell_type, pool_num):
    res_list=[]
    while i < len(basic_df):
        d = basic_df.iloc[i]
        try:
            tradingday_str = d['dt'].strftime('%Y%m%d')
            if sell_type == 'twap':
                res_df = func_twap.cal_LabelProfit_zt(d['Ticker'], tradingday_str, d['ZT_Time'], mdp,
                                                 input_param[(tradingday_str, d['Ticker'])])
                res_list.append(res_df)
            else:
                print('Error: sell_type=', sell_type)
        except Exception as e:
            print('!' * 10, d['Ticker'], d['dt'], e)
        i = i + pool_num
    return res_list

def factor_LabelProfit_zt(start_date, end_date, param, basic_file_path,
                          result_path='/data/group/800463/project/project1_prod/LabelProfit_zt/', sell_type='twap'):
    print(start_date, end_date, sell_type, param)
    basic_df = IO.read_data([start_date, end_date], alt=basic_file_path)
    input_param = change_param(basic_df, param, sell_type=sell_type)
    basic_df = basic_df.reset_index()

    from multiprocessing import Pool
    pool_num = 24 # ！！！并行化数量
    pool_num = min(pool_num, len(basic_df))
    print('多线程：', pool_num, '  样本数：', len(basic_df))
    pool = Pool(pool_num)
    task_list = []
    for index in range(pool_num):
        task_list.append(pool.apply_async(pool_fun, args=(index, basic_df, input_param, sell_type, pool_num)))
    pool.close()
    pool.join()
    res_list=[task.get() for task in task_list]
    data_list=[]
    for r in res_list:
        data_list = data_list + r

    factor_df = pd.concat(data_list, axis=0)
    factor_name = 'LabelProfit_zt_%s_%.2f_%d_%d_SH%d_SZ%d' % (sell_type, param['sell_vol_pct'],
                                                              param['max_amt'] // 10000, param['max_vol'], param['lag_ms_SH'],
                                                              param['lag_ms_SZ'])
    for factor in ['pct_t1', 'sell_length', 'pct','buy_vol', 'buy_amt', 'pct_t', 'delta_ms', 'target_vol',
                   'before_quick_vol', 'before_quick_amt']:
        if factor in factor_df.columns:
            factor_df[factor] = factor_df[factor].astype(float)
    if ('pct' in sell_type) and ('touch_ul' in factor_df.columns):
        factor_df['touch_ul'] = factor_df['touch_ul'].astype(float)
    if ('twap' in sell_type) and ('touch_ul' in factor_df.columns):
        factor_df['touch_ul'] = factor_df['touch_ul'].apply(lambda x:x[:13])
    if 'sell_date' in factor_df.columns:
        factor_df['sell_date'] = factor_df['sell_date'].apply(lambda x: x[:40])
    if 'sell_vol' in factor_df.columns:
        factor_df['sell_vol'] = factor_df['sell_vol'].apply(lambda x:x[:30])

    factor_name = '%s%s%s'%(result_path, factor_name, '.h5')
    if os.path.exists(factor_name):
        IO.pd_hdf5_writer(factor_df, factor_name, dataset='profit', append=True)
        new_factor_df = pd.read_hdf(factor_name).sort_index()
        IO.pd_hdf5_writer(new_factor_df, factor_name, dataset='profit', override=True)
    else:
        IO.pd_hdf5_writer(factor_df, factor_name, dataset='profit')

    return factor_df

if __name__ == '__main__':

    param = {'sell_vol_pct': 0.15,
             'max_amt': 2000 * 10000,
             'max_vol': 300,
             'lag_ms_SH': 250,
             'lag_ms_SZ': 20,
             'cover_amt': 1500}
    # start_date, end_date = 20150901, 20231001
    start_date, end_date = 20220518, 20230518

    basic_file_path = '/data/group/800463/project/project1_prod/left_v2212/Basic_zt_test/Basic_zt_001.h5'
    # result_path = '/data/group/800463/project/project1_prod/LabelProfit_fix/'
    result_path = '/data/user/015614/TEST/及时撤单/模拟收益_及时撤单/'
    factor_LabelProfit_zt(start_date, end_date, param, basic_file_path, result_path, 'twap')