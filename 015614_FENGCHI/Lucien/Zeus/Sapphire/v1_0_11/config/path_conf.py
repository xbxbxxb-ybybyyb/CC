# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/sunss/sapphire/20240828/p5/factor_df_p5_20160101_20210831.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/sapphire/profit/20240828/Sell_pct5_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p5/all/sapphire_xgb_importance_20200229_reg15_second_FSV8_all_label_diff_pct_after.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p5/all/sapphire_xgb_importance_20200831_reg15_second_FSV8_all_label_diff_pct_after.xlsx',
    xgb_fsv8_period3_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p5/all/sapphire_xgb_importance_20210228_reg15_second_FSV8_all_label_diff_pct_after.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p5/all/sapphire_xgb_importance_20200229_reg15_second_FSV10_all_label_diff_pct_after.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p5/all/sapphire_xgb_importance_20200831_reg15_second_FSV10_all_label_diff_pct_after.xlsx',
    xgb_fsv10_period3_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p5/all/sapphire_xgb_importance_20210228_reg15_second_FSV10_all_label_diff_pct_after.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p5/all/sapphire_xgb_importance_20200229_first_FSV11_all_label_diff_pct_after.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p5/all/sapphire_xgb_importance_20200831_first_FSV11_all_label_diff_pct_after.xlsx',
    xgb_fsv11_period3_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p5/all/sapphire_xgb_importance_20210228_first_FSV11_all_label_diff_pct_after.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/sapphire/20240828/p5/fsrs/fsrsv2_label_diff_pct_after_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/sapphire/20240828/p5/fsrs/fsrsv2_label_diff_pct_after_20160101_20200831.xlsx',
    fsrs_period3_fpath = '/data/group/800463/sunss/sapphire/20240828/p5/fsrs/fsrsv2_label_diff_pct_after_20160101_20210228.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/sapphire/fac_20240828/tsq/p5/fsci/fsci_label_diff_pct_after_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/sapphire/fac_20240828/tsq/p5/fsci/fsci_label_diff_pct_after_20160101_20200831.xlsx',
    fsci_period3_fpath = '/data/group/800463/xiely/factor_select/sapphire/fac_20240828/tsq/p5/fsci/fsci_label_diff_pct_after_20160101_20210228.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Sapphire/v1_0_11/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Sapphire/v1_0_11/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/sapphire/20240828/p5/factor_bank_inf_p5.xlsx',

    label = 'label_diff_pct_after',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/sapphire/20240828/p7/factor_df_p7_20160101_20210831.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/sapphire/profit/20240828/Sell_pct7_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p7/all/sapphire_xgb_importance_20200229_reg15_second_FSV8_all_label_diff_pct_after.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p7/all/sapphire_xgb_importance_20200831_reg15_second_FSV8_all_label_diff_pct_after.xlsx',
    xgb_fsv8_period3_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p7/all/sapphire_xgb_importance_20210228_reg15_second_FSV8_all_label_diff_pct_after.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p7/all/sapphire_xgb_importance_20200229_reg15_second_FSV10_all_label_diff_pct_after.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p7/all/sapphire_xgb_importance_20200831_reg15_second_FSV10_all_label_diff_pct_after.xlsx',
    xgb_fsv10_period3_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p7/all/sapphire_xgb_importance_20210228_reg15_second_FSV10_all_label_diff_pct_after.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p7/all/sapphire_xgb_importance_20200229_first_FSV11_all_label_diff_pct_after.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p7/all/sapphire_xgb_importance_20200831_first_FSV11_all_label_diff_pct_after.xlsx',
    xgb_fsv11_period3_fpath = f'/data/group/800463/xiely/factor_select/sapphire/fac_20240828/p7/all/sapphire_xgb_importance_20210228_first_FSV11_all_label_diff_pct_after.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/sapphire/20240828/p7/fsrs/fsrsv2_label_diff_pct_after_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/sapphire/20240828/p7/fsrs/fsrsv2_label_diff_pct_after_20160101_20200831.xlsx',
    fsrs_period3_fpath = '/data/group/800463/sunss/sapphire/20240828/p7/fsrs/fsrsv2_label_diff_pct_after_20160101_20210228.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/sapphire/fac_20240828/tsq/p7/fsci/fsci_label_diff_pct_after_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/sapphire/fac_20240828/tsq/p7/fsci/fsci_label_diff_pct_after_20160101_20200831.xlsx',
    fsci_period3_fpath = '/data/group/800463/xiely/factor_select/sapphire/fac_20240828/tsq/p7/fsci/fsci_label_diff_pct_after_20160101_20210228.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Sapphire/v1_0_11/config2/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Sapphire/v1_0_11/config2/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/sapphire/20240828/p7/factor_bank_inf_p7.xlsx',

    label = 'label_diff_pct_after',
)