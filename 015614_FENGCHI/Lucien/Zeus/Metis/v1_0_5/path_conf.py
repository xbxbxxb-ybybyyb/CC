# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

import os

version = 'v1_0_5'

#%% 根目录们
group_path = '/data/group/800463/'
fc_group_path = os.path.join(group_path, 'fengc/')
fc_path = '/data/user/015614/'

#%% 数据集
metis_v = 'v1'
data_path = os.path.join(group_path, f'sunss/metis/20230821/{metis_v}/')
data_fpath = os.path.join(data_path, f'factor_df_all_20160101_20210930_graded.pkl')

profit_data_fpath = f'/data/group/800463/sunss/profit/metis/20230821/v1/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.pkl'

#%% 因子筛选文件
xgb_imptc_path = os.path.join(group_path, f'xiely/factor_select/Metis/V1/fac_20230821/')
xgb_imptc_pct_fsv8_period1_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20190930_reg15_second_fac_20230821_FSV8_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv8_period2_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20200331_reg15_second_fac_20230821_FSV8_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv8_period3_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20200930_reg15_second_fac_20230821_FSV8_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv8_period4_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20210331_reg15_second_fac_20230821_FSV8_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv10_period1_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20190930_reg15_second_fac_20230821_FSV10_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv10_period2_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20200331_reg15_second_fac_20230821_FSV10_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv10_period3_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20200930_reg15_second_fac_20230821_FSV10_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv10_period4_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20210331_reg15_second_fac_20230821_FSV10_all_label_pct_graded.xlsx')
xgb_imptc_pct_fsv11_period1_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20190930_first_fac_20230821_FSV11_label_pct_graded.xlsx')
xgb_imptc_pct_fsv11_period2_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20200331_first_fac_20230821_FSV11_label_pct_graded.xlsx')
xgb_imptc_pct_fsv11_period3_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20200930_first_fac_20230821_FSV11_label_pct_graded.xlsx')
xgb_imptc_pct_fsv11_period4_fpath = os.path.join(xgb_imptc_path, f'metis_{metis_v}_xgb_importance_20210331_first_fac_20230821_FSV11_label_pct_graded.xlsx')


fsrs_imptc_path = os.path.join(group_path, f'sunss/metis/20230821/{metis_v}/fsrs/')
fsrs_imptc_pct_period1_fpath = os.path.join(fsrs_imptc_path, 'fsrsv3_label_pct_graded_20160101_20190930.xlsx')
fsrs_imptc_pct_period2_fpath = os.path.join(fsrs_imptc_path, 'fsrsv3_label_pct_graded_20160101_20200331.xlsx')
fsrs_imptc_pct_period3_fpath = os.path.join(fsrs_imptc_path, 'fsrsv3_label_pct_graded_20160101_20200930.xlsx')
fsrs_imptc_pct_period4_fpath = os.path.join(fsrs_imptc_path, 'fsrsv3_label_pct_graded_20160101_20210331.xlsx')

#%% 因子打分文件
factor_score_path = os.path.join(group_path, f'sunss/metis/20230821/{metis_v}/')
factor_score_20190930_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_20190930.xlsx')
factor_score_20200331_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_20200331.xlsx')
factor_score_20200930_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_20200930.xlsx')
factor_score_20210331_fpath = os.path.join(factor_score_path, f'factor_bank_inf_all_20210331.xlsx')

#%% 回测输出根路径
bt_out_path = os.path.join(fc_path, 'Zeus/backtest/')
pred_out_path = os.path.join(fc_path, 'Zeus/pred/')
log_path = os.path.join(fc_path, 'Zeus/logs/')
factor_path = os.path.join(fc_path, 'Zeus/factor_list/')
factor_select_path = os.path.join(fc_path, 'Zeus/factor_select/')

model_save_path = os.path.join(fc_path, 'Zeus/pred/')

#%% 因子筛选设置
fs_config = {
    'rffs': "'/data/user/015614/Zeus/factor_select/Metis/v1_0_5/rffs_%s.pkl' % period"
}

#%% 标签设置
label_config = {
    'pct': 'label_pct_graded',
    'pctAfter': 'label_pct_after_graded'
}

#%% 时间设置
date_config = {
    'period1': dict(train_start_date=20160101, train_end_date=20190331, valid_start_date=20190401, valid_end_date=20190930,
                    test_start_date=20191001, test_end_date=20200331, fit_start_date=20200401, fit_end_date=20201231),
    'period2': dict(train_start_date=20160101, train_end_date=20190930, valid_start_date=20191001, valid_end_date=20200331,
                    test_start_date=20200401, test_end_date=20200930, fit_start_date=20201001, fit_end_date=20210630),
    'period3': dict(train_start_date=20160101, train_end_date=20200331, valid_start_date=20200401, valid_end_date=20200930,
                    test_start_date=20201001, test_end_date=20210331, fit_start_date=20210401, fit_end_date=20211231),
    # 'period4': dict(train_start_date=20160101, train_end_date=20200930, valid_start_date=20201001, valid_end_date=20210331,
    #                 test_start_date=20210401, test_end_date=20210930, fit_start_date=20211001, fit_end_date=20220630),
    'period4': dict(train_start_date=20160101, train_end_date=20200930, valid_start_date=20201001, valid_end_date=20210331,
                    test_start_date=20210401, test_end_date=20210930, fit_start_date=20210901, fit_end_date=20210930),
    'period5': dict(train_start_date=20160101, train_end_date=20210331, valid_start_date=20210401, valid_end_date=20210930,
                    test_start_date=20211001, test_end_date=20220331, fit_start_date=20220301, fit_end_date=20220331),
    'period6': dict(train_start_date=20160101, train_end_date=20211231, valid_start_date=20220101, valid_end_date=20221231,
                    test_start_date=20220701, test_end_date=20221231, fit_start_date=20221201, fit_end_date=20221231),
}