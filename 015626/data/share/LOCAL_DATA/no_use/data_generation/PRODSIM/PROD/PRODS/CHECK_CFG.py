import sys
sys.path.insert(1,'/data/user/016700/Data/Codes/git_space/futures-factor-framework/factor_framework/')

import pandas as pd
import numpy as np
from data_center import DataCenter

import multifactor.utility.dt as udt
from multifactor.data.utils import *

fill_ratio_t = 0.95
fill_ratio_bar_t = 5

check_stock_list = ['volume', 'BuyTradeMoney', 'SellTradeMoney']
flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'

from xquant.xqutils.helper import link

def send_message(message):
    
    lm = link.LinkMessage()
    lm.sendMessage(message)
    del(lm)

def check_fill_ratio(date):
    dc_ic = DataCenter(variety = 'IC', data_type='IndexStock', instrument_type='recent', 
                    data_dict = {'Stock':check_stock_list}, start_date = str(date), end_date = str(date), days_past = 0)
    dc_if = DataCenter(variety = 'IF', data_type='IndexStock', instrument_type='recent', 
                    data_dict = {'Stock':check_stock_list}, start_date = str(date), end_date = str(date), days_past = 0)
 
    temp = dc_ic.get_stock_data()['volume'].join(dc_if.get_stock_data()['volume'])
    temp = temp > 0
    fill_ratio = temp.sum(axis = 1) / 800

    if len(fill_ratio[fill_ratio < fill_ratio_t]) > fill_ratio_bar_t:
        print('stock fill ratio wrong:  %s' %  'volume')

    temp = dc_ic.get_stock_data()['BuyTradeMoney'].join(dc_if.get_stock_data()['BuyTradeMoney'])
    temp = temp + dc_ic.get_stock_data()['SellTradeMoney'].join(dc_if.get_stock_data()['SellTradeMoney'])
    temp = temp > 0
    fill_ratio = temp.sum(axis = 1) / 800

    if len(fill_ratio[fill_ratio < fill_ratio_t]) > fill_ratio_bar_t:
        send_message('stock fill ratio wrong:  %s' %  'BuyTradeMoney SellTradeMoney')

def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_CFG.success'
    path2 = flag_rootpath + str(date) + '/' + str(date) + '_INDUSTRY.success'
    path3 = flag_rootpath + str(date) + '/' + str(date) + '_INDEX.success'
    path4 = flag_rootpath + str(date) + '/' + str(date) + '_stock_index_future_universe.success'
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)
    
    
if __name__ == '__main__':
    
    _, date, htv = check_update_date()
    flag_path = flag_rootpath + str(date) + '/'

    print('------wait minute flag')
    while True:
        if minute_flag_check(date):
            break
        time.sleep(60)
    print('flag check finished!')
    check_fill_ratio(date)