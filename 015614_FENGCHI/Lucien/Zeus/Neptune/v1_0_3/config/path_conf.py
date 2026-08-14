# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250526/factor_df_s1_20170110_20191231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/20250526/factor_df_s1_20170110_20191231.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250526/all/neptune_xgb_importance_%s_reg15_second_FSV8_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250526/all/neptune_xgb_importance_%s_reg15_second_FSV10_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250526/all/neptune_xgb_importance_%s_first_FSV11_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/neptune/20250526/fsrs_all/fsrsv2pool_label_t2o9d1_pos_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_3/config1/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_3/config1/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250526/factor_bank_inf_s1.xlsx',

    label = 'label_t2o9d1_pos',
)


#%% 分场景
config2 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250526/factor_df_s1_scene_low_filter_20170110_20191231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/20250526/factor_df_s1_scene_low_filter_20170110_20191231.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250526/all/neptune_xgb_importance_%s_reg15_second_FSV8_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250526/all/neptune_xgb_importance_%s_reg15_second_FSV10_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250526/all/neptune_xgb_importance_%s_first_FSV11_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/neptune/20250526/fsrs_all/fsrsv2pool_label_t2o9d1_pos_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_3/config2/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_3/config2/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250526/factor_bank_inf_s1.xlsx',

    label = 'label_t2o9d1_pos',
)

config3 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250526/factor_df_s1_scene_high_filter_20170110_20191231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/20250526/factor_df_s1_scene_high_filter_20170110_20191231.pkl',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250526/all/neptune_xgb_importance_%s_reg15_second_FSV8_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250526/all/neptune_xgb_importance_%s_reg15_second_FSV10_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250526/all/neptune_xgb_importance_%s_first_FSV11_all_label_t2o9d1_pos.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    fsrs_fpath = "'/data/group/800463/sunss/neptune/20250526/fsrs_all/fsrsv2pool_label_t2o9d1_pos_20160101_%s.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['valid_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_3/config3/rffs_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v1_0_3/config3/rffs2_%s.pkl' % period.replace('_roll', '').replace('_fit', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250526/factor_bank_inf_s1.xlsx',

    label = 'label_t2o9d1_pos',
)