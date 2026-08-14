# @Time : 2021/6/29 13:31
# @Author : Zhichen Lu
# @File : fix5minIntegration.py

import pandas as pd
import os
from Script.lzc.pitches_integration import out_signal

source = '/data/user/015836/HFmodel/M5Model/20210623DTC100Tree/'
target_path = '/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Min5Fixlize/'

tag = 'Tree5min'

if not os.path.exists(target_path):
    os.mkdir(target_path)
    os.mkdir(f'{target_path}{tag}')
    os.mkdir(f'{target_path}{tag}_val_pred/')

import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])
bar_list = [1000,1030,1100,1300,1330,1400,1430]
for i in range(100):
    _,train_end,_,_ = para_list[i][1]
    pred = pd.read_pickle(f'{source}pred/{i}.pkl')
    val = pd.read_pickle(f'{source}test/{i}.pkl')
    pred = pred[pred['time'].isin(bar_list)].set_index(['date','time','code'])
    val = val[val['time'].isin(bar_list)].set_index(['date','time','code'])
    pd.to_pickle(pred,f'{target_path}{tag}_val_pred/{train_end}.pkl')
    val.index[-1]