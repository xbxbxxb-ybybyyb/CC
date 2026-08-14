# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

config1 = dict(
    data_fpath = '/data/group/800463/sunss/saturn/20241129/factor_df_sc_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/saturn/profit/20241129/p2_profit_interval_sc_0.10_0.10_1000_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_reg15_second_FSV8_sc_label_v2o10dc.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_reg15_second_FSV10_sc_label_v2o10dc.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_first_FSV11_sc_label_v2o10dc.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/saturn/20241129/fsrs_sc/fsrsv2_label_v2o10dc_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/saturn/20241129/fsci_sc/fsci_label_v2o10dc_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/saturn/v5_0_2/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/saturn/v5_0_2/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/saturn/20241129/factor_bank_inf_sc.xlsx',

    label = 'label_v2o10dc',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/saturn/20241129/factor_df_sc_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/saturn/profit/20241129/p2_profit_interval_sc_0.10_0.10_1000_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_reg15_second_FSV8_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_reg15_second_FSV10_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_first_FSV11_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/saturn/20241129/fsrs_sc/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/saturn/20241129/fsci_sc/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/saturn/v5_0_2/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/saturn/v5_0_2/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/saturn/20241129/factor_bank_inf_sc.xlsx',

    label = 'label_pct_graded',
)

config3 = dict(
    data_fpath = '/data/group/800463/sunss/saturn/20241129/factor_df_sc_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/saturn/profit/20241129/p2_profit_interval_sc_0.10_0.10_1000_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_reg15_second_FSV8_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_reg15_second_FSV10_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_first_FSV11_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/saturn/20241129/fsrs_sc/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/saturn/20241129/fsci_sc/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/saturn/v5_0_2/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/saturn/v5_0_2/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/saturn/20241129/factor_bank_inf_sc.xlsx',

    label = 'self_pct_label2',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/saturn/20241129/factor_df_sc_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/saturn/profit/20241129/p2_profit_interval_sc_0.10_0.10_1000_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_reg15_second_FSV8_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_reg15_second_FSV10_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_first_FSV11_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/saturn/20241129/fsrs_sc/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/saturn/20241129/fsci_sc/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/saturn/v5_0_2/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/saturn/v5_0_2/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/saturn/20241129/factor_bank_inf_sc.xlsx',

    label = 'self_pct_label3',
)

config5 = dict(
    data_fpath = '/data/group/800463/sunss/saturn/20241129/factor_df_sc_20160101_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/saturn/profit/20241129/p2_profit_interval_sc_0.10_0.10_1000_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_reg15_second_FSV8_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_reg15_second_FSV10_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/saturn/fac_20241129/sc/saturn_xgb_importance_%s_first_FSV11_sc_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/saturn/20241129/fsrs_sc/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/saturn/20241129/fsci_sc/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/saturn/v5_0_2/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/saturn/v5_0_2/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/saturn/20241129/factor_bank_inf_sc.xlsx',

    label = 'label_Tc2To10c1',
)