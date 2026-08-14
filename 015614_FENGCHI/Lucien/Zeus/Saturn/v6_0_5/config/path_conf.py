# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

config1 = dict(
    data_fpath = '/data/group/800463/sunss/sr/20250714/factor_df_sr_20160101_20201231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/sr/profit/20250714/sr_profit_interval_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/sr/fac_20250714/all/sr_xgb_importance_%s_reg15_second_FSV8_all_label_TNv2t10.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/sr/fac_20250714/all/sr_xgb_importance_%s_reg15_second_FSV10_all_label_TNv2t10.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/sr/fac_20250714/all/sr_xgb_importance_%s_first_FSV11_all_label_TNv2t10.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/sr/20250714/fsrs/fsrsv2pool_label_TNv2t10_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/sr/20250724/fsci_sr/fsci_label_TNv2t10_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/sr/v6_0_5/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/sr/v6_0_5/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/sr/20250714/factor_bank_inf_all.xlsx',

    label = 'label_TNv2t10',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/sr/20250714/factor_df_sr_20160101_20201231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/sr/profit/20250714/sr_profit_interval_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/sr/fac_20250714/all/sr_xgb_importance_%s_reg15_second_FSV8_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/sr/fac_20250714/all/sr_xgb_importance_%s_reg15_second_FSV10_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/sr/fac_20250714/all/sr_xgb_importance_%s_first_FSV11_all_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/sr/20250714/fsrs/fsrsv2pool_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/sr/20250724/fsci_sr/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/sr/v6_0_5/config2/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/sr/v6_0_5/config2/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/sr/20250714/factor_bank_inf_all.xlsx',

    label = 'label_pct_graded',
)

config3 = dict(
    data_fpath = '/data/group/800463/sunss/sr/20250714/factor_df_sr_20160101_20201231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/sr/profit/20250714/sr_profit_interval_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/sr/fac_20250714/all/sr_xgb_importance_%s_reg15_second_FSV8_all_label_p5_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/sr/fac_20250714/all/sr_xgb_importance_%s_reg15_second_FSV10_all_label_p5_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/sr/fac_20250714/all/sr_xgb_importance_%s_first_FSV11_all_label_p5_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/sr/20250714/fsrs/fsrsv2pool_label_p5_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/sr/20250724/fsci_sr/fsci_label_p5_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/sr/v6_0_5/config3/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/sr/v6_0_5/config3/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/sr/20250714/factor_bank_inf_all.xlsx',

    label = 'label_p5_graded',
)
