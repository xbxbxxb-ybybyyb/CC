# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/sunss/p4/20250317_ns1/factor_df_ns1_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/p4/profit/20250317_ns1/p4_profit_interval_ns1_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/p4/fac_20250317_ns1/ns1/p4_xgb_importance_%s_reg15_second_FSV8_ns1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/p4/fac_20250317_ns1/ns1/p4_xgb_importance_%s_reg15_second_FSV10_ns1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/p4/fac_20250317_ns1/ns1/p4_xgb_importance_%s_first_FSV11_ns1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/p4/20250317_ns1/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/p4/20250317_ns1/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/P4/v1_0_5/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/P4/v1_0_5/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/p4/20250317_ns1/factor_bank_inf_ns1.xlsx',

    label = 'label_pct_graded',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/p4/20250317_ns1/factor_df_ns1_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/p4/profit/20250317_ns1/p4_profit_interval_ns1_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/p4/fac_20250317_ns1/ns1/p4_xgb_importance_%s_reg15_second_FSV8_ns1_label_v2o10nd1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/p4/fac_20250317_ns1/ns1/p4_xgb_importance_%s_reg15_second_FSV10_ns1_label_v2o10nd1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/p4/fac_20250317_ns1/ns1/p4_xgb_importance_%s_first_FSV11_ns1_label_v2o10nd1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/p4/20250317_ns1/fsrs/fsrsv2_label_v2o10_nd1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/p4/20250317_ns1/fsci/fsci_label_v2o10_nd1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/P4/v1_0_5/config2/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/P4/v1_0_5/config2/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/p4/20250317_ns1/factor_bank_inf_ns1.xlsx',

    label = 'label_v2o10nd1',
)

config3 = dict(
    data_fpath = '/data/group/800463/sunss/p4/20250317_ns1/factor_df_ns1_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/p4/profit/20250317_ns1/p4_profit_interval_ns1_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/p4/fac_20250317_ns1/ns1/p4_xgb_importance_%s_reg15_second_FSV8_ns1_label_pct2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/p4/fac_20250317_ns1/ns1/p4_xgb_importance_%s_reg15_second_FSV10_ns1_label_pct2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/p4/fac_20250317_ns1/ns1/p4_xgb_importance_%s_first_FSV11_ns1_label_pct2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/ceres/20250317_ns1/fsrs/fsrsv2_label_pct2_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/ceres/20250317_ns1/fsci/fsci_label_pct2_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/P4/v1_0_5/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/P4/v1_0_5/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/ceres/20250317_ns1/factor_bank_inf_ns1.xlsx',

    label = 'label_pct2_graded',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/ceres/20250317_ns1/factor_df_ns1_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/p4/profit/20250317_ns1/p4_profit_interval_ns1_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250317_ns1/s1/p4_xgb_importance_%s_reg15_second_FSV8_s1_with_p4_label_v2o10_ns1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250317_ns1/s1/p4_xgb_importance_%s_reg15_second_FSV10_s1_with_p4_label_v2o10_ns1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250317_ns1/s1/p4_xgb_importance_%s_first_FSV11_s1_with_p4_label_v2o10_ns1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/ceres/20250317_ns1/fsrs/fsrsv2_label_v2o10_ns1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/ceres/20250317_ns1/fsci/fsci_label_v2o10_ns1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/P4/v1_0_5/config2/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/P4/v1_0_5/config2/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/ceres/20250317_ns1/factor_bank_inf_s1_with_p4_filter.xlsx',

    label = 'label_v2o10_ns1',
)