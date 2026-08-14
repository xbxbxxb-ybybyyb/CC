# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

import os

version = 'v1_0_8'

#%% 根目录们
group_path = '/data/group/800463/'
fc_group_path = os.path.join(group_path, 'fengc/')
fc_path = '/data/user/015614/'

#%% 数据集
sapphire_v = 'p5'
data_path = os.path.join(group_path, f'sunss/sapphire/20240720/{sapphire_v}/')
# data_fpath = os.path.join(data_path, f'factor_df_{sapphire_v}_20160101_20200531.pkl')
data_fpath = os.path.join(f'/data/user/018107/share_file/for_fc/sapphire/20240720/{sapphire_v}/', f'factor_df_{sapphire_v}_20160101_20210531.pkl')

profit_data_fpath = f'/data/group/800463/sunss/sapphire/profit/20240720/Sell_pct5_0.15_2000_300_SH250_SZ20.h5'

#%% 因子筛选文件
xgb_imptc_path = os.path.join(group_path, f'xiely/factor_select/sapphire/fac_20240720/{sapphire_v}/all/')
xgb_imptc_pct_fsv8_period1_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20191130_reg15_second_FSV8_all_label_diff_pct.xlsx')
xgb_imptc_pct_fsv8_period2_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200331_reg15_second_FSV8_all_label_diff_pct.xlsx')
xgb_imptc_pct_fsv8_period3_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200930_reg15_second_FSV8_all_label_diff_pct.xlsx')
xgb_imptc_pct_fsv8_period4_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20210331_reg15_second_FSV8_all_label_diff_pct.xlsx')
xgb_imptc_pct_fsv10_period1_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20191130_reg15_second_FSV10_all_label_diff_pct.xlsx')
xgb_imptc_pct_fsv10_period2_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200331_reg15_second_FSV10_all_label_diff_pct.xlsx')
xgb_imptc_pct_fsv10_period3_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200930_reg15_second_FSV10_all_label_diff_pct.xlsx')
xgb_imptc_pct_fsv10_period4_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20210331_reg15_second_FSV10_all_label_diff_pct.xlsx')
xgb_imptc_pct_fsv11_period1_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20191130_first_FSV11_all_label_diff_pct.xlsx')
xgb_imptc_pct_fsv11_period2_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200331_first_FSV11_all_label_diff_pct.xlsx')
xgb_imptc_pct_fsv11_period3_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200930_first_FSV11_all_label_diff_pct.xlsx')
xgb_imptc_pct_fsv11_period4_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20210331_first_FSV11_all_label_diff_pct.xlsx')

xgb_imptc_pctAfter_fsv8_period1_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20191130_reg15_second_FSV8_all_label_diff_pct_after.xlsx')
xgb_imptc_pctAfter_fsv8_period2_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200331_reg15_second_FSV8_all_label_diff_pct_after.xlsx')
xgb_imptc_pctAfter_fsv8_period3_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200930_reg15_second_FSV8_all_label_diff_pct_after.xlsx')
xgb_imptc_pctAfter_fsv8_period4_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20210331_reg15_second_FSV8_all_label_diff_pct_after.xlsx')
xgb_imptc_pctAfter_fsv10_period1_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20191130_reg15_second_FSV10_all_label_diff_pct_after.xlsx')
xgb_imptc_pctAfter_fsv10_period2_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200331_reg15_second_FSV10_all_label_diff_pct_after.xlsx')
xgb_imptc_pctAfter_fsv10_period3_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200930_reg15_second_FSV10_all_label_diff_pct_after.xlsx')
xgb_imptc_pctAfter_fsv10_period4_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20210331_reg15_second_FSV10_all_label_diff_pct_after.xlsx')
xgb_imptc_pctAfter_fsv11_period1_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20191130_first_FSV11_all_label_diff_pct_after.xlsx')
xgb_imptc_pctAfter_fsv11_period2_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200331_first_FSV11_all_label_diff_pct_after.xlsx')
xgb_imptc_pctAfter_fsv11_period3_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20200930_first_FSV11_all_label_diff_pct_after.xlsx')
xgb_imptc_pctAfter_fsv11_period4_fpath = os.path.join(xgb_imptc_path, f'sapphire_xgb_importance_20210331_first_FSV11_all_label_diff_pct_after.xlsx')


fsrs_imptc_path = os.path.join(group_path, f'sunss/sapphire/20240720/{sapphire_v}/fsrs/')
fsrs_imptc_pct_period1_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_diff_pct_20160101_20191130.xlsx')
fsrs_imptc_pct_period2_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_diff_pct_20160101_20200331.xlsx')
fsrs_imptc_pct_period3_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_diff_pct_20160101_20200930.xlsx')
fsrs_imptc_pct_period4_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_diff_pct_20160101_20210331.xlsx')

fsrs_imptc_pctAfter_period1_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_diff_pct_after_20160101_20191130.xlsx')
fsrs_imptc_pctAfter_period2_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_diff_pct_after_20160101_20200331.xlsx')
fsrs_imptc_pctAfter_period3_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_diff_pct_after_20160101_20200930.xlsx')
fsrs_imptc_pctAfter_period4_fpath = os.path.join(fsrs_imptc_path, 'fsrsv2_label_diff_pct_after_20160101_20210331.xlsx')

#%% 因子打分文件
factor_score_path = os.path.join(group_path, f'sunss/Sapphire/20240720/{sapphire_v}/')
factor_score_20191130_fpath = os.path.join(factor_score_path, f'factor_bank_inf_{sapphire_v}.xlsx')
factor_score_20200331_fpath = os.path.join(factor_score_path, f'factor_bank_inf_{sapphire_v}.xlsx')
factor_score_20200930_fpath = os.path.join(factor_score_path, f'factor_bank_inf_{sapphire_v}.xlsx')
factor_score_20210331_fpath = os.path.join(factor_score_path, f'factor_bank_inf_{sapphire_v}.xlsx')

#%% 回测输出根路径
bt_out_path = os.path.join(fc_path, 'Zeus/backtest/')
pred_out_path = os.path.join(fc_path, 'Zeus/pred/')
log_path = os.path.join(fc_path, 'Zeus/logs/')
factor_path = os.path.join(fc_path, 'Zeus/factor_list/')
factor_select_path = os.path.join(fc_path, 'Zeus/factor_select/')

model_save_path = os.path.join(fc_path, 'Zeus/pred/')

#%% 因子筛选设置
fs_config = {
    'rffs': "'/data/user/015614/Zeus/factor_select/Sapphire/v1_0_8/rffs_%s.pkl' % period"
}

#%% 标签设置
label_config = {
    'pct': 'label_diff_pct',
    'pctAfter': 'label_diff_pct_after'
}

#%% 时间设置
date_config = {
    'period1': dict(train_start_date=20160101, train_end_date=20190531, valid_start_date=20190601, valid_end_date=20191130,
                    test_start_date=20191201, test_end_date=20200531, fit_start_date=20200601, fit_end_date=20210531),
    # 'period1': dict(train_start_date=20160101, train_end_date=20190531, valid_start_date=20190601, valid_end_date=20191130,
    #                 test_start_date=20191201, test_end_date=20200531, fit_start_date=20200501, fit_end_date=20200531),
    'period1_roll': dict(train_start_date=20160101, train_end_date=20190531, valid_start_date=20190601, valid_end_date=20200531,
                         test_start_date=20191201, test_end_date=20200531, fit_start_date=20200501, fit_end_date=20200531),
    'period2': dict(train_start_date=20160101, train_end_date=20191130, valid_start_date=20191201, valid_end_date=20200531,
                    test_start_date=20200601, test_end_date=20201130, fit_start_date=20201201, fit_end_date=20211130),
    # 'period2': dict(train_start_date=20160101, train_end_date=20191130, valid_start_date=20191201, valid_end_date=20200531,
    #                 test_start_date=20200601, test_end_date=20201130, fit_start_date=20201101, fit_end_date=20201130),
    'period2_roll': dict(train_start_date=20160101, train_end_date=20191130, valid_start_date=20191201, valid_end_date=20201130,
                         test_start_date=20200601, test_end_date=20201130, fit_start_date=20201101, fit_end_date=20201130),
    'period3': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20201130,
                    test_start_date=20201201, test_end_date=20210531, fit_start_date=20210601, fit_end_date=20220531),
    # 'period3': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20201130,
    #                 test_start_date=20201201, test_end_date=20210531, fit_start_date=20210501, fit_end_date=20210531),
    'period3_roll': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20210531,
                         test_start_date=20201201, test_end_date=20210531, fit_start_date=20210501, fit_end_date=20210531),

    'period4': dict(train_start_date=20160101, train_end_date=20201130, valid_start_date=20201201, valid_end_date=20210531,
                    test_start_date=20210601, test_end_date=20211130, fit_start_date=20211201, fit_end_date=20221130),
    # 'period4': dict(train_start_date=20160101, train_end_date=20201130, valid_start_date=20201201, valid_end_date=20210531,
    #                 test_start_date=20210601, test_end_date=20211130, fit_start_date=20211101, fit_end_date=20211130),
    'period4_roll': dict(train_start_date=20160101, train_end_date=20201130, valid_start_date=20201201, valid_end_date=20211130,
                         test_start_date=20210601, test_end_date=20211130, fit_start_date=20211101, fit_end_date=20211130),

    # 'period5': dict(train_start_date=20160101, train_end_date=20210531, valid_start_date=20210601, valid_end_date=20211130,
    #                 test_start_date=20211201, test_end_date=20220531, fit_start_date=20220601, fit_end_date=20230531),
    'period5': dict(train_start_date=20160101, train_end_date=20210531, valid_start_date=20210601, valid_end_date=20211130,
                    test_start_date=20211201, test_end_date=20220531, fit_start_date=20220501, fit_end_date=20220531),
    'period5_roll': dict(train_start_date=20160101, train_end_date=20210531, valid_start_date=20210601, valid_end_date=20220531,
                         test_start_date=20211201, test_end_date=20220531, fit_start_date=20220501, fit_end_date=20220531),

    # 'period6': dict(train_start_date=20160101, train_end_date=20211130, valid_start_date=20211201, valid_end_date=20220531,
    #                 test_start_date=20220601, test_end_date=20221130, fit_start_date=20221201, fit_end_date=20231130),
    'period6': dict(train_start_date=20160101, train_end_date=20211130, valid_start_date=20211201, valid_end_date=20220531,
                    test_start_date=20220601, test_end_date=20221130, fit_start_date=20221101, fit_end_date=20221130),
    'period6_roll': dict(train_start_date=20160101, train_end_date=20211130, valid_start_date=20211201, valid_end_date=20221130,
                         test_start_date=20220601, test_end_date=20221130, fit_start_date=20221101, fit_end_date=20221130),

    # 'period7': dict(train_start_date=20160101, train_end_date=20220531, valid_start_date=20220601, valid_end_date=20221130,
    #                 test_start_date=20221201, test_end_date=20230531, fit_start_date=20230601, fit_end_date=20231130),
    'period7': dict(train_start_date=20160101, train_end_date=20220531, valid_start_date=20220601, valid_end_date=20221130,
                    test_start_date=20221201, test_end_date=20230531, fit_start_date=20230501, fit_end_date=20230531),
    'period7_roll': dict(train_start_date=20160101, train_end_date=20220531, valid_start_date=20220601, valid_end_date=20230531,
                         test_start_date=20221201, test_end_date=20230531, fit_start_date=20230501, fit_end_date=20230531),

    # 'period8': dict(train_start_date=20160101, train_end_date=20221130, valid_start_date=20221201, valid_end_date=20230531,
    #                 test_start_date=20230601, test_end_date=20231130, fit_start_date=20231201, fit_end_date=20240531),
    'period8': dict(train_start_date=20160101, train_end_date=20221130, valid_start_date=20221201, valid_end_date=20230531,
                    test_start_date=20230601, test_end_date=20231130, fit_start_date=20231101, fit_end_date=20231130),
    'period8_roll': dict(train_start_date=20160101, train_end_date=20221130, valid_start_date=20221201, valid_end_date=20231130,
                    test_start_date=20230601, test_end_date=20231130, fit_start_date=20231101, fit_end_date=20231130),
}