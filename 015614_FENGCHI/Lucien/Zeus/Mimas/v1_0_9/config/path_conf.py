# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

config1 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20241225/factor_df_s1_20160101_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/profit/20241225/p2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_reg15_second_FSV8_s1_label_v2o10d1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_reg15_second_FSV10_s1_label_v2o10d1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_first_FSV11_s1_label_v2o10d1.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/mimas/20241225/fsrs_s1/fsrsv2_label_v2o10d1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/mimas/20241225/fsci/fsci_label_v2o10d1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/mimas/v1_0_9/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/mimas/v1_0_9/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20241225/factor_bank_inf_s1.xlsx',

    label = 'label_v2o10d1',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20241225/factor_df_s1_20160101_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/profit/20241225/p2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_reg15_second_FSV8_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_reg15_second_FSV10_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_first_FSV11_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/mimas/20241225/fsrs_s1/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/mimas/20241225/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/mimas/v1_0_9/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/mimas/v1_0_9/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20241225/factor_bank_inf_s1.xlsx',

    label = 'label_pct_graded',
)

config3 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20241225/factor_df_s1_20160101_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/profit/20241225/p2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_reg15_second_FSV8_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_reg15_second_FSV10_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_first_FSV11_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/mimas/20241225/fsrs_s1/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/mimas/20241225/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/mimas/v1_0_9/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/mimas/v1_0_9/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20241225/factor_bank_inf_s1.xlsx',

    label = 'self_pct_label2',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20241225/factor_df_s1_20160101_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/profit/20241225/p2_profit_interval_s1_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_reg15_second_FSV8_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_reg15_second_FSV10_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20241225/s1/mimas_xgb_importance_%s_first_FSV11_s1_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/mimas/20241225/fsrs_s1/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/mimas/20241225/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/mimas/v1_0_9/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/mimas/v1_0_9/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20241225/factor_bank_inf_s1.xlsx',

    label = 'self_pct_label3',
)

config5 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20241225_label3/factor_df_s1_20160101_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/profit/20241225_label3/p2_profit_interval_s1_label3_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20241225_label3/s1/mimas_xgb_importance_%s_reg15_second_FSV8_s1_label_pct_diff_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20241225_label3/s1/mimas_xgb_importance_%s_reg15_second_FSV10_s1_label_pct_diff_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20241225_label3/s1/mimas_xgb_importance_%s_first_FSV11_s1_label_pct_diff_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/mimas/20241225_label3/fsrs/fsrsv2_label_pct_diff_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/mimas/20241225_label3/fsci/fsci_label_pct_diff_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/mimas/v1_0_9/config5/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/mimas/v1_0_9/config5/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20241225_label/factor_bank_inf_s1.xlsx',

    label = 'label_pct_diff_graded',
)