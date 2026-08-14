# -*- coding: utf-8 -*-
# @Time    : 2019/12/26 16:21
# @Author  : wangweidi
# 第二版jupiter卖出收益
import os
import pickle
import datetime as dt
import numpy as np
import sys
sys.path.append("../../")
from LucienUtil import IO as self_IO
sys.path.append("/../..")
from xquant.factordata import FactorData
from xquant.xqutils.xqfile import HDFSFile
import pandas as pd
from ProdWork.Param_config_data import param
#import ProdWork.intra_strong.LabelProfit_zt.spark_LabelProfit_zt
s = FactorData()
hf = HDFSFile()
def change_param(basicDf, input_param_dic):
    today = dt.datetime.now().strftime('%Y%m%d')
    date_list = pd.Series(basicDf.index.get_level_values(0)).apply(lambda x: x.strftime('%Y%m%d'))
    start_date, end_date = min(date_list), max(date_list)
    md_data_path = '/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5'
    md_data = self_IO.read_data([start_date, today], columns=['volume', 'pre_close', 'close'], alt=md_data_path)
    basicDf['close'], basicDf['pre_close'] = md_data['close'], md_data['pre_close']

    basicDf = basicDf.reset_index()
    basicDf['dt'] = basicDf['dt'].apply(lambda x: x.strftime('%Y%m%d'))
    basicDf['date'] = basicDf['dt'].copy()
    basicDf = basicDf.reset_index().set_index(['date', 'Ticker'])
    basicDf['sell_vol_pct'] = input_param_dic['sell_vol_pct']  # 0.2
    basicDf['max_amt'] = input_param_dic['max_amt']#1000 0000
    basicDf['lag_ms'] = list(pd.Series(basicDf.index.get_level_values(1)).apply(
        lambda x: input_param_dic['lag_ms_SH'] if x[-2:] == 'SH' else input_param_dic['lag_ms_SZ']))
    param_dic = {}
    for index, value in basicDf.iterrows():
        param_dic[index] = dict(value[['sell_vol_pct', 'max_amt', 'lag_ms']])

    volume = md_data['volume'].unstack()
    date_list = np.array(pd.Series(volume.index).apply(lambda x: x.strftime('%Y%m%d')))
    for index, value in basicDf.iterrows():
        param_dic[index]['date_list'] = list(date_list[(date_list>=index[0]) & (volume[index[1]]>0)])
        param_dic[index]['close_price'] = value['close']
        if (value.name[0] >= '20200824') & (value.name[1][0]=='3'):
            param_dic[index]['ul_price'] = np.floor(value['pre_close'] * 100 * 1.2 + 0.5) / 100
        else:
            param_dic[index]['ul_price'] = np.floor(value['pre_close'] * 100 * 1.1 + 0.5) / 100
        if len(param_dic[index]['date_list'])>20:
            param_dic[index]['date_list'] = param_dic[index]['date_list'][:20]
    return param_dic

def factor_LabelProfit_zt(param,basic_file, result_path='/data/group/800463/project/project1_prod/LabelProfit_zt/'):
    # interval_list = s.tradingday(start_date, end_date)
    # basic_df = self_IO.read_data([start_date, end_date], alt=basic_file_path)
    basic_df = basic_file
    input_param = change_param(basic_df, param)
    basic_df = basic_df.reset_index()
    data_list = []
    print('不用spark')
    from xquant.marketdata import MarketData
    mdp = MarketData()
    sell_type = 'twap'
    import ProdWork.intra_strong.func_LabelProfit_zt_twap_raw as func
    for index, d in basic_df.iterrows():
        tradingday_str = d['dt'].strftime('%Y%m%d')
        if (tradingday_str == '20200727') & (d['Ticker'] == '000403.SZ'):
            pass
        else:
            this_param = input_param[(tradingday_str, d['Ticker'])]
            if d['dt'] <= pd.Timestamp('2020-05-26'):
                this_param['max_amt'] = 5 * 10000
            elif (d['dt'] >= pd.Timestamp('2020-05-27')) & (d['dt'] <=  pd.Timestamp('2020-06-12')):
                this_param['max_amt'] = 50 * 10000
            elif (d['dt'] >= pd.Timestamp('2020-06-15')) & (d['dt'] <=  pd.Timestamp('2020-06-16')):
                this_param['max_amt'] = 90 * 10000
            elif (d['dt'] >= pd.Timestamp('2020-06-17')) & (d['dt'] <=  pd.Timestamp('2020-06-23')):
                this_param['max_amt'] = 150 * 10000
            elif (d['dt'] >= pd.Timestamp('2020-06-24')) & (d['dt'] <=  pd.Timestamp('2020-07-02')) & (d['Ticker'][~0]=='H'):
                this_param['max_amt'] = 150 * 10000
            elif (d['dt'] >= pd.Timestamp('2020-06-24')) & (d['dt'] <=  pd.Timestamp('2020-07-02')) & (d['Ticker'][~0]=='Z'):
                this_param['max_amt'] = 280 * 10000
            elif (d['dt'] >= pd.Timestamp('2020-07-03')) & (d['dt'] <=  pd.Timestamp('2020-07-03')) & (d['Ticker'][~0]=='H'):
                this_param['max_amt'] = 200 * 10000
            elif (d['dt'] >= pd.Timestamp('2020-07-03')) & (d['dt'] <=  pd.Timestamp('2020-07-03')) & (d['Ticker'][~0]=='Z'):
                this_param['max_amt'] = 400 * 10000
            elif (d['dt'] >= pd.Timestamp('2020-07-06')) & (d['dt'] <=  pd.Timestamp('2020-07-08')) & (d['Ticker'][~0]=='H'):
                this_param['max_amt'] = 400 * 10000
            elif (d['dt'] >= pd.Timestamp('2020-07-06')) & (d['dt'] <=  pd.Timestamp('2020-07-08')) & (d['Ticker'][~0]=='Z'):
                this_param['max_amt'] = 600 * 10000
            elif (d['dt'] >= pd.Timestamp('2020-07-09')) & (d['dt'] <=  pd.Timestamp('2020-07-16')) & (d['Ticker'][~0]=='H'):
                this_param['max_amt'] = 600 * 10000
            elif (d['dt'] >= pd.Timestamp('2020-07-09')) & (d['dt'] <=  pd.Timestamp('2020-07-16'))  & (d['Ticker'][~0]=='Z'):
                this_param['max_amt'] = 800 * 10000
            elif d['dt'] >= pd.Timestamp('2020-07-17'):
                this_param['max_amt'] = 500 * 10000


            print(d['Ticker'], d['dt'], this_param['max_amt'])
            res_df = func.cal_LabelProfit_zt(d['Ticker'], tradingday_str, d['ZT_Time'], mdp, this_param)
            data_list.append(res_df)

    factor_df = pd.concat(data_list, axis=0)

    factor_name = 'LabelProfit_zt_%s_%.2f_%d_SH%d_SZ%d' % (sell_type, param['sell_vol_pct'],
                                                             param['max_amt'] // 10000, param['lag_ms_SH'],
                                                             param['lag_ms_SZ'])
    for factor in ['pct_t1', 'sell_length', 'pct','buy_vol','buy_amt', 'pct_t', 'delta_ms','finish_indicator']:
        if factor in factor_df.columns:
            factor_df[factor] = factor_df[factor].astype(float)

    if ('touch_ul' in factor_df.columns) and (sell_type=='pct'):
        factor_df['touch_ul'] = factor_df['touch_ul'].astype(float)
    return factor_df

if __name__ == '__main__':
    sell_type = 'twap'
    start_date, end_date = 20200610, 20200610
    #param = {'sell_vol_pct': 0.1, 'max_amt': 800 * 10000, 'lag_ms_SH': 450, 'lag_ms_SZ': 100}


    # 涨停
    basic_path = '/data/user/013600/generalStrong_v1/daily_data/20200610/Basic_zt_20200610_20200610.h5'
    result_path = '/data/group/800463/project/project1_prod/LabelProfit_zt/'
    basic = pd.read_excel('/data/group/800463/日内强势股/daily_20210326_20210407.xlsx', sheet_name='jupiter未成功下单票_20210326_20210407')
    basic['dt'] = basic['date'].apply(lambda x: pd.Timestamp(str(x)))
    basic['Ticker'] = basic['stock']
    basic = basic.set_index(['dt', 'Ticker'])
    profit = pd.read_hdf('/data/group/800463/project/project1_prod/LabelProfit_zt/LabelProfit_zt_twap_0.10_800_SH700_SZ200_20210326_20210407.h5')
    # profit.reindex(basic.index).reset_index().to_excel('/data/group/800463/日内强势股/20210326_20210406未下单jupiter样本.xlsx')
    factor_df = factor_LabelProfit_zt(param,basic)




