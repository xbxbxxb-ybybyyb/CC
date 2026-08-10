    # -*- coding: utf-8 -*-
"""
Stock Universe
@gzj
"""


import pandas as pd
import numpy as np
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import os 
import datetime as dt
import subprocess
import json
from log import Log
import config_reader
import htsc.quantAPI as qi
from htsc.quantEnum import *
from decimal import *
import time

logger = Log('update_universe')
"""Stock List/Date List"""

def get_stock_list(date):
    table_name = 'AShareDescription'
    h5_path = 'Z:\\warehouse\\prod\\DATABASE\\WIND\\'
    table_path = h5_path + table_name + '\\' +  table_name + '.h5'
    df = IO.read_data([20090101,21000101],columns=['S_INFO_LISTDATE', 'S_INFO_DELISTDATE'],alt = table_path)
    df.reset_index('dt', inplace=True)
    df.drop('dt', axis=1, inplace=True)   
    df.fillna(20990101, inplace = True)

    tmp_df = df[df['S_INFO_DELISTDATE'] > date]
    tmp_df = tmp_df[tmp_df['S_INFO_LISTDATE'] <= date]
    tmp_df['alla'] = True
    tmp_df = tmp_df[['alla']]
    return tmp_df


def get_next_day(sdate,next_day = 1):
    fdate_list_dt = IO.read_data([20020101, 20200101], ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    return fdate_list[fdate_list.index(sdate) + next_day]



def save_index_component(cdate_list,index_list,save_path):  
    date_min = {'HS300':20020104,
                'ZZ500':20050104,
                'CYB':20100601,
                'MS_cap':20050609,
                'SH50':20100104}
    dat_size = {'HS300':300,'ZZ500':500,'SH50':50}  
    if type(index_list) == str:
        index_list = [index_list]
    

    for date in cdate_list:        
        flag = False
        while not flag:
            try:
                finish_list=[]
                for index in index_list:
                    logger.info('-'*10 + index + '-'*10)
                    save_folder = save_path + index +'\\'    
                    if not os.path.exists(save_folder):
                        os.mkdir(save_folder)
                    logger.info(index +': '+str(date))
                    op_date = get_next_day(date,1)
                    print(op_date)
                    # op_date = date
                    if op_date<date_min[index]:
                        logger.info('skip')
                    elif op_date>=date_min[index]:
                        if index == 'HS300':
                            dat = qi.hset(PlateType.INDEX, op_date, IndexType.HS300)
                        elif index == 'ZZ500':
                            dat = qi.hset(PlateType.INDEX, op_date, IndexType.ZZ500)
                        elif index == 'SH50':
                            dat = qi.hset(PlateType.INDEX, op_date, IndexType.SH50)
                        dict_index = {}
                        if len(dat) == 0:
                            logger.error(index + ' no data at ' + str(date))
                            raise Exception
                        else:
                            dict_index['Ticker'] = dat[0]
                            dict_index[index] = dat[2]
                            if len(dat[0]) < dat_size[index] or len(dat[2]) < dat_size[index]:
                                logger.error(index + ' has only ' + str(len(dat[0])) + ' ' + str(len(dat[2])))
                                raise Exception
                        df = pd.DataFrame(dict_index)
                        df.set_index('Ticker', inplace=True)
                        df.sort_index(inplace=True)
                        df.to_csv(save_folder+str(date)+'.csv')
                        finish_list.append(index)
                if len(finish_list) == 3:
                    flag = True
            except Exception as e:
                logger.error(str(date) + ' update failed, and wait for next try 10 minutes later!')
                time.sleep(600)   


def updater_universe_csv(cdate_list):
    store_path = config_reader.getConfig('update_universe', 'csv_path')
    index_list = ['SH50', 'HS300','ZZ500']
    save_index_component(cdate_list, index_list, store_path)





def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day 
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    logger.info ('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x:abs(x-current_date) if x<=current_date else 100)
    if current_hour < new_date_time and nearest_date==current_date:
        logger.info ('Not till refresh time '+str(new_date_time)+':00')
        current_date = fdate_list[fdate_list.index(current_date)-1]
        logger.info ('Use previous trading date: '+str(current_date))
    elif nearest_date<current_date:
        current_date = nearest_date
    elif current_hour >= new_date_time and nearest_date==current_date:
        logger.info ('Right on time: '+str(current_date))
    return current_date



def date_period_handler(sdate=None,edate=None):
    last_day = get_current_date()
    if sdate is None and edate is None:
        sdate = last_day
        edate = last_day
        logger.info ('update for one day: '+str(sdate))
    if sdate is not None and edate is None:
        edate = last_day
    else:
        fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
        fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
        cdate_list = [i for i in fdate_list if i<=min(edate,last_day) and i>=sdate]
        sdate,edate = cdate_list[0],cdate_list[-1]
    return sdate,edate


def check_update_date(sdate=None,edate=None,use_len=None):
    #check_update_date(sdate=None,edate=None)
    use_len = 0 if use_len is None else use_len
    sdate,edate = date_period_handler(sdate,edate)
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    cdate_list = [i for i in fdate_list if i>=sdate and i<=edate]
    idx = max(0,fdate_list.index(cdate_list[0])-use_len)
    sdate_prev = fdate_list[idx]
    logger.info ('-'*20+'\ndata used: %d - %d '%(sdate_prev,edate))
    logger.info ('factor data: %d - %d \ntotal count: %d'%(sdate_prev,edate,len(cdate_list)))
    logger.info ('-'*20)
    return sdate_prev,edate,cdate_list


def update_universe_raw(cdate_list,csv_path,h5_path,factor_list,operation='append'):
    weight_list = ['index_weight_sh50','index_weight_hs300','index_weight_zz500']
    logger.info ('-'*60+'\nUpdating H5 from CSV \n'+h5_path)
    dump_list = [str(i) + '.csv' for i in cdate_list]
    pre_cwd = os.getcwd()
    df_list = []
    for date in cdate_list:
        tmp_list = []
        logger.info('--' + str(date))
        df = get_stock_list(date)
        df.reset_index(inplace=True)
        df['dt'] = dt.datetime.strptime(str(date),'%Y%m%d')
        df.set_index(['dt','Ticker'],inplace=True)
        tmp_list.append(df)
        for factor_name in factor_list:
            if factor_name == 'SH50':
                weight_name = 'index_weight_sh50'
            elif factor_name == 'ZZ500':
                weight_name = 'index_weight_zz500'
            elif factor_name == 'HS300':
                weight_name = 'index_weight_hs300'

            if factor_name == 'SH50' and date < 20100101:
                continue
            fname = csv_path+factor_name+'\\'+str(date)+'.csv'
            dat = pd.read_csv(fname)
            dat['dt'] = dt.datetime.strptime(str(date),'%Y%m%d')
            dat.set_index(['dt','Ticker'],inplace=True)
            dat.columns = [weight_name]
            dat = pd.concat([df,dat],axis=1)
            dat.fillna(0,inplace=True)
            dat[weight_name] = dat[weight_name] / 100.0

            if len(dat)>0:
                tmp_list.append(dat[[weight_name]])


        df = pd.concat(tmp_list,axis=1)

        for col in weight_list:
            if col not in df.columns:
                continue
            df[col].fillna(0,inplace=True)
        df_list.append(df)
    df = pd.concat(df_list)
    print(df)
    for colume in df.columns:
        if colume == 'alla':
            continue
        if operation == 'append':
            IO.pd_hdf5_writer(df[[colume]],h5_path,dataset=colume,append=True)
        else:
            IO.pd_hdf5_writer(df[[colume]],h5_path,dataset=colume)



class unv_factor(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.sdate_prev,self.edate,self.cdate_list = check_update_date(self.start_date,self.end_date)
        self.fail_dict = {}
        self.h5_root = config_reader.getConfig('root_path', 'h5_root')
    def retriever(self):
        updater_universe_csv(self.cdate_list)
        # updater_matlab_universe(self.cdate_list)

    def csv_to_database(self):
        csv_path = config_reader.getConfig('update_universe', 'csv_path')
        csv_path = 'Z:\\warehouse\\test\\stock_universe\\'


        factor_list = ['HS300','ZZ500','SH50']
        h5_path_source = 'Z:\\warehouse\\prod\\INDEXWEIGHT\\CHINA_STOCK\\DAILY\\CSI\\test_ftp.h5'

        update_universe_raw(self.cdate_list,csv_path,h5_path_source,factor_list,'create')


    def cronb(self):
        # self.retriever()
        self.csv_to_database()

def updater_universe(sdate=None,edate=None):
    # sdate = 20180903
    # edate = 20180904
    # 
    sdate,edate,cdate_list = check_update_date(sdate, edate)
    unv_factor(sdate, edate).cronb()
    # flag_root = 'Z:\\warehouse\\prod\\LOCAL_DATA\\FLAG\\' + str(edate) + '\\'
    # flag_path = flag_root + str(edate) + '_' + 'INDEX_WEIGHT.success'
    # with open(flag_path,'w') as file:
    #     pass

updater_universe(20150302,20190517)