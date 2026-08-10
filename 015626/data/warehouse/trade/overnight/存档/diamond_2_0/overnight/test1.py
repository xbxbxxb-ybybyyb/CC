import sys
sys.path.insert(4, '/data/user/017024')

import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from multiprocessing import Pool
import datetime as dt
from reportlab.platypus import Image, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from code_wsc.help_functions_wsc import *
from code_wsc.operators_wsc_1_0 import *
from code_wsc.SIF_Factor_Test18 import *
from overnight.factor_generator import *

TRADING_PLAN = read_json('/data/group/800466/trade/overnight/code/overnight/trading_plan.json')


'''原始收益序列导入'''
'''期货'''
future_ret_raw = IO.read_data([20130101, 20211231], columns = ['long_ret'], 
                    alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight_ret.h5').unstack()['long_ret'] - 0.5/1e4
future_ret_raw.columns = ['IC', 'IF', 'IH']

'''指数'''
spot_ret_raw = IO.read_data([20130101, 20211231], alt = 
                  '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight_indexret_10minsclose.h5').unstack()['ret']
spot_ret_raw.columns = ['IC', 'IF', 'IH']

'''基差'''
basis_ret_raw = future_ret_raw - spot_ret_raw


'''隔夜收益振幅及尾盘基差计算'''
'''隔夜收益振幅'''
price_ret_raw = IO.read_data([20130101, 20211231], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight_ret.h5')

price_ret_raw['MidPrice_am'] = (price_ret_raw['Buy1Price_am'] + price_ret_raw['Sell1Price_am']) / 2
price_ret_raw['MidPrice_pm'] = (price_ret_raw['Buy1Price_pm'] + price_ret_raw['Sell1Price_pm']) / 2
price_ret_raw['MidPrice_ret'] = price_ret_raw['MidPrice_am'] / price_ret_raw['MidPrice_pm'] - 1

overnight_ret_amplitude_ic = ts_mean(abs(price_ret_raw['MidPrice_ret'].xs('IC.CFE', level=1)), 20)
overnight_ret_amplitude_if = ts_mean(abs(price_ret_raw['MidPrice_ret'].xs('IF.CFE', level=1)), 20)
overnight_ret_amplitude_ih = ts_mean(abs(price_ret_raw['MidPrice_ret'].xs('IH.CFE', level=1)), 20)

'''尾盘基差'''
spot_close = IO.read_data([20130101, 20211231], columns = ['close_noon'], alt = 
                  '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight_indexret_10minsclose.h5')['close_noon'].unstack()
spot_close.columns = ['IC', 'IF', 'IH']

basis_close_ic = price_ret_raw['MidPrice_pm'].xs('IC.CFE', level=1) - spot_close['IC']
basis_close_if = price_ret_raw['MidPrice_pm'].xs('IF.CFE', level=1) - spot_close['IF']
basis_close_ih = price_ret_raw['MidPrice_pm'].xs('IH.CFE', level=1) - spot_close['IH']


'''因子值导入'''
def factor_aggregation_norm(factor_path):
    """
    read factors form the specified folder and aggregate the factors into a dataframe
    :param factor_path: str
        factor storage path
    :return: dataframe
        aggregated factor matrix, each column is a factor
    """
    factors = sorted([i for i in os.listdir(factor_path) if i.endswith('h5')])
    factors_list = [os.path.join(factor_path, i) for i in factors]

    factor_agg_df = None
    for i, i_name in enumerate(factors_list):
        factor = pd.read_hdf(i_name)['norm']
        factor.name = i_name.split('/')[-1][:-3]
        factor_agg_df = factor if factor_agg_df is None else pd.concat([factor_agg_df, factor], axis=1)

    return factor_agg_df
    
factor_prod_old = factor_aggregation_norm('/data/group/800466/trade/overnight/factor_temp/20210427/')  # 截止到20210421的因子值

path1 = '/data/group/800466/trade/overnight/factor_proof/'
Diamond_trading_days = [i for i in sorted(os.listdir(path1)) if (int(i.split('_')[0])>20210421)&(len(i)==8)]
factor_path = [os.path.join(path1, i, i) + '.csv' for i in Diamond_trading_days]

factor_prod_new = None
for i_path in factor_path:
    factor_norm = pd.read_csv(i_path, index_col=0)['norm']
    factor_norm.name = pd.to_datetime(i_path.split('/')[-2])
    factor_prod_new = factor_norm if factor_prod_new is None else pd.concat([factor_prod_new, factor_norm], axis=1, sort=True)
factor_prod_new = factor_prod_new.T

factor_prod = factor_prodfactor_prod = pd.concat([factor_prod_old, factor_prod_new], axis=0)
factor_prod = factor_prod.reindex(future_ret_raw['2017':].index)


'''Diamond信号值计算'''
def get_signal(factor_series):
    factor_series_open = factor_series[factor_series >= 0.75]
    signal_raw = factor_series_open.shape[0] / factor_series.shape[0]
    adjust_coef = np.searchsorted([0.75, 0.8, 0.85, 0.9, 0.95, 1], factor_series_open.mean()) * 0.2 + 0.4
    signal_final = signal_raw * adjust_coef
    return signal_final


def get_signal_final_Diamond_2_0(factor_series):
    future_ic = get_signal(factor_series.reindex(TRADING_PLAN['future_ic']))
    spot_ic = get_signal(factor_series.reindex(TRADING_PLAN['spot_ic']))
    future_if = get_signal(factor_series.reindex(TRADING_PLAN['future_if']))
    spot_if = get_signal(factor_series.reindex(TRADING_PLAN['spot_if']))
    future_ih = get_signal(factor_series.reindex(TRADING_PLAN['future_ih']))
    spot_ih = get_signal(factor_series.reindex(TRADING_PLAN['spot_ih']))
    signal_ic = (future_ic + spot_ic) / 2
    signal_if = (future_if + spot_if) / 2
    signal_ih = (future_ih + spot_ih) / 2
    signal = (signal_ic + signal_if + signal_ih) / 3
    return signal
    
Diamond_sig = pd.Series(index=factor_prod.index, name='Diamond_2_0_sig')

for i in factor_prod.index:
    factor_list_temp = factor_prod.loc[i]
    Diamond_sig.loc[i] = get_signal_final_Diamond_2_0(factor_list_temp)

Diamond_sig = Diamond_sig.astype('float')

Diamond_sig.to_hdf('/data/user/017024/share/for_zf/Diamond_2_0_sig.h5', key='Diamond_2_0_sig')

Diamond_daily_ret = future_ret_raw.multiply(Diamond_sig.fillna(0), axis=0)


'''报告绘制第二部分：因子表现'''
'''统计因子在Macbeth方法中使用的次数'''
factor_list = np.unique(TRADING_PLAN['future_ic'] + TRADING_PLAN['future_if'] + TRADING_PLAN['future_ih'] + 
                        TRADING_PLAN['spot_ic'] + TRADING_PLAN['spot_if'] + TRADING_PLAN['spot_ih'])

factor_usage = pd.DataFrame(index=factor_list, columns=['future_ic', 'future_if', 'future_ih', 'spot_ic', 'spot_if', 'spot_ih'])
for i in factor_usage.columns:
    for j in factor_usage.index:
        if j in TRADING_PLAN[i]:
            factor_usage.loc[j,i] = 1
        else:
            factor_usage.loc[j,i] = 0
factor_usage['sum'] = factor_usage.sum(axis=1)


'''因子报告生成'''
'''ic_layers4'''
stats_list = []

def func1(i):
    factor_temp = factor_prod.iloc[:,i]
    stats_temp1 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minstickvwap', direction='long',
                    ticker='IC.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=4,
                    savepath='/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/future/layers4/2021')
    temp1_picture = stats_temp1.draw_result()
    stats_temp2 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minsindexret', direction='long',
                        ticker='IC.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=4,
                        savepath='/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/spot/layers4/2021')
    temp2_picture = stats_temp2.draw_result()
    temp_df1 = pd.DataFrame(temp1_picture.values(), columns=[factor_temp.name], index=temp1_picture.keys())
    temp_df2 = pd.DataFrame(temp2_picture.values(), columns=[factor_temp.name], index=temp2_picture.keys())
    plt.clf()
    plt.cla()
    plt.close()
    return temp_df1, temp_df2

with Pool() as pool:
    stats_list = pool.map(func1, range(factor_prod.shape[1]))




