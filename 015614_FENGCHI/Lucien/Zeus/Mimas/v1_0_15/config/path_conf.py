# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20250225/factor_df_s1_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/profit/20250225/p2_profit_interval_t_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_reg15_second_FSV8_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_reg15_second_FSV10_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_first_FSV11_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/mimas/20250225/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/mimas/20250225/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_15/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_15/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20250225/factor_bank_inf_s1.xlsx',

    label = 'label_pct_graded',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20250225/factor_df_s1_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/profit/20250225/p2_profit_interval_t_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_reg15_second_FSV8_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_reg15_second_FSV10_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_first_FSV11_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/mimas/20250225/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/mimas/20250225/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_15/config2/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_15/config2/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20250225/factor_bank_inf_s1.xlsx',

    label = 'label_pct_graded',
)

config3 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20250225/factor_df_s1_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/profit/20250225/p2_profit_interval_t_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_reg15_second_FSV8_s1_label_v2o10_t.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_reg15_second_FSV10_s1_label_v2o10_t.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_first_FSV11_s1_label_v2o10_t.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/mimas/20250225/fsrs/fsrsv2_label_v2o10_t_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/mimas/20250225/fsci/fsci_label_v2o10_t_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_15/config3/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_15/config3/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20250225/factor_bank_inf_s1.xlsx',

    label = 'label_v2o10_t',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20250225/factor_df_s1_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/profit/20250225/p2_profit_interval_t_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_reg15_second_FSV8_s1_label_v2o10_t.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_reg15_second_FSV10_s1_label_v2o10_t.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250225/s1/mimas_xgb_importance_%s_first_FSV11_s1_label_v2o10_t.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/mimas/20250225/fsrs/fsrsv2_label_v2o10_t_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/mimas/20250225/fsci/fsci_label_v2o10_t_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_15/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Mimas/v1_0_15/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20250225/factor_bank_inf_s1.xlsx',

    label = 'label_v2o10_t',
)