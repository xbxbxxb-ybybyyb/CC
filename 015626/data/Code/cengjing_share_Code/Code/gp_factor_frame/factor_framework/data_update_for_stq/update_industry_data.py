import pandas as pd
import numpy as np
import os
import sys
from multiprocessing import Pool
from function_tools import get_trading_days
from xquant.thirdpartydata.marketdata import MarketData
from xquant.compute.aimr import AIMR
from multifactor.IO import IO

ROOT_PATH = '/data/user/015615/MarketData/MD/CHINA_INDUSTRY/MINUTE'

def resample_industry_data_by_date(symbol, date, freq='1T'):
    ma = MarketData()

    STR_START = '090000'
    STR_END = '153000'
    STR_AM_START = '093000'
    STR_AM_END = '112900'
    STR_PM_START = '130000'
    STR_PM_END = '145600'

    df_raw = ma.getMDSecurityTickDataFrame(symbol,'{}{}'.format(date,STR_START),'{}{}'.format(date,STR_END),0)
    df_raw['dt'] = pd.to_datetime(df_raw[['MDDate', 'MDTime']].apply(lambda x: x[0] + x[1], axis=1), format='%Y%m%d%H%M%S%f')

    df_industry_tick = df_raw.set_index('dt')
    old_columns = ['PreClosePx', 'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'OpenPx', 'HighPx', 'LowPx']
    df_industry_tick = df_industry_tick[old_columns]

    df_industry_tick['volume'] = df_industry_tick['TotalVolumeTrade'].diff()
    df_industry_tick['amount'] = df_industry_tick['TotalValueTrade'].diff()
    df_industry_tick['close'] = df_industry_tick['LastPx']
    df_industry_tick['TodayHigh'] = df_industry_tick['HighPx']
    df_industry_tick['TodayOpen'] = df_industry_tick['OpenPx']
    df_industry_tick['TodayLow'] = df_industry_tick['LowPx']
    df_industry_tick['open'] = df_industry_tick['LastPx']
    df_industry_tick['high'] = df_industry_tick['LastPx']
    df_industry_tick['low'] = df_industry_tick['LastPx']

    how_dict = {'volume': 'sum', 'amount': 'sum', 'close': 'last', 'TodayHigh': 'last', 'TodayOpen': 'last',
                'TodayLow': 'last', 'open': 'first', 'high': 'max',
                'low': 'min', 'TotalVolumeTrade': 'last', 'TotalValueTrade': 'last'}

    df_minute_data = df_industry_tick.resample(rule=freq, closed='left', label='left', how=how_dict)
    df_minute_data[['volume', 'amount']] = df_minute_data[['volume', 'amount']].fillna(0)
    df_minute_data = df_minute_data.fillna(method='ffill')

    dt_am_start = pd.to_datetime('{}{}'.format(date,STR_AM_START), format='%Y%m%d%H%M%S')
    dt_am_end = pd.to_datetime('{}{}'.format(date,STR_AM_END), format='%Y%m%d%H%M%S')
    dt_pm_start = pd.to_datetime('{}{}'.format(date,STR_PM_START), format='%Y%m%d%H%M%S')
    dt_pm_end = pd.to_datetime('{}{}'.format(date,STR_PM_END), format='%Y%m%d%H%M%S')

    df_result = df_minute_data.loc[dt_am_start:dt_am_end].append(df_minute_data.loc[dt_pm_start:dt_pm_end])
    df_result['Ticker'] = symbol

    return df_result

def check_folder(path):
    if not os.path.exists(path) or (not os.path.isdir(path)):
        os.mkdir(path)

def save_dataframe(df_input, symbol, date):
    folder_path = '{}/{}'.format(ROOT_PATH, symbol)
    check_folder(folder_path)

    df_input.to_csv('{}/{}.csv'.format(folder_path,date))
    print('{}_{} is saved!'.format(symbol, date))


if __name__ == '__main__':
    args = AIMR.getParam().split(',')
    # start_date = sys.argv[1]
    # end_date = sys.argv[2]
    start_date,end_date = args

    trading_days = get_trading_days(start_date,end_date)
    symbol_list = ['000928.SH','000929.SH','000930.SH','000931.SH','000932.SH','000933.SH','000934.SH','000935.SH',
                   '000936.SH','000937.SH']

    tasks = []

    # df_temp = resample_industry_data_by_date('000928.SH','20160104')
    # save_dataframe(df_temp,'000928.SH','20160104')
    with Pool(20) as pool:
        for symbol in symbol_list:
            for date in trading_days:
                print(symbol, date)
                tasks.append([pool.apply_async(resample_industry_data_by_date,args=(symbol,date,'1T')),symbol,date])

        for task,symbol,date in tasks:
            try:
                save_dataframe(task.get(),symbol,date)
            except:
                print('Error on {}_{}!'.format(symbol, date))



    for symbol in symbol_list:
        data_list = []
        for date in trading_days:
            try:
                data_list.append(pd.read_csv('{}/{}/{}.csv'.format(ROOT_PATH,symbol,date)))
            except:
                pass
        df_all = pd.concat(data_list)
        df_all['dt'] = pd.to_datetime(df_all['dt'])
        df_all = df_all.set_index(['dt','Ticker'])

        IO.pd_hdf5_writer(df_all,'{}/{}.h5'.format(ROOT_PATH,symbol),dataset=symbol,append=True)

