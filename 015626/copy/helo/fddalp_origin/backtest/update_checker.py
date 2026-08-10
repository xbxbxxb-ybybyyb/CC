# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 08:48:17 2018

@author: 012315
"""
import numpy as np
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import pandas as pd
import datetime as dt



def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day 
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print ('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x:abs(x-current_date) if x<=current_date else 100)
    if current_hour < new_date_time and nearest_date==current_date:
        print ('Not till refresh time '+str(new_date_time)+':00')
        current_date = fdate_list[fdate_list.index(current_date)-1]
        print ('Use previous trading date: '+str(current_date))
    elif nearest_date<current_date:
        current_date = nearest_date
    elif current_hour >= new_date_time and nearest_date==current_date:
        print ('Right on time: '+str(current_date))
    return current_date

def data_checker(cdate_list=None):
    if cdate_list == None:
        cdate_list = [get_current_date(new_date_time=18)]
    else:
        cdate_list = [int(cdate_list)] if type(cdate_list) !=list else cdate_list

    file_path = 'S:\\Quant\\backtest\\local_data\\log_master\\'
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    date_num = len(cdate_list)
    end_date = cdate_list[-1]
    if date_num<5:
        start_date = fdate_list[fdate_list.index(cdate_list[-1])-5]
    elif date_num>100:
        print ('check list larger than 100')
        raise AssertionError

    # Market Data
    print ('Checkinf H5 file')
    dat_dict = {}
    print ('md')
    dat_dict['md'] = IO.read_data([start_date,end_date],ftype=FType.MD,dsource=DSource.WIND,max_workers=1)
    print ('fdd')
    dat_dict['fdd'] = IO.read_data([start_date,end_date],columns=['pb_lf'],ftype=FType.FDD,dsource=DSource.WIND,dfreq=DFreq.DAILY,max_workers=1)
    # Risk Universe & Alpha Universe
    print ('risk')
    dat_dict['risk'] = IO.read_data([start_date,end_date],ftype=FType.UNIV,dsource=DSource.OPTM,columns=['risk_universe'])
    print ('alpha')
    dat_dict['alpha'] = IO.read_data([start_date,end_date],ftype=FType.UNIV,dsource=DSource.OPTM,columns=['alpha_universe'])
    # Style 
    print ('style')
    dat_dict['style'] = IO.read_data([start_date,end_date],ftype=FType.RISK,dsource=DSource.STYLEFACTOR,max_workers=1)
    # Benchmark
    print ('index')
    dat_dict['index'] = IO.read_data([start_date,end_date],['close'],ftype=FType.MD,dtype=DType.INDEX,dsource=DSource.WIND,max_workers=1)
    # Industry
    print ('industry')
    dat_dict['industry'] = IO.read_data([start_date,end_date],ftype=FType.INDUSTRY,dsource=DSource.WIND,columns=['industry3'],max_workers=1) 
    # Fundamental Data - Daily
    print ('risk source')
    risk_source_list = ['tot_assets','tot_liab','tot_non_cur_liab','tot_equity','yoy_tr','yoynetprofit']
    dat_dict['risk_source'] = IO.read_data([start_date,end_date],risk_source_list,ftype=FType.FDD,dfreq=DFreq.DAILY,dsource=DSource.WIND,max_workers=1)
    # Consensus Forecast - Basic Table
    print ('con_forecast')
    dat_dict['con_forecast'] = IO.read_data([start_date,end_date],ftype=FType.FCD,dsource=DSource.HTSC,max_workers=1)
    # Consensus Forecast - Target Price
    #h5_path_cfs = 'S:\\Quant\\data\\fcd\\CHINA_STOCK\\DAILY\\HTSC\\con_forecast_schedule.h5'
    # Conforecast Deriv Table
    #h5_path_so3 = 'S:\\Quant\\data\\fcd\\CHINA_STOCK\\DAILY\\HTSC\\stock_order3.h5'
    #h5_path_so2 = 'S:\\Quant\\data\\fcd\\CHINA_STOCK\\DAILY\\HTSC\\stock_order2.h5'
    # HTSC stock list
    #h5_trade_list = 'S:\\Quant\\backtest\\local_data\\stock_universe\\HTSC_trade_list.h5'
    #dat_trade = IO.read_data([20090101,20200205],alt=h5_trade_list)
    check_status = {}
    for fac in dat_dict:
        try:
            if fac=='con_forecast':
                check_status[fac] = np.isfinite(dat_dict[fac][['EPS','PB']]).groupby('dt').sum()
            else:    
                check_status[fac] = np.isfinite(dat_dict[fac]).groupby('dt').sum()
        except:
            print(fac)
    # Minute Data
    """record fail
    print (check_status)
    for fac in check_status:
    check_status[fac] = check_status[fac].to_dict('list') 
    log_file = file_path+str(fdate_list[-1])+'.json'
    with open(log_file, 'w') as f:
        json.dump(check_status, f)
    """
    
    now=dt.datetime.today()
    file_date=now.strftime("%Y%m%d_%H%M%S")    
    excel_name = file_path+str(cdate_list[-1])+'_check_time_'+file_date+'.xlsx'
    writer = pd.ExcelWriter(excel_name,engine='xlsxwriter')
    for fac in check_status:
        check_status[fac].to_excel(writer,sheet_name=fac)
    writer.save()
    print ('Check status saved in: ',excel_name)
    return     


data_checker()
