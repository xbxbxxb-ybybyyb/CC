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


def get_all_days(sdate,edate):
    h5_path = 'Z:\\warehouse\\prod\\CALENDAR\\nature_days.h5'
    df = IO.read_data([sdate,edate],alt=h5_path)
    df.reset_index(inplace=True)
    df['dt'] = df['dt'].apply(lambda x : int(str(x).replace('-','')[:8]))
    date_list = list(set(df['dt']))
    date_list.sort()
    return date_list







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
            # self.cdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in tdt.get_trading_date_range(self.sdate,self.edate)]
            all_days_list = get_all_days(sdate,edate)
            self.cdate_list = all_days_list


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
        dat_fig_dict = {'WIND_AShareAnnInf':{'dt': 'COLLECT_DT','Ticker': 'S_INFO_WINDCODE'},
                        'WIND_AShareInsiderTrade':{'dt':'ACTUAL_ANN_DT','Ticker':'S_INFO_WINDCODE'},
                        'WIND_AShareIllegality':{'dt':'ANN_DT','Ticker':'S_INFO_WINDCODE'},
                        'WIND_AShareCompRestricted': {'dt': 'ANN_DT', 'Ticker': 'S_INFO_WINDCODE'},
                        'WIND_AShareInsideHolder':{'dt':'ANN_DT','Ticker':'S_INFO_WINDCODE'},
                        'WIND_AShareHolderNumber':{'dt':'ANN_DT','Ticker':'S_INFO_WINDCODE'},

                        }
        sparse_list = []

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
                    if self.table_name == 'WIND_AShareAnnInf':
                        dat1['COLLECT_DT'] = dat1['COLLECT_DT'].apply(lambda x : int(str(x).replace('-','')[:8]))
                    dat = data_reformat(dat1, dat_fig)
                    if self.operation == 'append':      
                        curr_date = list(set(dat.index.get_level_values('dt')))[0]
                        print (curr_date)
                        if curr_date in dt_lst:
                            logger.info('csv2h5: exist: %s'%(curr_date))
                            # print('pass')
                            # continue
                            dummy_id = h5_store.remove(self.table_name,'dt=curr_date')
                            logger.info('csv2h5: append: %s'%(curr_date))
                    if self.table_name == 'WIND_AShareAnnInf':
                        def helper(x):
                            x = x.encode('utf-8')
                            return len(x)
                        dat['N_INFO_FCODE'] = dat['N_INFO_FCODE'].astype(str)
                        dat['N_INFO_STOCKID'] = dat['N_INFO_STOCKID'].astype(str)
                        dat['N_INFO_COMPANYID'] = dat['N_INFO_COMPANYID'].astype(str)
                        dat.drop(['N_INFO_ANNLINK','N_INFO_FTXT'],axis=1,inplace=True)
                        dat = dat[dat['N_INFO_TITLE'].apply(lambda x : helper(x)) <= 200]
                        dat = dat[dat['N_INFO_FCODE'].apply(lambda x : helper(x)) <= 200]
                        h5_store.append(self.table_name,dat, data_columns=True,min_itemsize={'N_INFO_TITLE':200,'N_INFO_FCODE':200,'N_INFO_STOCKID':20,'N_INFO_COMPANYID':20})
                    elif self.table_name == 'WIND_AShareInsiderTrade':
                        dat.drop(['IS_SHORT_TERM_TRADE'], axis=1, inplace=True)
                        h5_store.append(self.table_name,dat,data_columns=True, min_itemsize={'RELATED_MANAGER_POST': 100, 
                                                                                            'RELATED_MANAGER_NAME':100, 
                                                                                            'REPORTED_TRADER_NAME' :150, 
                                                                                           'TRADER_MANAGER_RELATION' : 150})
                    
                    elif self.table_name == 'WIND_AShareIllegality':
                        # print(dat.dtypes)
                        dat.drop(['BEHAVIOR','METHOD','REF_RULE'],axis=1,inplace=True)
                        dat['S_INFO_COMPCODE'] = dat['S_INFO_COMPCODE'].astype(str)
                        dat['SUBJECT'] = dat['SUBJECT'].astype(str)
                        h5_store.append(self.table_name,dat,data_columns=True, min_itemsize={'DISPOSAL_TYPE':200,'S_INFO_COMPCODE':40,'ILLEG_TYPE':200,'SUBJECT':200,'PROCESSOR':400})
                    
                    elif self.table_name == 'WIND_AShareCompRestricted':
                        h5_store.append(self.table_name,dat, data_columns=True,min_itemsize={'S_HOLDER_NAME':200,'S_SHARE_LSTTYPENAME':200})

                    elif self.table_name == 'WIND_AShareInsideHolder':
                        dat.drop(['S_HOLDER_MEMO'], axis=1, inplace=True)
                        dat['S_HOLDER_SEQUENCE'] = dat['S_HOLDER_SEQUENCE'].astype(str)
                        dat['S_HOLDER_SHARECATEGORYNAME'] = dat['S_HOLDER_SHARECATEGORYNAME'].astype(str)
                        dat['S_HOLDER_SHARECATEGORY'] = dat['S_HOLDER_SHARECATEGORY'].astype(str)
                        # print(dat.dtypes)

                        h5_store.append(self.table_name,dat,data_columns=True, min_itemsize={'S_HOLDER_NAME': 200, 
                                                                                            'S_HOLDER_ANAME':200,
                                                                                            'S_HOLDER_SEQUENCE':200,
                                                                                            'S_HOLDER_SHARECATEGORYNAME':200,
                                                                                            'S_HOLDER_SHARECATEGORY':200})

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
        if self.table_name in ['WIND_AShareDividend']:
            sql_where = ' where report_period='

        elif self.table_name in ['WIND_CMFOtherPortfolio',  'WIND_AShareHolderNumber', 'WIND_AShareIllegality',
                                'WIND_AShareInsideHolder', 'WIND_AShareMjrHolderTrade','WIND_AShareFloatHolder',
                                'WIND_AShareFFCalendar', 'WIND_AShareEquityPledgeInfo','WIND_AShareCompRestricted',
                                'WIND_ASarePlanTrade','WIND_AShareCompanyHoldShares']:
            sql_where = ' where ANN_DT='
        elif self.table_name in ['WIND_AShareAnnInf']:
            pass
        elif self.table_name in ['WIND_AShareInsiderTrade']:
            sql_where = ' where ACTUAL_ANN_DT='
            # do something special deal with datetime type 
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
            else:
                if self.table_name == 'WIND_AShareAnnInf':
                    sql_line = "select count(*) from " + self.table_name + " where COLLECT_DT>=to_date('" + str(date) +  " 0:00:00','YYYYMMDD HH24:mi:ss') and COLLECT_DT<=to_date('" +  str(date) + " 23:59:59','YYYYMMDD HH24:mi:ss')"
                    print(sql_line)
                    df = sql_parser(queryUserTableData(sql_line))
       
                else:
                    df = sql_parser(queryUserTableData('select count(*) from ' + self.table_name + sql_where + str(date)))
                total_row_count = int(df['COUNT(*)'])
                save_name = os.path.join(self.table_csv_path,str(date) + '.csv')

                if total_row_count < 100000:
                    if self.table_name == 'WIND_AShareAnnInf':
                        # sql_use = sql_select + " where ANN_DT=to_date(" + str(date) + ",'YYYYMMDD')"
                        sql_use = sql_select + " where COLLECT_DT>=to_date('" + str(date) + " 0:00:00','YYYYMMDD HH24:mi:ss') and COLLECT_DT<=to_date('" + str(date) + " 23:59:59','YYYYMMDD HH24:mi:ss')"
                 
                    else:
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
                        # not really need to add WIND_AShareAnnInf since it's not possible bigger than 100000;
                        if self.table_name == 'WIND_AShareAnnInf':
                            sql_where1 = " where COLLECT_DT>=to_date('" + str(date) + " 0:00:00','YYYYMMDD HH24:mi:ss') and COLLECT_DT<=to_date('" + str(date) + " 23:59:59','YYYYMMDD HH24:mi:ss')"
                            sql_use = 'select * from ' + self.table_name + ' where object_id in ((select object_id from ' + self.table_name + sql_where1 + ' and rownum <= ' +str(end_line) + ') ' + 'minus(select object_id from ' + self.table_name + sql_where1 + ' and rownum <= ' + str(start_line) + '))'
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
        
        update_list = []
        for date in self.cdate_list:
            update_list.append(os.path.join(self.table_csv_path,str(date)+'.csv'))

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

    if not table_name in ['WIND_FinancialNews']:
        if update_h5_flag:
            wind_db.dumper()
    # else:
        # print('Do not need to dump into h5')
    return 
 

def get_all_days(sdate,edate):
    h5_path = 'Z:\\warehouse\\prod\\CALENDAR\\nature_days.h5'
    df = IO.read_data([sdate,edate],alt=h5_path)
    df.reset_index(inplace=True)
    df['dt'] = df['dt'].apply(lambda x : int(str(x).replace('-','')[:8]))
    date_list = list(set(df['dt']))
    date_list.sort()
    return date_list

def add_new_tables(sdate,edate):
    qtr_list = []
    daily_list =  ['WIND_AShareInsiderTrade','WIND_AShareAnnInf','WIND_AShareIllegality',
                    'WIND_AShareCompRestricted','WIND_AShareInsideHolder','WIND_AShareHolderNumber']
  
    table_dict = {'DAILY':daily_list ,'QUARTERLY': []}

    for table_type in table_dict:
        for table_name in table_dict[table_type]:
            print (table_name)
            instantiate(table_name, sdate, edate, base_path = 'Z:\\warehouse\\prod\\', operation = 'append',table_dict=table_dict,update_h5_flag=True)
    
    logger.info('===============add_new_tables======================')

def get_current_nature_date(new_date_time=18):
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print('Current time: ' + str(current_time))
    h5_path = 'Z:\\warehouse\\prod\\CALENDAR\\nature_days.h5'
    fdate_list_dt = IO.read_data([19980101, 20200101], alt=h5_path).index.get_level_values(0)
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

sdate = get_current_nature_date()
print(sdate)
add_new_tables(sdate,sdate)

flag_root = 'Z:\\warehouse\\prod\\LOCAL_DATA\\FLAG\\' + str(sdate) + '\\'
if not os.path.exists(flag_root):
    os.makedirs(flag_root)
flag_path = flag_root + str(sdate) + '_' + 'SPECIAL.success'
with open(flag_path,'w') as file:
    pass

# add_new_tables(20040101,20190818)