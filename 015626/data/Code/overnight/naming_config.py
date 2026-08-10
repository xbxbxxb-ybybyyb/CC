import os
import datetime
import platform

# global variable
trade_start_time = datetime.time(9, 15)
trade_mid_time = datetime.time(14, 0)
trade_stop_time = datetime.time(14, 49)

minute_to_daily_start_time = datetime.time(9, 30)
minute_to_daily_stop_time = datetime.time(14, 49)

futures_data_morning_begin = '09:30:00'
futures_data_morning_end = '11:29:00'
futures_data_afternoon_begin = '13:00:00'
futures_data_afternoon_end = '14:57:00'

data_richness_threshold = 0.95
min_data_richness_threshold = 0.8

if platform.system() == 'Windows':
    trade_root = r'X:\trade\overnight'
elif platform.system() == 'Linux':
    trade_root = '/data/group/800466/trade/overnight'
    private_root = '/data/user/012245/warehouse/prod'
    public_root = '/data/group/800080/warehouse'
    futures_contract_info_path = '/data/user/012245/warehouse/prod/ETC/CHINA_FUTURES/WIND/futures_info.h5'
    minute_data_root = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/'
    gc_hispath = '/data/group/800466/warehouse/prod/MD/CHINA_RATES/MINUTE/CHINA_RATES_MINUTE.h5'
else:
    raise AssertionError

public_root_prod = os.path.join(public_root, 'prod')
hisdata_path = os.path.join(trade_root, 'history')
flag_path = os.path.join(trade_root, 'flag')
future_data_path = os.path.join(minute_data_root, 'MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5')
spot_data_path = os.path.join(public_root, 'prod', 'LOCAL_DATA', 'CSV', 'WIND', 'MINUTE', 'index')
alla_eod_path =  os.path.join(public_root, 'test', 'DATABASE', 'WIND', 'AShareEODPrices', 'AShareEODPrices.h5')
stock_minute_per_date_path = os.path.join(public_root, 'prod/LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate/')
factor_raw_save_path = os.path.join(trade_root, 'factor', 'raw')
factor_raw_load_path = os.path.join(trade_root, 'factor', 'history', 'raw')
factor_norm_save_path = os.path.join(trade_root, 'factor', 'norm')

