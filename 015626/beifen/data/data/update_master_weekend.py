# -*- coding: utf-8 -*-
"""
# data update master
"""

import os
import datetime as dt
import pandas as pd
from multifactor.data.utils import *

dir_path = os.path.dirname(os.path.realpath(__file__))+'\\'
#dir_path ='D:\\012315\\Code\\AlphaFactor\\AlphaSystem\\PythonVersion\\Data\\'
print (dir_path)
os.chdir(dir_path)
from weekend_job_wind_htsc import first_job,second_job
from update_wind import wind_weekend_job
# from update_wind_fin import update_weekend_fin_wind



def get_current_date():
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    print('Current time: ' + str(current_time))
    h5_path = 'Z:\\warehouse\\prod\\CALENDAR\\nature_days.h5'
    fdate_list_dt = IO.read_data([19980101, 20200101], alt=h5_path).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    idx = fdate_list.index(current_date)
    return fdate_list[idx-2], fdate_list[idx-1],current_date  

def flag_check(date):
    path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\FLAG\\' + str(date) +'\\' + str(date) + '_' + 'RDF.success'
    return os.path.exists(path)

lst_workday, sdate,edate = get_current_date()
print(lst_workday,sdate,edate)



flag_root = 'Z:\\warehouse\\prod\\LOCAL_DATA\\FLAG\\' + str(edate) + '\\'
if not os.path.exists(flag_root):
    os.mkdir(flag_root)

first_job(sdate,edate)

flag_path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\HTSC_FLAG\\' + str(edate) + '_' + 'rdf_csv.success'
with open(flag_path,'w') as file:
    pass
print('------wait--------')
while True:
    if flag_check(edate):
        break

wind_weekend_job()
flag_path = flag_root+ str(edate) + '_' + 'FDD.success'
with open(flag_path,'w') as file:
    pass

second_job(sdate, edate)




































