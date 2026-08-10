import sys, os
sys.path.insert(1,'/data/user/016700/Trade_Codes/futures-factor-framework/factor_framework/')
sys.path.insert(4,'/data/user/016700/Trade_Codes/futures-factors-2/utils')


from multifactor.data.utils import *
from multiprocessing import Pool
import multifactor.utility.dt as udt
import os
import pandas as pd
from joblib import Parallel, delayed
from xquant.xqutils.helper import link
from future_factor import FutureFactor
from data_player import DataPlayer
from data_center import DataCenter
_,date,_ = check_update_date()
last_date = udt.get_trading_day_offset(str(date),-1)[0].strftime('%Y%m%d')
next_date = udt.get_trading_day_offset(str(date),1)[0].strftime('%Y%m%d')
weight_path = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5'

flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' 


def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_ic_factors.success'
    path2 = flag_rootpath + str(date) + '/' + str(date) + '_if_factors.success'
    path3 = flag_rootpath + str(date) + '/' + str(date) + '_ic_zscore.success'
    path4 = flag_rootpath + str(date) + '/' + str(date) + '_if_zscore.success'
    path5 = flag_rootpath + str(date) + '/' + str(date) + '_im_zscore.success'
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4) and os.path.exists(path5)

print('------wait data flag')
while True:
    if minute_flag_check(date):
        break
    time.sleep(60)
print('flag check finished!')



def get_target_list(ticker, startdate, enddate):
    tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50','IM.CFE':'index_weight_zz1000'}
    tickercolumn = tickerdict[ticker]
    indexweight = IO.read_data([startdate, enddate],columns = [tickercolumn], alt = weight_path)
    indexweight = indexweight.unstack().shift(1).stack()
    universe = indexweight[indexweight[tickercolumn]>0]
    universe = universe.reset_index()
    universe['dt'] = universe.dt.apply(lambda x:int(str(x)[:10].replace('-','')))
    return np.array(universe).tolist()
_1 = get_target_list('IF.CFE', last_date, date) + get_target_list('IC.CFE', last_date, date) + get_target_list('IM.CFE', last_date, date)

_11 = pd.DataFrame(_1)
stock_list = list(_11[1])

#for stock in stock_list:

def check_minute(stock):
    temp = IO.read_data([date, next_date], alt = '/dfs/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE/' + stock + '.h5').loc[str(date)]
    if len(temp)!= 237:
        return stock
    else:
        return
with Pool(24) as pool:
    holder = pool.map(check_minute, stock_list)
holder = [item for item in holder if item != None]

lm = link.LinkMessage()
if len(holder) > 0:
    lm.sendMessage(str(holder))
else:
    lm = link.LinkMessage()
    lm.sendMessage('---------- 今日股票分钟无误 ----------')
    del lm


fill_ratio_t = 0.9
fill_ratio_bar_t = 5

check_stock_list = ['volume', 'BuyTradeMoney', 'SellTradeMoney', 'lo_amount']

def check_fill_ratio(date):
    dc_ic = DataCenter(variety = 'IC', data_type='IndexStock', instrument_type='recent', 
                    data_dict = {'Stock':check_stock_list}, start_date = str(date), end_date = str(date), days_past = 0)
    dc_if = DataCenter(variety = 'IF', data_type='IndexStock', instrument_type='recent', 
                    data_dict = {'Stock':check_stock_list}, start_date = str(date), end_date = str(date), days_past = 0)
    dc_im = DataCenter(variety = 'IM', data_type='IndexStock', instrument_type='recent', 
                    data_dict = {'Stock':check_stock_list}, start_date = str(date), end_date = str(date), days_past = 0)
    vic = dc_ic.get_stock_data()['volume'].copy()
    vif = dc_if.get_stock_data()['volume'].copy()
    vim = dc_im.get_stock_data()['volume'].copy()
    vicc = list(vic.columns)
    vifc = list(vif.columns)
    vimc = list(vim.columns)
    temp = vic.join(vif[list(set(vifc) - set(vicc))]).join(vim[list(set(vimc) - set(vifc) - set(vicc))])
    temp = temp > 0
    fill_ratio = temp.sum(axis = 1) / max(1800, temp.shape[1])

    if len(fill_ratio[fill_ratio < fill_ratio_t]) > fill_ratio_bar_t:
        print('stock fill ratio wrong:  %s' %  'volume')

    temp = dc_ic.get_stock_data()['BuyTradeMoney'].join(dc_if.get_stock_data()['BuyTradeMoney'][list(set(vifc) - set(vicc))]).join(dc_im.get_stock_data()['BuyTradeMoney'][list(set(vimc) - set(vifc) - set(vicc))])
    temp = temp + dc_ic.get_stock_data()['SellTradeMoney'].join(dc_if.get_stock_data()['SellTradeMoney'][list(set(vifc) - set(vicc))]).join(dc_im.get_stock_data()['SellTradeMoney'][list(set(vimc) - set(vifc) - set(vicc))])
    temp = temp + dc_ic.get_stock_data()['lo_amount'].join(dc_if.get_stock_data()['lo_amount'][list(set(vifc) - set(vicc))]).join(dc_im.get_stock_data()['lo_amount'][list(set(vimc) - set(vifc) - set(vicc))])
    temp = temp > 0
    fill_ratio = temp.sum(axis = 1) / max(1800, temp.shape[1])
    
    lm = link.LinkMessage()
    if len(fill_ratio[fill_ratio < fill_ratio_t]) > fill_ratio_bar_t:
        lm.sendMessage('stock fill ratio wrong:  %s' %  'BuyTradeMoney SellTradeMoney lo_amount')
    else:
        
        lm.sendMessage('---------- 今日股票数据无误 ----------')
        del lm

import multifactor.utility.dt as udt

check_fill_ratio(date)



for file in os.listdir('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/'):
    if 'if_ever' in file.lower() or 'ic_unifac' in file.lower() or 'im_unifac' in file.lower():
        read_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/' + file
        
        def check_factors1(item, read_path = read_path):
            #print(item)
            temp = pd.read_hdf(read_path +  '/minute_norm/'+ item)
            temp1 = pd.read_hdf(read_path +  '/minute_raw/'+ item)
            if len(temp.loc[str(last_date):]) != 474 or (int(temp1.loc[str(date)].isna().sum()) > 150):
                lm = link.LinkMessage()
                lm.sendMessage(read_path +  '_' + item)
                del lm
                return 1
            return 0
        
        with Pool(24) as pool:
            holder = pool.map(check_factors1, os.listdir(read_path + '/minute_norm/'))

if sum(holder) == 0:
    lm = link.LinkMessage()
    lm.sendMessage('---------- 今日因子生成无误 ----------')
    del lm