from overnight.naming_config import *
from overnight.utility import diller
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as tdt
import time
import pandas as pd
import numpy as np
import os
import sys
from WindPy import w

w.start()


def get_edb_api_data(indicator, start_date, end_date):
    if isinstance(indicator, list):
        indicator = ','.join(indicator)
    data = w.edb(indicator, IO.str_date_parser(start_date).strftime('%Y%m%d'),
                            IO.str_date_parser(end_date).strftime('%Y%m%d'))
    if data.Data != []:
        return pd.DataFrame(np.array(data.Data).T, index=pd.to_datetime(data.Times), columns=data.Codes)
    else:
        raise ConnectionError


def retrieve_futures_codes_helper():
    date = pd.Timestamp.now().strftime('%Y%m%d')
    cfe = 'a599010101000000'
    shf = 'a599010201000000'
    dce = 'a599010301000000'
    czc = 'a599010401000000'
    exchanges = [cfe, shf, dce, czc]
    code_list = []
    for ec in exchanges:
        try:
            data = w.wset("sectorconstituent", "date="+date+";sectorid="+ec+";field=date,wind_code,sec_name")
            data = pd.DataFrame(data.Data, index=data.Fields).T
            data=data[data['sec_name'].apply(lambda x: "仿真" not in x)]
            code_list.extend(data['wind_code'].tolist())
        except:
            continue
    assert len(code_list) != 0, 'No codes retrieved'
    out_path = os.path.join(trade_root, 'hot', date, 'futures_codes.pkl')
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    diller(out_path, code_list)
    return code_list


def retrieve_edb_helper(last_num_days=20):
    today = pd.Timestamp.now().strftime('%Y%m%d')
    end_date = IO.str_date_parser(today)
    start_date = tdt.get_trading_day_offset(end_date, -last_num_days)[0]
    AUDUSD = get_edb_api_data('M0000199', start_date, end_date).iloc[:, 0]
    USDJPY = get_edb_api_data('M0000204', start_date, end_date).iloc[:, 0]
    SHIBOR = get_edb_api_data('M0017138', start_date, end_date).iloc[:, 0]
    assert end_date in SHIBOR.index and end_date not in AUDUSD.index and end_date not in USDJPY.index
    AUDUSD.loc[end_date] = np.nan
    USDJPY.loc[end_date] = np.nan
    AUDJPY = (AUDUSD * USDJPY).shift(1)
    AUDJPY.name = 'AUDJPY'
    SHIBOR.name = 'SHIBOR'
    edb_pd = pd.concat([AUDJPY, SHIBOR], axis=1, sort=True).infer_objects()
    out_path = os.path.join(trade_root, 'hot', today, 'edb.h5')
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    edb_pd.to_hdf(out_path, 'edb', mode='w')
    return edb_pd


if __name__ == '__main__':
    retrieve_edb_helper()
    retrieve_futures_codes_helper()

