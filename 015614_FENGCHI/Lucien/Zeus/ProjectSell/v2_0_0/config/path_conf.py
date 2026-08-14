# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

config1 = dict(
    data_fpath = '/data/group/800463/sunss/project_sell/20240828/factor_df_v1_20160101_20210228.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/project_sell/profit/20240828/Sell_v1_0.10_2000_300_SH250_SZ20.h5',

    xgb_fsv8_period1_fpath = f'/data/group/800463/xiely/factor_select/project_sell/fac_20240828/all/project_sell_xgb_importance_20200229_reg15_second_FSV8_all_label_diff_pct.xlsx',
    xgb_fsv8_period2_fpath = f'/data/group/800463/xiely/factor_select/project_sell/fac_20240828/all/project_sell_xgb_importance_20200831_reg15_second_FSV8_all_label_diff_pct.xlsx',
    xgb_fsv10_period1_fpath = f'/data/group/800463/xiely/factor_select/project_sell/fac_20240828/all/project_sell_xgb_importance_20200229_reg15_second_FSV10_all_label_diff_pct.xlsx',
    xgb_fsv10_period2_fpath = f'/data/group/800463/xiely/factor_select/project_sell/fac_20240828/all/project_sell_xgb_importance_20200831_reg15_second_FSV10_all_label_diff_pct.xlsx',
    xgb_fsv11_period1_fpath = f'/data/group/800463/xiely/factor_select/project_sell/fac_20240828/all/project_sell_xgb_importance_20200229_first_FSV11_all_label_diff_pct.xlsx',
    xgb_fsv11_period2_fpath = f'/data/group/800463/xiely/factor_select/project_sell/fac_20240828/all/project_sell_xgb_importance_20200831_first_FSV11_all_label_diff_pct.xlsx',
    fsrs_period1_fpath = '/data/group/800463/sunss/project_sell/20240828/fsrs/fsrsv2_label_diff_pct_20160101_20200229.xlsx',
    fsrs_period2_fpath = '/data/group/800463/sunss/project_sell/20240828/fsrs/fsrsv2_label_diff_pct_20160101_20200831.xlsx',
    fsci_period1_fpath = '/data/group/800463/xiely/factor_select/project_sell/fac_20240828/tsq/fsci/fsci_label_diff_pct_20160101_20200229.xlsx',
    fsci_period2_fpath = '/data/group/800463/xiely/factor_select/project_sell/fac_20240828/tsq/fsci/fsci_label_diff_pct_20160101_20200831.xlsx',

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/ProjectSell/v2_0_0/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/ProjectSell/v2_0_0/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/project_sell/20240828/factor_bank_inf_v1.xlsx',

    label = 'label_diff_pct',
)