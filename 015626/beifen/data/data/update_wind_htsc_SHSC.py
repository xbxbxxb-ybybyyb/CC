"""
update wind_db from htsc matlab

"""


import datetime as dt
import pandas as pd
import scipy.io as sio  
import os
import numpy as np
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import os
from multiprocessing import Pool, Process, Manager
from multifactor.data.utils import *
import logging
from log import Log
import multifactor.utility.dt as tdt
import pickle
logger = Log('update_wind_htsc')

class WIND_DATABASE:
    def __init__(self, table_name, sdate, edate, 
                 base_path = 'Z:\\warehouse\\prod\\', 
                 dtype = 'STOCK',
                 mkttype = 'CHINA',
                 ftype = 'FDD',
                 dfreq = 'QUARTERLY',
                 dsource = 'WIND',
                 operation = 'append'):
        
        self.table_name = table_name
        self.sdate = sdate
        self.edate = edate
        self.dtype = dtype
        self.mkttype = mkttype
        self.ftype = ftype
        self.dfreq = dfreq
        self.dsource= dsource
        self.base_path = base_path
        self.source_path = os.path.join(base_path,'LOCAL_DATA\\CSV\\',dsource)
        self.operation = operation
        current_time = dt.datetime.strftime(dt.datetime.now(),'%Y%m%d')#_%H%M%S')
        self.table_csv_path =  os.path.join(self.source_path,self.table_name)
        name_mapping_dict = {}
        if self.table_name in name_mapping_dict:
            self.h5_name = name_mapping_dict[self.table_name]
        else:
            self.h5_name = self.table_name[5:]
        self.table_h5_path =  os.path.join(self.base_path,'DATABASE\\WIND\\', self.h5_name)
        self.table_h5_file =  os.path.join(self.table_h5_path,self.h5_name+'.h5')
        for path in [self.table_csv_path,self.table_h5_path]:
            if not os.path.exists(path):
                logger.info('retriever: create folder:%s'%(path))
                os.makedirs(path)
    
        if self.dfreq=='DAILY':
            pd_trading_dates = IO.read_data([self.sdate,self.edate],alt=r'Z:\warehouse\prod\CALENDAR\SHSC_TD.h5')
            td_list =  pd_trading_dates.index.get_level_values('dt').tolist()
            self.cdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in td_list]
            print(self.cdate_list)
            # raise Exception        


        elif self.dfreq=='QUARTERLY':
            qtr_list = get_qtr_list(self.sdate,self.edate,num_qtr=3)
            # qtr_list = [i for i in qtr_list if i>20090101]
            self.cdate_list = qtr_list
        else:
            raise Exception
        self.over_write_list = []    
    

    def csv2h5(self, update_list, min_size=0):
        """
            operation = 'append': for existing one - if operation =='append' - will remove existing one 
            operation = 'create': remove completely 
            Removed by type_dropna
            sorted by type_sort - e.g. sorted by entry time
            for removing duplicate - just drop last row for subgroup 
        """
        dat_fig_dict = {'WIND_SHSCDailyStatistics':{'dt':'TRADE_DT','Ticker':'S_INFO_EXCHMARKET'},
                        'WIND_SHSCTop10ActiveStocks':{'dt':'TRADE_DT','Ticker':'S_INFO_WINDCODE'},
                        'WIND_SHSCShortselling':{'dt':'TRADE_DT','Ticker':'S_INFO_WINDCODE'},
                        'WIND_SHSCChannelholdings':{'dt':'TRADE_DT','Ticker':'S_INFO_WINDCODE'},
                        }
        sparse_list = ['WIND_SHSCDailyStatistics','WIND_SHSCTop10ActiveStocks','WIND_SHSCShortselling','WIND_SHSCChannelholdings']

        logger.info('csv2h5: %s'%(self.table_name))
        dat_fig = dat_fig_dict[self.table_name]
        update_list.sort()
        

        if self.operation=='create':
            logger.info('csv2h5: create -  %s'%(self.table_h5_file))
            os.remove(self.table_h5_file) if os.path.exists(self.table_h5_file) else None
        elif self.operation == 'append':
            logger.info('csv2h5: append -  %s'%(self.table_h5_file))
    

        if self.table_name in self.over_write_list:
            logger.info('csv2h5: create -  %s'%(self.table_h5_file))
            os.remove(self.table_h5_file) if os.path.exists(self.table_h5_file) else None

        with pd.HDFStore(self.table_h5_file) as h5_store:
            logger.info('csv2h5: check date list')     
            if self.table_name in list(h5_store.root._v_groups.keys()):
                dt_lst = list(set(h5_store.select_column(self.table_name, 'dt')))
            else:
                dt_lst = [] 
            for fname in update_list:
                if not '.csv' in fname:
                    continue
                logger.info(fname)
                dat1 = pd.read_csv(fname, encoding='utf_8_sig')

                if len(dat1)<=min_size:
                    if self.table_name in sparse_list:
                        logger.warning('csv2h5: sparse table %s - data too little '%(self.table_name))
                        pass
                    else:
                        logger.error('csv2h5: source data %s too little!'%(self.table_name))
                        pass
                else:
                    dat = data_reformat(dat1, dat_fig)
                    if self.operation == 'append':      
                        curr_date = list(set(dat.index.get_level_values('dt')))[0]
                        print (curr_date)
                        if curr_date in dt_lst:
                            logger.info('csv2h5: exist: %s'%(curr_date))
                            continue
                            dummy_id = h5_store.remove(self.table_name,'dt=curr_date')
                            logger.info('csv2h5: append: %s'%(curr_date))
                    if self.table_name == 'WIND_SHSCDailyStatistics':
                        h5_store.append(self.table_name,dat,data_columns=True,  min_itemsize={'Ticker':10})
                    elif self.table_name == 'WIND_SHSCChannelholdings':
                        h5_store.append(self.table_name,dat,data_columns=True,  min_itemsize={'S_INFO_EXCHMARKETNAME':10})
                    elif self.table_name == 'WIND_SHSCTop10ActiveStocks':
                        h5_store.append(self.table_name,dat,data_columns=True,  min_itemsize={'MARKET':10,'S_INFO_EXCHMARKETNAME':10})
                    else:
                        h5_store.append(self.table_name,dat,data_columns=True)
    
                    logger.info('csv2h5: %s done'%(fname))
    
        logger.info('csv2h5 all done: %s'%(self.table_name))     
        return 
    

    def retriever(self):
        #  download table and save it to the csv file
        logger.info('retriever: fetch data from %s for %d - %d'%(self.table_name,self.sdate,self.edate))
        logger.info('retriever: data saved in:  %s'%(self.table_csv_path))
        # add condition
        if self.table_name in ['WIND_SHSCDailyStatistics','WIND_SHSCShortselling','WIND_SHSCTop10ActiveStocks','WIND_SHSCChannelholdings']:
            sql_where = ' where trade_dt=';         
    
        else:
            logger.error('retriever: table not defined: %s'%(self.table_name))
            raise Exception 
        sql_select = 'select * from '+ self.table_name
 
        for date in self.cdate_list:
            if self.table_name in self.over_write_list:
                df = sql_parser(queryUserTableData('select count(*) from ' + self.table_name))
                total_row_count = int(df['COUNT(*)'])
                if total_row_count < 100000:
                    sql_use = 'select * from ' + self.table_name
                    df = sql_parser(queryUserTableData(sql_use))
                else:
                    print(total_row_count)
                    df_list = []
                    group = int(total_row_count / 90000)
                    for i in range(group + 1):
                        start_line = i * 90000
                        end_line = min((i + 1) * 90000, total_row_count)
                        sql_use = '(select * from ' + self.table_name +  ' where rownum <= ' +str(end_line) + ') ' + 'minus(select * from ' + self.table_name + ' where rownum <= ' + str(start_line) + ')'
                        print(sql_use)
                        df = sql_parser(queryUserTableData(sql_use))
                        df_list.append(df)
                    df = pd.concat(df_list)
                    print(len(df))
                    print(total_row_count)
                df['date'] = date
                save_name = os.path.join(self.table_csv_path,self.table_name + '.csv')
                df.set_index('OBJECT_ID', inplace = True)
                df.to_csv(save_name, sep=',', encoding='utf_8_sig')
                logger.info('retriever: saved in :  %s'%(save_name))
            else:
                df = sql_parser(queryUserTableData('select count(*) from ' + self.table_name + sql_where + str(date)))
                total_row_count = int(df['COUNT(*)'])
                save_name = os.path.join(self.table_csv_path,str(date) + '.csv')

                if total_row_count < 100000:
                    sql_use = sql_select + sql_where + str(date)
                    print(sql_use)
                    logger.info(sql_use)
                    df = sql_parser(queryUserTableData(sql_use))
                else:
                    print(total_row_count)
                    df_list = []
                    group = int(total_row_count / 90000)
                    for i in range(group + 1):
                        start_line = i * 90000
                        end_line = min((i + 1) * 90000, total_row_count)
                        sql_use = '(select * from ' + self.table_name + sql_where + str(date) +' and rownum <= ' +str(end_line) + ') ' + 'minus(select * from ' + self.table_name + sql_where + str(date) + ' and rownum <= ' + str(start_line) + ')'
                        print(sql_use)
                        df = sql_parser(queryUserTableData(sql_use))
                        df_list.append(df)
                    df = pd.concat(df_list)
                    print(len(df))
                    print(total_row_count)

                df.set_index('OBJECT_ID', inplace = True)
                df.to_csv(save_name, sep=',', encoding='utf_8_sig')
                logger.info('retriever: saved in :  %s'%(save_name))
        logger.info('retriever: %s  done'%(self.table_name))
        return
    
        
    
    def dumper(self):
        logger.info('dump_h5: %s, %d, %d, %s, %s, %s'%(self.table_name,self.sdate,self.edate,self.ftype,self.dfreq,self.dsource))
            
        csv_list = [os.path.join(self.table_csv_path,i) for i in os.listdir(self.table_csv_path)]
        csv_list.sort()
        
        if self.dfreq =='QUARTERLY':
            update_list = [i for i in csv_list if int(i[-12:-4])>=self.sdate-10000 and int(i[-12:-4])<=self.edate and int(i[-12:-4])>=20000101] # update for 1 year
        elif self.dfreq =='DAILY':
            if self.table_name in self.over_write_list:
                update_list = csv_list
            else:
                update_list = []
                for i in self.cdate_list:
                    update_list.append(os.path.join(self.table_csv_path, str(i) + '.csv'))
        self.csv2h5(update_list)
        
        return 
    



def get_table_param(table_name,table_dict):
    param_dict = {}
    if table_name in table_dict['QUARTERLY']:
        param_dict['dfreq']='QUARTERLY'
    elif table_name in table_dict['DAILY']:
        param_dict['dfreq']='DAILY'
    else: 
        print ('table not defined: %s'%table_name)
        raise Exception   
    return param_dict


def instantiate(table_name, sdate, edate, base_path, operation,table_dict,update_h5_flag=False):
    param_dict = get_table_param(table_name,table_dict)
    wind_db = WIND_DATABASE(table_name, sdate, edate, base_path, 
                            dfreq = param_dict['dfreq'],
                            operation = operation)    
    wind_db.retriever()
# if not table_name in ['WIND_AShareEquityPledgeInfo']:
    if update_h5_flag:
        wind_db.dumper()
    # else:
        # print('Do not need to dump into h5')
    return 
 
    logger.info('===============late_job======================')


def morning_job(sdate,edate):
    sdate,edate,cdate_list = check_update_date(sdate = sdate, edate = edate)
    qtr_list = []
    # daily_list =  ['WIND_AIndexMembers','WIND_AShareConseption']
    # daily_list = ['WIND_AShareTradingSuspension']
    # daily_list =  ['WIND_htzqedbdzzbs','WIND_AIndexIndustriesEODCITICS','WIND_AShareTechIndicators', 'WIND_AshareintensitytrendADJ', 'WIND_AShareEnergyindexADJ','WIND_AShareswingRevADJ']

   # AShareAuditOpinion, AShareProfitExpress, AShareMonthlyReportsofBrokers

    table_dict = {'DAILY':['WIND_SHSCChannelholdings'],'QUARTERLY': []}

    for table_type in table_dict:
        for table_name in table_dict[table_type]:
            print (table_name)
            instantiate(table_name, sdate, edate, base_path = 'Z:\\warehouse\\prod\\', operation = 'append',table_dict=table_dict,update_h5_flag=True)
    
    logger.info('===============add_new_tables======================')




def SHSCC_tables(sdate,edate):
    date_list = ['WIND_SHSCDailyStatistics','WIND_SHSCShortselling','WIND_SHSCTop10ActiveStocks']
    table_dict = {'DAILY':date_list,'QUARTERLY': []}

    for table_type in table_dict:
        for table_name in table_dict[table_type]:
            print (table_name)
            instantiate(table_name, sdate, edate, base_path = 'Z:\\warehouse\\prod\\', operation = 'append',table_dict=table_dict,update_h5_flag=True)
    
    logger.info('===============add_new_tables======================')





