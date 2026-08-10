import os
import datetime
import platform

# global variable
trade_start_time = datetime.time(9, 15)
trade_mid_time = datetime.time(14, 0)
trade_stop_time = datetime.time(14, 49)

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
min_data_richness_threshold = 0.0

spot_list = ['000300.SH','000905.SH','000016.SH','000906.SH']
weight_universe = ['index_weight_hs300', 'index_weight_sh50', 'index_weight_zz500']
minute_to_daily_rule = {'open':'first','high':'max','low':'min','close':'last','volume':'sum','amount':'sum'}

price_per_point = {'IC.CFE':200, 'IF.CFE':300, 'IH.CFE':300}
account_number = {'IC': 5161001, 'IF': 5160501, 'IH': 5162003}

if platform.system() == 'Windows':
    trade_root = r'X:\trade\overnight'
elif platform.system() == 'Linux':
    trade_root = '/data/group/800466/trade/overnight'
    arch0_root = '/arch0/group/800466/trade/overnight'
    private_root = '/data/user/012245/warehouse/prod'
    public_root = '/data/group/800080/warehouse'
    futures_contract_info_path = '/data/user/012245/warehouse/prod/ETC/CHINA_FUTURES/WIND/futures_info.h5'
    minute_data_root = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/'
    gc_hispath = '/data/group/800466/warehouse/prod/MD/CHINA_RATES/MINUTE/CHINA_RATES_MINUTE.h5'
    public_root_prod = os.path.join(public_root, 'prod')
    hisdata_path = os.path.join(trade_root, 'history_arch0')
    hisfactor_path = os.path.join(trade_root, 'factor_proof')
    flag_path = os.path.join(trade_root, 'flag')
    futures_data_path = os.path.join(minute_data_root, 'MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5')
    spot_data_path = os.path.join(public_root, 'prod', 'LOCAL_DATA', 'CSV', 'WIND', 'MINUTE', 'index')
    alla_eod_path =  os.path.join(public_root, 'test', 'DATABASE', 'WIND', 'AShareEODPrices', 'AShareEODPrices.h5')
    stock_minute_per_date_path = os.path.join(public_root, 'prod/LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate/')
    trading_plan_path = os.path.join(trade_root, 'plan')
    json_path = os.path.join(trade_root, 'code', 'overnight')
    stock_close_multitime_path = os.path.join(trade_root, 'cache', 'stock_close_multitime.h5')
    universe_root = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5'
else:
    raise AssertionError


TRADING_PLAN = {
    "trade_seconds": 300,
    "total_money_limit": 66666666.666666664, 
    "init_money": 133333333.33333333, 
    "max_num_per_contract": 120,
    "future_ic": ["wsc10_overnight_future", "wsc25_overnight_cfg", "CC_12_CC", "wsc_limit_24",
                  "wsc21_overnight_index_if", "wsc_pv_7", "ICIF4_CC_IF", "CC_2_CC", "wsc_limit_9",
                  "wsc28_overnight_cfg", "wsc_pv_1", "GC001_corr_CC", "wyc_if_2hour_return_nr_as_cfg",
                  "wsc_factor_settlement", "wsc_limit_13", "wsc_limit_29", "IFIC4_CC", "wsc_return_comparison",
                  "wsc_pv_9", "wsc35_overnight_index_if", "wsc_limit_6", "wsc40_overnight_cfg",
                  "wsc11_overnight_future", "CC_4_CC", "MALS_CC", "CC_12_if_CC"],
    "future_if": ["wsc_limit_9", "wsc_pv_7", "wsc_limit_24", "CC_12_CC", "wsc10_overnight_future",
                  "wsc25_overnight_cfg", "ICIF4_CC_IF", "wsc11_overnight_future", "GC001_corr_CC", "wsc_limit_13",
                  "IFIC4_CC", "wsc28_overnight_cfg", "wsc_return_comparison", "wsc21_overnight_index_if", "wsc_pv_1",
                  "wsc35_overnight_index_if", "wsc_pv_9", "CC_2_CC", "wsc40_overnight_cfg", "wsc_factor_settlement",
                  "MALS_CC", "wsc_limit_29", "wsc_limit_23", "wsc_limit_6", "wyc_if_2hour_return_nr_as_cfg",
                  "wsc13_overnight_future"],
    "future_ih": ["wsc_pv_7", "wsc_limit_24", "CC_12_CC", "wsc10_overnight_future", "wsc28_overnight_cfg", "IFIC4_CC",
                  "wsc_return_comparison", "wsc11_overnight_future", "wsc25_overnight_cfg", "wsc21_overnight_index_if",
                  "wsc_limit_9", "wsc_limit_29", "ICIF4_CC_IF", "wsc_limit_13", "GC001_corr_CC",
                  "wsc13_overnight_future", "MALS_CC", "wsc_factor_settlement", "wsc_limit_23", "wsc40_overnight_cfg",
                  "wsc_pv_9", "wsc_pv_1", "wsc35_overnight_index_if", "wsc17_overnight_cfg", "CC_12_if_CC"],
    "spot_ic": ["wsc10_overnight_future", "wsc25_overnight_cfg", "CC_12_CC", "wsc_limit_24", "CC_2_CC",
                "wsc21_overnight_index_if", "wsc_return_comparison", "wyc_if_2hour_return_nr_as_cfg", "GC001_corr_CC",
                "wsc_limit_29", "wsc_pv_7", "wsc_pv_1", "ICIF4_CC_IF", "wsc28_overnight_cfg", "wsc18_overnight_cfg",
                "wsc13_overnight_future", "IFIC4_CC"],
    "spot_if": ["wsc_limit_9", "wsc10_overnight_future", "wsc_limit_24", "CC_12_CC", "wsc25_overnight_cfg",
                "wsc_return_comparison", "wsc_pv_7", "wsc_limit_29", "GC001_corr_CC", "wsc28_overnight_cfg", "IFIC4_CC",
                "wsc13_overnight_future", "wsc40_overnight_cfg", "wsc11_overnight_future", "wsc_pv_1", "CC_2_CC",
                "wyc_if_2hour_return_nr_as_cfg", "wsc_limit_13", "CC_12_if_CC", "MALS_CC", "wsc_pv_9",
                "wsc21_overnight_index_if", "wsc18_overnight_cfg", "wsc_limit_23"],
    "spot_ih": ["wsc_pv_7", "wsc_limit_24", "wsc_return_comparison", "wsc10_overnight_future", "CC_12_CC",
                "wsc28_overnight_cfg", "IFIC4_CC", "GC001_corr_CC", "wsc_limit_29", "wsc25_overnight_cfg",
                "wsc11_overnight_future", "wsc13_overnight_future", "wsc_limit_23", "MALS_CC", "wsc_pv_1",
                "wsc40_overnight_cfg", "CC_12_if_CC", "wsc21_overnight_index_if", "wsc_limit_13",
                "wsc_factor_settlement", "wsc_limit_6"],
    "Diamond_1_0": ["CC_12_CC", "CC_12_if_CC", "CC_13_if_CC", "CC_2_CC", "CC_4_CC", "CC_7_CC",
                    "CloseVoltoMean_ICIF_CC_IF", "ICIF4_CC_IF", "IFIC4_CC", "wsc_factor_settlement",
                    "wsc10_overnight_future", "wsc11_overnight_future", "wsc13_overnight_future",
                    "wsc16_overnight_cfg_if", "wsc17_overnight_cfg", "wsc18_overnight_cfg", "wsc21_overnight_index_if",
                    "wsc25_overnight_cfg", "wsc28_overnight_cfg", "wsc38_overnight_cfg", "wsc40_overnight_cfg",
                    "wsc4_spot_kpz_if", "wsc_return_comparison", "wyc_if_2hour_return_nr_as_cfg",
                    "wsc35_overnight_index_if"],
    "Diamond_3_0": ["CC_12_CC", "CC_12_if_CC", "CC_27_CC", "CC_31_CC", "CC_33_CC", "CC_7_CC",
                    "CloseVoltoMean_ICIF_CC_IF", "GC001_6_CC", "GC001_Adiff_CC", "GC001_corr_CC", "ICIF4_CC_IF",
                    "IFIC4_CC", "wsc10_overnight_future", "wsc11_overnight_future", "wsc16_overnight_cfg_if",
                    "wsc18_overnight_cfg", "wsc25_overnight_cfg", "wsc28_overnight_cfg", "wsc40_overnight_cfg",
                    "wsc41_overnight_index_rule", "wsc42_overnight_index_rule", "wsc43_overnight_index",
                    "wsc_factor_settlement", "wsc_limit_15", "wsc_limit_22", "wsc_limit_23", "wsc_limit_24",
                    "wsc_limit_27", "wsc_limit_28", "wsc_limit_29", "wsc_limit_30", "wsc_limit_31", "wsc_limit_32",
                    "wsc_limit_35", "wsc_limit_36", "wsc_limit_39_rule", "wsc_limit_4", "wsc_limit_40_rule",
                    "wsc_limit_41_rule", "wsc_limit_5", "wsc_limit_7", "wsc_pv_1", "wsc_pv_13", "wsc_pv_15",
                    "wsc_pv_18", "wsc_pv_19", "wsc_pv_2", "wsc_pv_20_if", "wsc_pv_21_if", "wsc_pv_5", "wsc_pv_6",
                    "wsc_pv_7", "wsc_return_comparison", "wsc_search3_if", "wyc_on31_DownBarNumPm_spot"],
    "future_ic_2_1": ["wsc10_overnight_future", "CC_33_CC", "wsc25_overnight_cfg", "wsc_limit_36", "wsc_pv_7",
                      "CC_2_CC", "ICIF4_CC_IF", "wsc_pv_9", "GC001_corr_CC", "wsc_limit_41_rule", "CC_12_CC",
                      "wsc21_overnight_index_if", "wsc_limit_24", "wsc_limit_9", "wsc28_overnight_cfg",
                      "wsc_return_comparison", "wsc_limit_29", "CC_4_CC", "wyc_if_2hour_return_nr_as_cfg",
                      "wsc_factor_settlement", "wsc_limit_6", "wsc35_overnight_index_if", "wsc_limit_31",
                      "wsc18_overnight_cfg", "wsc40_overnight_cfg", "wsc_limit_30", "wsc_pv_2", "wsc_limit_23",
                      "CC_12_if_CC"],
    "future_if_2_1": ["wsc10_overnight_future", "wsc_pv_7", "CC_33_CC", "wsc_limit_36", "wsc_limit_30", "ICIF4_CC_IF",
                      "wsc_limit_24", "GC001_corr_CC", "wsc25_overnight_cfg", "CC_12_CC", "wsc_limit_9", "wsc_pv_9",
                      "wsc_return_comparison", "wsc_factor_settlement", "wsc_limit_29", "wsc28_overnight_cfg",
                      "CC_2_CC", "wsc35_overnight_index_if", "wsc21_overnight_index_if", "wsc_limit_41_rule",
                      "wsc_limit_31", "wsc_limit_6", "wsc17_overnight_cfg", "wsc_limit_23", "CC_12_if_CC", "CC_4_CC"],
    "future_ih_2_1": ["wsc_pv_7", "wsc10_overnight_future", "wsc_limit_36", "CC_33_CC", "ICIF4_CC_IF", "wsc_limit_30",
                      "wsc_limit_24", "CC_12_CC", "GC001_corr_CC", "wsc28_overnight_cfg", "wsc_return_comparison",
                      "wsc13_overnight_future", "wsc_limit_41_rule", "wsc21_overnight_index_if", "wsc25_overnight_cfg",
                      "wsc_factor_settlement", "wsc_limit_29", "wsc_pv_9", "wsc_limit_23", "CC_2_CC",
                      "wsc40_overnight_cfg", "wsc_limit_9", "wsc17_overnight_cfg"],
    "spot_ic_2_1": ["wsc10_overnight_future", "wsc25_overnight_cfg", "CC_12_CC", "wsc_limit_24", "CC_2_CC", "CC_33_CC",
                    "wsc_limit_41_rule", "wsc_return_comparison", "GC001_corr_CC", "wsc21_overnight_index_if",
                    "wsc_limit_29", "wyc_if_2hour_return_nr_as_cfg", "wsc13_overnight_future", "wsc28_overnight_cfg",
                    "wsc18_overnight_cfg", "wsc_pv_7", "wsc_limit_31", "wsc_limit_36", "ICIF4_CC_IF"],
    "spot_if_2_1": ["wsc10_overnight_future", "wsc_limit_24", "CC_12_CC", "wsc_limit_41_rule", "wsc_return_comparison",
                    "wsc_pv_7", "wsc25_overnight_cfg", "CC_33_CC", "GC001_corr_CC", "wsc13_overnight_future",
                    "wsc_limit_36", "wsc_limit_30", "CC_2_CC", "wyc_if_2hour_return_nr_as_cfg", "wsc_limit_29",
                    "wsc28_overnight_cfg", "ICIF4_CC_IF", "wsc_limit_6", "CC_12_if_CC", "wsc40_overnight_cfg",
                    "wsc21_overnight_index_if"],
    "spot_ih_2_1": ["wsc_pv_7", "wsc10_overnight_future", "wsc_limit_24", "CC_12_CC", "wsc_limit_41_rule",
                    "wsc_return_comparison", "wsc_limit_36", "wsc28_overnight_cfg", "GC001_corr_CC",
                    "wsc13_overnight_future", "CC_33_CC", "wsc_limit_30", "ICIF4_CC_IF", "wsc_limit_29",
                    "wsc25_overnight_cfg", "CC_12_if_CC", "wsc21_overnight_index_if", "wsc_limit_6",
                    "wsc_factor_settlement", "wsc_limit_23", "wsc40_overnight_cfg"],
    "Diamond_2_2": ["CC_12_CC", "CC_12_if_CC", "CC_2_CC", "CC_4_CC", "GC001_corr_CC", "ICIF4_CC_IF",
                    "wsc10_overnight_future", "wsc11_overnight_future", "wsc13_overnight_future", "wsc17_overnight_cfg",
                    "wsc18_overnight_cfg", "wsc21_overnight_index_if", "wsc25_overnight_cfg", "wsc28_overnight_cfg",
                    "wsc35_overnight_index_if", "wsc40_overnight_cfg", "wsc_factor_settlement", "wsc_limit_23",
                    "wsc_limit_24", "wsc_limit_29", "wsc_limit_6", "wsc_limit_9", "wsc_pv_1", "wsc_pv_7", "wsc_pv_9",
                    "wyc_if_2hour_return_nr_as_cfg", "CC_7_CC", "wsc16_overnight_cfg_if", "wsc38_overnight_cfg",
                    "wsc_pv_2"],
    "Diamond_2_3": ["CC_12_CC", "CC_12_if_CC", "CC_2_CC", "CC_4_CC", "GC001_corr_CC", "ICIF4_CC_IF",
                    "wsc10_overnight_future", "wsc11_overnight_future", "wsc13_overnight_future", "wsc17_overnight_cfg",
                    "wsc18_overnight_cfg", "wsc21_overnight_index_if", "wsc25_overnight_cfg", "wsc28_overnight_cfg",
                    "wsc35_overnight_index_if", "wsc40_overnight_cfg", "wsc_factor_settlement", "wsc_limit_23",
                    "wsc_limit_24", "wsc_limit_29", "wsc_limit_6", "wsc_limit_9", "wsc_pv_1", "wsc_pv_7", "wsc_pv_9",
                    "wyc_if_2hour_return_nr_as_cfg", "CC_7_CC", "wsc16_overnight_cfg_if", "wsc38_overnight_cfg",
                    "wsc_pv_2", "wsc_pv_29", "CC_33_CC"],
    "Diamond_2_3_1429": ["wsc_limit_31_no_st", "wsc_limit_39_rule_no_st", "wsc_limit_41_rule_no_st", "CC_33_CC",
                         "wsc25_overnight_cfg", "wsc_pv_29", "wsc41_overnight_index_rule", "wsc_limit_9_no_st",
                         "wsc_limit_30_no_st", "wsc_pv_30_icif", "wyc_if_2hour_return_nr_as_cfg", "wsc_pv_13",
                         "CC_27_CC", "wsc_limit_22_no_st", "GC001_corr_CC", "wsc10_overnight_future",
                         "wsc_factor_settlement", "wsc_pv_32", "wsc_pv_36_if", "wsc_pv_31_icif", "GC001_Adiff_CC",
                         "wsc40_overnight_cfg", "wsc11_overnight_future", "wyc_on31_DownBarNumPm_spot", "CC_12_if_CC",
                         "wsc_pv_7", "CC_12_CC", "wsc28_overnight_cfg"], 
    "init_money_1429": 70000000,
    "total_money_limit_1429": 35000000}
