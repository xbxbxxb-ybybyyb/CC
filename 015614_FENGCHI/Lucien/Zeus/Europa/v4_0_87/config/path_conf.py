# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

config1 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_all_20160101_20240229.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV8_all_label_p7_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV10_all_label_p7_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_first_FSV11_all_label_p7_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_p7_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/europa/20240901/fsci/fsci_label_p7_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_all_period.xlsx',

    label = 'label_p7_graded',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_all_20160101_20240229.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV8_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV10_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_first_FSV11_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/europa/20240901/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_all_period.xlsx',

    label = 'label_pct_graded',
)


config3 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_all_20160101_20240229.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV8_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV10_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_first_FSV11_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/europa/20240901/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_all_period.xlsx',

    label = 'self_pct_label1',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_no2_industry2_20160101_20240229.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_%s_reg15_second_FSV8_no2_industry2_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_%s_reg15_second_FSV10_no2_industry2_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_%s_first_FSV11_no2_industry2_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/europa/20240901/fsrs_no2_industry2/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/europa/20240901/fsci_no2_industry2/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_no2_industry2_period.xlsx',

    label = 'label_pct_graded',
)

config5 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_all_20160101_20240229.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV8_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV10_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_first_FSV11_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/europa/20240901/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_all_period.xlsx',

    label = 'self_pct_label2',
)

# no_under3_market  pct
config6 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_no_under3_market_20160101_20240229.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_%s_reg15_second_FSV8_no_under3_market_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_%s_reg15_second_FSV10_no_under3_market_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_%s_first_FSV11_no_under3_market_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/europa/20240901/fsrs_no_under3_market/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/europa/20240901/fsci_no_under3_market/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_no_under3_market_period.xlsx',

    label = 'label_pct_graded',
)

# 新增两个标签，在全量样本上 20240925
config7 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_all_20160101_20240229.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV8_all_label_pct2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV10_all_label_pct2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_first_FSV11_all_label_pct2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_pct2_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/europa/20240901/fsci/fsci_label_pct2_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_all_period.xlsx',

    label = 'label_pct2_graded',
)

config8 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_all_20160101_20240229.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV8_all_label_TN_o2ul.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV10_all_label_TN_o2ul.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_first_FSV11_all_label_TN_o2ul.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_TN_o2ul_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/europa/20240901/fsci/fsci_label_TN_o2ul_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_all_period.xlsx',

    label = 'label_TN_o2ul',
)

config9 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_all_20160101_20240229.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV8_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_reg15_second_FSV10_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_%s_first_FSV11_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/europa/20240901/fsci/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_84/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_all_period.xlsx',

    label = 'self_pct_label3',
)