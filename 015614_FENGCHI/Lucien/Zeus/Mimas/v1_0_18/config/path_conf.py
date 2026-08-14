# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20250416/factor_df_hs1_20160101_20240630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/profit/20250416/p2_profit_interval_hs1_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20250416/hs1/mimas_xgb_importance_%s_reg15_second_FSV8_hs1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20250416/hs1/mimas_xgb_importance_%s_reg15_second_FSV10_hs1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20250416/hs1/mimas_xgb_importance_%s_first_FSV11_hs1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/mimas/20250416/fsrs_hs1/fsrsv2pool_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_18/config1/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_18/config1/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20250416/factor_bank_inf_hs1_20231231.xlsx',

    label = 'label_pct_graded',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20250416/factor_df_hs1_20160101_20240630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/profit/20250416/p2_profit_interval_hs1_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250416/hs1/mimas_xgb_importance_%s_reg15_second_FSV8_hs1_label_v2o10dh1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250416/hs1/mimas_xgb_importance_%s_reg15_second_FSV10_hs1_label_v2o10dh1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250416/hs1/mimas_xgb_importance_%s_first_FSV11_hs1_label_v2o10dh1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/mimas/20250416/fsrs_hs1/fsrsv2pool_label_v2o10dh1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_18/config2/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_18/config2/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20250416/factor_bank_inf_hs1_20231231.xlsx',

    label = 'label_v2o10dh1',
)
