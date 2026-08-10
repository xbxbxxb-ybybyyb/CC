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
Diamond_trading_days = [i for i in sorted(os.listdir(path1)) if (int(i.split('_')[0])>20210421)&(i.endswith('1449'))]
factor_path = [os.path.join(path1, i, i) + '.csv' for i in Diamond_trading_days]

factor_prod_new = None
for i_path in factor_path:
    factor_norm = pd.read_csv(i_path, index_col=0)['norm']
    factor_norm.name = pd.to_datetime(i_path.split('/')[-2][:8])
    factor_prod_new = factor_norm if factor_prod_new is None else pd.concat([factor_prod_new, factor_norm], axis=1, sort=True)
factor_prod_new = factor_prod_new.T

factor_prod = pd.concat([factor_prod_old, factor_prod_new], axis=0)
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
    
def get_signal_final_Diamond_1_0(factor_series):
    signal = get_signal(factor_series.reindex(TRADING_PLAN['Diamond_1_0']))
    return signal
    
Diamond_sig = pd.Series(index=factor_prod.index, name='Diamond_2_0_sig')
for i in factor_prod.index:
    factor_list_temp = factor_prod.loc[i]
    Diamond_sig.loc[i] = get_signal_final_Diamond_2_0(factor_list_temp)
Diamond_sig = Diamond_sig.astype('float')

Diamond_sig_1_0 = pd.Series(index=factor_prod.index, name='Diamond_1_0_sig')
for i in factor_prod.index:
    factor_list_temp = factor_prod.loc[i]
    Diamond_sig_1_0.loc[i] = get_signal_final_Diamond_1_0(factor_list_temp)
Diamond_sig_1_0 = Diamond_sig_1_0.astype('float')

Diamond_sig.to_hdf('/data/user/017024/share/for_zf/Diamond_2_0_sig.h5', key='Diamond_2_0_sig')
Diamond_sig_1_0.to_hdf('/data/user/017024/share/for_zf/Diamond_1_0_sig.h5', key='Diamond_1_0_sig')


'''计算尾盘结算比率'''
future_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/FUTURE_DATA_2020.pkl')

future_close = future_data['close']
future_mask = future_data['recent_month_mask']
future_amount = future_data['amount']
future_volume = future_data['volume']
amount_sum = ts_sum(future_amount, 60)
volume_sum = ts_sum(future_volume, 60)
vwap_60 = (amount_sum / volume_sum)[future_mask].sum(axis=1)
vwap_60 = vwap_60.iloc[vwap_60.index.indexer_at_time(trade_stop_time)].to_frame()
close_stop_time = future_close[future_mask].sum(axis=1)
close_stop_time = close_stop_time.iloc[close_stop_time.index.indexer_at_time(trade_stop_time)].to_frame()
settlement_ratio_ic = vwap_60 / 200 / close_stop_time
settlement_ratio_ic.columns = ['IC']
settlement_ratio_ic.index = pd.to_datetime(settlement_ratio_ic.index.date)

future_close = future_data['close_if']
future_mask = future_data['recent_month_mask']
future_amount = future_data['amount_if']
future_volume = future_data['volume_if']
amount_sum = ts_sum(future_amount, 60)
volume_sum = ts_sum(future_volume, 60)
vwap_60 = (amount_sum / volume_sum)[future_mask].sum(axis=1)
vwap_60 = vwap_60.iloc[vwap_60.index.indexer_at_time(trade_stop_time)].to_frame()
close_stop_time = future_close[future_mask].sum(axis=1)
close_stop_time = close_stop_time.iloc[close_stop_time.index.indexer_at_time(trade_stop_time)].to_frame()
settlement_ratio_if = vwap_60 / 300 / close_stop_time
settlement_ratio_if.columns = ['IF']
settlement_ratio_if.index = pd.to_datetime(settlement_ratio_if.index.date)

future_close = future_data['close_ih']
future_mask = future_data['recent_month_mask']
future_amount = future_data['amount_ih']
future_volume = future_data['volume_ih']
amount_sum = ts_sum(future_amount, 60)
volume_sum = ts_sum(future_volume, 60)
vwap_60 = (amount_sum / volume_sum)[future_mask].sum(axis=1)
vwap_60 = vwap_60.iloc[vwap_60.index.indexer_at_time(trade_stop_time)].to_frame()
close_stop_time = future_close[future_mask].sum(axis=1)
close_stop_time = close_stop_time.iloc[close_stop_time.index.indexer_at_time(trade_stop_time)].to_frame()
settlement_ratio_ih = vwap_60 / 300 / close_stop_time
settlement_ratio_ih.columns = ['IH']
settlement_ratio_ih.index = pd.to_datetime(settlement_ratio_ih.index.date)

settlement_ratio = pd.concat([settlement_ratio_ic, settlement_ratio_if, settlement_ratio_ih], axis=1)
settlement_ratio = settlement_ratio.reindex(Diamond_sig['2021':].index)

settlement_cut_ic = pd.cut(settlement_ratio['IC'], bins=[0, 0.997, 1.003, 2], labels=False).fillna(1)
settlement_cut_if = pd.cut(settlement_ratio['IF'], bins=[0, 0.997, 1.003, 2], labels=False).fillna(1)
settlement_cut_ih = pd.cut(settlement_ratio['IH'], bins=[0, 0.997, 1.003, 2], labels=False).fillna(1)
settlement_cut = pd.concat([settlement_cut_ic, settlement_cut_if, settlement_cut_ih], axis=1)

Diamond_sig_adjust = pd.concat([Diamond_sig, Diamond_sig, Diamond_sig], axis=1)['2021':].fillna(0)
Diamond_sig_adjust.columns = ['IC', 'IF', 'IH']

Diamond_sig_adjust[Diamond_sig_adjust<0.1] = 0
# Diamond_sig_adjust = Diamond_sig_adjust * settlement_cut
Diamond_daily_ret = future_ret_raw['2021':] * Diamond_sig_adjust



'''因子报告生成'''
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

stats_all_future = pd.concat([i[0] for i in stats_list], axis=1)
stats_all_spot = pd.concat([i[1] for i in stats_list], axis=1)    
stats_all_future.T.to_excel('/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/future/layers4/2021/stats.xlsx')
stats_all_spot.T.to_excel('/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/spot/layers4/2021/stats.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/future/layers4/2021/factor_usage.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/spot/layers4/2021/factor_usage.xlsx')

'''if_layers4'''
stats_list = []

def func1(i):
    factor_temp = factor_prod.iloc[:,i]
    stats_temp1 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minstickvwap', direction='long',
                    ticker='IF.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=4,
                    savepath='/data/user/017024/share/overnight/pictures/if/Diamond_2_0/future/layers4/2021')
    temp1_picture = stats_temp1.draw_result()
    stats_temp2 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minsindexret', direction='long',
                        ticker='IF.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=4,
                        savepath='/data/user/017024/share/overnight/pictures/if/Diamond_2_0/spot/layers4/2021')
    temp2_picture = stats_temp2.draw_result()
    temp_df1 = pd.DataFrame(temp1_picture.values(), columns=[factor_temp.name], index=temp1_picture.keys())
    temp_df2 = pd.DataFrame(temp2_picture.values(), columns=[factor_temp.name], index=temp2_picture.keys())
    plt.clf()
    plt.cla()
    plt.close()
    return temp_df1, temp_df2

with Pool() as pool:
    stats_list = pool.map(func1, range(factor_prod.shape[1]))
  
stats_all_future = pd.concat([i[0] for i in stats_list], axis=1)
stats_all_spot = pd.concat([i[1] for i in stats_list], axis=1)
stats_all_future.T.to_excel('/data/user/017024/share/overnight/pictures/if/Diamond_2_0/future/layers4/2021/stats.xlsx')
stats_all_spot.T.to_excel('/data/user/017024/share/overnight/pictures/if/Diamond_2_0/spot/layers4/2021/stats.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/if/Diamond_2_0/future/layers4/2021/factor_usage.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/if/Diamond_2_0/spot/layers4/2021/factor_usage.xlsx')

'''ih_layers4'''
stats_list = []

def func1(i):
    factor_temp = factor_prod.iloc[:,i]
    stats_temp1 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minstickvwap', direction='long',
                    ticker='IH.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=4,
                    savepath='/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/future/layers4/2021')
    temp1_picture = stats_temp1.draw_result()
    stats_temp2 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minsindexret', direction='long',
                        ticker='IH.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=4,
                        savepath='/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/spot/layers4/2021')
    temp2_picture = stats_temp2.draw_result()
    temp_df1 = pd.DataFrame(temp1_picture.values(), columns=[factor_temp.name], index=temp1_picture.keys())
    temp_df2 = pd.DataFrame(temp2_picture.values(), columns=[factor_temp.name], index=temp2_picture.keys())
    plt.clf()
    plt.cla()
    plt.close()
    return temp_df1, temp_df2

with Pool() as pool:
    stats_list = pool.map(func1, range(factor_prod.shape[1]))

stats_all_future = pd.concat([i[0] for i in stats_list], axis=1)
stats_all_spot = pd.concat([i[1] for i in stats_list], axis=1)
stats_all_future.T.to_excel('/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/future/layers4/2021/stats.xlsx')
stats_all_spot.T.to_excel('/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/spot/layers4/2021/stats.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/future/layers4/2021/factor_usage.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/spot/layers4/2021/factor_usage.xlsx')

'''ic_layers8'''
stats_list = []

def func1(i):
    factor_temp = factor_prod.iloc[:,i]
    stats_temp1 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minstickvwap', direction='long',
                    ticker='IC.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=8,
                    savepath='/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/future/layers8/2021')
    temp1_picture = stats_temp1.draw_result()
    stats_temp2 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minsindexret', direction='long',
                        ticker='IC.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=8,
                        savepath='/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/spot/layers8/2021')
    temp2_picture = stats_temp2.draw_result()
    temp_df1 = pd.DataFrame(temp1_picture.values(), columns=[factor_temp.name], index=temp1_picture.keys())
    temp_df2 = pd.DataFrame(temp2_picture.values(), columns=[factor_temp.name], index=temp2_picture.keys())
    plt.clf()
    plt.cla()
    plt.close()
    return temp_df1, temp_df2

with Pool() as pool:
    stats_list = pool.map(func1, range(factor_prod.shape[1]))
    
stats_all_future = pd.concat([i[0] for i in stats_list], axis=1)
stats_all_spot = pd.concat([i[1] for i in stats_list], axis=1)
stats_all_future.T.to_excel('/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/future/layers8/2021/stats.xlsx')
stats_all_spot.T.to_excel('/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/spot/layers8/2021/stats.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/future/layers8/2021/factor_usage.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/ic/Diamond_2_0/spot/layers8/2021/factor_usage.xlsx')

'''if_layers8'''
stats_list = []

def func1(i):
    factor_temp = factor_prod.iloc[:,i]
    stats_temp1 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minstickvwap', direction='long',
                    ticker='IF.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=8,
                    savepath='/data/user/017024/share/overnight/pictures/if/Diamond_2_0/future/layers8/2021')
    temp1_picture = stats_temp1.draw_result()
    stats_temp2 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minsindexret', direction='long',
                        ticker='IF.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=8,
                        savepath='/data/user/017024/share/overnight/pictures/if/Diamond_2_0/spot/layers8/2021')
    temp2_picture = stats_temp2.draw_result()
    temp_df1 = pd.DataFrame(temp1_picture.values(), columns=[factor_temp.name], index=temp1_picture.keys())
    temp_df2 = pd.DataFrame(temp2_picture.values(), columns=[factor_temp.name], index=temp2_picture.keys())
    plt.clf()
    plt.cla()
    plt.close()
    return temp_df1, temp_df2

with Pool() as pool:
    stats_list = pool.map(func1, range(factor_prod.shape[1]))
 
stats_all_future = pd.concat([i[0] for i in stats_list], axis=1)
stats_all_spot = pd.concat([i[1] for i in stats_list], axis=1)
stats_all_future.T.to_excel('/data/user/017024/share/overnight/pictures/if/Diamond_2_0/future/layers8/2021/stats.xlsx')
stats_all_spot.T.to_excel('/data/user/017024/share/overnight/pictures/if/Diamond_2_0/spot/layers8/2021/stats.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/if/Diamond_2_0/future/layers8/2021/factor_usage.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/if/Diamond_2_0/spot/layers8/2021/factor_usage.xlsx')

'''ih_layers8'''
stats_list = []

def func1(i):
    factor_temp = factor_prod.iloc[:,i]
    stats_temp1 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minstickvwap', direction='long',
                    ticker='IH.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=8,
                    savepath='/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/future/layers8/2021')
    temp1_picture = stats_temp1.draw_result()
    stats_temp2 = SIF_Factor_Test(factor_temp, factor_kind='overnight', return_price_kind='10minsindexret', direction='long',
                        ticker='IH.CFE', starttime=20210101, endtime=20211231, show_image=False, save_image=True, layers=8,
                        savepath='/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/spot/layers8/2021')
    temp2_picture = stats_temp2.draw_result()
    temp_df1 = pd.DataFrame(temp1_picture.values(), columns=[factor_temp.name], index=temp1_picture.keys())
    temp_df2 = pd.DataFrame(temp2_picture.values(), columns=[factor_temp.name], index=temp2_picture.keys())
    plt.clf()
    plt.cla()
    plt.close()
    return temp_df1, temp_df2

with Pool() as pool:
    stats_list = pool.map(func1, range(factor_prod.shape[1]))

stats_all_future = pd.concat([i[0] for i in stats_list], axis=1)
stats_all_spot = pd.concat([i[1] for i in stats_list], axis=1)    
stats_all_future.T.to_excel('/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/future/layers8/2021/stats.xlsx')
stats_all_spot.T.to_excel('/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/spot/layers8/2021/stats.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/future/layers8/2021/factor_usage.xlsx')
factor_usage.to_excel('/data/user/017024/share/overnight/pictures/ih/Diamond_2_0/spot/layers8/2021/factor_usage.xlsx')


'''报告绘制第一部分：策略表现及市场状态描述'''
fig = plt.figure(figsize=[15,20])#, dpi=540)
plt.subplots_adjust(hspace=0.5)

ax0 = fig.add_subplot(4,1,1)
plt.plot(Diamond_daily_ret['2021':]['IC'].cumsum(), label='IC')
plt.plot(Diamond_daily_ret['2021':]['IF'].cumsum(), label='IF')
plt.plot(Diamond_daily_ret['2021':]['IH'].cumsum(), label='IH')
plt.legend(loc='best', fontsize=12)
ax0.set_title('strategic ret', fontsize=24)

ax1 = fig.add_subplot(4,2,3)
plt.plot(future_ret_raw['IC']['2021':].cumsum(), label='future ret')
plt.plot(spot_ret_raw['IC']['2021':].cumsum(), label='spot ret')
plt.plot(basis_ret_raw['IC']['2021':].cumsum(), label='basis ret')
plt.legend(loc='best', fontsize=12)
plt.xticks(rotation=30)
ax1.set_title('IC', fontsize=24)

ax2_left = fig.add_subplot(4,2,4)
plt.xticks(rotation=30)
ax2_left.plot(overnight_ret_amplitude_ic['2021':], label='ret amplitude(left axis)', color='darkorange')
ax2_left.legend(loc=2, fontsize=12)
ax2_right = ax2_left.twinx()
ax2_right.plot(basis_close_ic['2021':], label='closing basis(right axis)')
ax2_right.legend(loc=4, fontsize=12)
# ax2.set_title('spot&basis_ret', fontsize=18)

ax3 = fig.add_subplot(4,2,5)
plt.plot(future_ret_raw['IF']['2021':].cumsum(), label='future ret')
plt.plot(spot_ret_raw['IF']['2021':].cumsum(), label='spot ret')
plt.plot(basis_ret_raw['IF']['2021':].cumsum(), label='basis ret')
plt.legend(loc='best', fontsize=12)
plt.xticks(rotation=30)
ax3.set_title('IF', fontsize=24)

ax4_left = fig.add_subplot(4,2,6)
plt.xticks(rotation=30)
ax4_left.plot(overnight_ret_amplitude_if['2021':], label='ret amplitude(left axis)', color='darkorange')
ax4_left.legend(loc=2, fontsize=12)
ax4_right = ax4_left.twinx()
ax4_right.plot(basis_close_if['2021':], label='closing basis(right axis)')
ax4_right.legend(loc=4, fontsize=12)
# ax2.set_title('spot&basis_ret', fontsize=18)

ax5 = fig.add_subplot(4,2,7)
plt.plot(future_ret_raw['IH']['2021':].cumsum(), label='future ret')
plt.plot(spot_ret_raw['IH']['2021':].cumsum(), label='spot ret')
plt.plot(basis_ret_raw['IH']['2021':].cumsum(), label='basis ret')
plt.legend(loc='best', fontsize=12)
plt.xticks(rotation=30)
ax5.set_title('IH', fontsize=24)

ax6_left = fig.add_subplot(4,2,8)
plt.xticks(rotation=30)
ax6_left.plot(overnight_ret_amplitude_ih['2021':], label='ret amplitude(left axis)', color='darkorange')
ax6_left.legend(loc=2, fontsize=12)
ax6_right = ax6_left.twinx()
ax6_right.plot(basis_close_ih['2021':], label='closing basis(right axis)')
ax6_right.legend(loc=4, fontsize=12)
# ax2.set_title('spot&basis_ret', fontsize=18)
fig.suptitle('strategic performance', fontsize=36, fontweight='bold')
plt.savefig('/data/user/017024/share/overnight/strategy_tracking_report/Diamond_2_0/strategic_performance.png', dpi=360)


'''报告绘制第二部分：因子表现'''
'''因子值转化为仓位'''
factor_temp = factor_prod['2021':][factor_list].copy()
factor_temp = factor_temp.reindex(future_ret_raw['2021':].index)
adj_coef = pd.DataFrame(np.searchsorted([0.75, 0.8, 0.85, 0.9, 0.95, 1], factor_temp) * 0.2 + 0.4, index=factor_temp.index, columns=factor_temp.columns)
factor_temp[factor_temp < 0.75] = 0
factor_temp[factor_temp > 0] = 1
factor_temp_adj = factor_temp * adj_coef

single_factor_ret_ic = factor_temp_adj.multiply(future_ret_raw['2021':]['IC'], axis=0)
single_factor_ret_if = factor_temp_adj.multiply(future_ret_raw['2021':]['IF'], axis=0)
single_factor_ret_ih = factor_temp_adj.multiply(future_ret_raw['2021':]['IH'], axis=0)

'''ic绘图'''
fig = plt.figure(figsize=[15,24])#, dpi=540)
plt.subplots_adjust(hspace=1)
ax1 = fig.add_subplot(3,1,1)
temp_df1 = single_factor_ret_ic.iloc[-10:].sum().sort_values(ascending=False)
plt.bar(range(temp_df1.shape[0]), temp_df1, tick_label=temp_df1.index)
plt.xticks(rotation=90)
ax1.set_title('total return: last 10d', fontsize=24)

ax2 = fig.add_subplot(3,1,2)
temp_df2 = single_factor_ret_ic.iloc[-30:].sum().sort_values(ascending=False)
plt.bar(range(temp_df2.shape[0]), temp_df2, tick_label=temp_df2.index)
plt.xticks(rotation=90)
ax2.set_title('total return: last 30d', fontsize=24)

ax2 = fig.add_subplot(3,1,3)
temp_df3 = single_factor_ret_ic.sum().sort_values(ascending=False)
plt.bar(range(temp_df3.shape[0]), temp_df3, tick_label=temp_df3.index)
plt.xticks(rotation=90)
ax2.set_title('total return: ytd', fontsize=24)

fig.suptitle('factor performance: IC.CFE', fontsize=36, fontweight='bold')
plt.savefig('/data/user/017024/share/overnight/strategy_tracking_report/Diamond_2_0/factor_performance_IC.png', dpi=360)

'''if绘图'''
fig = plt.figure(figsize=[15,24])#, dpi=540)
plt.subplots_adjust(hspace=1)
ax1 = fig.add_subplot(3,1,1)
temp_df1 = single_factor_ret_if.iloc[-10:].sum().sort_values(ascending=False)
plt.bar(range(temp_df1.shape[0]), temp_df1, tick_label=temp_df1.index)
plt.xticks(rotation=90)
ax1.set_title('total return: last 10d', fontsize=24)

ax2 = fig.add_subplot(3,1,2)
temp_df2 = single_factor_ret_if.iloc[-30:].sum().sort_values(ascending=False)
plt.bar(range(temp_df2.shape[0]), temp_df2, tick_label=temp_df2.index)
plt.xticks(rotation=90)
ax2.set_title('total return: last 30d', fontsize=24)

ax2 = fig.add_subplot(3,1,3)
temp_df3 = single_factor_ret_if.sum().sort_values(ascending=False)
plt.bar(range(temp_df3.shape[0]), temp_df3, tick_label=temp_df3.index)
plt.xticks(rotation=90)
ax2.set_title('total return: ytd', fontsize=24)

fig.suptitle('factor performance: IF.CFE', fontsize=36, fontweight='bold')
plt.savefig('/data/user/017024/share/overnight/strategy_tracking_report/Diamond_2_0/factor_performance_IF.png', dpi=360)

'''ih绘图'''
fig = plt.figure(figsize=[15,24])#, dpi=540)
plt.subplots_adjust(hspace=1)
ax1 = fig.add_subplot(3,1,1)
temp_df1 = single_factor_ret_ih.iloc[-10:].sum().sort_values(ascending=False)
plt.bar(range(temp_df1.shape[0]), temp_df1, tick_label=temp_df1.index)
plt.xticks(rotation=90)
ax1.set_title('total return: last 10d', fontsize=24)

ax2 = fig.add_subplot(3,1,2)
temp_df2 = single_factor_ret_ih.iloc[-30:].sum().sort_values(ascending=False)
plt.bar(range(temp_df2.shape[0]), temp_df2, tick_label=temp_df2.index)
plt.xticks(rotation=90)
ax2.set_title('total return: last 30d', fontsize=24)

ax2 = fig.add_subplot(3,1,3)
temp_df3 = single_factor_ret_ih.sum().sort_values(ascending=False)
plt.bar(range(temp_df3.shape[0]), temp_df3, tick_label=temp_df3.index)
plt.xticks(rotation=90)
ax2.set_title('total return: ytd', fontsize=24)

fig.suptitle('factor performance: IH.CFE', fontsize=36, fontweight='bold')
plt.savefig('/data/user/017024/share/overnight/strategy_tracking_report/Diamond_2_0/factor_performance_IH.png', dpi=360)


'''PDF生成'''
story = []
stylesheet=getSampleStyleSheet()
normalStyle = stylesheet['Normal']


img1 = Image('/data/user/017024/share/overnight/strategy_tracking_report/Diamond_2_0/strategic_performance.png', width=450, height=650)
story.append(img1)
img2 = Image('/data/user/017024/share/overnight/strategy_tracking_report/Diamond_2_0/factor_performance_IC.png', width=450, height=650)
story.append(img2)
img3 = Image('/data/user/017024/share/overnight/strategy_tracking_report/Diamond_2_0/factor_performance_IF.png', width=450, height=650)
story.append(img3)
img4 = Image('/data/user/017024/share/overnight/strategy_tracking_report/Diamond_2_0/factor_performance_IH.png', width=450, height=650)
story.append(img4)

doc = SimpleDocTemplate('/data/user/017024/share/overnight/strategy_tracking_report/Diamond_2_0/Diamond_tracking_report_' + future_ret_raw.index[-1].strftime('%Y%m%d') +'11.pdf')
doc.build(story)



