import pandas as pd
from multifactor.IO import IO
pd.set_option('max_columns', 50)
import datetime
import re
import os
import time
from multifactor.data.utils import *



def get_futuretick_bydate(sdate = None, edate = None, kind = 'MAIN'):
    _,_,cdate_list = check_update_date(sdate, edate)
            
    root_path = '/data/user/015626/data/share/future/new_STOCK_INDEX_FUTURE'
    save_path = '/data/user/015626/data/share/future/new_STOCK_INDEX_FUTURE_MAIN'
    for i in range(len(cdate_list)):
        starttime = time.time()
        if i == 0:
           continue
        wind_code_list = IO.read_data([cdate_list[i]], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/DAILY/' + kind + '/MD_CHINA_FUTURES_DAILY_' + kind + '.h5').WIND_CODE.tolist()
        for ticker in wind_code_list:
           
            exchange = ticker.split('.')[1]
            contract = ticker.split('.')[0]
            category = ''.join(re.findall(r'[A-Za-z]', contract))
        
            if category not in ['IF', 'IC','IH']:
                continue
           
            dtime = str(cdate_list[i])
            print(dtime,' ' , category + '_' + exchange, ' ',ticker)
            
            try:
                read_path = os.path.join(root_path, contract, dtime + '.csv')
                csv_path = os.path.join(save_path, category + '_' + exchange, dtime + '.csv')
            
                df = pd.read_csv(read_path)
                df.to_csv(csv_path, index = False)
            except Exception as e:
                print(e)
           
        
get_futuretick_bydate(20160830, 20200319, kind = 'MAIN')
