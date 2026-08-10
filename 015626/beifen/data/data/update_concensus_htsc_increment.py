# -*- coding: utf-8 -*-
"""
update_concensus_htsc

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
from increment_checker import increment_checker
from log import Log
import config_reader
import urllib
import winreg
import re
logger = Log('update_concensus_htsc')

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

def index_match(ticker_num):
    if not ticker_num.isnumeric():
        return str(ticker_num)
    if str(ticker_num)[:3] == '000':
        suffix = '.SH'
    elif str(ticker_num)[:3] == '399':
        suffix = '.SZ'
    else:
        return str(ticker_num)
    ticker_num = int(ticker_num)
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
            elif 'index_match' in dat_fig.keys():
                # dat = dat.query("dat_fig['Ticker'] != 'A00000'")
                dat[dat_fig['Ticker']] = dat[dat_fig['Ticker']].apply(index_match)
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
            # if table_name in ['CMB_REPORT_SUBTABLE', 'DER_REPORT_SUBTABLE', 'CMB_REPORT_RESEARCH', 'DER_REPORT_RESEARCH', 
            #     'CMB_REPORT_ADJUST', 'CMB_REPORT_SCORE_ADJUST', 'I_ORGAN_SCORE', 'REPORT_AUTHOR', 'GG_ORG_LIST',
            #      'I_REPORT_TYPE', 'AUTHOR_CORE_TYPE', 'AUTHOR_CORE', 'T_AUTHOR_HONOR', 'AUTHOR_PJ', 'AUTHOR_PJHB', 
            #      'T_GREAT_AUTHOR']:
            # else:            #     dt_lst = list(set(h5_store.select(table_name).index))
            # print(h5_store.select(table_name))
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
                if table_name in ['CON_FORECAST_IDX','CON_FORECAST_C2_IDX','CON_FORECAST_C3_IDX']:
                    h5_store.append(table_name,dat, data_columns=True,min_itemsize={'STOCK_NAME':50})
                else:
                    h5_store.append(table_name,dat,data_columns=True)
                logger.info('done')


    logger.info('data loading complete!')     
    return fail_list    


def retrieve(table_name,cdate_list,root_folder):
    print('start to download table ' + table_name)
    if table_name in ['con_forecast_schedule', 'con_forecast_stk','cmb_report_subtable',
            'cmb_report_research','der_report_subtable', 'der_report_research', 'cmb_report_adjust',
            'cmb_report_score_adjust', 'i_organ_score','report_author','researcher_info','gg_org_list',
            'i_report_type','con_forecast_c2_stk','con_forecast_c3_cgb_stk','con_forecast_c3_stk','con_forecast_cb_stk',
            'change_type','change_event','CON_FORECAST_IDX','CON_FORECAST_C2_IDX','CON_FORECAST_C3_IDX']:
        table_name_sql = 'G_' + table_name
    else:
        table_name_sql = 'GN_' + table_name

    table_folder = root_folder + table_name + '\\'
    if not os.path.exists(table_folder):
        os.mkdir(table_folder)
    sql_select = 'select * from ' + table_name_sql +' '
    use_date = 1
    if table_name  == 'con_excess_stock':
        sql_where = ' where ReportYear='
    elif table_name in ['cmb_report_research', 'der_report_research','cmb_report_subtable', 'der_report_subtable', 
                        'cmb_report_adjust',  'report_author','cmb_report_score_adjust','change_type','change_event']:
        use_date = 0
        sql_where = ' where EntryDate='

    elif table_name in ['author_pj']:
        use_date = 4
        sql_where = ' where Rpt_Date='
    elif table_name in ['researcher_info', 'author_core', 'author_core_type', 'i_report_type', 'i_organ_score', 
                         'gg_org_list',  't_great_author', 'author_pjhb','t_author_honor']:
        use_date = 3
        sql_where = ''
        print(use_date)
    else:
        sql_where = ' where tdate='
    
    for date in cdate_list:
        if use_date  == 1:
            sql_use = sql_select + sql_where + str(date)
        elif use_date == 3:
            sql_use = sql_select + sql_where
            df = sql_parser(queryUserTableData('select count(*) from ' + table_name_sql))
            total_row_count = int(df['COUNT(*)'])
            if total_row_count < 100000:
                sql_use = 'select * from ' + table_name_sql
                df = sql_parser(queryUserTableData(sql_use))
            else:
                print(total_row_count)
                df_list = []
                group = int(total_row_count / 90000)
                for i in range(group + 1):
                    start_line = i * 90000
                    end_line = min((i + 1) * 90000, total_row_count)
                    sql_use = '(select * from ' + table_name_sql +  ' where rownum <= ' +str(end_line) + ') ' + 'minus(select * from ' + table_name_sql + ' where rownum <= ' + str(start_line) + ')'
                    print(sql_use)
                    df = sql_parser(queryUserTableData(sql_use))
                    df_list.append(df)
                df = pd.concat(df_list)
                print(len(df))
                print(total_row_count)
        elif use_date == 4:
            sql_use = sql_select + sql_where + str(date)[:4]

        else:
            sql_use = sql_select + sql_where + "to_date(" + str(date) +  ",'YYYYMMDD')"

        if not use_date == 3:
            print(sql_use)
            df = sql_parser(queryUserTableData(sql_use))
        override = False

        if table_name in ['con_forecast_schedule','con_forecast_stk','stock_diversity','con_stock_deviation',
        'stock_diversity', 'stock_emotion','stock_report_extremum','stock_report_number','con_forecast_c2_stk',
         'con_forecast_c3_cgb_stk','con_forecast_c3_stk','con_forecast_cb_stk','con_stock_income']:
            dat_fig = {'dt':'TDATE','Ticker':'STOCK_CODE','ticker_match':'STOCK_CODE'}    
        elif table_name in ['CON_FORECAST_IDX','CON_FORECAST_C2_IDX','CON_FORECAST_C3_IDX']:
            dat_fig = {'dt':'TDATE','Ticker':'STOCK_CODE','index_match':'STOCK_CODE'}    

        elif table_name in ['cmb_report_subtable', 'der_report_subtable', 
                  'i_organ_score', 'report_author', 'gg_org_list','i_report_type', 
                  'author_core_type',  't_great_author','cmb_report_research', 'der_report_research',
                  'change_type','change_event']:
            dat_fig = {'dt':'ENTRYDATE'}
        
        elif table_name in ['cmb_report_adjust', 'cmb_report_score_adjust','author_pj', 'author_pjhb','author_core']:
            dat_fig = {'dt':'ENTRYDATE','Ticker':'STOCK_CODE','ticker_match':'STOCK_CODE'}
        
        elif table_name in ['t_author_honor']:
            dat_fig = {'dt':'ENTRYDATE','Ticker':'CODE','ticker_match':'CODE'}

        elif table_name in ['researcher_info']:
            dat_fig = {}
            override = True
        else:    
            dat_fig = {'dt':'TDATE','Ticker':'STOCK_CODE','ticker_match':'STOCK_CODE','drop':['CONKEYTMS']}


        if table_name not in ['cmb_report_research','der_report_research','change_type','change_event']:
            df = data_reformat(df, dat_fig)

        if table_name in 'researcher_info':
            df.set_index('ID', inplace=True)
            df.to_csv(table_folder + 'researcher_info.csv', sep=',', encoding='utf_8_sig')
        elif table_name in ['author_core', 'author_core_type', 'i_report_type', 'i_organ_score', 
                         'gg_org_list',  't_great_author', 'author_pjhb','t_author_honor']:
            df.to_csv(table_folder + table_name + '.csv', sep=',', encoding='utf_8_sig')
        elif table_name in ['cmb_report_research','der_report_research']:
            csv_path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc\\' + table_name + '\\' + str(date) + '.csv'
            # df.to_csv(csv_path, sep=',', encoding='utf_8_sig')
            # df = pd.read_csv(csv_path)
            df['CONTENT'] = df['CONTENT'].astype(str)
            df['CONTENT'] = df['CONTENT'].apply(lambda x : x.replace('\n', ''))
            df['CONTENT'] = df['CONTENT'].apply(lambda x : x.replace('\r', ''))
            df['CONTENT'] = df['CONTENT'].apply(lambda x : x.replace(',', '，'))

            df['AUTHOR'] = df['AUTHOR'].astype(str)
            df['AUTHOR'] = df['AUTHOR'].apply(lambda x : x.replace('\n', ''))
            df['AUTHOR'] = df['AUTHOR'].apply(lambda x : x.replace('\r', ''))
            df['AUTHOR'] = df['AUTHOR'].apply(lambda x : x.replace(',', '，'))

            df['TITLE'] = df['TITLE'].astype(str)
            df['TITLE'] = df['TITLE'].apply(lambda x : x.replace('\n', ''))
            df['TITLE'] = df['TITLE'].apply(lambda x : x.replace('\r', ''))
            df['TITLE'] = df['TITLE'].apply(lambda x : x.replace(',', '，'))

            df.to_csv(csv_path, sep=',', encoding='utf_8_sig')

        elif table_name == 'der_report_subtable':
            csv_path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc\\der_report_subtable\\' + str(date) + '.csv'
            df.to_csv(csv_path, sep=',', encoding='utf_8_sig')
            df = pd.read_csv(csv_path)         
            df['ID'] = df['ID'].astype('int')
            df['REPORT_SEARCH_ID'] = df['REPORT_SEARCH_ID'].astype('int')
            df['TIME_YEAR'] = df['TIME_YEAR'].astype('int')
            df.to_csv(csv_path, sep=',', encoding='utf_8_sig')
        elif table_name == 'author_pj':
            df.to_csv(table_folder + str(date)[:4] + '.csv', sep=',', encoding='utf_8_sig')
        else:
            df.to_csv(table_folder + str(date) + '.csv', sep=',', encoding='utf_8_sig')

def update_consensus_data(sdate=None,edate=None,operation='append'):
    logger.info('-'*40 + 'update concensus data' + '-'*40)
    table_list = ['con_forecast_stk', 'con_forecast_schedule','stock_order3','stock_report_adjustment',
                  'stock_report_number','stock_order2','stock_report_adjustment2','stock_concern_level',
                  'con_stock_deviation3','con_stock_deviation2','con_stock_deviation',
                  'stock_diversity','stock_emotion','stock_report_extremum',
                  'der_report_subtable', 'cmb_report_score_adjust', 'i_organ_score', 'report_author', 
                  'cmb_report_adjust', 'gg_org_list', 'i_report_type', 'author_core_type', 'author_core',
                  'cmb_report_subtable', 'author_pj', 'author_pjhb', 't_great_author',
                  'con_forecast_c2_stk', 'con_forecast_c3_cgb_stk', 'con_forecast_c3_stk', 'con_forecast_cb_stk', 
                  'researcher_info', 't_author_honor', 'der_report_research','cmb_report_research']

    
    table_list3 = ['researcher_info', 'author_core', 'author_core_type', 'i_report_type', 't_author_honor',
                    'i_organ_score', 'gg_org_list', 't_great_author', 'author_pjhb']

    sdate,edate,cdate_list = check_update_date(sdate,edate)

    root_folder = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc\\'
    root_path = 'Z:\\warehouse\\prod\\'
    total_table_list = ['CON_FORECAST_IDX','CON_FORECAST_C2_IDX','CON_FORECAST_C3_IDX']
    # total_table_list = table_list
    for table_name in ['CON_FORECAST_C2_IDX']:
        if table_name in table_list3:
            print(cdate_list[-1:])
            retrieve(table_name, cdate_list[-1:], root_folder)
        else:
            pass
            # retrieve(table_name, cdate_list,root_folder)

        if table_name not in ['cmb_report_research','der_report_research','author_pj']:
            if table_name =='con_forecast_stk':
                h5_path = root_path+'FCD\\CHINA_STOCK\\DAILY\\SUNTIME\\FCD_CHINA_STOCK_DAILY_SUNTIME.h5'
            else:
                h5_path = root_path+'DATABASE\\SUNTIME\\'+ table_name + '\\' + table_name + '.h5'
                if not os.path.exists(root_path+'DATABASE\\SUNTIME\\'+ table_name):
                    os.makedirs(root_path+'DATABASE\\SUNTIME\\'+ table_name)
            source_path = root_folder + table_name + '\\'
            csv_list = [source_path+i for i in os.listdir(source_path)]
            if table_name in table_list3:
                csv2h5(csv_list, h5_path, table_name, 'create', min_size=0)
            else:
                csv_list.sort()
                csv_date_list = [int(i[-12:-4]) for i in csv_list]
                csv_date_list_take = [i for i in csv_date_list if i>=sdate and i<=edate]
                csv_list_take = [source_path+str(i)+'.csv' for i in csv_date_list_take]
                csv_list_take.sort()
                csv2h5(csv_list_take,h5_path,table_name,'create',min_size=0)

# CON_FORECAST_IDX,CON_FORECAST_C2_IDX,CON_FORECAST_C3_IDX
if __name__ == '__main__':
    start_date = 20090101
    end_date = 20190924
    start_date, end_date, _ = check_update_date(start_date,end_date)
    update_consensus_data(start_date,end_date)


