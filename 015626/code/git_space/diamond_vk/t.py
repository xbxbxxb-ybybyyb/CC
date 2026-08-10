from diamond_vk.factor_generator import *
from diamond_vk.prepare_hot_dummy import *
import json,datetime,os,glob
from multiprocessing.pool import Pool
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
import multifactor.utility.dt as udt

#executor()

# retrieve data
#def get_data(date):
##    if os.path.exists('/arch0/group/800466/trade/diamond_vk/history/%d/history_09301446.pkl' % date) and os.path.exists('/arch0/group/800466/trade/diamond_vk/hot_proof/%d/ccbond_stock_kline_1min_092500_144300.h5' % date):
##        return
#    prepare_history(date)
#    prepare_hot_dummy(date)
    
#get_data(20220228)
executor()   

#_,_,date_list = check_update_date(20180901,20181101)
#with Pool(24) as pool:
#    pool.map(get_data, date_list)

# get history factor
#def get_factor(date):
#    print(date)
#    executor_factor(trade_date=date, max_workers = 1)
    
#def get_model(date):
#    print(date)
#    executor_model(trade_date=date)

#_,_,date_list = check_update_date(20220211,20220228)
#for date in date_list:
#    get_model(date)
#with Pool(24) as pool:
#    pool.map(get_factor, date_list)
    