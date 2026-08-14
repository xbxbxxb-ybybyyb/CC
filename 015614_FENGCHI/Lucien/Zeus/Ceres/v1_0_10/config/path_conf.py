# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/sunss/ceres/20250213/factor_df_s1_with_p4_under5_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/ceres/profit/20250213/sp2_profit_interval_s1_with_p4_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_under5/ceres_xgb_importance_%s_reg15_second_FSV8_s1_with_p4_under5_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_under5/ceres_xgb_importance_%s_reg15_second_FSV10_s1_with_p4_under5_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_under5/ceres_xgb_importance_%s_first_FSV11_s1_with_p4_under5_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/ceres/20250213/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/ceres/20250213/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Ceres/v1_0_10/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Ceres/v1_0_10/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/ceres/20250213/factor_bank_inf_s1_with_p4_under5.xlsx',

    label = 'label_pct_graded',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/ceres/20250213/factor_df_s1_with_p4_up4_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/ceres/profit/20250213/sp2_profit_interval_s1_with_p4_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_up4/ceres_xgb_importance_%s_reg15_second_FSV8_s1_with_p4_up4_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_up4/ceres_xgb_importance_%s_reg15_second_FSV10_s1_with_p4_up4_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_up4/ceres_xgb_importance_%s_first_FSV11_s1_with_p4_up4_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/ceres/20250213/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/ceres/20250213/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Ceres/v1_0_10/config2/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Ceres/v1_0_10/config2/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/ceres/20250213/factor_bank_inf_s1_with_p4_up4.xlsx',

    label = 'label_pct_graded',
)

config3 = dict(
    data_fpath = '/data/group/800463/sunss/ceres/20250213/factor_df_s1_with_p4_under5_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/ceres/profit/20250213/sp2_profit_interval_s1_with_p4_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_under5/ceres_xgb_importance_%s_reg15_second_FSV8_s1_with_p4_under5_label_v2o10d1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_under5/ceres_xgb_importance_%s_reg15_second_FSV10_s1_with_p4_under5_label_v2o10d1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_under5/ceres_xgb_importance_%s_first_FSV11_s1_with_p4_under5_label_v2o10d1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/ceres/20250213/fsrs/fsrsv2_label_v2o10d1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/ceres/20250213/fsci/fsci_label_v2o10d1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Ceres/v1_0_10/config3/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Ceres/v1_0_10/config3/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/ceres/20250213/factor_bank_inf_s1_with_p4_under5.xlsx',

    label = 'label_v2o10d1',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/ceres/20250213/factor_df_s1_with_p4_up4_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/ceres/profit/20250213/sp2_profit_interval_s1_with_p4_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_up4/ceres_xgb_importance_%s_reg15_second_FSV8_s1_with_p4_up4_label_v2o10d1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_up4/ceres_xgb_importance_%s_reg15_second_FSV10_s1_with_p4_up4_label_v2o10d1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250213/s1_with_p4_up4/ceres_xgb_importance_%s_first_FSV11_s1_with_p4_up4_label_v2o10d1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/ceres/20250213/fsrs/fsrsv2_label_v2o10d1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/ceres/20250213/fsci/fsci_label_v2o10d1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Ceres/v1_0_10/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Ceres/v1_0_10/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/ceres/20250213/factor_bank_inf_s1_with_p4_up4.xlsx',

    label = 'label_v2o10d1',
)