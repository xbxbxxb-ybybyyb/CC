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
            self.cdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in tdt.get_trading_date_range(self.sdate,self.edate)]
        elif self.dfreq=='QUARTERLY':
            qtr_list = get_qtr_list(self.sdate,self.edate,num_qtr=3)
            # qtr_list = [i for i in qtr_list if i>20090101]
            self.cdate_list = qtr_list
        else:
            raise Exception
        self.over_write_list = ['WIND_AShareRegInv','WIND_AshareOfferforoffer','WIND_AShareConseption']    
    
    def retriever(self):
        #  download table and save it to the csv file
        logger.info('retriever: fetch data from %s for %d - %d'%(self.table_name,self.sdate,self.edate))
        logger.info('retriever: data saved in:  %s'%(self.table_csv_path))
        # add condition
        if self.table_name in ['WIND_AShareMajorEvent']:
            sql_where = ' where S_EVENT_HAPDATE='
        elif self.table_name in ['WIND_AShareEquFroInfo','WIND_AShareOperationEvent','WIND_MergerIntelligence']:
            sql_where = ' where ANN_DATE='
        elif self.table_name in self.over_write_list:
            sql_where = ''
        elif self.table_name in ['WIND_AShareGuarantee']:
            sql_where = ' where REPORT_PERIOD='
        elif self.table_name in ['WIND_AShareProsecution','WIND_AShareIllegality','WIND_AShareCompanyfilings',
                                'WIND_AshareRestructuringEvents']:
            sql_where = ' where ANN_DT='
        elif self.table_name in ['WIND_AShareRegional','WIND_AShareOwnership']:
            sql_where = ' where ENTRY_DT='
        else:
            logger.error('retriever: table not defined: %s'%(self.table_name))
            raise Exception 
        sql_select = 'select * from '+ self.table_name
        # download data - save to csv
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
                break
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

def add_new_tables(sdate,edate):
    sdate,edate,cdate_list = check_update_date(sdate = sdate, edate = edate)
    qtr_list = ['WIND_AShareGuarantee']
    daily_list =  ['WIND_AShareRegInv','WIND_AShareEquFroInfo','WIND_AshareOfferforoffer',
                'WIND_AShareOperationEvent','WIND_AShareProsecution','WIND_AShareIllegality',         
                'WIND_AShareCompanyfilings','WIND_AshareRestructuringEvents','WIND_MergerIntelligence',
                'WIND_AShareConseption','WIND_AShareRegional',
                'WIND_AShareOwnership','WIND_AShareMajorEvent']
    # daily_list = ['WIND_AShareTradingSuspension']
    # daily_list =  ['WIND_htzqedbdzzbs','WIND_AIndexIndustriesEODCITICS','WIND_AShareTechIndicators', 'WIND_AshareintensitytrendADJ', 'WIND_AShareEnergyindexADJ','WIND_AShareswingRevADJ']

   # AShareAuditOpinion, AShareProfitExpress, AShareMonthlyReportsofBrokers

    table_dict = {'QUARTERLY': qtr_list,'DAILY':[]}

    for table_type in table_dict:
        for table_name in table_dict[table_type]:
            print (table_name)
            instantiate(table_name, sdate, edate, base_path = 'Z:\\warehouse\\prod\\', operation = 'append',table_dict=table_dict)
    
    logger.info('===============add_new_tables======================')

add_new_tables(20130101,20190212)

# add_new_tables(20190214,20190214)
# WIND_AShareConseptionZL 落地库没有