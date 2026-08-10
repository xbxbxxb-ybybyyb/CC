import pandas as pd
import numpy as np
from multifactor.IO import IO
import datetime
import os

future_universe_path = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/UNIV/CHINA_COMMODITY_MAIN_SECONDMAIN_PERDAY.h5'

def get_universe_contract(variety = 'IC', instrument_type = 'main', date = None):
    assert instrument_type in ['main'], 'instrument type must be in [main, recent]'
    col_dict = {'main':'contract_main'}
    col_name = col_dict[instrument_type]
    univ = IO.read_data([date],columns=[col_name], alt = future_universe_path)
    if len(univ) == 0:
        print('the date maybe is not trading day')
        raise Exception
    return univ.xs('%s' % variety, level = 1)[col_name][0]

def select_data_by_univ(data = None, variety = 'IC', instrument_type = 'main'):
    assert isinstance(data.index, pd.MultiIndex)
    assert instrument_type in ['main'], 'instrument type must be in [main]'
    
    col_dict = {'main':'contract_main', 'recent':'contract_00'}
    col_name = col_dict[instrument_type]

    data['date'] = data.index.get_level_values(0).date
    datelist = data.date.tolist()
    sdate = str(datelist[0]).replace('-','')
    edate = str(datelist[-1]).replace('-','')
    univ = IO.read_data([sdate, edate],columns=[col_name], alt = future_universe_path).xs('%s.CFE'%variety, level = 1)
    univ = univ.reset_index().rename(columns = {'dt':'date',col_name:'Ticker'}).set_index(['date','Ticker'])

    data = data.reset_index().set_index(['date','Ticker'])
    data = data.join(univ, how = 'inner').reset_index().drop(['date'], axis = 1).set_index(['dt','Ticker']).sort_index()
    return data