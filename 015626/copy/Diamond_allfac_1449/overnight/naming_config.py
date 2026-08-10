import os
import platform
import datetime as dt

# global variable
trade_start_time = dt.time(9, 15)
trade_mid_time = dt.time(14, 29)
trade_stop_time = dt.time(14, 49)

calculate_volume_start_time = dt.time(14, 50)
calculate_volume_stop_time = dt.time(14, 57)
calculate_volume_histdays = 10
calculate_volume_ratio = 0.2

minute_to_daily_start_time = dt.time(9, 30)
minute_to_daily_stop_time = trade_stop_time
minute_to_daily_tag = minute_to_daily_start_time.strftime('%H%M') + minute_to_daily_stop_time.strftime('%H%M')

futures_data_morning_begin = dt.time(9, 30)
futures_data_morning_end = dt.time(11, 29)
futures_data_afternoon_begin = dt.time(13, 0)
futures_data_afternoon_end = dt.time(14, 57)

factor_raw_histdays = 120
data_richness_threshold = 0.95
min_data_richness_threshold = 0

spot_list = ['000300.SH','000905.SH','000016.SH','000906.SH']
weight_universe = ['index_weight_hs300', 'index_weight_sh50', 'index_weight_zz500']
minute_to_daily_rule = {'open':'first','high':'max','low':'min','close':'last','volume':'sum','amount':'sum'}

price_per_point = {'IC.CFE':200, 'IF.CFE':300, 'IH.CFE':300}
#account_number_long = {'IC': 5160605, 'IF': 5160605, 'IH': 5160605}
account_number_long = {'IC': 203203, 'IF': 203203, 'IH': 203203}
#account_number_short = {'IC': 5160604, 'IF': 5160604, 'IH': 5160604}
#account_number_long = {'IC': 5160501, 'IF': 5160501, 'IH': 5160501}
# account_number_short = {'IC': 5160703, 'IF': 5160703, 'IH': 5160703}
account_number_short = {'IC': 203203, 'IF': 203203, 'IH': 203203}
#security_account = '00000004'
security_account = '00060160'
#afternoon_trade_direction_long = {'IC': 'buy_close', 'IF': 'buy_close', 'IH': 'buy_open'}
#morning_trade_direction_long = {'IC': 'sell_close', 'IF': 'sell_close', 'IH': 'sell_close'}
#afternoon_trade_direction_short = {'IC': 'sell_close', 'IF': 'sell_close', 'IH': 'sell_open'}
#morning_trade_direction_short = {'IC': 'buy_close', 'IF': 'buy_close', 'IH': 'buy_close'}
afternoon_trade_direction_long = {'IC': 'buy_open', 'IF': 'buy_open', 'IH': 'buy_open'}
morning_trade_direction_long = {'IC': 'sell_close', 'IF': 'sell_close', 'IH': 'sell_close'}
afternoon_trade_direction_short = {'IC': 'sell_open', 'IF': 'sell_open', 'IH': 'sell_open'}
morning_trade_direction_short = {'IC': 'buy_close', 'IF': 'buy_close', 'IH': 'buy_close'}
afternoon_system_start_time = dt.time(14,49)
afternoon_system_end_time = dt.time(14,59,30)
morning_system_start_time = dt.time(9,30)
morning_system_end_time = dt.time(9,39)
num_per_order = 1
max_contracts_total = 500
max_contracts_perseconds = 50
min_order_interval = 1
max_order_num = 600
max_withd_num = 300
max_withd_cancel_num = 100
max_order_num_past_1min = 120
max_withd_num_past_1min = 120
max_cancellation_num = 300

if platform.system() == 'Windows':
    trade_root = r'X:\trade\overnight'
elif platform.system() == 'Linux':
    trade_root = '/dfs/group/800466/trade/overnight'
    public_root = '/data/group/800080/warehouse'
    futures_contract_info_path = '/data/user/012245/warehouse/prod/ETC/CHINA_FUTURES/WIND/futures_info.h5'
    minute_data_root = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/'
    gc_hispath = '/data/group/800466/warehouse/prod/MD/CHINA_RATES/MINUTE/CHINA_RATES_MINUTE.h5'
    public_root_prod = os.path.join(public_root, 'prod')
    hisdata_path = os.path.join(trade_root, 'history')
    hotdata_path = os.path.join(trade_root, 'hot')
    factor_path = os.path.join(trade_root, 'factor')
    hisfactor_path = os.path.join(trade_root, 'factor_proof')
    flag_path = os.path.join(trade_root, 'flag')
    futures_data_path = os.path.join(minute_data_root, 'MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5')
    spot_data_path = os.path.join(public_root, 'prod', 'LOCAL_DATA', 'CSV', 'WIND', 'MINUTE', 'index')
    alla_eod_path =  os.path.join(public_root, 'test', 'DATABASE', 'WIND', 'AShareEODPrices', 'AShareEODPrices.h5')
    stock_minute_per_date_path = os.path.join(public_root, 'prod/LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate/')
    trading_plan_path = os.path.join(trade_root, 'plan')
    stock_close_multitime_path = os.path.join(trade_root, 'cache', 'stock_close_multitime.h5')
    log_path = os.path.join(trade_root, 'log')
    universe_root = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5'
else:
    raise AssertionError

# trading key parm
amp_threshold = 0.003
long_threshold = 0.159
short_threshold = 0.04
low_amp_long_threshold = 0.2

# strategy and money
trading_version_1 = 'Diamond_1_0'
# 振幅下界，振幅上界，资金
init_money_1_vals = [
        (0,     0.003, 4e8/3),
        (0.003, 0.004, 7e8/3),
        (0.004, 1,     10e8/3)]

trading_version_2 = 'Diamond_4_0'
init_money_2_vals = [
        (0,     0.003, 5e8/3),
        (0.003, 0.004, 5e8/3),
        (0.004, 1,     5e8/3)]

total_money_limit_vals = [
        (0,     0.003, 2e8/3),
        (0.003, 0.004, 4e8/3),
        (0.004, 1,     7e8/3)]

trading_version_3 = 'Diamond_volsig'
init_money_3 = 0.6e8/3
# 加上volsig后总仓位不得超过此值
max_money_3 = 7e8/3

# 最终仓位资金小于此值则不做
least_money = 0.6e8/3

open_short = False
short_money = 1e8/3

getdata_parallel_count = 24

TRADING_PLAN = {
    'trade_seconds': 300, 
    'max_num_per_contract': 120,
    'Diamond_1_0': ['CC_12_CC', 'CC_12_if_CC', 'CC_13_if_CC', 'CC_2_CC', 'CC_4_CC', 'CC_7_CC', 
                    'CloseVoltoMean_ICIF_CC_IF', 'ICIF4_CC_IF', 'IFIC4_CC', 'wsc_factor_settlement', 
                    'wsc10_overnight_future', 'wsc11_overnight_future', 'wsc13_overnight_future', 
                    'wsc16_overnight_cfg_if', 'wsc17_overnight_cfg', 'wsc18_overnight_cfg', 'wsc21_overnight_index_if', 
                    'wsc25_overnight_cfg', 'wsc28_overnight_cfg', 'wsc38_overnight_cfg', 'wsc40_overnight_cfg', 
                    'wsc4_spot_kpz_if', 'wsc_return_comparison', 'wyc_if_2hour_return_nr_as_cfg', 
                    'wsc35_overnight_index_if'], 
    'Diamond_3_0': ['CC_12_CC', 'CC_12_if_CC', 'CC_27_CC', 'CC_31_CC', 'CC_33_CC', 'CC_7_CC', 
                    'CloseVoltoMean_ICIF_CC_IF', 'GC001_6_CC', 'GC001_Adiff_CC', 'GC001_corr_CC', 'ICIF4_CC_IF', 
                    'IFIC4_CC', 'wsc10_overnight_future', 'wsc11_overnight_future', 'wsc16_overnight_cfg_if', 
                    'wsc18_overnight_cfg', 'wsc25_overnight_cfg', 'wsc28_overnight_cfg', 'wsc40_overnight_cfg', 
                    'wsc41_overnight_index_rule', 'wsc42_overnight_index_rule', 'wsc43_overnight_index', 
                    'wsc_factor_settlement', 'wsc_limit_15', 'wsc_limit_22', 'wsc_limit_23', 'wsc_limit_24', 
                    'wsc_limit_27', 'wsc_limit_28', 'wsc_limit_29', 'wsc_limit_30', 'wsc_limit_31', 'wsc_limit_32', 
                    'wsc_limit_35', 'wsc_limit_36', 'wsc_limit_39_rule', 'wsc_limit_4', 'wsc_limit_40_rule', 
                    'wsc_limit_41_rule', 'wsc_limit_5', 'wsc_limit_7', 'wsc_pv_1', 'wsc_pv_13', 'wsc_pv_15', 
                    'wsc_pv_18', 'wsc_pv_19', 'wsc_pv_2', 'wsc_pv_20_if', 'wsc_pv_21_if', 'wsc_pv_5', 'wsc_pv_6', 
                    'wsc_pv_7', 'wsc_return_comparison', 'wsc_search3_if', 'wyc_on31_DownBarNumPm_spot'], 
    'Diamond_2_2': ['CC_12_CC', 'CC_12_if_CC', 'CC_2_CC', 'CC_4_CC', 'GC001_corr_CC', 'ICIF4_CC_IF', 
                    'wsc10_overnight_future', 'wsc11_overnight_future', 'wsc13_overnight_future', 'wsc17_overnight_cfg',
                    'wsc18_overnight_cfg', 'wsc21_overnight_index_if', 'wsc25_overnight_cfg', 'wsc28_overnight_cfg', 
                    'wsc35_overnight_index_if', 'wsc40_overnight_cfg', 'wsc_factor_settlement', 'wsc_limit_23', 
                    'wsc_limit_24', 'wsc_limit_29', 'wsc_limit_6', 'wsc_limit_9', 'wsc_pv_1', 'wsc_pv_7', 'wsc_pv_9', 
                    'wyc_if_2hour_return_nr_as_cfg', 'CC_7_CC', 'wsc16_overnight_cfg_if', 'wsc38_overnight_cfg', 
                    'wsc_pv_2'], 
    'Diamond_2_3': ['CC_12_CC', 'CC_12_if_CC', 'CC_2_CC', 'CC_4_CC', 'GC001_corr_CC', 'ICIF4_CC_IF', 
                    'wsc10_overnight_future', 'wsc11_overnight_future', 'wsc13_overnight_future', 'wsc17_overnight_cfg',
                    'wsc18_overnight_cfg', 'wsc21_overnight_index_if', 'wsc25_overnight_cfg', 'wsc28_overnight_cfg', 
                    'wsc35_overnight_index_if', 'wsc40_overnight_cfg', 'wsc_factor_settlement', 'wsc_limit_23', 
                    'wsc_limit_24', 'wsc_limit_29', 'wsc_limit_6', 'wsc_limit_9', 'wsc_pv_1', 'wsc_pv_7', 'wsc_pv_9', 
                    'wyc_if_2hour_return_nr_as_cfg', 'CC_7_CC', 'wsc16_overnight_cfg_if', 'wsc38_overnight_cfg', 
                    'wsc_pv_2', 'wsc_pv_29', 'CC_33_CC'], 
    'Diamond_4_0': ['CC_11_CC', 'CC_12_CC', 'CC_12_if_CC', 'CC_13_if_CC', 'CC_27_CC', 'CC_28_CC', 'CC_29_CC', 'CC_2_CC', 
                    'CC_31_CC', 'CC_32_CC', 'CC_33_CC', 'CC_33_if_CC', 'CC_4_CC', 'CC_7_CC', 'CloseVoltoMean_ICIF_CC_IF', 
                    'GC001_6_CC', 'GC001_Adiff_CC', 'GC001_corr_CC', 'ICIF4_CC_IF', 'IFIC4_CC', 'MALS_CC', 
                    'wsc10_overnight_future', 'wsc11_overnight_future', 'wsc13_overnight_future', 'wsc16_overnight_cfg_if', 
                    'wsc17_overnight_cfg', 'wsc18_overnight_cfg', 'wsc19_overnight_future', 'wsc21_overnight_index_if', 
                    'wsc25_overnight_cfg', 'wsc28_overnight_cfg', 'wsc2_overnight_hf', 'wsc35_overnight_index_if', 
                    'wsc38_overnight_cfg', 'wsc38_overnight_cfg_alla', 'wsc40_overnight_cfg', 'wsc40_overnight_cfg_alla', 
                    'wsc41_overnight_index_rule', 'wsc42_overnight_index_rule', 'wsc43_overnight_index', 'wsc4_spot_kpz_if', 
                    'wsc6_overnight_hf', 'wsc7_overnight_hf', 'wsc9_overnight_hf', 'wsc_factor_settlement', 'wsc_hf3', 
                    'wsc_limit_1', 'wsc_limit_10', 'wsc_limit_10_no_st', 'wsc_limit_11', 'wsc_limit_11_no_st', 'wsc_limit_12', 
                    'wsc_limit_12_no_st', 'wsc_limit_13', 'wsc_limit_13_no_st', 'wsc_limit_14', 'wsc_limit_14_no_st', 
                    'wsc_limit_15', 'wsc_limit_15_no_st', 'wsc_limit_16', 'wsc_limit_16_no_st', 'wsc_limit_17', 
                    'wsc_limit_17_no_st', 'wsc_limit_18', 'wsc_limit_18_no_st', 'wsc_limit_19', 'wsc_limit_19_no_st', 
                    'wsc_limit_1_no_st', 'wsc_limit_2', 'wsc_limit_20', 'wsc_limit_20_no_st', 'wsc_limit_21', 
                    'wsc_limit_21_no_st', 'wsc_limit_22', 'wsc_limit_22_no_st', 'wsc_limit_23', 'wsc_limit_23_no_st', 
                    'wsc_limit_24', 'wsc_limit_24_no_st', 'wsc_limit_25', 'wsc_limit_25_no_st', 'wsc_limit_26', 
                    'wsc_limit_26_no_st', 'wsc_limit_27', 'wsc_limit_27_no_st', 'wsc_limit_28', 'wsc_limit_28_no_st', 
                    'wsc_limit_29', 'wsc_limit_29_no_st', 'wsc_limit_2_no_st', 'wsc_limit_3', 'wsc_limit_30', 
                    'wsc_limit_30_no_st', 'wsc_limit_31', 'wsc_limit_31_no_st', 'wsc_limit_32', 'wsc_limit_32_no_st', 
                    'wsc_limit_33', 'wsc_limit_33_no_st', 'wsc_limit_34', 'wsc_limit_34_no_st', 'wsc_limit_35', 
                    'wsc_limit_35_no_st', 'wsc_limit_36', 'wsc_limit_36_no_st', 'wsc_limit_39_rule', 'wsc_limit_39_rule_no_st', 
                    'wsc_limit_3_no_st', 'wsc_limit_4', 'wsc_limit_40_rule', 'wsc_limit_40_rule_no_st', 'wsc_limit_41_rule', 
                    'wsc_limit_41_rule_no_st', 'wsc_limit_4_no_st', 'wsc_limit_5', 'wsc_limit_5_no_st', 'wsc_limit_6', 
                    'wsc_limit_6_no_st', 'wsc_limit_7', 'wsc_limit_7_no_st', 'wsc_limit_8', 'wsc_limit_8_no_st', 'wsc_limit_9', 
                    'wsc_limit_9_no_st', 'wsc_pv_1', 'wsc_pv_11', 'wsc_pv_12', 'wsc_pv_13', 'wsc_pv_14', 'wsc_pv_15', 
                    'wsc_pv_16', 'wsc_pv_17', 'wsc_pv_18', 'wsc_pv_19', 'wsc_pv_2', 'wsc_pv_20_if', 'wsc_pv_21_if', 'wsc_pv_22', 
                    'wsc_pv_23', 'wsc_pv_24', 'wsc_pv_25', 'wsc_pv_26_if', 'wsc_pv_27_ih', 'wsc_pv_28_ih_rule', 'wsc_pv_29', 
                    'wsc_pv_3', 'wsc_pv_30_icif', 'wsc_pv_31_icif', 'wsc_pv_32', 'wsc_pv_33_if', 'wsc_pv_34', 'wsc_pv_35', 
                    'wsc_pv_36_if', 'wsc_pv_37', 'wsc_pv_38_if', 'wsc_pv_39_if', 'wsc_pv_4', 'wsc_pv_5', 'wsc_pv_6', 'wsc_pv_7', 
                    'wsc_pv_8', 'wsc_pv_9', 'wsc_return_comparison', 'wsc_search3_if', 'wyc_if_2hour_return_nr_as_cfg', 
                    'wyc_mf10_tbuydiff', 'wyc_mf11_nmgjd', 'wyc_mf13_nmdiffstknum', 'wyc_mf14_mdgjd', 'wyc_mf15_amtdiffstd', 
                    'wyc_mf16_voldiffstd', 'wyc_mf17_dealhigh', 'wyc_mf18_countratio', 'wyc_mf19_netvolmulret', 'wyc_mf1_tbuy', 
                    'wyc_mf20_positionskew', 'wyc_mf21_tailreverse', 'wyc_mf2_bbuymsbuy', 'wyc_mf3_mbuyvol', 'wyc_mf4_sbuyvol', 
                    'wyc_mf5_ssellvol', 'wyc_mf6_sbuyvol', 'wyc_mf7_smcountratio', 'wyc_mf8_totalcount', 'wyc_mf9_sbuymratio', 
                    'wyc_on31_DownBarNumPm_spot', 'wyc_on32_UpBarNumPm_spot', 'wyc_on33_BenFord_cfg', 'wyc_on34_BaseUpDown_spot'],
    }

cfg_hf_data_columns = ['Ask1AmtMean_500', 'Bid1AmtMean_500', 'BidAskSpreadMean_500', 'BuyOrderQtySumMean_500', 'BuyTradeMoney_500', 'BuyTradeQuantity_500', 'BuyUniqueOrderNum_500', 'SellOrderQtySumMean_500', 'SellTradeMoney_500', 'SellTradeQuantity_500', 'SellUniqueOrderNum_500', 'WeightBuyOrderQtySumMean_500', 'WeightSellOrderQtySumMean_500', 'amount_500', 'buy_bigorder_count_500', 'buy_bigorder_money_500', 'buy_midorder_count_500', 'buy_midorder_volume_500', 'buy_smallorder_count_500', 'buy_smallorder_money_500', 'buy_smallorder_volume_500', 'buy_superorder_count_500', 'buy_superorder_money_500', 'buy_superorder_volume_500', 'close_500', 'sell_bigorder_count_500', 'sell_midorder_count_500', 'sell_midorder_volume_500', 'sell_smallorder_count_500', 'sell_smallorder_volume_500', 'sell_superorder_count_500', 'volume_500', 'weight_500']
cfg_hf_index_columns = ['close_spot']
cfg_hf_data_path = '/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/IC_cfg_hf_data_2023.pkl'
cfg_hf_index_path = '/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/SPOT_DATA_2020.pkl'