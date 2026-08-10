import sys
sys.path.insert(4,'/data/group/800466/trade/overnight/code/')

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

def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day
    """
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([19980101, 21000101], ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(datetime.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x: abs(x - current_date) if x <= current_date else 100)
    if current_hour < new_date_time and nearest_date == current_date:
        print('Not till refresh time ' + str(new_date_time) + ':00')
        current_date = fdate_list[fdate_list.index(current_date) - 1]
        print('Use previous trading date: ' + str(current_date))
    elif nearest_date < current_date:
        current_date = nearest_date
    elif current_hour >= new_date_time and nearest_date == current_date:
        print('Right on time: ' + str(current_date))
    return current_date

date = get_current_date()
print(date)
a = pd.read_hdf('/data/group/800466/trade/overnight/cache/edb.h5')
b = pd.read_hdf('/data/group/800466/trade/overnight/hot/%s/edb.h5' % str(date))
b = b.loc[~b.index.isin(a.index)]
a.append(b).sort_index().to_hdf('/data/group/800466/trade/overnight/cache/edb.h5', 'edb')

prepare_hot_dummy(date)
facdf = executor(trade_date = date, mode = 'history')
savepath = os.path.join('/data/group/800466/trade/overnight/factor_proof', str(date))
if not os.path.exists(savepath):
    os.makedirs(savepath)
facdf.to_csv(os.path.join(savepath, str(date) + '.csv'))