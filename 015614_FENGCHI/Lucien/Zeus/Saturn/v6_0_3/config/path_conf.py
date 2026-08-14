# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

config1 = dict(
    data_fpath = '/data/group/800463/sunss/saturn/20250721/factor_df_t_20160101_20231231_20240701_20241231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/saturn/profit/20250721/p2_profit_interval_t_0.10_0.10_1000_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_reg15_second_FSV8_t_label_v2t10.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_reg15_second_FSV10_t_label_v2t10.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_first_FSV11_t_label_v2t10.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/saturn/20250721/fsrs/fsrsv2pool_label_v2t10_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/saturn/20250721/fsci_t/fsci_label_v2t10_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/saturn/v6_0_3/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/saturn/v6_0_3/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/saturn/20250721/factor_bank_inf_t.xlsx',

    label = 'label_v2t10',
)

config2 = dict(
    data_fpath = '/data/group/800463/sunss/saturn/20250721/factor_df_t_20160101_20231231_20240701_20241231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/saturn/profit/20250721/p2_profit_interval_t_0.10_0.10_1000_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_reg15_second_FSV8_t_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_reg15_second_FSV10_t_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_first_FSV11_t_label_pct_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/saturn/20250721/fsrs/fsrsv2pool_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsci_fpath = "'/data/group/800463/tangsq/saturn/20250721/fsci_t/fsci_label_pct_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/saturn/v6_0_3/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/saturn/v6_0_3/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/saturn/20250721/factor_bank_inf_t.xlsx',

    label = 'label_pct_graded',
)

config3 = dict(
    data_fpath = '/data/group/800463/sunss/saturn/20250721/factor_df_t_20160101_20231231_20240701_20241231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/saturn/profit/20250721/p2_profit_interval_t_0.10_0.10_1000_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_reg15_second_FSV8_t_label_p5_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_reg15_second_FSV10_t_label_p5_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_first_FSV11_t_label_p5_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/saturn/20250721/fsrs/fsrsv2pool_label_p5_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/saturn/20250721/fsci_t/fsci_label_p5_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/saturn/v6_0_3/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/saturn/v6_0_3/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/saturn/20250721/factor_bank_inf_t.xlsx',

    label = 'label_p5_graded',
)

config4 = dict(
    data_fpath = '/data/group/800463/sunss/saturn/20250721/factor_df_t_20160101_20231231_20240701_20241231.pkl',
    profit_data_fpath = f'/data/group/800463/sunss/saturn/profit/20250721/p2_profit_interval_t_0.10_0.10_1000_1500_250_20.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_reg15_second_FSV8_t_label_p2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_reg15_second_FSV10_t_label_p2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/saturn/fac_20250721/t/saturn_xgb_importance_%s_first_FSV11_t_label_p2_graded.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath="'/data/group/800463/sunss/saturn/20250721/fsrs/fsrsv2pool_label_p2_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsci_fpath="'/data/group/800463/tangsq/saturn/20250721/fsci_t/fsci_label_p2_graded_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/saturn/v6_0_3/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/saturn/v6_0_3/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/sunss/saturn/20250721/factor_bank_inf_t.xlsx',

    label = 'label_p2_graded',
)