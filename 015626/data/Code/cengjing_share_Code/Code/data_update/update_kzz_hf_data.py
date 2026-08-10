from xquant.bonddata import BondData

import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import numpy as np
import os
from multiprocessing import Pool
import time
from multifactor.data.utils import *

def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
    
def get_dt(a, b):
    year = a//10000
    month = a%10000//100
    day = a%100
    
    hour = b//100
    minute = b%100
    return datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),0)
    

def get_hfdata_test(para):
    bd = BondData()
    date = para[0]
    symbol = para[1]
    
 
    tick =  bd.get_bond_data(symbol, "%s 090000000" % str(date), "%s 150000000" % str(date), 'TICK')
    del(bd)
    
def get_target_list(cdatelist):
    bd = BondData()
    paralist = []
    for cdate in cdatelist:
        paralist = paralist + [[cdate, x] for x in bd.get_bond_set(str(cdate), 'kzz')]
    del(bd)
    return paralist

def get_index_fromdate(date):
    t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00',
                                                                                              '15:00:00',
                                                                                              freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for m in t_mins_list:
        index_list.append(str(date) + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    return index_min.set_index('dt').sort_index()
    

        
if __name__ == '__main__':
    rootpath = '/arch1/group/800466/warehouse/prod/MD/CHINA_CONVERTIBLE_BOND/tick_transaction_to_minute/'
   
    _,_,cdatelist = check_update_date(20210723,20210726)

    paralist = get_target_list(cdatelist)

    for x in list(set([y[0] for y in paralist])):
        csvpath = os.path.join(rootpath, str(x))
        if not os.path.exists(csvpath):
            os.makedirs(csvpath)
            
    # download data   
    #for para in paralist:
    #    get_hfdata_test(para)    
    with Pool(processes = 6) as pool:
        pool.map(get_hfdata_test, paralist)

   
