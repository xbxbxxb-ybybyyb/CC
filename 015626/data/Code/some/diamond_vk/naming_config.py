import os
import datetime
import platform

# trade variable
num_lim = 60
quota_limit = 0.0075
quota_scaler = 2.5
total_quota = 1.2E8
close_lim = 80
return_lim = -0.5

# insight variable
morning_start_time = datetime.time(9, 25)
morning_end_time = datetime.time(9, 40)
mid_job_time = datetime.time(14, 0)
ref_close_start_time = datetime.time(14, 30)
ref_close_end_time = datetime.time(14, 44)
stock_ref_limit_end_time = datetime.time(14, 43)

# global variable
trade_start_time = datetime.time(9, 15)
trade_mid_time = datetime.time(14, 30)
trade_stop_time = datetime.time(14, 45)

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
                    'wyc_k4_maxpct_kzz', 
                    'wyc_k201_highlowt_kzz', 'wyc_k202_highdailymax_kzz', 'wyc_k203_stkretpath_stk', 'wyc_k204_kzzretpath_kzz', 
                    'wyc_k205_vwaptwap_kzz', 'wyc_k206_highlowdaily_kzz', 'wyc_k207_highlowdaily_stk', 'wyc_k208_highclosedaily_kzz', 
                    'wyc_k209_retdaily_stk', 'wyc_k210_multimean_kzz', 'wyc_k211_ocpxpath_stk', 'wyc_k212_stdinday_stk', 
                    'wyc_k213_updownstd_stk', 'wyc_k214_updownstd_kzz', 'wyc_k215_retstddaily_stk', 'wyc_k216_stddiff_kzzstk', 
                    'wyc_k217_upnum_kzz', 'wyc_k218_noonWeightedAmount_kzz', 'wyc_k219_cochloRetDaily_kzz', 'wyc_k220_HL5Days_kzz', 
                    'wyc_k221_mmRet_kzz', 'wyc_k222_CHRet_kzz', 'wyc_k223_lowWeightedAmount_kzz', 'wyc_k224_amtRank_kzz', 
                    'wyc_k225_HO_kzz', 'wyc_k226_MDD_kzz', 'wyc_k227_AmtWeightedSum_kzz', 'wyc_k228_HighDailyDiff_kzz', 
                    'wyc_k229_CL_kzz', 'wyc_k230_CL_stk', 'wyc_k231_CM_stk', 'wyc_k232_skew_kzz', 'wyc_k233_Boll_kzz',
                    'CB22_CC', 'wyc_k22_vs_kzz', 'wyc_k26_ast_kzz', 'wyc_k28_cm_kzz']

factor_final_list = ['CB13_CC', 'CB14_CC', 'CB17_CC', 'CB1_CC', 'CB25_CC', 'CB27_CC', 'CB2_CC', 'CB31_CC', 'CB32_CC', 
                    'CB36_CC', 'CB4_CC', 'CB5_CC', 'kzz_crssuper', 'wyc_k10_onret_y', 'wyc_k110_BR_kzz', 'wyc_k154_TYP_kzz', 
                    'wyc_k15_yue_kzzrdf', 'wyc_k16_vturnoverrate_kzzrdf', 'wyc_k161_obv_kzz', 'wyc_k192_stdv_kzz', 
                    'wyc_k203_stkretpath_stk', 'wyc_k204_kzzretpath_kzz', 'wyc_k205_vwaptwap_kzz', 'wyc_k207_highlowdaily_stk', 
                    'wyc_k210_multimean_kzz', 'wyc_k213_updownstd_stk', 'wyc_k214_updownstd_kzz', 'wyc_k215_retstddaily_stk', 
                    'wyc_k223_lowWeightedAmount_kzz', 'wyc_k225_HO_kzz', 'wyc_k230_CL_stk', 'wyc_k231_CM_stk', 'wyc_k233_Boll_kzz', 
                    'wyc_k31_arc_kzz', 'wyc_k41_ADXpdm_kzz']

if platform.system() == 'Windows':
    trade_root = r'X:\trade\diamond_vk'
elif platform.system() == 'Linux':
    trade_root = '/data/user/015626/trade/diamond_vk/'
#    hot_root = '/data/user/012245/projects/SimHF/ccbond/Data/Hot/'
    private_root = '/data/user/015626/data/share/'
    public_root = '/data/group/800080/warehouse/'
    hot_root = os.path.join(trade_root,'hot')

    hisfactor_path = os.path.join(trade_root, 'factor')
    factor_savepath = os.path.join(trade_root, 'factor')

    kzz_stock_minute_path = os.path.join(private_root,'MD','CHINA_CONVERTIBLE_BOND','MINUTE','CHINA_CONVERTIBLE_BOND_MINUTE_AND_STOCK.h5')
    kzz_stock_mapping_file = os.path.join(private_root,'MD','CHINA_CONVERTIBLE_BOND','CHINA_CONVERTIBLE_BOND_INFO.csv')
    kzz_onret_path = os.path.join(private_root,'MD','CHINA_CONVERTIBLE_BOND','DAILY','overnight_ret_kzz.h5')
    kzz_universe_path = os.path.join(private_root,'MD','CHINA_CONVERTIBLE_BOND','UNIVERSE','CHINA_CONVERTIBLE_BOND_UNIVERSE.h5')
    kzz_model_value_key = 'scores_univ_K5_20230117'
    kzz_model_value_path = os.path.join(trade_root, 'model', 'model_value', '%s.h5' % kzz_model_value_key)
    kzz_model_file_path = os.path.join(trade_root, 'model', 'model_file', 'kzz_models_univ_K5_20230117.pkl')
    kzz_model_result_savepath = os.path.join(trade_root, 'model', 'model_result')
    kzz_select_list_savepath = os.path.join(trade_root, 'select_list')
    json_result_savepath = os.path.join(trade_root, 'result')

    alla_eod_path =  os.path.join(public_root, 'test', 'DATABASE', 'WIND', 'AShareEODPrices', 'AShareEODPrices.h5')
else:
    raise AssertionError


