# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

config1 = dict(
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
