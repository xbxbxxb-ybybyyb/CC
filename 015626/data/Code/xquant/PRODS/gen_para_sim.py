# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 17:41:43 2022

@author: appadmin
"""
import json,datetime,os,glob
from multiprocessing.pool import Pool
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import numpy as np
pd.set_option('max_columns', 200)
import glob
import bottleneck as bk
from xquant.factordata import FactorData

from xquant.xqutils.helper import link


sim = True

_,date,_ = check_update_date()

next_tday = udt.get_trading_day_offset(str(date),1)[0].strftime('%Y%m%d')
last_tday = udt.get_trading_day_offset(str(date),-1)[0].strftime('%Y%m%d')

close_data = IO.read_data([last_tday, next_tday], columns = 'close', alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5')

di_cszj_cat = {}
#for contractc in ['IC.CFE', 'IF.CFE', 'IM.CFE']:
#    close = close_data.xs(contractc, level = 1)['close']
#    close = close.between_time('0930', '1456')
#    ret = close.groupby(close.index.date).apply(lambda x:x.pct_change(1))
#    std = ret.rolling(30, min_periods = 20).std()
#    std = std.groupby(std.index.date).mean()
#    std.index = pd.to_datetime(std.index)
#    std = std.loc[str(date)]
#    print(close.index[-1], std)
#    if std < 0.0004:
#        di_cszj_cat[contractc] = 1.5e8 / 10000000
#    elif (std >= 0.0004) and (std < 0.0005):
#        di_cszj_cat[contractc] = 2e8 / 10000000
#    elif (std >= 0.0005) and (std < 0.0006):
#        di_cszj_cat[contractc] = 2.5e8 / 10000000
#    elif (std >= 0.0006) and (std < 0.0007):
#        di_cszj_cat[contractc] = 3e8 / 10000000
#    elif (std >= 0.0007) and (std < 0.0008):
#        di_cszj_cat[contractc] = 3.5e8 / 10000000
#    elif (std >= 0.0008):
#        di_cszj_cat[contractc] = 4e8 / 10000000

di_cszj_cat['IF.CFE'] = 2.5e8 / 10000000
di_cszj_cat['IC.CFE'] = 4e8 / 10000000
di_cszj_cat['IM.CFE'] = 4.5e8 / 10000000

jyzh_ic_buy = '203202'
jyzh_ic_sell = '203202'

jyzh_if_buy = '203202'
jyzh_if_sell = '203202'

jyzh_im_buy = '203202'
jyzh_im_sell = '203202'

recent_future_ic = ''
recent_future_if = ''
recent_future_im = ''

future_list_ic = 'IC2503.CF,IC2502.CF'
kcbl_list_ic = '6:2'
future_list_if = 'IF2503.CF,IF2502.CF'
kcbl_list_if = '1:0'
future_list_im = 'IM2503.CF,IM2502.CF'
kcbl_list_im = '7:2'

force_equal_ic = False
force_equal_if = False
force_equal_im = False

# 平今接口
pjjk_ic = 'hongye'
pjjk_if = 'hongye'
pjjk_im = 'hongye'

filter_num = 1
filter_bool_dict = {}
filter_bool_dict['IC.CFE'] = True
filter_bool_dict['IF.CFE'] = True
filter_bool_dict['IM.CFE'] = True

filter_name = 'futures_long_vol'
filter_dict = {}
filter_dict['futures_long_vol'] = {}
filter_dict['futures_long_vol']['IC.CFE'] = '>=0.00045'
filter_dict['futures_long_vol']['IF.CFE'] = '>=0.00045'
filter_dict['futures_long_vol']['IM.CFE'] = '>=0.00045'

cxsj_ic = 4
cxsj_if = 4
cxsj_im = 4

#model_list = ['ic_v7unifac', 'ic_v7c_orig', 'ic_short_v3c','if_v6nl', 'if_v7c_orig']

model_list = ['ic_v7unifac_orig_norm2',  
              'ic_v7unifac_crn_norm2', 
              'if_v7c_orig_norm2', 
              'if_v7_crn_norm2', 
              'im_v1unifac_crn_norm2', 
              'im_v1unifac_orig_norm2'
              ]
              #'im_v1unifac_crn', 'im_v1unifac_orig']


model_date_dict = {
                   #'if_v7c': '20241213_if_if_v7c',
                   #'if_v7c_orig': '20231229_if_if_v7c',
                   #'if_v7_crn': '20241213_if_if_v7_crn',
                   'if_v7c_orig_norm2': '20241213_if_if_v7c',
                   'if_v7_crn_norm2': '20241213_if_if_v7_crn',
                   
                   #'ic_v7c': '20230224_ic_ic_v7c',
                   'ic_v7unifac_crn_norm2': '20241213_ic_ic_v7unifac_crn',
                   'ic_v7unifac_orig_norm2': '20240628_ic_ic_v7unifac',                  
                   #'ic_v7unifac_crn': '20231229_ic_ic_v7unifac_crn',
                   #'ic_v7unifac_orig': '20231229_ic_ic_v7unifac',
                   #'ic_v7unifac': '20231229_ic_ic_v7unifac',
                
                   #'im_v1unifac_crn': '20231229_im_im_v1unifac_crn',
                   'im_v1unifac_crn_norm2': '20241213_im_im_v1unifac_crn',
                   #'im_v1unifac_orig': '20231229_im_im_v1unifac',
                   'im_v1unifac_orig_norm2': '20240628_im_im_v1unifac' 
                   }

# 初始资金
cszj_dict = {
            
             'if_v7c': 0,
             'if_v7c_orig': 0,
             'if_v7_crn': 0, 
             'if_v7c_orig_norm2': di_cszj_cat['IF.CFE'],
             'if_v7_crn_norm2':di_cszj_cat['IF.CFE'],
            
             'ic_v8unifac_crn_norm2':0,
             'ic_v7unifac_orig_norm2': di_cszj_cat['IC.CFE'],
             'ic_v7unifac_crn_norm2':di_cszj_cat['IC.CFE'],            
             'ic_v7unifac_orig': 0,
             'ic_v7unifac_crn': 0,
             'ic_v7unifac':0,
            
             'im_v1unifac_crn': 0,
             'im_v1unifac_crn_norm2': di_cszj_cat['IM.CFE'], 
             'im_v1unifac_orig': 0,
             'im_v1unifac_orig_norm2': di_cszj_cat['IM.CFE'],                   
            }


rank_dict = {
                   'if_v7c': [4800, 2400],
                   'if_v7c_orig_norm2': [4800, 2400],
                   'if_v7_crn_norm2': [4800, 2400],
                   'if_v7c_orig': [4800, 2400],
                   'if_v7_crn': [4800, 2400],
                   
                   'ic_v7unifac_crn': [4800, 2400],
                   'ic_v7unifac_orig':[4800, 2400],
                   'ic_v7unifac_crn_norm2': [4800, 2400],
                   'ic_v8unifac_crn_norm2': [4800, 2400],
                   'ic_v7unifac_orig_norm2':[4800, 2400],
                   'ic_v7unifac':[4800, 2400],
    
                   'im_v1unifac_crn_norm2': [4800, 2400],
                   'im_v1unifac_crn': [4800, 2400],
                   'im_v1unifac_orig_norm2': [4800, 2400],
                   'im_v1unifac_orig': [4800, 2400],
                    }

lstm_dict = {
                   'if_v7c': 10,
                   'if_v7c_orig_norm2': 10, 
                   'if_v7_crn_norm2': 10,
                   'if_v7c_orig': 10, 
                   'if_v7_crn': 10,
                
                
                   'ic_v7unifac_crn_norm2': 10,
                   'ic_v8unifac_crn_norm2': 10,
                   'ic_v7unifac_orig_norm2': 10,
                   'ic_v7unifac_crn': 10,
                   'ic_v7unifac_orig': 10,
                   'ic_v7unifac':10,
                   
                   'im_v1unifac_crn': 10,
                   'im_v1unifac_crn_norm2': 10,
                   'im_v1unifac_orig': 10,
                   'im_v1unifac_orig_norm2': 10,
                    }
                
vol_dict = {       'if_v7c': 30,
                   'if_v7c_orig_norm2': 0, 
                   'if_v7_crn_norm2': 0,
                   'if_v7c_orig': 0, 
                   'if_v7_crn': 0,
                   
                   'ic_v7unifac_crn_norm2': 0,
                   'ic_v8unifac_crn_norm2': 0,
                   'ic_v7unifac_orig_norm2': 0,
                   'ic_v7unifac_crn': 0,
                   'ic_v7unifac_orig': 0, 
                   'ic_v7unifac': 30,
                
                   'im_v1unifac_crn': 0,
                   'im_v1unifac_crn_norm2': 0,
                   'im_v1unifac_orig': 0,
                   'im_v1unifac_orig_norm2': 0,
                    }

pos_dict = {}


                            
pos_dict['if_v7c'] = [[0.0,    0.0001, 0.0002, 0.0003, 0.0005, 0.0006, 0.0007, 0.0008],
                      [0.0001, 0.0002, 0.0003, 0.0005, 0.0006, 0.0007, 0.0008, 100],
                      [0, 0, 0, 0, 0, 3.33, 6.66, 10],
                      [0, 3.33, 6.66, 10, 10, 10, 10, 10]]

pos_dict['ic_v7unifac'] = [[0.0,    0.0001, 0.0002, 0.0003, 0.0005, 0.0006, 0.0007, 0.0008],
                          [0.0001, 0.0002, 0.0003, 0.0005, 0.0006, 0.0007, 0.0008, 100],
                          [0, 0, 0, 0, 0, 3.33, 6.66, 10],
                          [0, 3.33, 6.66, 10, 10, 10, 10, 10]]
       
pos_dict['if_v7c_orig'] = [[0.0, 0.1, 0.2, 0.8,  0.85, 0.9,  0.95],
                          [0.1,  0.2, 0.8, 0.85, 0.9,  0.95, 100.0],
                          [0,    0,   0,   2.5,  5,    7.5,  10],
                          [0,    5,   10,  10,   10,   10,   10]]

pos_dict['if_v7_crn'] =[[0.0,  0.1, 0.2, 0.8,  0.85, 0.9,  0.95],
                        [0.1,  0.2, 0.8, 0.85, 0.9,  0.95, 100.0],
                        [0,    0,   0,   2.5,  5,    7.5,  10],
                        [0,    5,   10,  10,   10,   10,   10]]

                                                                                                                                                 
pos_dict['if_v7c_orig_norm2'] =[[0.0,  0.15, 0.25, 0.58, 0.64, 0.7, 0.77],
                                    [0.15, 0.25, 0.58, 0.64, 0.7, 0.77,  100.0],
                                    [0,    0,    0,    2.5,  5,    7.5,  10],
                                    [0,    5,    10,   10,   10,   10,   10]]

pos_dict['if_v7_crn_norm2'] =[[0.0,  0.07, 0.15, 0.66,  0.72, 0.78,  0.85],
                              [0.07, 0.15, 0.66,  0.72, 0.78,  0.85, 100.0],
                              [0,    0,    0,    2.5,  5,    7.5,  10],
                              [0,    5,    10,   10,   10,   10,   10]]

pos_dict['ic_v7unifac_crn'] =[[0.0,  0.1, 0.2, 0.8,  0.85, 0.9,  0.95],
                             [0.1,  0.2, 0.8, 0.85, 0.9,  0.95, 100.0],
                             [0,    0,   0,   2.5,  5,    7.5,  10],
                             [0,    5,   10,  10,   10,   10,   10]]
                            
pos_dict['ic_v7unifac_orig'] =[[0.0, 0.2, 0.3, 0.8,  0.85, 0.9,  0.95],
                              [0.2,  0.3, 0.8, 0.85, 0.9,  0.95, 100.0],
                              [0,    0,   0,   2.5,  5,    7.5,  10],
                              [0,    5,   10,  10,   10,   10,   10]]
                                
pos_dict['ic_v7unifac_orig_norm2'] =[[0.0,  0.15, 0.25, 0.61, 0.67, 0.73, 0.8],
                                    [0.15, 0.25, 0.61, 0.67, 0.73, 0.8,  100.0],
                                    [0,    0,    0,    2.5,  5,    7.5,  10],
                                    [0,    5,    10,   10,   10,   10,   10]]

pos_dict['ic_v7unifac_crn_norm2'] =[[0.0,  0.07, 0.15, 0.66,  0.72, 0.78,  0.85],
                                      [0.07, 0.15, 0.66,  0.72, 0.78,  0.85, 100.0],
                                      [0,    0,    0,    2.5,  5,    7.5,  10],
                                      [0,    5,    10,   10,   10,   10,   10]]

pos_dict['ic_v8unifac_crn_norm2'] =[[0.0,  0.07, 0.15, 0.7,  0.75, 0.8,  0.85],
                                    [0.07, 0.15, 0.7,  0.75, 0.8,  0.85, 100.0],
                                    [0,    0,    0,    2.5,  5,    7.5,  10],
                                    [0,    5,    10,   10,   10,   10,   10]]


pos_dict['im_v1unifac_crn'] =[[0.0,  0.1, 0.2, 0.8,  0.85, 0.9,  0.95],
                             [0.1,  0.2, 0.8, 0.85, 0.9,  0.95, 100.0],
                             [0,    0,   0,   2.5,  5,    7.5,  10],
                             [0,    5,   10,  10,   10,   10,   10]]

pos_dict['im_v1unifac_crn_norm2'] =[[0.0,  0.07, 0.15, 0.69,  0.75, 0.81,  0.88],
                                    [0.07, 0.15, 0.69,  0.75, 0.81,  0.88, 100.0],
                                    [0,    0,    0,    2.5,  5,    7.5,  10],
                                    [0,    5,    10,   10,   10,   10,   10]]

pos_dict['im_v1unifac_orig'] =[[0.0,  0.1, 0.2, 0.8,  0.85, 0.9,  0.95],
                             [0.1,  0.2, 0.8, 0.85, 0.9,  0.95, 100.0],
                             [0,    0,   0,   2.5,  5,    7.5,  10],
                             [0,    5,   10,  10,   10,   10,   10]]

                            
pos_dict['im_v1unifac_orig_norm2'] =[[0.0,  0.15, 0.25, 0.61, 0.67, 0.73, 0.8],
                                [0.15, 0.25, 0.61, 0.67, 0.73, 0.8,  100.0],
                                [0,    0,    0,    2.5,  5,    7.5,  10],
                                [0,    5,    10,   10,   10,   10,   10]]


for item in pos_dict.keys():
    assert(len(pos_dict[item][0]) == len(pos_dict[item][1]) == len(pos_dict[item][2]) == len(pos_dict[item][3])), 'FUCK!'


    
model_date_ic = []
vol_window_ic = []
cszj_ic = []
rank_list1_ic = [] 
rank_list2_ic = []

model_date_if = []
vol_window_if = []
cszj_if = []
rank_list1_if = [] 
rank_list2_if = []

model_date_im = []
vol_window_im = []
cszj_im = []
rank_list1_im = [] 
rank_list2_im = []

pos_ic0 = []
pos_ic1 = []
pos_ic2 = []
pos_ic3 = []
pos_ic4 = []

pos_if0 = []
pos_if1 = []
pos_if2 = []
pos_if3 = []
pos_if4 = []

pos_im0 = []
pos_im1 = []
pos_im2 = []
pos_im3 = []
pos_im4 = []

lstm_ic = []
lstm_if = []
lstm_im = []

norm2_ic = []
norm2_if = []
norm2_im = []

count_ic = 0
count_if = 0
count_im = 0



for model in (model_list):
    if 'ic_' in model:

        count_ic = count_ic + 1
        model_date_ic.append(model_date_dict[model])
        vol_window_ic.append(vol_dict[model])
        lstm_ic.append(lstm_dict[model])
        cszj_ic.append(cszj_dict[model])
        rank_list1_ic.append(rank_dict[model][0])
        rank_list2_ic.append(rank_dict[model][1])
        pos_ic0 = pos_ic0 + (pos_dict[model][0])
        pos_ic1 = pos_ic1 + (pos_dict[model][1])
        pos_ic2 = pos_ic2 + (pos_dict[model][2])
        pos_ic3 = pos_ic3 + (pos_dict[model][3])
        pos_ic4_temp = [count_ic] *len(pos_dict[model][0])
        pos_ic4 = pos_ic4 + pos_ic4_temp
        
        if 'norm2' in model:
            norm2_ic.append('norm2')
        else:
            norm2_ic.append('norm')
    elif 'if_' in model:

        count_if = count_if + 1
        model_date_if.append(model_date_dict[model])
        vol_window_if.append(vol_dict[model])
        lstm_if.append(lstm_dict[model])
        cszj_if.append(cszj_dict[model])
        rank_list1_if.append(rank_dict[model][0])
        rank_list2_if.append(rank_dict[model][1])
        pos_if0 = pos_if0 + (pos_dict[model][0])
        pos_if1 = pos_if1 + (pos_dict[model][1])
        pos_if2 = pos_if2 + (pos_dict[model][2])
        pos_if3 = pos_if3 + (pos_dict[model][3])
        pos_if4_temp = [count_if] *len(pos_dict[model][0])
        pos_if4 = pos_if4 + pos_if4_temp
        if 'norm2' in model:
            norm2_if.append('norm2')
        else:
            norm2_if.append('norm')
    elif 'im_' in model:

        count_im = count_im + 1
        model_date_im.append(model_date_dict[model])
        vol_window_im.append(vol_dict[model])
        lstm_im.append(lstm_dict[model])
        cszj_im.append(cszj_dict[model])
        rank_list1_im.append(rank_dict[model][0])
        rank_list2_im.append(rank_dict[model][1])
        pos_im0 = pos_im0 + (pos_dict[model][0])
        pos_im1 = pos_im1 + (pos_dict[model][1])
        pos_im2 = pos_im2 + (pos_dict[model][2])
        pos_im3 = pos_im3 + (pos_dict[model][3])
        pos_im4_temp = [count_im] *len(pos_dict[model][0])
        pos_im4 = pos_im4 + pos_im4_temp
        if 'norm2' in model:
            norm2_im.append('norm2')
        else:
            norm2_im.append('norm')
        


savepath = os.path.join('/data/user/015626/data/share/para/', 'Mobius_' + next_tday)
if not os.path.exists(savepath):
    os.makedirs(savepath)


iw = IO.read_data([date], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
zz500_list = iw[iw.index_weight_zz500 > 0].index.get_level_values(1).tolist()
hs300_list = iw[iw.index_weight_hs300 > 0].index.get_level_values(1).tolist()
zz1000_list = iw[iw.index_weight_zz1000 > 0].index.get_level_values(1).tolist()

def retrieve_suspension_helper(release_resource = True):
    data = job_wrapper(query_last_mdcontant, OnRecvMDConstant, postprocess_mdconstant, release_resource = release_resource)
    data = data[data.TradingPhaseCode == '8']
    return data.index.tolist()

#suspension_list = retrieve_suspension_helper()

#zz800_list = zz500_list + hs300_list
#zz800_suspension_list = list(set(zz800_list) & set(suspension_list))
#if len(zz800_suspension_list) == 0:
#    suspension_info = '    '
#else:
#    suspension_info = str(zz800_suspension_list)[1:-1].replace("'","").replace(' ','')
suspension_info = '    '
s = FactorData()
print('start')
WIND_AShareEODPrices = s.get_factor_value('WIND_AShareEODPrices',factors = ['S_INFO_WINDCODE','S_DQ_CLOSE','S_DQ_ADJFACTOR'], trade_dt=str(date))
WIND_AShareEODPrices = WIND_AShareEODPrices.sort_values(by = ['S_INFO_WINDCODE'])
WIND_AShareEODPrices.columns = ['股票代码','T-1日收盘价','T-1日adjFactor']
WIND_AShareEODPrices['T-1日收盘价'] = WIND_AShareEODPrices['T-1日收盘价'].fillna(1.0)
WIND_AShareEODPrices['T日查到的前收盘价'] = WIND_AShareEODPrices['T-1日收盘价']
WIND_AShareEODPrices = WIND_AShareEODPrices[['股票代码','T-1日收盘价','T日查到的前收盘价','T-1日adjFactor']]
zz500 = WIND_AShareEODPrices[WIND_AShareEODPrices['股票代码'].isin(zz500_list)]
hs300 = WIND_AShareEODPrices[WIND_AShareEODPrices['股票代码'].isin(hs300_list)]
zz1000 = WIND_AShareEODPrices[WIND_AShareEODPrices['股票代码'].isin(zz1000_list)]
print('end')
'''
FUCK CDR, FUCK CSI

fuck = '689009.SH'
from xquant.marketdata import MarketData
mdp = MarketData()
tick = mdp.get_data_by_date("Stock", fuck, str(date), ['1','2','3', '4','5'])
def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
tick['dt'] = tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
tick = tick.set_index('dt')
preclose_spec = float(tick['LastPx'].iloc[-1])
temp_listdf = pd.DataFrame([fuck, preclose_spec, preclose_spec, 1], index = zz500.columns).T
zz500 = pd.concat([zz500, temp_listdf])
'''
zz1000.to_csv(os.path.join(savepath, 'zz1000.csv'), index = False, encoding='gbk')
zz500.to_csv(os.path.join(savepath, 'zz500.csv'), index = False, encoding='gbk')
hs300.to_csv(os.path.join(savepath, 'hs300.csv'), index = False, encoding='gbk')

fore30day = udt.get_trading_day_offset(str(date), -30)[0].strftime('%Y%m%d')
future_univ = IO.read_data([fore30day, next_tday],columns=['contract_main','contract_00'], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
future_univ = future_univ.reset_index().set_index('Ticker').loc[['IC.CFE', 'IF.CFE', 'IH.CFE', 'IM.CFE']].reset_index().set_index(['dt', 'Ticker']).sort_index()
future_univ = future_univ[['contract_main','contract_00']].reset_index()
future_univ['Ticker'] = future_univ.Ticker.apply(lambda x:x.split('.')[0])
future_univ.columns = ['交易日','期货品种','主力合约代码','近月合约代码']
future_univ['主力合约代码'] = future_univ['主力合约代码'].apply(lambda x:x[:-1])
future_univ['近月合约代码'] = future_univ['近月合约代码'].apply(lambda x:x[:-1])
future_univ.columns = ['交易日','期货品种','主力合约代码','近月合约代码']
fu = future_univ.copy()
#    # 给出次日universe，默认和前一日一样
#    nextfuture_univ = future_univ[future_univ['交易日'] == pd.to_datetime(str(date))]
#    nextfuture_univ['交易日'] = pd.to_datetime(str(next_tday))
#    future_univ = future_univ.append(nextfuture_univ)
#    future_univ = future_univ.sort_values(by = '交易日')

future_univ['交易日'] = future_univ['交易日'].apply(lambda x:x.strftime('%Y-%m-%d'))
future_univ = future_univ.replace('NaN','na')
future_univ = future_univ.fillna(value = 'na')


future_univ.to_csv(os.path.join(savepath, 'future_univ.csv'), index = False, encoding='gbk')

for contract_cat in ['IF.CFE', 'IC.CFE', 'IM.CFE']:
    trade_nextday = fu.set_index(['交易日', '期货品种']).xs(contract_cat.replace('.CFE', ''), level = 1)['近月合约代码'].loc[str(next_tday)]
    trade_lastday = fu.set_index(['交易日', '期货品种']).xs(contract_cat.replace('.CFE', ''), level = 1)['近月合约代码'].loc[str(date)]
    if trade_nextday != trade_lastday:
        lm = link.LinkMessage()
        lm.sendMessage('即将换月，交易品种%s'%trade_nextday)
        del lm
    
    
    if 'IC' in contract_cat:
        dyjdxdsf = 'alg4'
        force_equal = force_equal_ic
        pos0 = pos_ic0
        pos1 = pos_ic1
        pos2 = pos_ic2
        pos3 = pos_ic3
        pos4 = pos_ic4
        future_list = future_list_ic
        kcbl_list = kcbl_list_ic
        model_date = model_date_ic
        vol_window = vol_window_ic
        cszj = cszj_ic
        rank_list1 = rank_list1_ic
        rank_list2 = rank_list2_ic
        lstm = lstm_ic
        jyzh_buy = jyzh_ic_buy
        jyzh_sell = jyzh_ic_sell
        recent_future = recent_future_ic
        norm2 = norm2_ic
        cxsj = cxsj_ic
        trail = ''
        machine = '#503101'
    elif 'IF' in contract_cat:
        dyjdxdsf = 'alg4'
        force_equal = force_equal_if
        pos0 = pos_if0
        pos1 = pos_if1
        pos2 = pos_if2
        pos3 = pos_if3
        pos4 = pos_if4
        future_list = future_list_if
        kcbl_list = kcbl_list_if
        model_date = model_date_if
        vol_window = vol_window_if
        cszj = cszj_if
        rank_list1 = rank_list1_if
        rank_list2 = rank_list2_if
        lstm = lstm_if
        jyzh_buy = jyzh_if_buy
        jyzh_sell = jyzh_if_sell
        recent_future = recent_future_if
        norm2 = norm2_if
        cxsj = cxsj_if
        trail = '_if'
        machine = '#503102'
    elif 'IM' in contract_cat:
        dyjdxdsf = 'alg4'
        force_equal = force_equal_im
        pos0 = pos_im0
        pos1 = pos_im1
        pos2 = pos_im2
        pos3 = pos_im3
        pos4 = pos_im4
        future_list = future_list_im
        kcbl_list = kcbl_list_im
        model_date = model_date_im
        vol_window = vol_window_im
        cszj = cszj_im
        rank_list1 = rank_list1_im
        rank_list2 = rank_list2_im
        lstm = lstm_im
        jyzh_buy = jyzh_im_buy
        jyzh_sell = jyzh_im_sell
        recent_future = recent_future_im
        norm2 = norm2_im
        cxsj = cxsj_im
        trail = '_im'
        machine = '#503103'
        
        
    sc = []
    hsig = []
    filter_name_final_list = []
    filter_bar_list = []
    filter_num_list = []
    filter_bool_list = []
    for i, mi in enumerate(model_date):
        
        history_menu_title = str(next_tday) + '_' + str(mi)
        
        sc.append('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/%s/' % (str(mi)))
        
        if (filter_bool_dict[contract_cat] == True) and (norm2[i] != 'norm'):
            filter_name_final_list.append(filter_name + trail)
            filter_bar_list.append(filter_dict[filter_name][contract_cat])
            filter_num_list.append(filter_num)
            filter_bool_list.append(1)
        else:
            filter_name_final_list.append('')
            filter_bar_list.append('')
            filter_num_list.append('')
            filter_bool_list.append(0)
        
        if norm2[i] == 'norm':
            hsig.append(('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historySignal' % (history_menu_title)))
        else:
            hsig.append(('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/signalNorm2Value' % (history_menu_title)))
            
        
    if recent_future.endswith( '.CF'):
        pass
    else:
        recent_future = IO.read_data([next_tday], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
        recent_future = recent_future.xs(contract_cat, level = 1)['contract_00'].tolist()[0][:-1]
    print(recent_future)
    if len(future_list) == 0:
        future_list1 = []
        future_list1.append(recent_future)
    else:
        future_list1 = [item.replace(' ', '') for item in future_list.split(',')]
    kclb = str(future_list1).replace('[', '').replace(']', '').replace("'", "").replace(' ', '')
    def get_trade_starttime(date, next_tday):
        if (datetime.datetime.strptime(str(next_tday),'%Y%m%d') - datetime.datetime.strptime(str(date),'%Y%m%d')).days > 3:
            return '10:00:00'
        else:
            return '09:39:00'

    trade_starttime = get_trade_starttime(date, next_tday)
    if jyzh_buy == '5160701':
        mmbm_buy = '00000004'
        pjjk_buy = 'hongye'
    elif jyzh_buy == '5160702':
        mmbm_buy = '00060160'
        pjjk_buy = 'hongye'
    elif jyzh_buy == '5160603':
        mmbm_buy = '00060160'
        pjjk_buy = 'huatai'
    elif jyzh_buy == '203202':
        mmbm_buy = '00060160'
        pjjk_buy = 'hongye'
    
    if jyzh_sell == '5160701':
        mmbm_sell = '00000004'
        pjjk_sell = 'hongye'
    elif jyzh_sell == '5160702':
        mmbm_sell = '00060160'
        pjjk_sell = 'hongye'
    elif jyzh_sell == '5160603':
        mmbm_sell = '00060160'
        pjjk_sell = 'huatai'
    elif jyzh_sell == '203202':
        mmbm_sell = '00060160'
        pjjk_sell = 'hongye'
    
    di_long = []
    di_short = []
    
    jyzh = jyzh_buy

    dfff = pd.read_excel('/data/user/011477/order/tradingReport/tradingStat_%s.xlsx'%date, sheet_name='Tri_51606')#.set_index('委托方向')
    l = dfff['组合名称']
    l = [item for item in l if (('mobius' in item.lower()) & (jyzh in item)) | ((jyzh in item))][0]
    positions = dfff[dfff['组合名称'] == l]['期货持仓'].iloc[0]
    dic_temp = json.loads(positions.replace("'", '"'))
    
    if sim == False:
        for future in future_list1:
            try:
                short_temp = dic_temp[future[:-3] + '空仓']
            except:
                short_temp = 0
            try:
                long_temp = dic_temp[future[:-3] + '多仓']
            except:
                long_temp = 0
            if force_equal == False:
                pass
            else:
                if long_temp == short_temp:
                    pass
                else:
                    long_temp = min([long_temp, short_temp])
                    short_temp = min([long_temp, short_temp])
            di_long.append(long_temp)
            di_short.append(short_temp)
        
    elif sim == True:
        di_long = [0] * len(future_list1)
        di_short = [0] * len(future_list1)
    else:
        pass
    

           
    if 'IC' in contract_cat.upper():
        factor_init = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_V5.0.3.2.json'
        xdjg = 1
        xdjg2 = 0.8
        hycs = 200
        pjjk = pjjk_ic
        zcdybh = 'no'#''200000320
        
    elif 'IF' in contract_cat.upper():
        factor_init = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_IF_V5.0.3.json'
        xdjg = 0.6
        xdjg2 = 0.4
        hycs = 300
        pjjk = pjjk_if
        zcdybh = 'no'#''200000320
        
        
    elif 'IM' in contract_cat.upper():
        factor_init = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_IM_V5.0.3.json'
        xdjg = 1
        xdjg2 = 0.8
        hycs = 200
        pjjk = pjjk_im
        zcdybh = 'no'#''200000320
        
    # 交易账户为5160603时 证券账户为  00060160

    paradict = {
                '开仓列表': kclb,
                '开仓比例': kcbl_list,
                '交易日期': int(next_tday),
                '行情分钟数据目录': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/mobius_data_for_prod/minuteData/%s/' % str(next_tday),
                
                '历史因子文件目录': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/' % (next_tday + '_all' + trail),
                '因子配置文件': factor_init,
                '是否记录因子值': 'true',
                '静态信息查询失败时是否使用本地文件': 'true',
                '是否校验历史数据': 'false',
                '中证1800停牌列表': suspension_info,
                '开始处理分钟聚合数据时间': '09:30:00',
                '买入交易账户': jyzh_buy,
                '卖出交易账户': jyzh_sell,
                '买入证券账户': mmbm_buy,
                '卖出证券账户': mmbm_sell,
                '合约乘数': hycs,
                #'初始资金（千万元）': 40,
                '下单价格滑点': xdjg,
                '第二阶段下单价格滑点':xdjg2,
                '下单间隔': 0.8,
                '订单存续时间(秒)': cxsj,

                '交易开始时间': trade_starttime,
                '开仓截止时间': '14:29:00',
                '平仓开始时间': '14:45:00',
                '平仓结束时间': '14:50:00',
                '废单次数上限': 800,
                '过去1分钟最大下单次数': 120,
                '过去1分钟最大撤单次数': 120,
                '当日成交总量': 1600,
                #'是否调用平今仓接口': pjjk,
                '当日撤单次数上限': 320,
                '最大委托次数': 3000,
                '最大撤废次数':50,
                '多组模型是否并行预测': 'true',
                #'平今仓使用账户所属期货公司': pjjk,
                '买入交易账户平今仓查询公司': pjjk_buy,
                '卖出交易账户平今仓查询公司': pjjk_sell,
                '资产单元编号': zcdybh,
                '保证金查询阈值1(千万元)': 5,
                '保证金查询阈值2(千万元)': 2,
                '每分钟成交量上限': 80,
                '委托参考tick数量': 4,
                '单笔委托上限':3,
                '最大委托价格档位':2,
                '第二阶段最大委托价格档位':1,
                '下单第一阶段存续时间(S)':10,
                '第一阶段下单算法':dyjdxdsf,
                '第二阶段下单算法':'alg4',
                'Alg4撤单间隔时间(ms)':100,
               }
    FAK = { 'FAK委托slippage列表': ['0.6,0.8,1,1.2'],
            'FAK单个slippage下单次数': [2],
            'FAK 1秒内发单次数上限': [5],
            'FAK发单间隔': [0.2],
            'FAK单笔委托数量': [2]

            }
    paradict2 = {'合约代码': future_list1,
                 '平仓优先级': list(range(1, len(future_list1) + 1)),
                 '卖出交易账户多头持仓': di_long,
                 '买入交易账户空头持仓': di_short
        
                }
                
    
    paradict3 = {'信号编号': list(range(1, len(sc)+1)),
                 '对应模型目录': sc,
                 '历史信号文件目录':hsig,
                 '初始资金（千万元）': cszj,
                 '波动率时间窗口': vol_window,
                 'Rank周期1':  rank_list1,
                 'Rank周期2':  rank_list2,
                 'LSTM模型输入因子步长':lstm,
                 'Rank计算方法':  norm2,
                 '是否启用过滤': filter_bool_list,
                 '过滤指标满足数量': filter_num_list,
                 '过滤指标':filter_name_final_list,
                 '过滤指标对应阈值' :filter_bar_list,

                }
    
    lm = link.LinkMessage()
    lm.sendMessage(str(future_list1))
    lm.sendMessage(str(cszj) + ' 千万')
    del lm
    
    
    signal_to_pos = {'信号左边界': pos0,
                     '信号右边界': pos1,
                     '仓位左边界': pos2,
                     '仓位右边界': pos3,
                     '所属信号编号': pos4}
    
                        
    signal_to_pos = pd.DataFrame(signal_to_pos)   
    FAK = pd.DataFrame(FAK)
    InitialBasicParam = pd.DataFrame(paradict, index = ['num'])
    InitialPos = pd.DataFrame(paradict2)
    Sig_init = pd.DataFrame(paradict3)
    if sim == True:
        writer = pd.ExcelWriter(os.path.join(savepath, 'MobiusStrategy_%s_sim#102313.xlsx' % (contract_cat[:-4] + '_' +str(next_tday))))
    else:
        writer = pd.ExcelWriter(os.path.join(savepath, 'MobiusStrategy_%s.xlsx' % (contract_cat[:-4] + '_' +str(next_tday) + machine)))
    InitialBasicParam.to_excel(writer, 'InitialBasicParam', index=False)
    FAK.to_excel(writer, 'FAK下单参数', index=False)
    InitialPos.to_excel(writer, '期初持仓列表', index=False)
    signal_to_pos.to_excel(writer, '信号到仓位配置参数', index=False)
    Sig_init.to_excel(writer, '信号模型配置列表', index=False)
    hs300.to_excel(writer, '沪深300成分股收盘价信息', index=False)
    zz500.to_excel(writer, '中证500成分股收盘价信息', index=False)
    zz1000.to_excel(writer, '中证1000成分股收盘价信息', index=False)
    future_univ.to_excel(writer, '最近30个交易日主力近月合约信息', index=False)
    writer.save()


