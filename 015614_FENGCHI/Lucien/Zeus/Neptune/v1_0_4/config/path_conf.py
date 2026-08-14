# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250528/factor_df_s1_filter_20170110_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/20250528/factor_df_s1_filter_20170110_20210630.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/all/neptune_xgb_importance_%s_reg15_second_FSV8_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/all/neptune_xgb_importance_%s_reg15_second_FSV10_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/all/neptune_xgb_importance_%s_first_FSV11_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/neptune/20250528/fsrs_all/fsrsv2pool_label_t2o9d1_pos_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config1/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config1/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250528/factor_bank_inf_s1.xlsx',

    label = 'label_t2o9d1_pos',
)


#%% 分场景
config2 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250528/factor_df_s1_sw_low_filter_20170110_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/20250528/factor_df_s1_sw_low_filter_20170110_20210630.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/sw_low/neptune_xgb_importance_%s_reg15_second_FSV8_sw_low_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/sw_low/neptune_xgb_importance_%s_reg15_second_FSV10_sw_low_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/sw_low/neptune_xgb_importance_%s_first_FSV11_sw_low_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/neptune/20250528/fsrs_all/fsrsv2pool_label_t2o9d1_pos_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config2/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config2/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250528/factor_bank_inf_s1.xlsx',

    label = 'label_t2o9d1_pos',
)

config3 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250528/factor_df_s1_sw_high_filter_20170110_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/20250528/factor_df_s1_sw_high_filter_20170110_20210630.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/sw_high/neptune_xgb_importance_%s_reg15_second_FSV8_sw_high_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/sw_high/neptune_xgb_importance_%s_reg15_second_FSV10_sw_high_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/sw_high/neptune_xgb_importance_%s_first_FSV11_sw_high_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/neptune/20250528/fsrs_all/fsrsv2pool_label_t2o9d1_pos_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config3/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config3/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250528/factor_bank_inf_s1.xlsx',

    label = 'label_t2o9d1_pos',
)

config4 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250528/factor_df_s1_vol_low_filter_20170110_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/20250528/factor_df_s1_vol_low_filter_20170110_20210630.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/vol_low/neptune_xgb_importance_%s_reg15_second_FSV8_vol_low_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/vol_low/neptune_xgb_importance_%s_reg15_second_FSV10_vol_low_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/vol_low/neptune_xgb_importance_%s_first_FSV11_vol_low_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/neptune/20250528/fsrs_all/fsrsv2pool_label_t2o9d1_pos_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config4/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config4/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250528/factor_bank_inf_s1.xlsx',

    label = 'label_t2o9d1_pos',
)

config5 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250528/factor_df_s1_vol_high_filter_20170110_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/20250528/factor_df_s1_vol_high_filter_20170110_20210630.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/vol_high/neptune_xgb_importance_%s_reg15_second_FSV8_vol_high_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/vol_high/neptune_xgb_importance_%s_reg15_second_FSV10_vol_high_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250528/vol_high/neptune_xgb_importance_%s_first_FSV11_vol_high_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/neptune/20250528/fsrs_all/fsrsv2pool_label_t2o9d1_pos_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config5/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config5/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250528/factor_bank_inf_s1.xlsx',

    label = 'label_t2o9d1_pos',
)

config6 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250603/factor_df_sc_filter_20170110_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/20250603/factor_df_sc_filter_20170110_20210630.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250603/vol_high/neptune_xgb_importance_%s_reg15_second_FSV8_vol_high_label_t2o10dc_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250603/vol_high/neptune_xgb_importance_%s_reg15_second_FSV10_vol_high_label_t2o10dc_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250603/vol_high/neptune_xgb_importance_%s_first_FSV11_vol_high_label_t2o10dc_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/neptune/20250603/fsrs_all/fsrsv2pool_label_t2o10dc_pos_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config6/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config6/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250603/factor_bank_inf_s1.xlsx',

    label = 'label_t2o10dc_pos',
)

config7 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250603/factor_df_sc_vol_high_filter_20170110_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/20250603/factor_df_sc_vol_high_filter_20170110_20210630.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250603/vol_high/neptune_xgb_importance_%s_reg15_second_FSV8_vol_high_label_t2o10dc_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250603/vol_high/neptune_xgb_importance_%s_reg15_second_FSV10_vol_high_label_t2o10dc_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250603/vol_high/neptune_xgb_importance_%s_first_FSV11_vol_high_label_t2o10dc_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/neptune/20250603/fsrs_all/fsrsv2pool_label_t2o10dc_pos_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config7/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config7/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250603/factor_bank_inf_s1.xlsx',

    label = 'label_t2o10dc_pos',
)

config8 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250603/factor_df_sc_vol_high_filter_20170110_20210630.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/20250603/factor_df_sc_vol_high_filter_20170110_20210630.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250603/vol_high/neptune_xgb_importance_%s_reg15_second_FSV8_vol_high_label_t2o10dc_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250603/vol_high/neptune_xgb_importance_%s_reg15_second_FSV10_vol_high_label_t2o10dc_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250603/vol_high/neptune_xgb_importance_%s_first_FSV11_vol_high_label_t2o10dc_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/neptune/20250603/fsrs_all/fsrsv2pool_label_t2o10dc_pos_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config8/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_4/config8/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250603/factor_bank_inf_s1.xlsx',

    label = 'label_t2o10dc_pos',
)