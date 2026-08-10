from multiprocessing.pool import Pool
import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from os import listdir
from os.path import isfile, join
import os
import pickle
import numpy as np
from overnight.data_center import *
from overnight.utility import *
from overnight.naming_config import *
from overnight.factor_generator import *
from overnight.prepare_hot_dummy import *
import warnings
from multiprocessing import Pool
import importlib
from xquant.xqutils.helper import link
lm = link.LinkMessage()


need_path1 = '/data/group/800466/trade/overnight/history/'
need_days = [i for i in os.listdir(need_path1) if (int(i)>20210531)&(int(i)<20210806)]

#list_a = []
#for i in need_days:
#    temp_path = os.path.join(need_path1, i)
#    if not os.path.exists(os.path.join(temp_path, 'history_09301409.pkl')):
#        list_a.append(i)
#need_days = list_a.copy()

need_days = ['20170616', '20161010', '20161207', '20160802']

def func1(date):
    try:
        print(date)
        prepare_history(trade_date = date, has_hist=False, need_raw=False)
    except Exception as e:
        print(e)
        pd.Series(e).to_csv('/data/user/017024/waiting_for_delete/' + date + '_hist_1409.csv')
    
    
if __name__ == '__main__':
    with Pool() as pool:
        pool.map(func1, need_days)
    lm.sendMessage('hist_data更新完毕！')
#    for i in need_days:
#        func1(date=i)