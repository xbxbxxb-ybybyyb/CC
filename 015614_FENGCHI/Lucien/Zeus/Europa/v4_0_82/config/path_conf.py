# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

# config1 = dict(
#     data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_all_20160101_20210228.pkl',
#     profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/v1/LabelProfit_zt_twap_pct_931_0.10_2000_300_SH250_SZ20.h5',
#
#     xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200229_reg15_second_FSV8_all_label_v1_graded.xlsx',
#     xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200831_reg15_second_FSV8_all_label_v1_graded.xlsx',
#     xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200229_reg15_second_FSV10_all_label_v1_graded.xlsx',
#     xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200831_reg15_second_FSV10_all_label_v1_graded.xlsx',
#     xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200229_first_FSV11_all_label_v1_graded.xlsx',
#     xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200831_first_FSV11_all_label_v1_graded.xlsx',
#     fsrs_period1_fpath = '/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_v1_graded_20160101_20200229.xlsx',
#     fsrs_period2_fpath = '/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_v1_graded_20160101_20200831.xlsx',
#     fsci_period1_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci/fsci_label_v1_graded_20160101_20200229.xlsx',
#     fsci_period2_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci/fsci_label_v1_graded_20160101_20200831.xlsx',
#
#     fs_config = {
#             'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config1/rffs_%s.pkl' % period.replace('_roll', '')",
#             'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
#         },
#
#     factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_all_period.xlsx',
#
#     label = 'label_v1_graded',
# )

config1 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_all_20160101_20210228.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/px/LabelProfit_zt_twap_quickt_p7_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200229_reg15_second_FSV8_all_label_p7_graded.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200831_reg15_second_FSV8_all_label_p7_graded.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200229_reg15_second_FSV10_all_label_p7_graded.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200831_reg15_second_FSV10_all_label_p7_graded.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200229_first_FSV11_all_label_p7_graded.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200831_first_FSV11_all_label_p7_graded.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_p7_graded_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_p7_graded_20160101_20200831.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci/fsci_label_p7_graded_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci/fsci_label_p7_graded_20160101_20200831.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_all_period.xlsx',

    label = 'label_p7_graded',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_all_20160101_20210228.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200229_reg15_second_FSV8_all_label_pct_graded.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200831_reg15_second_FSV8_all_label_pct_graded.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200229_reg15_second_FSV10_all_label_pct_graded.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200831_reg15_second_FSV10_all_label_pct_graded.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200229_first_FSV11_all_label_pct_graded.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/all/europa_xgb_importance_20200831_first_FSV11_all_label_pct_graded.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_pct_graded_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/europa/20240901/fsrs/fsrsv2_label_pct_graded_20160101_20200831.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci/fsci_label_pct_graded_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci/fsci_label_pct_graded_20160101_20200831.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_all_period.xlsx',

    label = 'label_pct_graded',
)



# 分场景
# config4 = dict(
#     data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_no2_industry2_20160101_20210228.pkl',
#     profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/v1/LabelProfit_zt_twap_pct_931_0.10_2000_300_SH250_SZ20.h5',
#
#     xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200229_reg15_second_FSV8_all_label_v1_graded.xlsx',
#     xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200831_reg15_second_FSV8_all_label_v1v1_graded.xlsx',
#     xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200229_reg15_second_FSV10_all_label_v1_graded.xlsx',
#     xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200831_reg15_second_FSV10_all_label_v1_graded.xlsx',
#     xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200229_first_FSV11_all_label_v1_graded.xlsx',
#     xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200831_first_FSV11_all_label_v1_graded.xlsx',
#     fsrs_period1_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no2_industry2/fsrsv2_label_v1_graded_20160101_20200229.xlsx',
#     fsrs_period2_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no2_industry2/fsrsv2_label_v1_graded_20160101_20200831.xlsx',
#     fsci_period1_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no2_industry2/fsci_label_v1_graded_20160101_20200229.xlsx',
#     fsci_period2_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no2_industry2/fsci_label_v1_graded_20160101_20200831.xlsx',
#
#     fs_config = {
#             'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs_%s.pkl' % period.replace('_roll', '')",
#             'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
#         },
#
#     factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_no2_industry2_period.xlsx',
#
#     label = 'label_v1_graded',
# )

config3 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_no2_industry2_20160101_20210228.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/px/LabelProfit_zt_twap_quickt_p7_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200229_reg15_second_FSV8_no2_industry2_label_p7_graded.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200831_reg15_second_FSV8_no2_industry2_label_p7_graded.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200229_reg15_second_FSV10_no2_industry2_label_p7_graded.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200831_reg15_second_FSV10_no2_industry2_label_p7_graded.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200229_first_FSV11_no2_industry2_label_p7_graded.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200831_first_FSV11_no2_industry2_label_p7_graded.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no2_industry2/fsrsv2_label_p7_graded_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no2_industry2/fsrsv2_label_p7_graded_20160101_20200831.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no2_industry2/fsci_label_p7_graded_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no2_industry2/fsci_label_p7_graded_20160101_20200831.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config5/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config5/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_no2_industry2_period.xlsx',

    label = 'label_p7_graded',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_no2_industry2_20160101_20210228.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200229_reg15_second_FSV8_no2_industry2_label_pct_graded.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200831_reg15_second_FSV8_no2_industry2_label_pct_graded.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200229_reg15_second_FSV10_no2_industry2_label_pct_graded.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200831_reg15_second_FSV10_no2_industry2_label_pct_graded.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200229_first_FSV11_no2_industry2_label_pct_graded.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no2_industry2/europa_xgb_importance_20200831_first_FSV11_no2_industry2_label_pct_graded.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no2_industry2/fsrsv2_label_pct_graded_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no2_industry2/fsrsv2_label_pct_graded_20160101_20200831.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no2_industry2/fsci_label_pct_graded_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no2_industry2/fsci_label_pct_graded_20160101_20200831.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_no2_industry2_period.xlsx',

    label = 'label_pct_graded',
)

# config7 = dict(
#     data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_no_under3_market_20160101_20210228.pkl',
#     profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/v1/LabelProfit_zt_twap_pct_931_0.10_2000_300_SH250_SZ20.h5',
#
#     xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200229_reg15_second_FSV8_all_label_p7_graded.xlsx',
#     xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200831_reg15_second_FSV8_all_label_p7_graded.xlsx',
#     xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200229_reg15_second_FSV10_all_label_p7_graded.xlsx',
#     xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200831_reg15_second_FSV10_all_label_p7_graded.xlsx',
#     xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200229_first_FSV11_all_label_p7_graded.xlsx',
#     xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200831_first_FSV11_all_label_p7_graded.xlsx',
#     fsrs_period1_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no_under3_market/fsrsv2_label_p7_graded_20160101_20200229.xlsx',
#     fsrs_period2_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no_under3_market/fsrsv2_label_p7_graded_20160101_20200831.xlsx',
#     fsci_period1_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no_under3_market/fsci_label_p7_graded_20160101_20200229.xlsx',
#     fsci_period2_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no_under3_market/fsci_label_p7_graded_20160101_20200831.xlsx',
#
#     fs_config = {
#             'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs_%s.pkl' % period.replace('_roll', '')",
#             'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
#         },
#
#     factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_no_under3_market_period.xlsx',
#
#     label = 'label_v1_graded',
# )

config5 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_no_under3_market_20160101_20210228.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/px/LabelProfit_zt_twap_quickt_p7_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200229_reg15_second_FSV8_no_under3_market_label_p7_graded.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200831_reg15_second_FSV8_no_under3_market_label_p7_graded.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200229_reg15_second_FSV10_no_under3_market_label_p7_graded.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200831_reg15_second_FSV10_no_under3_market_label_p7_graded.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200229_first_FSV11_no_under3_market_label_p7_graded.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200831_first_FSV11_no_under3_market_label_p7_graded.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no_under3_market/fsrsv2_label_p7_graded_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no_under3_market/fsrsv2_label_p7_graded_20160101_20200831.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no_under3_market/fsci_label_p7_graded_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no_under3_market/fsci_label_p7_graded_20160101_20200831.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_no_under3_market_period.xlsx',

    label = 'label_p7_graded',
)

config6 = dict(
    data_fpath = '/data/group/800463/sunss/europa/20240901/factor_df_no_under3_market_20160101_20210228.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200229_reg15_second_FSV8_no_under3_market_label_pct_graded.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200831_reg15_second_FSV8_no_under3_market_label_pct_graded.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200229_reg15_second_FSV10_no_under3_market_label_pct_graded.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200831_reg15_second_FSV10_no_under3_market_label_pct_graded.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200229_first_FSV11_no_under3_market_label_pct_graded.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/europa/fac_20240901/no_under3_market/europa_xgb_importance_20200831_first_FSV11_no_under3_market_label_pct_graded.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no_under3_market/fsrsv2_label_pct_graded_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/europa/20240901/fsrs_no_under3_market/fsrsv2_label_pct_graded_20160101_20200831.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no_under3_market/fsci_label_pct_graded_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/europa/fac_20240901/tsq/fsci_no_under3_market/fsci_label_pct_graded_20160101_20200831.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_82/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/europa/20240901/factor_bank_inf_no_under3_market_period.xlsx',

    label = 'label_pct_graded',
)