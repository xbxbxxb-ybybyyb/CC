# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250627/20170110_20200630/factor_df_sa_filter_short_term_20170110_20200630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250627/p2_profit_intervalTwap_sa_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/all/neptune_xgb_importance_%s_reg15_second_FSV8_all_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/all/neptune_xgb_importance_%s_reg15_second_FSV10_all_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/all/neptune_xgb_importance_%s_first_FSV11_all_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_saore_fpath = f'/data/group/800463/tangsq/neptune/20250627/factor_bank_inf_sa.xlsx',

    label = 'label_pct_short_term',
)

config2 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250627/20170110_20200630/factor_df_sa_sw_high_filter_short_term_20170110_20200630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250627/p2_profit_intervalTwap_sa_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/sw_high/neptune_xgb_importance_%s_reg15_second_FSV8_sw_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/sw_high/neptune_xgb_importance_%s_reg15_second_FSV10_sw_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/sw_high/neptune_xgb_importance_%s_first_FSV11_sw_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_saore_fpath = f'/data/group/800463/tangsq/neptune/20250627/factor_bank_inf_sa.xlsx',

    label = 'label_pct_short_term',
)

config3 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250627/20170110_20200630/factor_df_sa_sw_low_filter_short_term_20170110_20200630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250627/p2_profit_intervalTwap_sa_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/sw_low/neptune_xgb_importance_%s_reg15_second_FSV8_sw_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/sw_low/neptune_xgb_importance_%s_reg15_second_FSV10_sw_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/sw_low/neptune_xgb_importance_%s_first_FSV11_sw_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_saore_fpath = f'/data/group/800463/tangsq/neptune/20250627/factor_bank_inf_sa.xlsx',

    label = 'label_pct_short_term',
)

config4 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250627/20170110_20200630/factor_df_sa_vol_low_filter_short_term_20170110_20200630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250627/p2_profit_intervalTwap_sa_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/vol_low/neptune_xgb_importance_%s_reg15_second_FSV8_vol_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/vol_low/neptune_xgb_importance_%s_reg15_second_FSV10_vol_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/vol_low/neptune_xgb_importance_%s_first_FSV11_vol_low_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_saore_fpath = f'/data/group/800463/tangsq/neptune/20250627/factor_bank_inf_sa.xlsx',

    label = 'label_pct_short_term',
)

config5 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250627/20170110_20200630/factor_df_sa_vol_high_filter_short_term_20170110_20200630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250627/p2_profit_intervalTwap_sa_short_term_0.10_0.10.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/vol_high/neptune_xgb_importance_%s_reg15_second_FSV8_vol_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/vol_high/neptune_xgb_importance_%s_reg15_second_FSV10_vol_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250627/sa/vol_high/neptune_xgb_importance_%s_first_FSV11_vol_high_label_pct_short_term.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    factor_saore_fpath = f'/data/group/800463/tangsq/neptune/20250627/factor_bank_inf_sa.xlsx',

    label = 'label_pct_short_term',
)