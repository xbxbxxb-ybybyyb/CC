# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20230630/factor_df_sc_filter_mid_term_20170110_20230630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_mid_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_reg15_second_FSV8_all_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_reg15_second_FSV10_all_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_first_FSV11_all_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc_20221231.xlsx',

    label = 'label_pct_mid_term',
)

config2 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20230630/factor_df_sc_sw_high_filter_mid_term_20170110_20230630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_mid_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_reg15_second_FSV8_sw_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_reg15_second_FSV10_sw_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_first_FSV11_sw_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc_20221231.xlsx',

    label = 'label_pct_mid_term',
)

config3 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20230630/factor_df_sc_sw_low_filter_mid_term_20170110_20230630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_mid_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_reg15_second_FSV8_sw_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_reg15_second_FSV10_sw_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_first_FSV11_sw_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc_20221231.xlsx',

    label = 'label_pct_mid_term',
)

config4 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20230630/factor_df_sc_vol_low_filter_mid_term_20170110_20230630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_mid_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_reg15_second_FSV8_vol_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_reg15_second_FSV10_vol_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_first_FSV11_vol_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc_20221231.xlsx',

    label = 'label_pct_mid_term',
)

config5 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20230630/factor_df_sc_vol_high_filter_mid_term_20170110_20230630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_mid_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_reg15_second_FSV8_vol_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_reg15_second_FSV10_vol_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_first_FSV11_vol_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc_20221231.xlsx',

    label = 'label_pct_mid_term',
)


#----

config6 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20230630/factor_df_s1_filter_short_term_20170110_20230630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_s1_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/all/neptune_xgb_importance_%s_reg15_second_FSV8_all_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/all/neptune_xgb_importance_%s_reg15_second_FSV10_all_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/all/neptune_xgb_importance_%s_first_FSV11_all_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_s1ore_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_s1.xlsx',

    label = 'label_pct_short_term',
)

config7 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20230630/factor_df_s1_sw_high_filter_short_term_20170110_20230630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_s1_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/sw_high/neptune_xgb_importance_%s_reg15_second_FSV8_sw_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/sw_high/neptune_xgb_importance_%s_reg15_second_FSV10_sw_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/sw_high/neptune_xgb_importance_%s_first_FSV11_sw_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_s1ore_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_s1.xlsx',

    label = 'label_pct_short_term',
)

config8 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20230630/factor_df_s1_sw_low_filter_short_term_20170110_20230630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_s1_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/sw_low/neptune_xgb_importance_%s_reg15_second_FSV8_sw_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/sw_low/neptune_xgb_importance_%s_reg15_second_FSV10_sw_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/sw_low/neptune_xgb_importance_%s_first_FSV11_sw_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_s1ore_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_s1.xlsx',

    label = 'label_pct_short_term',
)

config9 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20230630/factor_df_s1_vol_low_filter_short_term_20170110_20230630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_s1_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/vol_low/neptune_xgb_importance_%s_reg15_second_FSV8_vol_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/vol_low/neptune_xgb_importance_%s_reg15_second_FSV10_vol_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/vol_low/neptune_xgb_importance_%s_first_FSV11_vol_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_s1ore_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_s1.xlsx',

    label = 'label_pct_short_term',
)

config10 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20230630/factor_df_s1_vol_high_filter_short_term_20170110_20230630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_s1_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/vol_high/neptune_xgb_importance_%s_reg15_second_FSV8_vol_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/vol_high/neptune_xgb_importance_%s_reg15_second_FSV10_vol_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/s1/vol_high/neptune_xgb_importance_%s_first_FSV11_vol_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_s1ore_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_s1.xlsx',

    label = 'label_pct_short_term',
)