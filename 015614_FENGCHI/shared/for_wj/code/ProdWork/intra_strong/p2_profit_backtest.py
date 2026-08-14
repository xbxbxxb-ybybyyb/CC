# -*- coding: utf-8 -*-
# @Time    : 2020/11/13 13:17
# @Author  : wangweidi
# 调用saturn模拟收益调用
import pickle
import datetime as dt
import numpy as np
from LucienUtil import IO as self_IO
from xquant.factordata import FactorData
from xquant.xqutils.xqfile import HDFSFile
import pandas as pd
import ProdWork.intra_strong.func_p2_profit_backtest as func
s = FactorData()
hf = HDFSFile()

def change_param(basic_df, input_param_dic):
    date_list = pd.Series(basic_df.index.get_level_values(0)).apply(lambda x: x.strftime('%Y%m%d'))
    start_date, end_date = min(date_list), max(date_list)
    end_date_ = s.tradingday(end_date, 40)[-1]
    md_data_path = '/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5'
    # md_data_path = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5'
    md_data = self_IO.read_data([start_date, end_date_], columns=['volume', 'pre_close', 'close'], alt=md_data_path)
    md_data['float_mv'] = self_IO.read_data([start_date, end_date_], columns=['S_DQ_MV'], alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5')['S_DQ_MV']
    basic_df['close'], basic_df['pre_close'] = md_data['close'], md_data['pre_close']
    basic_df['float_mv'] = md_data['float_mv']

    basic_df = basic_df.reset_index()
    basic_df['dt'] = basic_df['dt'].apply(lambda x: x.strftime('%Y%m%d'))
    basic_df['date'] = basic_df['dt'].copy()
    basic_df = basic_df.reset_index().set_index(['date', 'Ticker'])
    basic_df['buy_vol_pct'] = input_param_dic['buy_vol_pct']  # 0.2
    basic_df['sell_vol_pct'] = input_param_dic['sell_vol_pct']  # 0.1
    basic_df['max_amt'] = input_param_dic['max_amt']#1000 0000
    basic_df['cover_amt'] = input_param_dic['cover_amt']
    basic_df['p2_type'] = input_param_dic['p2_type']

    param_dic = {}
    for index, value in basic_df.iterrows():
        param_dic[index] = dict(value[['buy_vol_pct', 'sell_vol_pct', 'max_amt', 'cover_amt', 'pre_close', 'close', 'p2_type']])

    volume = md_data['volume'].unstack()
    pre_close = md_data['pre_close'].unstack()
    close = md_data['close'].unstack()
    date_list = np.array(pd.Series(volume.index).apply(lambda x: x.strftime('%Y%m%d')))
    for index, value in basic_df.iterrows():
        tradingday, code = index[0], index[1]
        ul_pct = 1.2 if ((code[:2] in ['30', '68']) and (tradingday>='20200824')) else 1.1
        param_dic[index]['date_list'] = list(date_list[(date_list>index[0]) & (volume[index[1]]>0)])
        pre_close_list = list(pre_close[code][(date_list>index[0]) & (volume[index[1]]>0)])
        close_list = list(close[code][(date_list > index[0]) & (volume[index[1]] > 0)])
        # param_dic[index]['close_price'] = value['close']
        # param_dic[index]['ul_price'] = np.floor(value['pre_close'] * 100 * ul_pct + 0.5) / 100
        if len(param_dic[index]['date_list'])>20:
            param_dic[index]['date_list'] = param_dic[index]['date_list'][:20]
            pre_close_list = pre_close_list[:20]
            close_list = close_list[:20]
        param_dic[index]['pre_close_list'] = pre_close_list
        param_dic[index]['close_list'] = close_list
    return param_dic

def factor_p2_profit_backtest(param, basic_file):
    basic_df = basic_file
    input_param = change_param(basic_df, param)
    basic_df = basic_df.reset_index()
    data_list = []
    print('不用spark')
    from xquant.marketdata import MarketData
    mdp = MarketData()
    for index, d in basic_df.iterrows():
        print(d['Ticker'], d['dt'])
        # if d['Ticker'] == '000811.SZ':
        #     x= 0
        # else:
        #     continue
        tradingday_str = d['dt'].strftime('%Y%m%d')
        res_df = func.cal_p2_profit_backtest(mdp, tradingday_str, d['Ticker'], input_param[(tradingday_str, d['Ticker'])])
        data_list.append(res_df)

    factor_df = pd.concat(data_list, axis=0)
    for key in ['buy_vol', 'buy_amt', 'buy_vwap', 'pct_T', 'pct_T1', 'sell_len', 'pct', 'buy_tick_num', 'last_buy_time']:
        factor_df[key] = factor_df[key].astype(float)
    for key in ['date_list', 'touch_list', 'vol_list']:
        factor_df[key] = factor_df[key].astype(str)
    factor_df['absolute_profit'] = factor_df['buy_amt'] * factor_df['pct']
    return factor_df

'''if __name__ == '__main__':
    start_date, end_date = 20160101, 20201130
    param = {'buy_vol_pct':0.2, 'sell_vol_pct': 0.1, 'max_amt': 500 * 10000, 'cover_amt':1500,
             'p2_type':'930'}

    #basic_path = '/data/user/013550/New_Strategy_Manager/Basic/Basic_last_zt_all_20201110_20160101_20200831.h5'
    # basic_path = '/data/user/013600/tmp/Basic_closed_hf_finish_20150901_20201130.h5'
    # basic_path = '/data/user/013550/project2_prod/everyday_Basic/20210101_20210312/Basic_closed_hf_finish_20210101_20210312.h5'
    # basic_path = '/data/user/013550/project2_prod/everyday_Basic/20210101_20210301/Basic_closed_hf_finish_20210101_20210301.h5'
    result_path = '/data/group/800463/project/project2_prod/profit_backtest/'
    basic_path = pd.read_hdf('/data/group/800463/project/project2_prod/everyday_Basic/20160101_20210312/Basic_closed_hf_finish_20160101_20210312.h5')

    # 涨停
    factor_df = factor_p2_profit_backtest(param, basic_file)'''
