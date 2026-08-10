# -*- coding: utf-8 -*-
"""
# data update master
"""

import os
from multifactor.data.utils import *

dir_path = os.path.dirname(os.path.realpath(__file__))+'\\'
#dir_path ='D:\\012315\\Code\\AlphaFactor\\AlphaSystem\\PythonVersion\\Data\\'
print (dir_path)
os.chdir(dir_path)
from update_wind_htsc_SHSC import morning_job

def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([19980101, 20200101], alt=r'Z:\warehouse\prod\CALENDAR\SHSC_TD.h5').index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
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


def date_period_handler(sdate=None, edate=None):
    last_day = get_current_date()
    if sdate is None and edate is None:
        sdate = last_day
        edate = last_day
        print('update for one day: ' + str(sdate))
    if sdate is not None and edate is None:
        edate = last_day
    else:
        fdate_list_dt = IO.read_data([19980101, 20200101],  alt=r'Z:\warehouse\prod\CALENDAR\SHSC_TD.h5').index.get_level_values(0)
        fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
        cdate_list = [i for i in fdate_list if i <= min(edate, last_day) and i >= sdate]
        sdate, edate = cdate_list[0], cdate_list[-1]
    return sdate, edate


def check_update_date(sdate=None, edate=None, use_len=None):
    # check_update_date(sdate=None,edate=None)
    use_len = 0 if use_len is None else use_len
    sdate, edate = date_period_handler(sdate, edate)
    fdate_list_dt = IO.read_data([19980101, 20200101],  alt=r'Z:\warehouse\prod\CALENDAR\SHSC_TD.h5').index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    cdate_list = [i for i in fdate_list if i >= sdate and i <= edate]
    idx = max(0, fdate_list.index(cdate_list[0]) - use_len)
    sdate_prev = fdate_list[idx]
    print('-' * 20, '\ndata used: %d - %d ' % (sdate_prev, edate))
    print('factor data: %d - %d \ntotal count: %d' % (sdate_prev, edate, len(cdate_list)))
    print('-' * 20)
    return sdate_prev, edate, cdate_list




sdate,edate,cdate_list = check_update_date()
print(sdate,edate,cdate_list)
morning_job(sdate,edate)



































