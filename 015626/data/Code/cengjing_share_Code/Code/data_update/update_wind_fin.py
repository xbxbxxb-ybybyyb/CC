# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:17:25 2018

@author: 012315
"""

from WindPy import w
import datetime as dt
import pandas as pd
import os
import numpy as np
import json
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
w.start()


def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day 
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print ('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20000101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
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



def date_period_handler(sdate=None,edate=None):
    last_day = get_current_date()
    if sdate is None and edate is None:
        sdate = last_day
        edate = last_day
        print ('update for one day: '+str(sdate))
    if sdate is not None and edate is None:
        edate = last_day
    else:
        fdate_list_dt = IO.read_data([20000101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
        fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
        cdate_list = [i for i in fdate_list if i<=min(edate,last_day) and i>=sdate]
        sdate,edate = cdate_list[0],cdate_list[-1]
    return sdate,edate


def check_update_date(sdate=None,edate=None,use_len=None):
    #check_update_date(sdate=None,edate=None)
    use_len = 0 if use_len is None else use_len
    sdate,edate = date_period_handler(sdate,edate)
    fdate_list_dt = IO.read_data([20000101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    cdate_list = [i for i in fdate_list if i>=sdate and i<=edate]
    idx = max(0,fdate_list.index(cdate_list[0])-use_len)
    sdate_prev = fdate_list[idx]
    print ('-'*20,'\ndata used: %d - %d '%(sdate_prev,edate))
    print ('factor data: %d - %d \ntotal count: %d'%(sdate_prev,edate,len(cdate_list)))
    print ('-'*20)
    return sdate_prev,edate,cdate_list

def get_stock_list(cdate_list):
    cdate_list = [cdate_list] if type(cdate_list)!=list else cdate_list
    wind_stock_path = 'S:\\Quant\\backtest\\local_data\\wind_data\\wind_stock_list\\'
    fdate_list = [int(i[:-4]) for i in os.listdir(wind_stock_path)]
    need_list = list(set(cdate_list) - set(fdate_list))
    fail_list = []
    print ('Need to download stock list for: ',len(need_list),' days')
    for date in need_list:
        try:
            dat = w.wset('SectorConstituent','date='+str(date)+';sectorId=a001010100000000;field=wind_code')
            if len(dat.Data[0]) ==1:
                print (dat.Data[0][0])
                raise Exception
            else:
                df = pd.DataFrame(dat.Data[0],columns=['Ticker'])
                df.to_csv(wind_stock_path+str(date)+'.csv',index = False)
        except:
            print ('fail... ',date)
            raise Exception
            fail_list.append(date)
    return fail_list


def get_qtr_list(end_date=None,num_qtr=4):
    end_date = end_date[-1] if type(end_date)==list else end_date
    if end_date == None:
        end_date = get_current_date(new_date_time=18)

    if end_date< 20000105:
        last_day = 20000105
    else:
        last_day = end_date
            
    year_list = [str(i) for i in range(2000,2030)]
    month_date = ['0331','0630','0930','1231']
    date_list_complete = [i+j for i in year_list for j in month_date]
    qtr_list = [int(i) for i in date_list_complete if int(i)<=last_day][-1*num_qtr:]
    get_stock_list(qtr_list)
    universe_folder = 'S:\\Quant\\backtest\\local_data\\wind_data\\wind_stock_list\\'
    stock_set = set()
    for qtr_date in qtr_list: 
        stock_code = pd.read_csv(universe_folder+str(qtr_date)+'.csv',header=0)['Ticker'].values.tolist()
        stock_set = stock_set.union(set(stock_code))
    stock_code = list(stock_set)
    return qtr_list,stock_code


def save_one_factor(factor_list,date_list,save_path,use_wind_list=True,stock_code=None,over_ride_name=None):
    tmp_date_list = IO.read_data([20000101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    tmp_date_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in tmp_date_list]
    cur_date = get_current_date()
    wind_stock_path = 'S:\\Quant\\backtest\\local_data\\wind_data\\wind_stock_list\\'
    fail_dict ={}
    if type(factor_list) == str:
        factor_list = [factor_list]
    for factor_name in factor_list:
        print ('-'*10, factor_name, '-'*10)
        
        if over_ride_name !=None:
            save_folder = save_path + over_ride_name+'\\'
        else: 
            save_folder = save_path + factor_name+'\\'    
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)
        fail_dict[factor_name] = []     
        if factor_name.find(',') == -1:
            column_name = factor_name
        else: 
            column_name = factor_name.rsplit(sep=',')
        
        for date in date_list:
            print (factor_name+': '+str(date))
            try:
                if use_wind_list == True:
                    stock_code_df = pd.read_csv(wind_stock_path+str(date)+'.csv',header=0)
                    stock_code = stock_code_df['Ticker'].values.tolist()
                    Data_list = []
                    Codes_list = []
                    issuing_df = IO.read_data(date,['stm_issuingdate'],alt = r'Z:\warehouse\prod\FDD\CHINA_STOCK\QUARTERLY\WIND\FDD_CHINA_STOCK_QUARTERLY_WIND.h5')
                    issuing_df.reset_index('dt',inplace=True)
                    index_list = list(set(issuing_df.index))
                    download_dict = {}
                    for ticker in stock_code:
                        if not ticker in index_list:
                            print(ticker)
                            continue
                        issuing_date = int(str(issuing_df.loc[ticker]['stm_issuingdate']).replace('-',''))
                        if issuing_date == 18991230:
                            # print(ticker)
                            # continue
                            Codes_list.append(ticker)
                            Data_list.append(np.nan)
                        else:
                            while issuing_date not in tmp_date_list:
                                issuing_date += 1
                            if issuing_date > int(cur_date):
                                print(str(cur_date) +'<' + str(issuing_date))
                                Codes_list.append(ticker)
                                Data_list.append(np.nan)
                                continue
                            if not issuing_date in download_dict:
                                download_dict[issuing_date] = []
                            download_dict[issuing_date].append(ticker)

                    for download_dt in download_dict:
                        # dat = w.wss(download_dict[download_dt],factor_name,'tradeDate='+str(download_dt))
                        dat = w.wsd(download_dict[download_dt], factor_name, str(download_dt), str(download_dt), '')

                        if dat.ErrorCode != 0:
                            print (dat.Data[0])
                            fail_dict[factor_name].append(date)
                            raise Exception
                        
                        Codes_list.extend(dat.Codes)
                        Data_list.extend(dat.Data[0])

                # dat = w.wsd(stock_code, factor_name, str(date), str(date), 'unit=1;Period=Q;Days=Alldays')

                    df = pd.DataFrame(Data_list,index=Codes_list)
                    df.columns = [column_name]
                    df.index.names= ['Ticker']
                    df.to_csv(save_folder+str(date)+'.csv')
            except Exception as e:
                print(e)
                print ('fail')
                fail_dict[factor_name].append(date)                              
                raise Exception
    return fail_dict


def get_wind_qtr_csv_with_backfill(cdate_list,csv_path,factor_name_dict):
    qtr_list,stock_code = get_qtr_list(cdate_list)
    # print(stock_code)
    print ('Getting quarterly wind data for ',str(qtr_list))
    fail_list = []
    for ft in factor_name_dict:
        try:
            print (ft)
            factor_list = factor_name_dict[ft] 
            save_one_factor(factor_list,qtr_list,csv_path,use_wind_list=True,stock_code=stock_code) 
        except:
            print ('fail')
            fail_list.append(ft)
            raise Exception
    return fail_list


def get_wind_qtr_csv_original(cdate_list,csv_path,factor_name_dict):
    qtr_list,stock_code = get_qtr_list(cdate_list)
    print ('Getting quarterly wind data for ',str(qtr_list))
    fail_list = []
    for ft in factor_name_dict:
        try:
            print (ft)
            factor_list = factor_name_dict[ft] 
            save_one_factor_original(factor_list,qtr_list,csv_path,use_wind_list=True,stock_code=stock_code) 
        except Exception as e:
            print (e)
            fail_list.append(ft)
            raise Exception
    return fail_list

def save_one_factor_original(factor_list,date_list,save_path,use_wind_list=True,stock_code=None,over_ride_name=None):
    tmp_date_list = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    tmp_date_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in tmp_date_list]

    wind_stock_path = 'S:\\Quant\\backtest\\local_data\\wind_data\\wind_stock_list\\'
    fail_dict ={}
    if type(factor_list) == str:
        factor_list = [factor_list]
    for factor_name in factor_list:
        print ('-'*10, factor_name, '-'*10)
        
        if over_ride_name !=None:
            save_folder = save_path + over_ride_name+'\\'
        else: 
            save_folder = save_path + factor_name+'\\'    
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)
        fail_dict[factor_name] = []     
        if factor_name.find(',') == -1:
            column_name = factor_name
        else: 
            column_name = factor_name.rsplit(sep=',')
        
        for date in date_list:
            print (factor_name+': '+str(date))
            try:
                if use_wind_list == True:
                    stock_code_df = pd.read_csv(wind_stock_path+str(date)+'.csv',header=0)
                    stock_code = stock_code_df['Ticker'].values.tolist()
                    if factor_name in ['acctandnotes_payable','acctandnotes_rcv','holder_num','holder_pctbyinst','stmnote_salestop5_pct']:
                        # dat = w.wss(stock_code,factor_name,'unit=1;rptDate='+str(date)+';rptType=1')
                        dat = w.wsd(stock_code, factor_name, str(date), str(date), 'unit=1;rptType=1;Period=Q;Days=Alldays')

                    elif factor_name in ['fa_mlev','pe_ttm','pb_lf','val_petohist60',
                    'ps_ttm','pcf_ocf_ttm','pcf_ncf_ttm','dividendyield2','val_ortoev_ttm',
                    'val_tatoev','val_mvtofcff']:
                        # dat = w.wss(stock_code,factor_name,'unit=1;tradeDate='+str(date))
                        dat = w.wsd(stock_code, factor_name, str(date), str(date), '')
                    elif factor_name == 'share_pledgeda_pct_holder':
                        dat = w.wsd(stock_code, factor_name, str(date), str(date), 'order=1')
                    if dat.ErrorCode != 0:
                        print(dat)
                        fail_dict[factor_name].append(date)
                        raise Exception
                # dat = w.wsd(stock_code, factor_name, str(date), str(date), 'unit=1;Period=Q;Days=Alldays')

                    df = pd.DataFrame(dat.Data,columns=dat.Codes,index=[column_name]).T
                    df.index.names= ['Ticker']
                    df.to_csv(save_folder+str(date)+'.csv')
            except Exception as e:
                print(e)
                print ('fail')
                fail_dict[factor_name].append(date)                              
                raise Exception
    return fail_dict

def CSV2H5(date_list,h5_name,save_path,factor_name,operation):
    fail_list = []
    h5_address = save_path+h5_name
    if operation=='create':
        os.remove(h5_address) if os.path.exists(h5_address) else None
    with pd.HDFStore(h5_address) as hdf_store:        
        for date in date_list:
            print (date)
            try:
                dat = pd.read_csv(save_path+factor_name+'\\'+str(date)+'.csv',index_col=0,header=0)
                dat = dat.reset_index(drop=True)
                dat = dat.set_index(['dt','Ticker'])
                dat = dat.sort_index(level=1) # sort by ticker 
            except: 
                print (str(date)+' read failed!')
                fail_list.append(date)
            try:
                hdf_store.append(factor_name,dat)
            except:
                print (str(date)+' save to h5 failed')  
                fail_list.append(date)
    print ('data loading complete!')    
    print (fail_list)        
    return fail_list


def update_wind_qtr_h5(qtr_list,factor_name_dict,csv_path,h5_path,operation='append'):
    #date_list_dt = [dt.datetime.strptime(str(i),'%Y%m%d') for i in date_list]
    dump_fail_dict={}
    for factor_type in factor_name_dict:
        print (factor_type)
        for factor_name in factor_name_dict[factor_type]:
            print ('-',factor_name)
            dump_fail_dict[factor_name] = []
            try:
                file_folder = csv_path+factor_name+'\\'
                if operation=='append':
                    for date in qtr_list:
                        print ('--',str(date))
                        fname = file_folder+str(date)+'.csv'
                        dat = pd.read_csv(fname)
                        dat['dt'] = dt.datetime.strptime(str(date),'%Y%m%d')
                        dat.set_index(['dt','Ticker'],inplace=True)
                        if len(dat)>0:
                            IO.pd_hdf5_writer(dat, h5_path, dataset=factor_name, append=True)
                elif operation=='create':
                    print ('create new dataset: ',factor_name)
                    file_list = [file_folder+i for i in os.listdir(file_folder)]
                    file_list.sort()
                    IO.csv_dumper(file_list, h5_path, factor_name)                    
            except:
                print ('failed')
                dump_fail_dict[factor_name].append(date)
    return dump_fail_dict


def update_wind_daily_h5(cdate_list,daily_factor,csv_path,h5_path,operation='append',factor_scale=None):
    """factor_scale for maintaining consistent level between HTSC and WIND data"""
    factor_scale = {} if factor_scale == None else factor_scale
    fail_list = []
    for factor_name in daily_factor:
        print (factor_name)
        try:
            file_folder = csv_path+factor_name+'\\'
            if operation=='append':
                for date in cdate_list:
                    print ('--',str(date))
                    fname = file_folder+str(date)+'.csv'
                    dat = pd.read_csv(fname)
                    dat['dt'] = dt.datetime.strptime(str(date),'%Y%m%d')
                    dat.set_index(['dt','Ticker'],inplace=True)
                    if factor_name in factor_scale:
                        print ('scale')
                        dat[factor_name] = dat[factor_name]/factor_scale[factor_name]
                    if len(dat)>0:
                        if factor_name == 'industry_citiccode': # for legacy reason
                            dat.columns = ['industry3']
                            IO.pd_hdf5_writer(dat, h5_path, dataset='industry3',append=True)
                        else:
                            IO.pd_hdf5_writer(dat, h5_path, dataset=factor_name,append=True)
            elif operation =='create':
                print ('create new dataset: ',factor_name)
                file_list = [file_folder+i for i in os.listdir(file_folder)]
                file_list.sort()
                IO.csv_dumper(file_list, h5_path, factor_name)    
        except:
            print ('failed')
            fail_list.append(factor_name)
    return fail_list


def update_weekend_fin_wind(sdate=None,edate=None):
    sdate_prev,edate,cdate_list = check_update_date(sdate,edate)

    w.start()
    """ Set path"""
    csv_path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\fdd_fin_wind_api\\'
    h5_quarterly_path= 'Z:\\warehouse\\prod\\DATABASE\\WIND\\APIQUARTERLY\\APIQUARTERLY.h5'    
    h5_daily_fdd_path = 'Z:\\warehouse\\prod\\DATABASE\\WIND\\APIDAILY\\APIDAILY.h5'
    fail_dict_master = {}
    qtr_list,stock_code = get_qtr_list(end_date=edate)  
    
    fail_dict_master['stock_list'] = get_stock_list(cdate_list)
  

    daily_list = ['pcf_ncf_ttm','val_ortoev_ttm','val_tatoev','val_mvtofcff','dividendyield2','share_pledgeda_pct_holder']

    factor_list = ['fa_retainedearn_ttm','fa_roc_ttm','fa_protocost_ttm',
                'fa_ebittogr_ttm','fa_taxratio_ttm','fa_acca_ttm','fa_berryratio_ttm',
                'fa_cashrecovratio_ttm','fa_ltdebttoasset','fa_equitytofixedasset',
                'fa_intangassetratio','fa_debttotangibleafybl','fa_ocftointerestdebt_ttm',
                'fa_ocftonetdebt_ttm','fa_cfotocurliabs_ttm','fa_faturn_ttm',
                'fa_invturn_ttm','fa_currtassetstrate_ttm','fa_naturn_ttm',
                'fa_ncgr_ttm','fa_tpgr_ttm','fa_oigr_ttm','fa_nppcgr_ttm','fa_cfogr_ttm',
                'fa_cffgr_ttm','fa_cfigr_ttm','fa_gpmgr_ttm']
    # original
    factor_list_original = ['acctandnotes_payable','acctandnotes_rcv','stmnote_salestop5_pct']
    # added
    factor_name_dict = {'fin':factor_list}  
    factor_name_dict2 = {'fin1':factor_list_original}

    fail_dict_master['fdd_qtr_csv'] = get_wind_qtr_csv_with_backfill(cdate_list,csv_path,factor_name_dict)     
    fail_dict_master['fdd_qtr_h5'] = update_wind_qtr_h5(qtr_list,factor_name_dict,csv_path,h5_quarterly_path)
    fail_dict_master['fdd_qtr_csv'] = get_wind_qtr_csv_original(cdate_list,csv_path,factor_name_dict2)     
    fail_dict_master['fdd_qtr_h5'] = update_wind_qtr_h5(qtr_list,factor_name_dict2,csv_path,h5_quarterly_path)
                                    
    # fail_dict_master['fdd_daily_csv'] = save_one_factor_original(daily_list,cdate_list,csv_path,use_wind_list=True)
    # fail_dict_master['fdd_daily_h5'] = update_wind_daily_h5(cdate_list,daily_list,csv_path,h5_daily_fdd_path)

    print (fail_dict_master)


# update_weekend_fin_wind()
