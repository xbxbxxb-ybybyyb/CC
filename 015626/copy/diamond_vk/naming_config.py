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
calculate_volume_stop_time = datetime.time(14, 56)
calculate_volume_histdays = 10
calculate_volume_ratio = 0.08

minute_to_daily_start_time = datetime.time(9, 30)
minute_to_daily_stop_time = trade_stop_time
minute_to_daily_tag = minute_to_daily_start_time.strftime('%H%M') + minute_to_daily_stop_time.strftime('%H%M')

data_morning_begin = datetime.time(9, 30)
data_morning_end = datetime.time(11, 29)
data_afternoon_begin = datetime.time(13, 0)
data_afternoon_end = datetime.time(14, 56)

factor_raw_histdays = 120
data_richness_threshold = 0.95
min_data_richness_threshold = 0.8

section_rank_threshold = 0.5
ts_rank_window = 50
ts_rank_threshold = 0
open_num_threshold = 3
amount_threshold = 1.5e8

factor_trade_list = ['wyc_k1_cvcorr_kzz', 'CB2_CC', 'CB1_CC', 'CB29_CC', 'wyc_k26_ast_kzz', 'wyc_k212_stdinday_stk', 'CB5_CC', 
'wyc_k203_stkretpath_stk', 'wyc_k10_onret_y', 'wyc_k219_cochloRetDaily_kzz', 'CB32_CC', 'wyc_k226_MDD_kzz', 'CB33_CC', 'CB13_CC', 
'wyc_k15_yue_kzzrdf', 'CB15_CC', 'wyc_k220_HL5Days_kzz', 'CB23_CC', 'wyc_k201_highlowt_kzz', 'CB24_CC', 'wyc_k205_vwaptwap_kzz', 
'wyc_k208_highclosedaily_kzz', 'wyc_k222_CHRet_kzz', 'wyc_k154_TYP_kzz', 'kzz_crssuper', 'CB28_CC', 'wyc_k43_DC_kzz', 
'wyc_k16_vturnoverrate_kzzrdf', 'wyc_k161_obv_kzz', 'wyc_k210_multimean_kzz', 'wyc_k225_HO_kzz', 'CB12_CC', 'wyc_k4_maxpct_kzz', 
'wyc_k192_stdv_kzz', 'wyc_k206_highlowdaily_kzz', 'CB10_CC', 'wyc_k233_Boll_kzz', 'CB17_CC', 'wyc_k224_amtRank_kzz', 'CB25_CC', 
'wyc_k31_arc_kzz', 'CB22_CC', 'wyc_k12_convvalue_kzzrdf', 'wyc_k202_highdailymax_kzz', 'CB35_CC', 'wyc_k204_kzzretpath_kzz', 
'CB36_CC', 'wyc_k198_stda_kzz', 'wyc_k215_retstddaily_stk', 'wyc_k227_AmtWeightedSum_kzz', 'wyc_k110_BR_kzz', 
'wyc_k216_stddiff_kzzstk', 'wyc_k28_cm_kzz', 'wyc_k207_highlowdaily_stk', 'wyc_k223_lowWeightedAmount_kzz', 'CB14_CC', 'CB27_CC', 
'CB31_CC', 'wyc_k230_CL_stk', 'CB4_CC', 'wyc_k2_retdiffstd_ks', 'wyc_k29_cstd_kzz', 'wyc_k107_AD_kzz', 'CB16_CC', 
'wyc_k218_noonWeightedAmount_kzz', 'wyc_k232_skew_kzz', 'CB8_CC', 'kzz_cssuper', 'wyc_k11_doublelow_kzzrdf', 
'wyc_k213_updownstd_stk', 'wyc_k211_ocpxpath_stk', 'wyc_k217_upnum_kzz', 'kzz_assuper', 'wyc_k41_ADXpdm_kzz', 'wyc_k22_vs_kzz', 
'wyc_k214_updownstd_kzz', 'wyc_k228_HighDailyDiff_kzz', 'CB26_CC', 'wyc_k177_ADOWN_kzz', 'wyc_k44_MTM_kzz', 'wyc_k30_neta_kzz', 
'wyc_k231_CM_stk', 'wyc_k229_CL_kzz', 'wyc_k183_sqret_kzz', 'wyc_k221_mmRet_kzz', 'wyc_k129_Chande_kzz', 'wyc_k209_retdaily_stk', 
'factor_708_stk', 'factor_709_stk', 'factor_710_stk', 'factor_711_stk', 'factor_712_stk', 'factor_713_stk', 'factor_714_stk',
'factor_715_stk', 'factor_734_0', 'factor_734_1', 'factor_734_2', 'factor_734_3', 'factor_700_stk', 'factor_702_stk', 
'factor_704_stk', 'factor_705_stk', 'factor_706_stk', 'factor_707_stk', 'factor_700_amm_stk', 'factor_702_amm_stk', 'factor_726', 
'factor_727', 'factor_728', 'factor_729', 'factor_730', 'factor_734_0_stk', 'factor_734_1_stk', 'factor_734_2_stk', 
'factor_734_3_stk', 'factor_731_stk', 'factor_732_stk', 'factor_726_stk', 'factor_727_stk', 'factor_728_stk', 'factor_729_stk', 
'factor_730_stk', 'factor_708', 'factor_709', 'factor_710', 'factor_711', 'factor_712', 'factor_713', 'factor_714', 'factor_715', 
'factor_717', 'factor_718', 'factor_719', 'factor_720', 'factor_721', 'factor_722', 'factor_723', 'factor_724', 'factor_725', 
'factor_717_stk', 'factor_718_stk', 'factor_719_stk', 'factor_720_stk', 'factor_721_stk', 'factor_722_stk', 'factor_723_stk',
 'factor_724_stk', 'factor_725_stk', 'factor_735_0', 'factor_735_1', 'factor_735_2', 'factor_735_0_stk', 'factor_735_1_stk', 
 'factor_735_2_stk', 'factor_700', 'factor_702', 'factor_704', 'factor_705', 'factor_706', 'factor_707', 'factor_700_amm', 
 'factor_702_amm', 'factor_731', 'factor_732', 'factor_733_stk', 'factor_736_0_stk', 'factor_736_1_stk', 'factor_736_2_stk', 
 'factor_736_3_stk', 'factor_736_4_stk', 'factor_736_0', 'factor_736_1', 'factor_736_2', 'factor_736_3', 'factor_736_4', 
 'factor_733']

factor_final_list = ['wyc_k1_cvcorr_kzz', 'CB2_CC', 'CB1_CC', 'CB29_CC', 'wyc_k26_ast_kzz', 'wyc_k212_stdinday_stk', 'CB5_CC', 
'wyc_k203_stkretpath_stk', 'wyc_k10_onret_y', 'wyc_k219_cochloRetDaily_kzz', 'CB32_CC', 'wyc_k226_MDD_kzz', 'CB33_CC', 'CB13_CC', 
'wyc_k15_yue_kzzrdf', 'CB15_CC', 'wyc_k220_HL5Days_kzz', 'CB23_CC', 'wyc_k201_highlowt_kzz', 'CB24_CC', 'wyc_k205_vwaptwap_kzz', 
'wyc_k208_highclosedaily_kzz', 'wyc_k222_CHRet_kzz', 'wyc_k154_TYP_kzz', 'kzz_crssuper', 'CB28_CC', 'wyc_k43_DC_kzz', 
'wyc_k16_vturnoverrate_kzzrdf', 'wyc_k161_obv_kzz', 'wyc_k210_multimean_kzz', 'wyc_k225_HO_kzz', 'CB12_CC', 'wyc_k4_maxpct_kzz', 
'wyc_k192_stdv_kzz', 'wyc_k206_highlowdaily_kzz', 'CB10_CC', 'wyc_k233_Boll_kzz', 'CB17_CC', 'wyc_k224_amtRank_kzz', 'CB25_CC', 
'wyc_k31_arc_kzz', 'CB22_CC', 'wyc_k12_convvalue_kzzrdf', 'wyc_k202_highdailymax_kzz', 'CB35_CC', 'wyc_k204_kzzretpath_kzz', 
'CB36_CC', 'wyc_k198_stda_kzz', 'wyc_k215_retstddaily_stk', 'wyc_k227_AmtWeightedSum_kzz', 'wyc_k110_BR_kzz', 
'wyc_k216_stddiff_kzzstk', 'wyc_k28_cm_kzz', 'wyc_k207_highlowdaily_stk', 'wyc_k223_lowWeightedAmount_kzz', 'CB14_CC', 'CB27_CC', 
'CB31_CC', 'wyc_k230_CL_stk', 'CB4_CC', 'wyc_k2_retdiffstd_ks', 'wyc_k29_cstd_kzz', 'wyc_k107_AD_kzz', 'CB16_CC', 
'wyc_k218_noonWeightedAmount_kzz', 'wyc_k232_skew_kzz', 'CB8_CC', 'kzz_cssuper', 'wyc_k11_doublelow_kzzrdf', 
'wyc_k213_updownstd_stk', 'wyc_k211_ocpxpath_stk', 'wyc_k217_upnum_kzz', 'kzz_assuper', 'wyc_k41_ADXpdm_kzz', 'wyc_k22_vs_kzz', 
'wyc_k214_updownstd_kzz', 'wyc_k228_HighDailyDiff_kzz', 'CB26_CC', 'wyc_k177_ADOWN_kzz', 'wyc_k44_MTM_kzz', 'wyc_k30_neta_kzz', 
'wyc_k231_CM_stk', 'wyc_k229_CL_kzz', 'wyc_k183_sqret_kzz', 'wyc_k221_mmRet_kzz', 'wyc_k129_Chande_kzz', 'wyc_k209_retdaily_stk', 
'factor_708_stk', 'factor_709_stk', 'factor_710_stk', 'factor_711_stk', 'factor_712_stk', 'factor_713_stk', 'factor_714_stk',
'factor_715_stk', 'factor_734_0', 'factor_734_1', 'factor_734_2', 'factor_734_3', 'factor_700_stk', 'factor_702_stk', 
'factor_704_stk', 'factor_705_stk', 'factor_706_stk', 'factor_707_stk', 'factor_700_amm_stk', 'factor_702_amm_stk', 'factor_726', 
'factor_727', 'factor_728', 'factor_729', 'factor_730', 'factor_734_0_stk', 'factor_734_1_stk', 'factor_734_2_stk', 
'factor_734_3_stk', 'factor_731_stk', 'factor_732_stk', 'factor_726_stk', 'factor_727_stk', 'factor_728_stk', 'factor_729_stk', 
'factor_730_stk', 'factor_708', 'factor_709', 'factor_710', 'factor_711', 'factor_712', 'factor_713', 'factor_714', 'factor_715', 
'factor_717', 'factor_718', 'factor_719', 'factor_720', 'factor_721', 'factor_722', 'factor_723', 'factor_724', 'factor_725', 
'factor_717_stk', 'factor_718_stk', 'factor_719_stk', 'factor_720_stk', 'factor_721_stk', 'factor_722_stk', 'factor_723_stk',
 'factor_724_stk', 'factor_725_stk', 'factor_735_0', 'factor_735_1', 'factor_735_2', 'factor_735_0_stk', 'factor_735_1_stk', 
 'factor_735_2_stk', 'factor_700', 'factor_702', 'factor_704', 'factor_705', 'factor_706', 'factor_707', 'factor_700_amm', 
 'factor_702_amm', 'factor_731', 'factor_732', 'factor_733_stk', 'factor_736_0_stk', 'factor_736_1_stk', 'factor_736_2_stk', 
 'factor_736_3_stk', 'factor_736_4_stk', 'factor_736_0', 'factor_736_1', 'factor_736_2', 'factor_736_3', 'factor_736_4', 
 'factor_733']

if platform.system() == 'Windows':
    trade_root = r'X:\trade\diamond_vk'
elif platform.system() == 'Linux':
    trade_root = '/dfs/user/015626/trade/diamond_vk/'
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
    kzz_model_value_key = 'kzz_models_all_univ_K5_bench'
    kzz_model_value_path = os.path.join(trade_root, 'model', 'model_value', '%s.h5' % kzz_model_value_key)
    kzz_model_file_path = os.path.join(trade_root, 'model', 'model_file', 'kzz_models_all_univ_K5_bench.pkl')
    kzz_model_result_savepath = os.path.join(trade_root, 'model', 'model_result')
    kzz_select_list_savepath = os.path.join(trade_root, 'select_list')
    json_result_savepath = os.path.join(trade_root, 'result')

    alla_eod_path =  os.path.join(public_root, 'test', 'DATABASE', 'WIND', 'AShareEODPrices', 'AShareEODPrices.h5')
else:
    raise AssertionError


