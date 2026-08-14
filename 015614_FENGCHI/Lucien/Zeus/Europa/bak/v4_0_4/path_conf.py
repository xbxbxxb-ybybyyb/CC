# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

import os

version = 'v4_0_4'

#%% 根目录们
group_path = '/data/group/800463/'
fc_group_path = os.path.join(group_path, 'fengc/')
fc_path = '/data/user/015614/'

#%% 数据集
data_path = os.path.join(group_path, f'sunss/europa/20231101/')
# data_fpath = os.path.join(data_path, f'factor_df_filter_v1_20160101_20211231.pkl')
data_all_fpath = os.path.join(data_path, f'factor_df_all_20160101_20200531.pkl')

profit_data_fpath = f'/data/group/800463/sunss/profit/europa/20230925/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5'

#%% 因子筛选文件
xgb_imptc_path = os.path.join(group_path, f'xiely/factor_select/Europa/fac_20231101/')
xgb_imptc_pct_fsv8_period1_fpath = os.path.join(xgb_imptc_path, f'europa_total_xgb_importance_20191130_reg15_second_fac_20231101_FSV8_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv10_period1_fpath = os.path.join(xgb_imptc_path, f'europa_total_xgb_importance_20191130_reg15_second_fac_20231101_FSV10_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv11_period1_fpath = os.path.join(xgb_imptc_path, f'europa_total_xgb_importance_20191130_first_fac_20231101_FSV11_label_pct_graded.xlsx')

fsrs_imptc_path = os.path.join(group_path, f'sunss/europa/20231101/fsrs/')
fsrs_imptc_pct_period1_fpath = os.path.join(fsrs_imptc_path, 'fsrsv3_label_pct_graded_20160101_20191130.xlsx')

#%% 因子打分文件
factor_score_path = os.path.join(group_path, f'sunss/europa/20231101/')
factor_score_20191130_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_20191130.xlsx')

#%% 回测输出根路径
bt_out_path = os.path.join(fc_path, 'Zeus/backtest/')
pred_out_path = os.path.join(fc_path, 'Zeus/pred/')
log_path = os.path.join(fc_path, 'Zeus/logs/')
factor_path = os.path.join(fc_path, 'Zeus/factor_list/')
factor_select_path = os.path.join(fc_path, 'Zeus/factor_select/')

model_save_path = os.path.join(fc_path, 'Zeus/pred/')

#%% 因子筛选设置
fs_config = {
    'rffs': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_4/rffs_%s.pkl' % period.replace('_roll', '')",
    'rffs2': "'/data/user/015614/Zeus/factor_select/Europa/v4_0_4/rffs2_%s.pkl' % period.replace('_roll', '')",
}

#%% 标签设置
label_config = {
    'pct': 'label_pct_graded',
    # 'pctAfter': 'label_pct_after_graded'
}

#%% 时间设置
date_config = {
    # 'period1': dict(train_start_date=20160101, train_end_date=20190531, valid_start_date=20190601, valid_end_date=20191130,
    #                 test_start_date=20191201, test_end_date=20200531, fit_start_date=20200601, fit_end_date=20210531),
    'period1': dict(train_start_date=20160101, train_end_date=20190531, valid_start_date=20190601, valid_end_date=20191130,
                    test_start_date=20191201, test_end_date=20200531, fit_start_date=20200501, fit_end_date=20200531),
    'period1_roll': dict(train_start_date=20160101, train_end_date=20190531, valid_start_date=20190601, valid_end_date=20200531,
                    test_start_date=20191201, test_end_date=20200531, fit_start_date=20200501, fit_end_date=20200531),
    'period2': dict(train_start_date=20160101, train_end_date=20191130, valid_start_date=20191201, valid_end_date=20200531,
                    test_start_date=20200601, test_end_date=20201130, fit_start_date=20201201, fit_end_date=20211130),
    'period3': dict(train_start_date=20160101, train_end_date=20200531, valid_start_date=20200601, valid_end_date=20201130,
                    test_start_date=20201201, test_end_date=20210531, fit_start_date=20210601, fit_end_date=20220531),
    'period4': dict(train_start_date=20160101, train_end_date=20201130, valid_start_date=20201201, valid_end_date=20210531,
                    test_start_date=20210601, test_end_date=20211130, fit_start_date=20211201, fit_end_date=20221130),
    'period5': dict(train_start_date=20160101, train_end_date=20210531, valid_start_date=20210601, valid_end_date=20211130,
                    test_start_date=20211201, test_end_date=20220531, fit_start_date=20220601, fit_end_date=20230531),
    'period6': dict(train_start_date=20160101, train_end_date=20211130, valid_start_date=20211201, valid_end_date=20220531,
                    test_start_date=20220601, test_end_date=20221130, fit_start_date=20221201, fit_end_date=20231130),
}