# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_filter_short_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_reg15_second_FSV8_all_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_reg15_second_FSV10_all_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_first_FSV11_all_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_short_term',
)

config2 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_filter_mid_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_mid_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_reg15_second_FSV8_all_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_reg15_second_FSV10_all_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_first_FSV11_all_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_mid_term',
)

config3 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_filter_long_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_long_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_reg15_second_FSV8_all_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_reg15_second_FSV10_all_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/all/neptune_xgb_importance_%s_first_FSV11_all_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_long_term',
)

#----

config4 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_sw_high_filter_short_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_reg15_second_FSV8_sw_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_reg15_second_FSV10_sw_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_first_FSV11_sw_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_short_term',
)

config5 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_sw_high_filter_mid_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_mid_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_reg15_second_FSV8_sw_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_reg15_second_FSV10_sw_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_first_FSV11_sw_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_mid_term',
)

config6 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_sw_high_filter_long_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_long_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_reg15_second_FSV8_sw_high_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_reg15_second_FSV10_sw_high_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_high/neptune_xgb_importance_%s_first_FSV11_sw_high_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_long_term',
)

# --- 
config7 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_sw_low_filter_short_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_reg15_second_FSV8_sw_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_reg15_second_FSV10_sw_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_first_FSV11_sw_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_short_term',
)

config8 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_sw_low_filter_mid_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_mid_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_reg15_second_FSV8_sw_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_reg15_second_FSV10_sw_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_first_FSV11_sw_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_mid_term',
)

config9 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_sw_low_filter_long_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_long_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_reg15_second_FSV8_sw_low_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_reg15_second_FSV10_sw_low_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/sw_low/neptune_xgb_importance_%s_first_FSV11_sw_low_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_long_term',
)

# ---
config10 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_vol_low_filter_short_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_reg15_second_FSV8_vol_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_reg15_second_FSV10_vol_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_first_FSV11_vol_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_short_term',
)

config11 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_vol_low_filter_mid_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_mid_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_reg15_second_FSV8_vol_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_reg15_second_FSV10_vol_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_first_FSV11_vol_low_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_mid_term',
)

config12 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_vol_low_filter_long_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_long_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_reg15_second_FSV8_vol_low_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_reg15_second_FSV10_vol_low_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_low/neptune_xgb_importance_%s_first_FSV11_vol_low_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_long_term',
)

# ---
config13 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_vol_high_filter_short_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_reg15_second_FSV8_vol_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_reg15_second_FSV10_vol_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_first_FSV11_vol_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_short_term',
)

config14 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_vol_high_filter_mid_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_mid_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_reg15_second_FSV8_vol_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_reg15_second_FSV10_vol_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_first_FSV11_vol_high_label_pct_mid_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_mid_term',
)

config15 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609/20170110_20211231/factor_df_sc_vol_high_filter_long_term_20170110_20211231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_sc_long_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_reg15_second_FSV8_vol_high_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_reg15_second_FSV10_vol_high_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609/sc/vol_high/neptune_xgb_importance_%s_first_FSV11_vol_high_label_pct_long_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609/factor_bank_inf_sc.xlsx',

    label = 'label_pct_long_term',
)