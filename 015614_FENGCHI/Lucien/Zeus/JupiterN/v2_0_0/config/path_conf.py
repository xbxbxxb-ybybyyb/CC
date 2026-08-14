# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

config1 = dict(
    data_fpath = '/data/group/800463/sunss/jupiterN/20240911/factor_df_all_20160101_20210228.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/jupiterN/profit/20240911/px/LabelProfit_zt_twap_quickt_p5_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200229_reg15_second_FSV8_all_label_p5_graded.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200831_reg15_second_FSV8_all_label_p5_graded.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200229_reg15_second_FSV10_all_label_p5_graded.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200831_reg15_second_FSV10_all_label_p5_graded.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200229_first_FSV11_all_label_p5_graded.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200831_first_FSV11_all_label_p5_graded.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/jupiterN/20240911/fsrs/fsrsv2_label_p5_graded_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/jupiterN/20240911/fsrs/fsrsv2_label_p5_graded_20160101_20200831.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/tsq/fsci/fsci_label_p5_graded_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/tsq/fsci/fsci_label_p5_graded_20160101_20200831.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/JupiterN/v2_0_0/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/JupiterN/v2_0_0/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/jupiterN/20240911/factor_bank_inf_all_period.xlsx',

    label = 'label_p5_graded',
)

config3 = dict(
    data_fpath = '/data/group/800463/sunss/jupiterN/20240911/factor_df_all_20160101_20210228.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/jupiterN/profit/20240911/px/LabelProfit_zt_twap_quickt_p5_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200229_reg15_second_FSV8_all_label_p5_graded.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200831_reg15_second_FSV8_all_label_p5_graded.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200229_reg15_second_FSV10_all_label_p5_graded.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200831_reg15_second_FSV10_all_label_p5_graded.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200229_first_FSV11_all_label_p5_graded.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200831_first_FSV11_all_label_p5_graded.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/jupiterN/20240911/fsrs/fsrsv2_label_p5_graded_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/jupiterN/20240911/fsrs/fsrsv2_label_p5_graded_20160101_20200831.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/tsq/fsci/fsci_label_p5_graded_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/tsq/fsci/fsci_label_p5_graded_20160101_20200831.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/JupiterN/v2_0_0/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/JupiterN/v2_0_0/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/jupiterN/20240911/factor_bank_inf_all_period.xlsx',

    label = 'self_pct_label2',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/jupiterN/20240911/factor_df_all_20160101_20210228.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/jupiterN/profit/20240911/px/LabelProfit_zt_twap_quickt_p5_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200229_reg15_second_FSV8_all_label_p5_graded.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200831_reg15_second_FSV8_all_label_p5_graded.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200229_reg15_second_FSV10_all_label_p5_graded.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200831_reg15_second_FSV10_all_label_p5_graded.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200229_first_FSV11_all_label_p5_graded.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/all/jupiterN_xgb_importance_20200831_first_FSV11_all_label_p5_graded.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/jupiterN/20240911/fsrs/fsrsv2_label_p5_graded_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/jupiterN/20240911/fsrs/fsrsv2_label_p5_graded_20160101_20200831.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/tsq/fsci/fsci_label_p5_graded_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/jupiterN/fac_20240911/tsq/fsci/fsci_label_p5_graded_20160101_20200831.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/JupiterN/v2_0_0/config4/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/JupiterN/v2_0_0/config4/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/jupiterN/20240911/factor_bank_inf_all_period.xlsx',

    label = 'self_pct_label3',
)