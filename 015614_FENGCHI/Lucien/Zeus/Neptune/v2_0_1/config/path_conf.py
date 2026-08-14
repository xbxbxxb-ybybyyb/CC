# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01


config1 = dict(
    data_fpath = '/data/group/800463/tangsq/neptune/20250609_a/factor_df_s1_filter_20170110_20191231.pkl',
    profit_data_fpath = f'/data/group/800463/tangsq/neptune/profit/20250609_a/neg/zz1000_profit_interval.h5',

    xgb_fsv8_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609_a/s1/all/neptune_xgb_importance_%s_reg15_second_FSV8_all_label_ta2to10_neg.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv10_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609_a/s1/all/neptune_xgb_importance_%s_reg15_second_FSV10_all_label_ta2to10_neg.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",
    xgb_fsv11_fpath = "'/data/group/800463/xiely/factor_select/neptune/fac_20250609_a/s1/all/neptune_xgb_importance_%s_first_FSV11_all_label_ta2to10_neg.xlsx' % (DATE_CONFIG[period.replace('_roll', '')]['train_end_date'])",

    fs_config = {
            'rffs': "'/data/user/015614/Zeus/factor_select/Neptune/v2_0_1/config1/rffs_%s.pkl' % period.replace('_roll', '')",
            'rffs2': "'/data/user/015614/Zeus/factor_select/Neptune/v2_0_1/config1/rffs2_%s.pkl' % period.replace('_roll', '')",
        },

    factor_score_fpath = f'/data/group/800463/tangsq/neptune/20250609_a/factor_bank_inf_s1.xlsx',

    label = 'label_ta2to10_neg',
)