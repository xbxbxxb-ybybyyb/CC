from xquant.futuredata import FutureData
from multifactor.IO import IO
import numpy as np
import pandas as pd
import sys
from function_tools import get_trading_days
from multiprocessing import Pool
from xquant.compute.aimr import AIMR


FILE_PATH = '/data/user/015615/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5'
VARIETY_LIST = ['IC','IF','IH','T']

def get_universe_contract_info_by_date(date):

    fd = FutureData()
    data_list = []

    print('Start acquiring contract info on {}'.format(date))

    for i in VARIETY_LIST:
        instrument_dict = dict()
        instrument_dict['Ticker'] = i + '.CFE'
        instrument_dict['contract_00'] = sorted(fd.get_instrument_all(i, date, date))[0] + 'E'
        instrument_dict['contract_main'] = fd.get_change_date(i, date, 'ZL00')[0] + 'E'
        instrument_dict['wind_main'] = 'Nan'
        data_list.append(instrument_dict)

    df_date = pd.DataFrame.from_dict(data_list)
    df_date['dt'] = pd.to_datetime(date)

    return df_date.set_index(['dt', 'Ticker'])


if __name__ == '__main__':
    args = AIMR.getParam().split(',')
    # start_date = sys.argv[1]
    # end_date = sys.argv[2]
    start_date,end_date = args

    date_list = get_trading_days(start_date, end_date)

    tasks = []
    data_list = []

    with Pool(20) as pool:

        for date in date_list:
            tasks.append(pool.apply_async(get_universe_contract_info_by_date,args=(date,)))
        
        for t in tasks:
            data_list.append(t.get())

    df_data = pd.concat(data_list).sort_index()

    IO.pd_hdf5_writer(df_data, FILE_PATH, dataset='universe', append=True)

    print('All universe contract info is updated!')