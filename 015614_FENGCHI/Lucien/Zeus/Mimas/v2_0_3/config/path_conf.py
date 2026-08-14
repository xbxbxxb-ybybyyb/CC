# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20250911_mimas3/factor_df_s_20160101_20220331.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/20250911_mimas3/profit_s_0.10_0.10_500_1500_250_20.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_reg15_second_FSV8_s_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_reg15_second_FSV10_s_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_first_FSV11_s_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/mimas/20250911_mimas3/fsrs/fsrsv2pool_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Mimas/v2_0_3/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Mimas/v2_0_3/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20250911_mimas3/factor_bank_p.xlsx',

    label = 'label_pct_graded',
)

config2 = dict(
    data_fpath='/data/group/800463/sunss/mimas/20250911_mimas3/factor_df_s_20160101_20220331.pkl',
    profit_data_fpath=f'/data/group/800463/sunss/mimas/20250911_mimas3/profit_s_0.10_0.10_500_1500_250_20.pkl',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_reg15_second_FSV8_s_label_p2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_reg15_second_FSV10_s_label_p2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_first_FSV11_s_label_p2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/mimas/20250911_mimas3/fsrs/fsrsv2pool_label_p2_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config={
        'rffs': "'/data/user/015614/Zeus/factor_select/Mimas/v2_0_3/config1/rffs_%s.pkl' % period.replace('_roll', '')",
        'rffs2': "'/data/user/015614/Zeus/factor_select/Mimas/v2_0_3/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
    },

    factor_score_fpath=f'/data/group/800463/sunss/mimas/20250911_mimas3/factor_bank_p.xlsx',

    label='label_p2_graded',
)

config3 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20250911_mimas3/factor_df_s_20160101_20220331.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/20250911_mimas3/profit_s_0.10_0.10_500_1500_250_20.pkl',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_reg15_second_FSV8_s_label_TNv2t110.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_reg15_second_FSV10_s_label_TNv2t110.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_first_FSV11_s_label_TNv2t110.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/mimas/20250911_mimas3/fsrs/fsrsv2pool_label_v2o10_d1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Mimas/v2_0_3/config2/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Mimas/v2_0_3/config2/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20250911_mimas3/factor_bank_p.xlsx',

    label = 'label_TNv2t110',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/mimas/20250911_mimas3/factor_df_s_20160101_20220331.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/mimas/20250911_mimas3/profit_s_0.10_0.10_500_1500_250_20.pkl',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_reg15_second_FSV8_s_label_p5_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_reg15_second_FSV10_s_label_p5_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/mimas/fac_20250911_mimas3/s/mimas_xgb_importance_%s_first_FSV11_s_label_p5_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/mimas/20250911_mimas3/fsrs/fsrsv2pool_label_v2o10_d1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Mimas/v2_0_3/config2/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Mimas/v2_0_3/config2/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/mimas/20250911_mimas3/factor_bank_p.xlsx',

    label = 'label_p5_graded',
)