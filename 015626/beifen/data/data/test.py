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

def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x:abs(x-current_date) if x<=current_date else 100)
    if current_hour < new_date_time and nearest_date==current_date:
        current_date = fdate_list[fdate_list.index(current_date)-1]
    elif nearest_date<current_date:
        current_date = nearest_date
    elif current_hour >= new_date_time and nearest_date==current_date:
        print(current_date)
    return current_date



def date_period_handler(sdate=None,edate=None):
    last_day = get_current_date()
    if sdate is None and edate is None:
        sdate = last_day
        edate = last_day
    if sdate is not None and edate is None:
        edate = last_day
    else:
        fdate_list_dt = IO.read_data([20050101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
        fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
        cdate_list = [i for i in fdate_list if i<=min(edate,last_day) and i>=sdate]
        sdate,edate = cdate_list[0],cdate_list[-1]
    return sdate,edate


def check_update_date(sdate=None,edate=None,use_len=None):
    #check_update_date(sdate=None,edate=None)
    use_len = 0 if use_len is None else use_len
    sdate,edate = date_period_handler(sdate,edate)
    fdate_list_dt = IO.read_data([20050101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    cdate_list = [i for i in fdate_list if i>=sdate and i<=edate]
    idx = max(0,fdate_list.index(cdate_list[0])-use_len)
    sdate_prev = fdate_list[idx]
    return sdate_prev,edate,cdate_list

def get_all_days(sdate,edate):
    h5_path = 'Z:\\warehouse\\prod\\CALENDAR\\nature_days.h5'
    df = IO.read_data([sdate,edate],alt=h5_path)
    df.reset_index(inplace=True)
    df['dt'] = df['dt'].apply(lambda x : int(str(x).replace('-','')[:8]))
    date_list = list(set(df['dt']))
    date_list.sort()
    return date_list


# sdate,edate,cdate_list_workday = check_update_date(20050104,20191029)
#
# cdate_list_allday = get_all_days(20050104,20191029)
# cdate_list_weekendday = list(set(cdate_list_allday) - set(cdate_list_workday))
# cdate_list_weekendday.sort()
#
# for date in cdate_list_weekendday:
# 	print(date)
# 	df = sql_parser(queryUserTableData('select * from G_con_forecast_zx where TDATE =' + str(date)))
# 	if(len(df) > 0):
# 		print(df)

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

df = sql_parser(queryUserTableData('select * from WIND_AShareTechIndicators  where trade_dt=20191122'))
# df = IO.read_data([20191101, 20191111], alt = r'Z://warehouse//prod//MD//CHINA_STOCK//DAILY//WIND//HIGH_FREQ_DAILY_MD.h5')
# df = IO.read_data([20191112,20191113],columns=['vwap_halfday_1','vwap_halfday_2'] , alt = r'Z:\\warehouse\\prod\\VD\\CHINA_STOCK\\DAILY\\WIND\\VD_CHINA_STOCK_DAILY_WIND.h5')
# print(df[df.index.get_level_value(1) == '1000011297000000'])
# print(df)
# print(len(df[df.S_DQ_CLOSE > 0]))
# df.to_csv('Z:\warehouse\\test\LOCAL_DATA\CSV\gogoal_htsc\con_forecast_zx\\new_WIND_AIndexIndustriesEODCITICS.csv',encoding = 'utf-8')
# with pd.HDFStore('Z:\warehouse\\prod\DATABASE\SUNTIME\\researcher_info\\researcher_info.h5', 'r') as hdf_store:
#     print(hdf_store.researcher_info)
# print(df.columns,df.TDATE.max(),df.TDATE.min())
# df = IO.read_data(20191108,
#                              alt=r'Z:/warehouse/prod/DATABASE/WIND/AIndexConsensusData/AIndexConsensusData.h5')
#
# print(dfprices0)
print(df)
