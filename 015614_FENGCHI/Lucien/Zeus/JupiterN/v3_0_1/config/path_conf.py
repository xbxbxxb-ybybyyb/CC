# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

config1 = dict(
    data_fpath = '/data/group/800463/sunss/jupiterN/20241107_B/factor_df_all_20160101_20200831.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/jupiterN/profit/20241107_B/LabelProfit_zt_twap_0.10_1000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_reg15_second_FSV8_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_reg15_second_FSV10_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_first_FSV11_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/jupiterN/20241107_B/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/jupiterN/20241107_B/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/JupiterN/v4_0_84/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/JupiterN/v4_0_84/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/jupiterN/20241107_B/factor_bank_inf_all_period.xlsx',

    label = 'label_pct_graded',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/jupiterN/20241107_B/factor_df_all_20160101_20200831.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/jupiterN/profit/20241107_B/LabelProfit_zt_twap_0.10_1000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_reg15_second_FSV8_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_reg15_second_FSV10_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_first_FSV11_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/jupiterN/20241107_B/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/jupiterN/20241107_B/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/JupiterN/v4_0_84/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/JupiterN/v4_0_84/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/jupiterN/20241107_B/factor_bank_inf_all_period.xlsx',

    label = 'self_pct_label1',
)

config3 = dict(
    data_fpath = '/data/group/800463/sunss/jupiterN/20241107_B/factor_df_all_20160101_20200831.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/jupiterN/profit/20241107_B/LabelProfit_zt_twap_0.10_1000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_reg15_second_FSV8_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_reg15_second_FSV10_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_first_FSV11_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/jupiterN/20241107_B/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/jupiterN/20241107_B/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/JupiterN/v4_0_84/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/JupiterN/v4_0_84/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/jupiterN/20241107_B/factor_bank_inf_all_period.xlsx',

    label = 'self_pct_label2',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/jupiterN/20241107_B/factor_df_all_20160101_20200831.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/jupiterN/profit/20241107_B/LabelProfit_zt_twap_0.10_1000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_reg15_second_FSV8_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_reg15_second_FSV10_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_first_FSV11_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/jupiterN/20241107_B/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/jupiterN/20241107_B/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/JupiterN/v4_0_84/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/JupiterN/v4_0_84/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/jupiterN/20241107_B/factor_bank_inf_all_period.xlsx',

    label = 'self_pct_label3',
)

config5 = dict(
    data_fpath = '/data/group/800463/sunss/jupiterN/20241107_B/factor_df_all_20160101_20200831.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/jupiterN/profit/20241107_B/LabelProfit_zt_twap_0.10_1000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_reg15_second_FSV8_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_reg15_second_FSV10_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/jupiterN/fac_20241107_B/all/jupiterN_xgb_importance_%s_first_FSV11_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/jupiterN/20241107_B/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/jupiterN/20241107_B/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/JupiterN/v4_0_84/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/JupiterN/v4_0_84/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/jupiterN/20241107_B/factor_bank_inf_all_period.xlsx',

    label = 'label_TN_o2ul',
)