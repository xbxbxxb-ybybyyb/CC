# -*- coding: utf-8 -*-
"""
@author: 013160
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
def init_trading_day(h5_path=None):
    h5_path = 'S:\\Quant\\data\\calendar\\CHINA_STOCK\\DAILY\\HTSC\\CALENDAR_CHINA_STOCK_DAILY_HTSC_2019new.h5' if h5_path==None else h5_path
    forward_date = (dt.datetime.now()+dt.timedelta(days=1000)).strftime("%Y-%m-%d")
    dat = w.tdays('1991-01-01',forward_date,'')
    calendar_df = pd.DataFrame([dat.Data[0],len(dat.Data[0])*['CHINA'],[1]*len(dat.Data[0])],index=['dt','Ticker','calendar']).T
    calendar_df.calendar = calendar_df.calendar.astype(int)
    calendar_df = calendar_df.set_index(['dt','Ticker'])
    IO.pd_hdf5_writer(calendar_df,h5_path,'china_stock_tradingDay')
    return None

def init_SHSC_trading_day(h5_path=None):
    h5_path = 'Z:\\warehouse\\prod\\CALENDAR\\SHSC_TD.h5' if h5_path==None else h5_path
    forward_date = (dt.datetime.now()+dt.timedelta(days=1000)).strftime("%Y-%m-%d")
    dat = w.tdays('1991-01-01',forward_date,'TradingCalendar=HKEX')
    calendar_df = pd.DataFrame([dat.Data[0],len(dat.Data[0])*['HONGKONG'],[1]*len(dat.Data[0])],index=['dt','Ticker','calendar']).T
    calendar_df.calendar = calendar_df.calendar.astype(int)
    calendar_df = calendar_df.set_index(['dt','Ticker'])
    IO.pd_hdf5_writer(calendar_df,h5_path,'hongkong_stock_tradingDay')
    return None

def init_US_trading_day(h5_path=None):
    h5_path = 'Z:\\warehouse\\prod\\CALENDAR\\US_TD.h5' if h5_path==None else h5_path
    forward_date = (dt.datetime.now()+dt.timedelta(days=1000)).strftime("%Y-%m-%d")
    dat = w.tdays('1991-01-01',forward_date,'TradingCalendar=NYSE')
    calendar_df = pd.DataFrame([dat.Data[0],len(dat.Data[0])*['USA'],[1]*len(dat.Data[0])],index=['dt','Ticker','calendar']).T
    calendar_df.calendar = calendar_df.calendar.astype(int)
    calendar_df = calendar_df.set_index(['dt','Ticker'])
    IO.pd_hdf5_writer(calendar_df,h5_path,'us_stock_tradingDay')
    return None

def init_nature_day(h5_path=None):
    h5_path = 'Z:\\warehouse\\prod\\CALENDAR\\nature_days.h5' if h5_path==None else h5_path
    forward_date = (dt.datetime.now()+dt.timedelta(days=1000)).strftime("%Y-%m-%d")
    dat = w.tdays('1991-01-01',forward_date,'Days=Alldays')
    calendar_df = pd.DataFrame([dat.Data[0],len(dat.Data[0])*['ALLDAYS'],[1]*len(dat.Data[0])],index=['dt','Ticker','calendar']).T
    calendar_df.calendar = calendar_df.calendar.astype(int)
    calendar_df = calendar_df.set_index(['dt','Ticker'])
    IO.pd_hdf5_writer(calendar_df,h5_path,'all_days')
    return None

init_nature_day()
