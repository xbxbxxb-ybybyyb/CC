import os
import datetime
import platform

# global variable
trade_start_time = datetime.time(9, 15)
trade_mid_time = datetime.time(14, 30)
trade_stop_time = datetime.time(14, 49)

calculate_volume_start_time = datetime.time(14, 50)
calculate_volume_stop_time = datetime.time(14, 57)
calculate_volume_histdays = 10
calculate_volume_ratio = 0.08

minute_to_daily_start_time = datetime.time(9, 30)
minute_to_daily_stop_time = trade_stop_time
minute_to_daily_tag = minute_to_daily_start_time.strftime('%H%M') + minute_to_daily_stop_time.strftime('%H%M')

data_morning_begin = datetime.time(9, 30)
data_morning_end = datetime.time(11, 29)
data_afternoon_begin = datetime.time(13, 0)
data_afternoon_end = datetime.time(14, 57)

factor_raw_histdays = 120
data_richness_threshold = 0.95
min_data_richness_threshold = 0.8

section_rank_threshold = 0.5
ts_rank_window = 50
ts_rank_threshold = 0
open_num_threshold = 3
amount_threshold = 1.5e8

factor_trade_list = ['CB10_CC', 'CB12_CC', 'CB13_CC', 'CB14_CC', 'CB15_CC', 'CB16_CC', 'CB17_CC', 'CB1_CC', 'CB23_CC', 
                    'CB24_CC', 'CB25_CC', 'CB26_CC', 'CB27_CC', 'CB28_CC', 'CB29_CC', 'CB2_CC', 'CB31_CC', 'CB32_CC', 
                    'CB33_CC', 'CB35_CC', 'CB36_CC', 'CB4_CC', 'CB5_CC', 'CB8_CC', 'kzz_assuper', 'kzz_crssuper', 
                    'kzz_cssuper', 'wyc_k107_AD_kzz', 'wyc_k10_onret_y', 'wyc_k110_BR_kzz', 'wyc_k11_doublelow_kzzrdf', 
                    'wyc_k129_Chande_kzz', 'wyc_k12_convvalue_kzzrdf', 'wyc_k154_TYP_kzz', 'wyc_k15_yue_kzzrdf', 
                    'wyc_k161_obv_kzz', 'wyc_k16_vturnoverrate_kzzrdf', 'wyc_k177_ADOWN_kzz', 'wyc_k183_sqret_kzz', 
                    'wyc_k192_stdv_kzz', 'wyc_k198_stda_kzz', 'wyc_k1_cvcorr_kzz', 'wyc_k29_cstd_kzz', 'wyc_k2_retdiffstd_ks', 
                    'wyc_k30_neta_kzz', 'wyc_k31_arc_kzz', 'wyc_k41_ADXpdm_kzz', 'wyc_k43_DC_kzz', 'wyc_k44_MTM_kzz', 
                    'wyc_k4_maxpct_kzz']

if platform.system() == 'Windows':
    trade_root = r'X:\trade\diamond_vk'
elif platform.system() == 'Linux':
    trade_root = '/arch0/group/800466/trade/diamond_vk/'
    hot_root = '/data/user/012245/projects/SimHF/ccbond/Data/Hot/'
    private_root = '/data/user/015626/data/share/'
    public_root = '/data/group/800080/warehouse/'
    # hot_root = os.path.join(trade_root,'hot_proof')

    hisfactor_path = os.path.join(trade_root, 'factor')
    factor_savepath = os.path.join(trade_root, 'factor')

    kzz_stock_minute_path = os.path.join(private_root,'MD','CHINA_CONVERTIBLE_BOND','MINUTE','CHINA_CONVERTIBLE_BOND_MINUTE_AND_STOCK.h5')
    kzz_stock_mapping_file = os.path.join(private_root,'MD','CHINA_CONVERTIBLE_BOND','CHINA_CONVERTIBLE_BOND_INFO.csv')
    kzz_onret_path = os.path.join(private_root,'MD','CHINA_CONVERTIBLE_BOND','DAILY','overnight_ret_kzz.h5')
    kzz_universe_path = os.path.join(private_root,'MD','CHINA_CONVERTIBLE_BOND','UNIVERSE','CHINA_CONVERTIBLE_BOND_UNIVERSE.h5')
    kzz_model_value_path = os.path.join(trade_root, 'model', 'model_value', 'kzz_model.h5')
    kzz_model_file_path = os.path.join(trade_root, 'model', 'model_file', 'kzz_models.pkl')
    kzz_model_result_savepath = os.path.join(trade_root, 'model', 'model_result')
    kzz_select_list_savepath = os.path.join(trade_root, 'select_list')

    alla_eod_path =  os.path.join(public_root, 'test', 'DATABASE', 'WIND', 'AShareEODPrices', 'AShareEODPrices.h5')
else:
    raise AssertionError


