# coding: utf-8
# Author：fengchi863
# Date ：2022/11/28 9:01

import os

#%% 根目录们
group_path = '/data/group/800463/'
fc_group_path = os.path.join(group_path, 'fengc/')
fc_path = '/data/user/015614/'
fc_cheat_path = '/data/user/015614/junkData/cheat/'

#%% 数据集
data_path = os.path.join(group_path, 'sunss/europa/20230329_new_pct_quick/')
data_test_fpath_with_label = os.path.join(data_path, 'factor_df_all_20160101_20211231_graded.pkl')
data_fit_fpath_with_label = os.path.join(data_path, 'factor_df_all_20160101_20211231_graded.pkl')

#%% 因子筛选文件
xgb_imptc_path = os.path.join(group_path, 'xiely/factor_select/Europa/fac_20230329_quick/')
xgb_imptc_emotion_path = os.path.join(xgb_imptc_path, 'Emotion/')
xgb_imptc_noemotion_path = os.path.join(xgb_imptc_path, 'noEmotion/')
xgb_imptc_emotion_fsv8_period1_fpath = os.path.join(xgb_imptc_emotion_path, 'europa_quick_xgb_importance_20190930_reg15_second_fac_20230329_FSV8_all_label_pct_quick_graded_Emotion.xlsx')
xgb_imptc_emotion_fsv10_period1_fpath = os.path.join(xgb_imptc_emotion_path, 'europa_quick_xgb_importance_20190930_reg15_second_fac_20230329_FSV10_all_label_pct_quick_graded_Emotion.xlsx')
xgb_imptc_emotion_fsv11_period1_fpath = os.path.join(xgb_imptc_emotion_path, 'europa_quick_xgb_importance_20190930_first_fac_20230329_FSV11_label_pct_quick_graded_Emotion.xlsx')
xgb_imptc_emotion_fsv8_period2_fpath = os.path.join(xgb_imptc_emotion_path, 'europa_quick_xgb_importance_20200331_reg15_second_fac_20230329_FSV8_all_label_pct_quick_graded_Emotion.xlsx')
xgb_imptc_emotion_fsv10_period2_fpath = os.path.join(xgb_imptc_emotion_path, 'europa_quick_xgb_importance_20200331_reg15_second_fac_20230329_FSV10_all_label_pct_quick_graded_Emotion.xlsx')
xgb_imptc_emotion_fsv11_period2_fpath = os.path.join(xgb_imptc_emotion_path, 'europa_quick_xgb_importance_20200331_first_fac_20230329_FSV11_label_pct_quick_graded_Emotion.xlsx')
xgb_imptc_emotion_fsv8_period3_fpath = os.path.join(xgb_imptc_emotion_path, 'europa_quick_xgb_importance_20200930_reg15_second_fac_20230329_FSV8_all_label_pct_quick_graded_Emotion.xlsx')
xgb_imptc_emotion_fsv10_period3_fpath = os.path.join(xgb_imptc_emotion_path, 'europa_quick_xgb_importance_20200930_reg15_second_fac_20230329_FSV10_all_label_pct_quick_graded_Emotion.xlsx')
xgb_imptc_emotion_fsv11_period3_fpath = os.path.join(xgb_imptc_emotion_path, 'europa_quick_xgb_importance_20200930_first_fac_20230329_FSV11_label_pct_quick_graded_Emotion.xlsx')

xgb_imptc_noEmotion_fsv8_period1_fpath = os.path.join(xgb_imptc_noemotion_path, 'europa_quick_xgb_importance_20190930_reg15_second_fac_20230329_FSV8_all_label_pct_quick_graded_noEmotion.xlsx')
xgb_imptc_noEmotion_fsv10_period1_fpath = os.path.join(xgb_imptc_noemotion_path, 'europa_quick_xgb_importance_20190930_reg15_second_fac_20230329_FSV10_all_label_pct_quick_graded_noEmotion.xlsx')
xgb_imptc_noEmotion_fsv11_period1_fpath = os.path.join(xgb_imptc_noemotion_path, 'europa_quick_xgb_importance_20190930_first_fac_20230329_FSV11_label_pct_quick_graded_noEmotion.xlsx')
xgb_imptc_noEmotion_fsv8_period2_fpath = os.path.join(xgb_imptc_noemotion_path, 'europa_quick_xgb_importance_20200331_reg15_second_fac_20230329_FSV8_all_label_pct_quick_graded_noEmotion.xlsx')
xgb_imptc_noEmotion_fsv10_period2_fpath = os.path.join(xgb_imptc_noemotion_path, 'europa_quick_xgb_importance_20200331_reg15_second_fac_20230329_FSV10_all_label_pct_quick_graded_noEmotion.xlsx')
xgb_imptc_noEmotion_fsv11_period2_fpath = os.path.join(xgb_imptc_noemotion_path, 'europa_quick_xgb_importance_20200331_first_fac_20230329_FSV11_label_pct_quick_graded_noEmotion.xlsx')
xgb_imptc_noEmotion_fsv8_period3_fpath = os.path.join(xgb_imptc_noemotion_path, 'europa_quick_xgb_importance_20200930_reg15_second_fac_20230329_FSV8_all_label_pct_quick_graded_noEmotion.xlsx')
xgb_imptc_noEmotion_fsv10_period3_fpath = os.path.join(xgb_imptc_noemotion_path, 'europa_quick_xgb_importance_20200930_reg15_second_fac_20230329_FSV10_all_label_pct_quick_graded_noEmotion.xlsx')
xgb_imptc_noEmotion_fsv11_period3_fpath = os.path.join(xgb_imptc_noemotion_path, 'europa_quick_xgb_importance_20200930_first_fac_20230329_FSV11_label_pct_quick_graded_noEmotion.xlsx')

#%% 因子打分文件
factor_score_path = os.path.join(group_path, 'sunss/europa/20230329_new_pct_quick/')
factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_all.xlsx')

fsrs_emotion_path = os.path.join(factor_score_path, 'fsrs')
fsrs_noemotion_path = os.path.join(factor_score_path, 'fsrs_noemotion')

fsrs_imptc_emotion_period1_fpath = os.path.join(fsrs_emotion_path, 'fsrsv2_label_pct_quick_graded_20160101_20190930.xlsx')
fsrs_imptc_emotion_period2_fpath = os.path.join(fsrs_emotion_path, 'fsrsv2_label_pct_quick_graded_20160101_20200331.xlsx')
fsrs_imptc_emotion_period3_fpath = os.path.join(fsrs_emotion_path, 'fsrsv2_label_pct_quick_graded_20160101_20200930.xlsx')
fsrs_imptc_noEmotion_period1_fpath = os.path.join(fsrs_noemotion_path, 'fsrsv2_label_pct_quick_graded_20160101_20190930.xlsx')
fsrs_imptc_noEmotion_period2_fpath = os.path.join(fsrs_noemotion_path, 'fsrsv2_label_pct_quick_graded_20160101_20200331.xlsx')
fsrs_imptc_noEmotion_period3_fpath = os.path.join(fsrs_noemotion_path, 'fsrsv2_label_pct_quick_graded_20160101_20200930.xlsx')

#%% 回测输出根路径
bt_out_path = os.path.join(fc_path, 'Zeus/backtest/')
pred_out_path = os.path.join(fc_path, 'Zeus/pred/')
log_path = os.path.join(fc_path, 'Zeus/logs/')
factor_path = os.path.join(fc_path, 'Zeus/factor_list/')
factor_select_path = os.path.join(fc_path, 'Zeus/factor_select/')

junk_path = os.path.join(fc_path, 'junkData/')

#%% 时间设置
date_config = {
    'period1': dict(train_start_date=20160101, train_end_date=20190331, valid_start_date=20190401, valid_end_date=20190930,
                    test_start_date=20191001, test_end_date=20200331, fit_start_date=20200401, fit_end_date=20201231),
    'period2': dict(train_start_date=20160101, train_end_date=20190930, valid_start_date=20191001, valid_end_date=20200331,
                    test_start_date=20200401, test_end_date=20200930, fit_start_date=20201001, fit_end_date=20210630),
    'period3': dict(train_start_date=20160101, train_end_date=20200331, valid_start_date=20200401, valid_end_date=20200930,
                    test_start_date=20201001, test_end_date=20210331, fit_start_date=20210401, fit_end_date=20211231)
}