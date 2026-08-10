# -*- coding: utf-8 -*-
"""
update_concensus_htsc

"""



# -*- coding: utf-8 -*-
"""
update wind_db from htsc matlab

"""


import datetime as dt
import pandas as pd
import scipy.io as sio  
import os
import numpy as np
import json
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import os
import subprocess
from functools import partial
import time
import scipy.io as sio  
import numba
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

from log import Log
import config_reader
from concurrent.futures import ProcessPoolExecutor as Pool
from concurrent.futures import as_completed
import urllib
import winreg
import time
import re
logger = Log('check_increment')




def getQPUserInfo():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Wow6432Node\QuantPF")
        userid,type = winreg.QueryValueEx(key,"userid")
        session,type = winreg.QueryValueEx(key,"session")
        ipaddr,type = winreg.QueryValueEx(key,"ipaddr")
    except:
        try:
            key,type = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\QuantPF")
            userid,type = winreg.QueryValueEx(key,"userid")
            session,type = winreg.QueryValueEx(key,"session")
            ipaddr,type = winreg.QueryValueEx(key,"ipaddr")
        except:
            userid = '000000'
            session = 'Invalid session'
            ipaddr = 'Invalid IP'
    return userid,session,ipaddr


def queryUserTableData(sqlStr='', rownum=100000):
    if sqlStr == '':
        print('[queryUserTableData函数]参数queryUserTableData为空，请重新输入！')
        return
    dbPath = 'http://eip.htsc.com.cn/QuantiveService/DataSetService/'
    urlVersion = '0161'
    url = dbPath + 'queryUserTableDataset'
    userid,session,ipaddr = getQPUserInfo() #获取用户登录信息
    #传递参数获取数据
    parms = urllib.parse.urlencode({'apiparam':urlVersion,'userid':userid,'session':session,
                                    'ipaddr':ipaddr,'rownum':str(rownum),'strsql':sqlStr})
    parms = parms.encode('utf-8')
    data = urllib.request.urlopen(url,parms)
    data = data.read().decode('utf-8')
    data = ('[['+data[1:-1] +']]').replace(';','],[')
    return data

def sql_parser(data):
    NaN = np.nan
    try:
        _data = eval(data)
    except SyntaxError as _exp:
        if 'triple-quoted string' in _exp.msg:
            try:
                _data = re.sub(r"'{3,}", '', data)
                _data = re.sub(r'"{3,}', '', _data)
                _data = eval(_data)
            except:
                _data = re.sub(r"'{2}", '', data)
                _data = re.sub(r'"{2}', '', _data)
                _data = re.sub(r"(?<=,),", 'NaN,', _data)
                _data = re.sub(r"'{3,}", '', _data)
                _data = re.sub(r'"{3,}', '', _data)
                _data = eval(_data)
        else:
            raise SyntaxError
    try:
        res = pd.DataFrame(_data[1:], columns=_data[0])
    except OverflowError:
        res = pd.DataFrame(_data, columns=_data[0])
        res = res.drop([0], axis=0).reset_index(drop=True)
    return res

def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day 
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    logger.info('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x:abs(x-current_date) if x<=current_date else 100)
    if current_hour < new_date_time and nearest_date==current_date:
        logger.info('Not till refresh time '+str(new_date_time)+':00')
        current_date = fdate_list[fdate_list.index(current_date)-1]
        logger.info('Use previous trading date: '+str(current_date))
    elif nearest_date<current_date:
        current_date = nearest_date
    elif current_hour >= new_date_time and nearest_date==current_date:
        logger.info('Right on time: '+str(current_date))
    return current_date



def date_period_handler(sdate=None,edate=None):
    last_day = get_current_date()
    if sdate is None and edate is None:
        sdate = last_day
        edate = last_day
        logger.info('update for one day: '+str(sdate))
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
    logger.info('-'*20 + '\ndata used: %d - %d '%(sdate_prev,edate))
    logger.info('factor data: %d - %d \ntotal count: %d'%(sdate_prev,edate,len(cdate_list)))
    logger.info('-'*20)
    return sdate_prev,edate,cdate_list


def ticker_match(ticker_num): # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker

def data_reformat(dat,dat_fig):
    if dat.empty:
        logger.info('data today is empty')
        return dat
    if 'drop' in dat_fig.keys():
        dat = dat.drop(dat_fig['drop'],axis=1)

    # format_list = [type(i) for i in dat.iloc[0,:]]
    format_list = dat.dtypes
    # print(format_list)
    num_list = [i != np.dtype('object') for i in format_list]    
    str_list = [i==np.dtype('object') for i in format_list]
    col_list = dat.columns.values
    for i in range(len(str_list)):
        if str_list[i]:
            dat[col_list[i]] = dat[col_list[i]].astype('object')
    dat.iloc[:,str_list] = dat.iloc[:,str_list].applymap(lambda x:x if len(x)>0 else '')
    for i in range(len(num_list)):
        if num_list[i]:
            dat[col_list[i]] = dat[col_list[i]].astype('float64')
   
    if 'dt' in dat_fig.keys():
        dat[dat_fig['dt']] = dat[dat_fig['dt']].apply(lambda x: dt.datetime.strptime(str(int(x.replace('-','')[:8])),'%Y%m%d')
                                            if type(x) == np.str_ or type(x) == str else  dt.datetime.strptime(str(int(x)),'%Y%m%d'))
        
        if 'Ticker' in dat_fig.keys():
            if 'ticker_match' in dat_fig.keys():
                # dat = dat.query("dat_fig['Ticker'] != 'A00000'")
                dat[dat_fig['Ticker']] = dat[dat_fig['Ticker']].apply(lambda x: 'drop' if not x.isnumeric() else x)
                dat = dat[dat[dat_fig['Ticker']] != 'drop']
                dat[dat_fig['Ticker']] = dat[dat_fig['Ticker']].apply(ticker_match)
                # dat[dat_fig['Ticker']] = dat[dat_fig['Ticker']].apply(lambda x: )

            else:
                dat[dat_fig['Ticker']] = dat[dat_fig['Ticker']].astype('str')
            dat = dat.sort_values([dat_fig['dt'],dat_fig['Ticker']])
            dat = dat.set_index([dat_fig['dt'],dat_fig['Ticker']])
            dat.index.names = ['dt','Ticker']
        else:
            dat = dat.sort_values([dat_fig['dt'], 'ID'])
            dat = dat.set_index([dat_fig['dt'], 'ID'])
            dat.index.names = ['dt', 'ID']
            # print(dat)

    # logger.info(dat)
    return dat
    
def retrieve(table_name, date, update_flg = False):
    cdate_list = [date]
    print('start to download table ' + table_name)
    if table_name in ['con_forecast_schedule', 'con_forecast_stk','cmb_report_subtable',
            'cmb_report_research','der_report_subtable', 'der_report_research', 'cmb_report_adjust',
            'cmb_report_score_adjust', 'i_organ_score','report_author','researcher_info','gg_org_list',
            'i_report_type','con_forecast_c2_stk','con_forecast_c3_cgb_stk','con_forecast_c3_stk','con_forecast_cb_stk']:
        table_name_sql = 'G_' + table_name
    else:
        table_name_sql = 'GN_' + table_name


    sql_select = 'select * from ' + table_name_sql +' '
    use_date = 1
    if table_name  == 'con_excess_stock':
        sql_where = ' where ReportYear='
    elif table_name in ['cmb_report_subtable', 'der_report_subtable', 'der_report_research', 'cmb_report_adjust',  'report_author','author_pj']:
        use_date = 0
        sql_where = ' where EntryDate='
    elif table_name in ['cmb_report_research']:
        use_date = 0
        sql_where = ' where Create_Date='

    elif table_name in ['researcher_info', 'author_core', 'author_core_type','t_author_honor', 'i_report_type', 'i_organ_score', 
                         'gg_org_list',  't_great_author', 'author_pjhb' ,'cmb_report_score_adjust']:
        use_date = 3
        sql_where = ''
    else:
        sql_where = ' where tdate='
    
    for date in cdate_list:
        if use_date  == 1:
            sql_use = sql_select + sql_where + str(date)
        elif use_date == 3:
            sql_use = sql_select + sql_where
        else:
            sql_use = sql_select + sql_where + "to_date(" + str(date) +  ",'YYYYMMDD')"
        print(sql_use)
        df = sql_parser(queryUserTableData(sql_use))
        override = False

        if table_name in ['con_forecast_schedule','con_forecast_stk','stock_diversity','con_stock_deviation',
        'stock_diversity', 'stock_emotion','stock_report_extremum','stock_report_number','con_forecast_c2_stk',
         'con_forecast_c3_cgb_stk','con_forecast_c3_stk','con_forecast_cb_stk']:
            dat_fig = {'dt':'TDATE','Ticker':'STOCK_CODE','ticker_match':'STOCK_CODE'}    


        elif table_name in ['cmb_report_subtable', 'der_report_subtable',  'der_report_research', 
                  'i_organ_score', 'report_author', 'gg_org_list','i_report_type', 
                  'author_core_type',  't_great_author']:
            dat_fig = {'dt':'ENTRYDATE'}
        
        elif table_name in ['cmb_report_adjust', 'cmb_report_score_adjust','author_pj', 'author_pjhb','author_core']:
            dat_fig = {'dt':'ENTRYDATE','Ticker':'STOCK_CODE','ticker_match':'STOCK_CODE'}
        
        elif table_name in ['t_author_honor']:
            dat_fig = {'dt':'ENTRYDATE','Ticker':'CODE','ticker_match':'CODE'}

        elif table_name in ['cmb_report_research']:
            dat_fig = {'dt': 'Create_Date'}
        elif table_name in ['researcher_info']:
            dat_fig = {}
            override = True
        else:    
            dat_fig = {'dt':'TDATE','Ticker':'STOCK_CODE','ticker_match':'STOCK_CODE','drop':['CONKEYTMS']}

        if table_name not in ['cmb_report_research','der_report_research']:
            df = data_reformat(df, dat_fig)

        if not update_flg: 
            if table_name in 'researcher_info':
                df.set_index('ID', inplace=True)
                df.to_csv('Z:\\warehouse\\test\\test.csv', sep=',', encoding='utf_8_sig')
            elif table_name in ['author_core', 'author_core_type','t_author_honor', 'i_report_type', 'i_organ_score', 
                             'gg_org_list',  't_great_author', 'author_pjhb' ,'cmb_report_score_adjust']:
                df.to_csv('Z:\\warehouse\\test\\test.csv', sep=',', encoding='utf_8_sig')
            else:
                df.to_csv('Z:\\warehouse\\test\\test.csv', sep=',', encoding='utf_8_sig')

            df = pd.read_csv('Z:\\warehouse\\test\\test.csv')
            df.fillna('NAN', inplace=True)
            return df
        else:
            table_folder = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc\\' + table_name + '\\'
            # table_folder = 'Z:\\test\\' + table_name + '\\'
            if not os.path.exists(table_folder):
                os.mkdir(table_folder)
            if table_name in 'researcher_info':
                df.set_index('ID', inplace=True)
                df.to_csv(table_folder + 'researcher_info.csv', sep=',', encoding='utf_8_sig')
            elif table_name in ['author_core', 'author_core_type','t_author_honor', 'i_report_type', 'i_organ_score', 
                             'gg_org_list',  't_great_author', 'author_pjhb' ,'cmb_report_score_adjust']:
                df.to_csv(table_folder + table_name + '.csv', sep=',', encoding='utf_8_sig')
            else:
                df.to_csv(table_folder + str(date) + '.csv', sep=',', encoding='utf_8_sig')

def override_data(diff_list, date):
    table_list3 = ['researcher_info', 'author_core', 'author_core_type', 't_author_honor', 
    'i_report_type','i_organ_score', 'gg_org_list', 't_great_author', 'author_pjhb',
     'cmb_report_score_adjust']
    root_folder = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc\\'
    root_path = 'Z:\\warehouse\\prod\\'

    for table_name in diff_list:
        retrieve(table_name, date, update_flg = True)
        if table_name not in ['cmb_report_research','der_report_research']:
            if table_name =='con_forecast_stk':
                h5_path = root_path+'FCD\\CHINA_STOCK\\DAILY\\SUNTIME\\SUNTIME_fcd_china_stock_daily_SUNTIME.h5'
            else:
                h5_path = root_path+'DATABASE\\SUNTIME\\'+ table_name + '\\' + table_name + '.h5'
            source_path = root_folder + table_name + '\\'
            csv_list = [source_path+i for i in os.listdir(source_path)]
            if table_name in table_list3:
                csv2h5(csv_list, h5_path, table_name, 'create', min_size=0)
            else:
                csv_list_take = [source_path + str(date) + '.csv']
                csv2h5(csv_list_take,h5_path,table_name,'append',min_size=0)

def csv2h5(csv_list,h5_path,table_name,operation,min_size=0):
    fail_list = []   
    if operation=='create':
        logger.info('Create new h5: '+h5_path)
        if os.path.exists(h5_path):
            logger.info('Remove existing h5:'+h5_path)
            os.remove(h5_path) 
    elif operation == 'append':
        logger.info('Append to: '+ h5_path)
    with pd.HDFStore(h5_path) as h5_store:
        logger.info('check date list takes some time')
        if table_name in list(h5_store.root._v_groups.keys()):

            dt_lst = list(set(h5_store.select_column(table_name, 'dt')))
        else:
            dt_lst = []
        for fname in csv_list:
            logger.info(fname)
            logger.info('read')
            dat = pd.read_csv(fname, encoding='utf_8_sig')
            columns = dat.columns.values

            if 'dt' in columns:
                dat['dt'] = dat['dt'].apply(lambda x: dt.datetime.strptime(x.replace('-',''),'%Y%m%d'))
                print(type(dat['dt'][0]))
            if 'dt' in columns and 'Ticker' in columns:
                dat.set_index(['dt', 'Ticker'], inplace=True)
            elif 'dt' in columns and 'ID' in columns:
                dat.set_index(['dt', 'ID'], inplace=True)

            if 'CON_HISDATE' in columns:
                dat['CON_HISDATE'] = dat['CON_HISDATE'].astype('str')

            if len(dat)<min_size or dat.empty:
                print(dat)
                logger.info('csv data too little!')
                fail_list.append(fname+'@amount_fail')
            else:
                if operation == 'append':      
                    curr_date = list(set(dat.index.get_level_values('dt')))[0]
                    logger.info(curr_date)
                    if curr_date in dt_lst:
                        logger.info('Already exists: '+str(curr_date))
                        dummy_id = h5_store.remove(table_name,'dt=curr_date')
                        logger.info('Append: '+str(curr_date))
                        # continue
                logger.info('insert')
                h5_store.append(table_name,dat,data_columns=True)
                logger.info('done')


    logger.info('data loading complete!')     
    return fail_list    




def get_origin_df(table_name, date):
    table_list3 = ['researcher_info', 'author_core', 'author_core_type', 't_author_honor', 'i_report_type', 
                'i_organ_score', 'gg_org_list', 't_great_author', 'author_pjhb', 'cmb_report_score_adjust']
    path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc\\'
    if table_name in table_list3:
        csv_path = path + table_name + '\\' + table_name + '.csv'
    else:
        csv_path = path + table_name + '\\' + str(date) + '.csv'

    df = pd.read_csv(csv_path) 
    # df.set_index(['dt', 'Ticker'], inplace=True)
    # df.reset_index('dt', inplace=True)
    # df.drop('dt', axis = 1, inplace=True)
    df.fillna('NAN', inplace=True)
    return df
def increment_checker(date):
    logger.info('-'*40 + 'start to check' + '-'*40)
    table_list = ['con_forecast_stk', 'con_forecast_schedule','stock_order3','stock_order2',
                  'stock_report_adjustment2','stock_report_adjustment','stock_concern_level',
                  'con_stock_deviation3','con_stock_deviation2','con_stock_deviation',
                  'stock_diversity','stock_emotion','stock_report_extremum','stock_report_number',
                  'der_report_subtable', 'cmb_report_score_adjust', 'i_organ_score', 'report_author', 
                  'cmb_report_adjust', 'gg_org_list', 'i_report_type', 'author_core_type', 'author_core',
                  'cmb_report_subtable', 'author_pjhb', 't_great_author',
                  'con_forecast_c2_stk', 'con_forecast_c3_cgb_stk', 'con_forecast_c3_stk', 'con_forecast_cb_stk', 
                  'researcher_info', 't_author_honor']
    # table_list = ['researcher_info']
    dict_table = {} 
    for table_name in table_list:
        dict_table[table_name] = get_origin_df(table_name, date)

    same_flag = True
    # time.sleep(1800)
    diff_list = []
    while same_flag:
        same_flag = False
        for table_name in table_list:
            df = retrieve(table_name,date, update_flg = False)
            length = len(df)
            if len(df) != len(dict_table[table_name]):
                diff_list.append(table_name)
                print(len(df), len(dict_table[table_name]))
            else:
                rst = df == dict_table[table_name]
                rst = rst.sum()
                for row in rst:
                    if not row == length:
                        print(row, length)
                        diff_list.append(table_name)
        if len(diff_list) != 0:
            for factor_name in diff_list:
                logger.info(factor_name)
            override_data(diff_list, date)

    logger.info('=============================================== check increment completed')


