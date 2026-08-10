import os
import datetime
import platform

# global variable
trade_start_time = datetime.time(9, 15)
trade_mid_time = datetime.time(14, 0)
trade_stop_time = datetime.time(14, 29)

calculate_volume_start_time = datetime.time(14, 50)
calculate_volume_stop_time = datetime.time(14, 57)
calculate_volume_histdays = 10
calculate_volume_ratio = 0.08

minute_to_daily_start_time = datetime.time(9, 30)
minute_to_daily_stop_time = trade_stop_time
minute_to_daily_tag = minute_to_daily_start_time.strftime('%H%M') + minute_to_daily_stop_time.strftime('%H%M')

futures_data_morning_begin = datetime.time(9, 30)
futures_data_morning_end = datetime.time(11, 29)
futures_data_afternoon_begin = datetime.time(13, 0)
futures_data_afternoon_end = datetime.time(14, 57)

factor_raw_histdays = 120
data_richness_threshold = 0.95
min_data_richness_threshold = 0.8

spot_list = ['000300.SH','000905.SH','000016.SH','000906.SH']
weight_universe = ['index_weight_hs300', 'index_weight_sh50', 'index_weight_zz500']
minute_to_daily_rule = {'open':'first','high':'max','low':'min','close':'last','volume':'sum','amount':'sum'}

account_number = {'IC': 5161001, 'IF': 5160501, 'IH': 5162003}
security_account = '00000004'
afternoon_trade_direction = 'buy_open'
morning_trade_direction = 'sell_close'
afternoon_system_start_time = datetime.time(14,54)
afternoon_system_end_time = datetime.time(14,59)
morning_system_start_time = datetime.time(9,30)
morning_system_end_time = datetime.time(9,35)
num_per_order = 1
max_contracts_total = 500
max_contracts_perseconds = 50
min_order_interval = 3



if platform.system() == 'Windows':
    trade_root = r'X:\trade\overnight'
elif platform.system() == 'Linux':
    trade_root = '/data/group/800466/trade/overnight'
    private_root = '/data/user/012245/warehouse/prod'
    public_root = '/data/group/800080/warehouse'
    futures_contract_info_path = '/data/user/012245/warehouse/prod/ETC/CHINA_FUTURES/WIND/futures_info.h5'
    minute_data_root = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/'
    gc_hispath = '/data/group/800466/warehouse/prod/MD/CHINA_RATES/MINUTE/CHINA_RATES_MINUTE.h5'
    public_root_prod = os.path.join(public_root, 'prod')
    hisdata_path = os.path.join(trade_root, 'history')
    hisfactor_path = os.path.join(trade_root, 'factor')
    flag_path = os.path.join(trade_root, 'flag')
    futures_data_path = os.path.join(minute_data_root, 'MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5')
    spot_data_path = os.path.join(public_root, 'prod', 'LOCAL_DATA', 'CSV', 'WIND', 'MINUTE', 'index')
    alla_eod_path =  os.path.join(public_root, 'test', 'DATABASE', 'WIND', 'AShareEODPrices', 'AShareEODPrices.h5')
    stock_minute_per_date_path = os.path.join(public_root, 'prod/LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate/')
    trading_plan_path = os.path.join(trade_root, 'plan')
    json_path = os.path.join(trade_root, 'code', 'overnight')
else:
    raise AssertionError


