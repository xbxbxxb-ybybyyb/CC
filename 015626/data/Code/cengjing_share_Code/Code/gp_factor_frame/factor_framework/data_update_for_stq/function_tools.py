import pandas as pd
import numpy as np
from multifactor.IO import IO
import datetime
import os

rootpath = '/data/user/015615/MarketData/MD/'
calendar_path = os.path.join(rootpath,'CALENDAR','CALENDAR_CHINA_STOCK_DAILY_HTSC.pkl')
indexweight_path = os.path.join(rootpath,'UNIVERSE','INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
future_universe_path = os.path.join(rootpath,'UNIVERSE','MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')

def get_trading_days(start_date, end_date):
    return pd.read_pickle(calendar_path).loc[start_date:end_date].trading_days.tolist()

def get_constituent_stock_list(index_type = 'ZZ500', date= None):
    assert index_type in ['ZZ500','HS300','SH50']
    col_dict = {'ZZ500':'index_weight_zz500','HS300':'index_weight_hs300','SH50':'index_weight_sh50'}
    col_name = col_dict[index_type]
    predate = datetime.datetime.strptime(str(date),'%Y%m%d') - datetime.timedelta(15)
    tdayslist = get_trading_days(predate, date)
    assert date == tdayslist[-1], 'target date is not trading day'
    wdf = IO.read_data([tdayslist[-2]],columns=[col_name], alt = indexweight_path)
    stock_list = wdf[wdf[col_name] > 0].index.get_level_values(1).tolist()
    return stock_list

def get_all_stocklist_by_period(variety = 'IC', start_date = '20130101', end_date = '20220101'):
    assert variety in ['IC', 'IF', 'IH']
    col_dict = {'IC': 'index_weight_zz500', 'IF': 'index_weight_hs300', 'IH': 'index_weight_sh50'}
    col_name = col_dict[variety]
    predate = datetime.datetime.strptime(start_date, '%Y%m%d') - datetime.timedelta(15)
    wdf = IO.read_data([predate, end_date], columns=[col_name], alt=indexweight_path)
    stock_list = wdf[wdf[col_name] > 0].index.get_level_values(1).unique().tolist()
    return stock_list

def get_universe_contract(variety = 'IC', instrument_type = 'main', date = None):
    assert variety in ['IC','IF','IH','T'], 'variety must be in [IC, IF, IH, T]'
    assert instrument_type in ['main','recent'], 'instrument type must be in [main, recent]'
    col_dict = {'main':'contract_main', 'recent':'contract_00'}
    col_name = col_dict[instrument_type]
    univ = IO.read_data([date],columns=[col_name], alt = future_universe_path)
    if len(univ) == 0:
        print('the date maybe is not trading day')
        raise Exception
    return univ.xs('%s.CFE' % variety, level = 1)[col_name][0]

def select_data_by_univ(data = None, variety = 'IC', instrument_type = 'main'):
    assert isinstance(data.index, pd.MultiIndex)
    assert variety in ['IC','IF','IH', 'T'], 'variety must be in [IC, IF, IH, T]'
    assert instrument_type in ['main','recent'], 'instrument type must be in [main, recent]'
    
    col_dict = {'main':'contract_main', 'recent':'contract_00'}
    col_name = col_dict[instrument_type]

    data['date'] = data.index.get_level_values(0).date
    datelist = data.date.tolist()
    sdate = str(datelist[0]).replace('-','')
    edate = str(datelist[-1]).replace('-','')
    univ = IO.read_data([sdate, edate],columns=[col_name], alt = future_universe_path).xs('%s.CFE'%variety, level = 1)
    univ = univ.reset_index().rename(columns = {'dt':'date',col_name:'Ticker'}).set_index(['date','Ticker'])

    data = data.reset_index()
    data = data[~data['Ticker'].isna()].set_index(['date','Ticker'])
    data = data.join(univ, how = 'inner').reset_index().drop(['date'], axis = 1).set_index(['dt','Ticker']).sort_index()
    return data