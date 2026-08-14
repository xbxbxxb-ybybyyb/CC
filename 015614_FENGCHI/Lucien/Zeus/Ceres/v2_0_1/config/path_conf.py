# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/sunss/ceres/20250828_v/factor_df_v_20160101_20210930.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/ceres/20250828_v/profit_v_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/ceres/fac_20250828_v/v/ceres_xgb_importance_%s_reg15_second_FSV8_v_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/ceres/fac_20250828_v/v/ceres_xgb_importance_%s_reg15_second_FSV10_v_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/ceres/fac_20250828_v/v/ceres_xgb_importance_%s_first_FSV11_v_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/ceres/20250828_v/fsrs/fsrsv2pool_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Ceres/v2_0_1/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Ceres/v2_0_1/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/ceres/20250828_v/factor_bank_v.xlsx',

    label = 'label_pct_graded',
)

config2 = dict(
    data_fpath='/data/group/800463/sunss/ceres/20250828_v/factor_df_v_20160101_20210930.pkl',
    profit_data_fpath=f'/data/group/800463/sunss/ceres/20250828_v/profit_v_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250828_v/v/ceres_xgb_importance_%s_reg15_second_FSV8_v_label_TNv2To10_v.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250828_v/v/ceres_xgb_importance_%s_reg15_second_FSV10_v_label_TNv2To10_v.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/ceres/fac_20250828_v/v/ceres_xgb_importance_%s_first_FSV11_v_label_TNv2To10_v.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/ceres/20250828_v/fsrs/fsrsv2pool_label_TNv2To10_v_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config={
        'rffs': "'/data/user/015614/Zeus/factor_select/Ceres/v2_0_1/config1/rffs_%s.pkl' % period.replace('_roll', '')",
        'rffs2': "'/data/user/015614/Zeus/factor_select/Ceres/v2_0_1/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
    },

    factor_score_fpath=f'/data/group/800463/sunss/ceres/20250828_v/factor_bank_v.xlsx',

    label='label_TNv2To10_v',
)

config3 = dict(
    data_fpath = '/data/group/800463/sunss/ceresp4/20250828_v/factor_df_v_20160101_20210930.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/ceres/20250828_v/profit_v_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/ceresp4/fac_20250828_v/v/ceresp4_xgb_importance_%s_reg15_second_FSV8_v_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/ceresp4/fac_20250828_v/v/ceresp4_xgb_importance_%s_reg15_second_FSV10_v_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/ceresp4/fac_20250828_v/v/ceresp4_xgb_importance_%s_first_FSV11_v_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/ceres/20250828_v/fsrs/fsrsv2pool_label_v2o10_d1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Ceres/v2_0_1/config2/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Ceres/v2_0_1/config2/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/ceresp4/20250828_v/factor_bank_v.xlsx',

    label = 'label_pct_graded',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/ceres/20250828_v/factor_df_v_20160101_20210930.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/ceres/20250828_v/profit_v_0.10_0.10_500_1500_250_20.h5',

    xgb_fsv8_fpath="'/data/group/800463/xiely/factor_select/ceresp4/fac_20250828_v/v/ceresp4_xgb_importance_%s_reg15_second_FSV8_v_label_TNv2To10_v.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath="'/data/group/800463/xiely/factor_select/ceresp4/fac_20250828_v/v/ceresp4_xgb_importance_%s_reg15_second_FSV10_v_label_TNv2To10_v.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath="'/data/group/800463/xiely/factor_select/ceresp4/fac_20250828_v/v/ceresp4_xgb_importance_%s_first_FSV11_v_label_TNv2To10_v.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/ceres/20250828_v/fsrs/fsrsv2pool_label_v2o10_d1_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Ceres/v2_0_1/config2/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Ceres/v2_0_1/config2/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/ceresp4/20250828_v/factor_bank_v.xlsx',

    label = 'label_TNv2To10_v',
)