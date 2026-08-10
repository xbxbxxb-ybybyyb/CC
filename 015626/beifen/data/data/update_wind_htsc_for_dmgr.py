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
                 base_path = 'Z:\\warehouse\\test\\', 
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
        name_mapping_dict = {'WIND_AShareAFIndicator': 'AShareANNFinancialIndicator'}
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
            self.cdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in tdt.get_trading_date_range(self.sdate,self.edate)]
        elif self.dfreq=='QUARTERLY':
            qtr_list = get_qtr_list(self.sdate,self.edate,num_qtr=3)
            # qtr_list = [i for i in qtr_list if i>20090101]
            self.cdate_list = qtr_list
        else:
            raise Exception
        self.over_write_list = ['WIND_AShareIndClassCITICS']    
    

    def retriever(self):
        #  download table and save it to the csv file
        logger.info('retriever: fetch data from %s for %d - %d'%(self.table_name,self.sdate,self.edate))
        logger.info('retriever: data saved in:  %s'%(self.table_csv_path))
        # add condition
        if self.table_name in ['WIND_AShareProfitExpress','WIND_AShareBalanceSheet','WIND_AShareCashFlow']:
            sql_where = ' where report_period='
        elif self.table_name in ['WIND_AShareStrangeTradedetail']:
            sql_where = ' where END_DT='
        elif self.table_name in ['WIND_AShareStrangeTrade']:
            sql_where = ' where S_STRANGE_ENDDATE='
        elif self.table_name in ['WIND_AShareMjrHolderTrade','WIND_AShareInsiderTrade','WIND_AShareCompRestricted']:
            sql_where = ' where ANN_DT='
        else:
            logger.error('retriever: table not defined: %s'%(self.table_name))
            raise Exception 
        sql_select = 'select * from '+ self.table_name
 
        for date in self.cdate_list:
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
            if self.table_name in ['WIND_AShareProfitExpress']:
                df.drop(['OBJECT_ID','MEMO','BRIEF_PERFORMANCE'],axis=1,inplace=True)
                df.set_index('S_INFO_WINDCODE', inplace = True)
            elif self.table_name in ['WIND_AShareStrangeTradedetail','WIND_AShareStrangeTrade']:
                df.drop(['OBJECT_ID'],axis=1,inplace=True)
                df.set_index('S_INFO_WINDCODE', inplace = True)
            elif self.table_name in ['WIND_AShareMjrHolderTrade']:
                df.drop(['OBJECT_ID'],axis=1,inplace=True)
                df.set_index('S_INFO_WINDCODE', inplace = True)
            elif self.table_name in ['WIND_AShareInsiderTrade']:
                df.drop(['OBJECT_ID','REPORTED_TRADER_NAME','RELATED_MANAGER_NAME'],axis=1,inplace=True)
                df.set_index('S_INFO_WINDCODE', inplace = True)
            else:
                df.set_index('S_INFO_WINDCODE',inplace=True)
            # df['BRIEF_PERFORMANCE'] = df['BRIEF_PERFORMANCE'].astype(str)
            # df['BRIEF_PERFORMANCE'] = df['BRIEF_PERFORMANCE'].apply(lambda x : x.replace('\n', ''))
            # df['BRIEF_PERFORMANCE'] = df['BRIEF_PERFORMANCE'].apply(lambda x : x.replace('\r', ''))
            # df['BRIEF_PERFORMANCE'] = df['BRIEF_PERFORMANCE'].apply(lambda x : x.replace(',', '，'))

            if self.table_name in ['WIND_AShareMjrHolderTrade','WIND_AShareCompRestricted']:
                df.to_csv(save_name, sep='|', encoding='gbk')
            else:
                df.to_csv(save_name, sep=',', encoding='utf_8_sig')

            logger.info('retriever: saved in :  %s'%(save_name))
        logger.info('retriever: %s  done'%(self.table_name))
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


def instantiate(table_name, sdate, edate, base_path, operation,table_dict):
    param_dict = get_table_param(table_name,table_dict)
    wind_db = WIND_DATABASE(table_name, sdate, edate, base_path, 
                            dfreq = param_dict['dfreq'],
                            operation = operation)    
    wind_db.retriever()

    return 
 
def first_job(sdate,edate):
    sdate,edate,cdate_list = check_update_date(sdate = sdate, edate = edate)
    qtr_list = ['WIND_AShareProfitExpress','WIND_AShareBalanceSheet','WIND_AShareCashFlow']
    first_daily_list = ['WIND_AShareStrangeTrade','WIND_AShareCompRestricted'] 

    table_dict = {'QUARTERLY': [], 'DAILY':['WIND_AShareCompRestricted'] }
    for table_type in table_dict:
        for table_name in table_dict[table_type]:
            print (table_name)
            instantiate(table_name, sdate, edate, base_path = 'Z:\\warehouse\\test\\', operation = 'append',table_dict=table_dict)
    
    logger.info('===============1st job upload finish======================')


first_job(20120101,20190708)