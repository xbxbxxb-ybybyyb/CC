import sys
import os

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
import pandas as pd
from StrongStockModel.model.Modelmpl.XGBRegression_all_factor import XGBRegression
from StrongStockModel.conf.path_config import strong_stock_path, all_mkt_preprocessed_ts_maxmin_by_date_path, all_mkt_preprocessed_ts_norm_by_date_path, \
    all_mkt_preprocessed_ts_pct_by_date_path
from StrongStockModel.conf.model_param_config import best_param_clf_xgb
from xquant.compute.aimr import AIMR
aimr_param = [(0, (20150105, 20151030, 20151102, 20151113)),
 (1, (20150119, 20151113, 20151116, 20151127)),
 (2, (20150202, 20151127, 20151130, 20151211)),
 (3, (20150216, 20151211, 20151214, 20151225)),
 (4, (20150309, 20151225, 20151228, 20160111)),
 (5, (20150323, 20160111, 20160112, 20160125)),
 (6, (20150407, 20160125, 20160126, 20160215)),
 (7, (20150421, 20160215, 20160216, 20160229)),
 (8, (20150506, 20160229, 20160301, 20160314)),
 (9, (20150520, 20160314, 20160315, 20160328)),
 (10, (20150603, 20160328, 20160329, 20160412)),
 (11, (20150617, 20160412, 20160413, 20160426)),
 (12, (20150702, 20160426, 20160427, 20160511)),
 (13, (20150716, 20160511, 20160512, 20160525)),
 (14, (20150730, 20160525, 20160526, 20160608)),
 (15, (20150813, 20160608, 20160613, 20160624)),
 (16, (20150827, 20160624, 20160627, 20160708)),
 (17, (20150914, 20160708, 20160711, 20160722)),
 (18, (20150928, 20160722, 20160725, 20160805)),
 (19, (20151019, 20160805, 20160808, 20160819)),
 (20, (20151102, 20160819, 20160822, 20160902)),
 (21, (20151116, 20160902, 20160905, 20160920)),
 (22, (20151130, 20160920, 20160921, 20161011)),
 (23, (20151214, 20161011, 20161012, 20161025)),
 (24, (20151228, 20161025, 20161026, 20161108)),
 (25, (20160112, 20161108, 20161109, 20161122)),
 (26, (20160126, 20161122, 20161123, 20161206)),
 (27, (20160216, 20161206, 20161207, 20161220)),
 (28, (20160301, 20161220, 20161221, 20170104)),
 (29, (20160315, 20170104, 20170105, 20170118)),
 (30, (20160329, 20170118, 20170119, 20170208)),
 (31, (20160413, 20170208, 20170209, 20170222)),
 (32, (20160427, 20170222, 20170223, 20170308)),
 (33, (20160512, 20170308, 20170309, 20170322)),
 (34, (20160526, 20170322, 20170323, 20170407)),
 (35, (20160613, 20170407, 20170410, 20170421)),
 (36, (20160627, 20170421, 20170424, 20170508)),
 (37, (20160711, 20170508, 20170509, 20170522)),
 (38, (20160725, 20170522, 20170523, 20170607)),
 (39, (20160808, 20170607, 20170608, 20170621)),
 (40, (20160822, 20170621, 20170622, 20170705)),
 (41, (20160905, 20170705, 20170706, 20170719)),
 (42, (20160921, 20170719, 20170720, 20170802)),
 (43, (20161012, 20170802, 20170803, 20170816)),
 (44, (20161026, 20170816, 20170817, 20170830)),
 (45, (20161109, 20170830, 20170831, 20170913)),
 (46, (20161123, 20170913, 20170914, 20170927)),
 (47, (20161207, 20170927, 20170928, 20171018)),
 (48, (20161221, 20171018, 20171019, 20171101)),
 (49, (20170105, 20171101, 20171102, 20171115)),
 (50, (20170119, 20171115, 20171116, 20171129)),
 (51, (20170209, 20171129, 20171130, 20171213)),
 (52, (20170223, 20171213, 20171214, 20171227)),
 (53, (20170309, 20171227, 20171228, 20180111)),
 (54, (20170323, 20180111, 20180112, 20180125)),
 (55, (20170410, 20180125, 20180126, 20180208)),
 (56, (20170424, 20180208, 20180209, 20180301)),
 (57, (20170509, 20180301, 20180302, 20180315)),
 (58, (20170523, 20180315, 20180316, 20180329)),
 (59, (20170608, 20180329, 20180330, 20180416)),
 (60, (20170622, 20180416, 20180417, 20180502)),
 (61, (20170706, 20180502, 20180503, 20180516)),
 (62, (20170720, 20180516, 20180517, 20180530)),
 (63, (20170803, 20180530, 20180531, 20180613)),
 (64, (20170817, 20180613, 20180614, 20180628)),
 (65, (20170831, 20180628, 20180629, 20180712)),
 (66, (20170914, 20180712, 20180713, 20180726)),
 (67, (20170928, 20180726, 20180727, 20180809)),
 (68, (20171019, 20180809, 20180810, 20180823)),
 (69, (20171102, 20180823, 20180824, 20180906)),
 (70, (20171116, 20180906, 20180907, 20180920)),
 (71, (20171130, 20180920, 20180921, 20181012)),
 (72, (20171214, 20181012, 20181015, 20181026)),
 (73, (20171228, 20181026, 20181029, 20181109)),
 (74, (20180112, 20181109, 20181112, 20181123)),
 (75, (20180126, 20181123, 20181126, 20181207)),
 (76, (20180209, 20181207, 20181210, 20181221))]

def main_window_search(i):
    strong_pool = pd.read_pickle(strong_stock_path)
    # strong_pool = pd.read_pickle(ghost_stock_path)
    strong_pool.columns = [int(x[:-3]) for x in strong_pool.columns]
    strong_pool.index = strong_pool.index.astype(int)
    # best_param_clf_xgb['weight'] = {1: 0.4, -1: 0.6}

    # lr = LR(20140101, 20181231, strong_pool.loc[20140101:20181231], feature_address=all_mkt_preprocessed_ts_norm_by_date_path)
    # label = lr.rolling_train_and_predict_fix_dataset_scale(params=best_param_clf_lr, train_set_num=40000, test_set_num=10000, max_test_day=1, label_methodology='fix_window', label_param={'threshold': 0.02},
    #                                             factor_nums=200, kernel=10)
    # lr.check_dataset(params=best_param_clf_lr, period=240, predict_period=20, label_param={'threshold': 0.02}, kernel=10)
    train_period = 100
    test_period = 10
    factor_num = -1
    N = 40
    all_mkt_preprocessed_ts_norm_by_date_path = '/data/group/800319/junkData/StrongStock/processed_factor_all_pool_by_date/ts_norm_%d_and_binary/'%N
    train_idx,_,_,test_idx = aimr_param[i][1]
    out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/all_factor/XGBAllFactor_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (train_period, test_period, factor_num,N)
    if os.path.exists(out_file.replace('.pkl','_%d.pkl'%test_idx)):
        print(test_idx,'exist')
        return
    # print(aimr_param[i][1])
    # model = XGBRegression(train_idx, test_idx, None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path)
    model = XGBRegression(20150702,20181231, None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path)
    print(out_file)
    best_param_clf_xgb['objective'] = 'reg:squarederror'
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param_clf_xgb['train_pred_path'] = out_file.replace('.pkl', '_train_pred/')
    best_param_clf_xgb['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['load local model'] = False
    # best_param_clf_xgb.update({'subsample': 0.3,'sampling_method': 'gradient_based'})

    label = model.rolling_train_and_predict(params=best_param_clf_xgb, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, out_file.replace('.pkl','_%d.pkl'%test_idx))
    # os.mkdir('/data/group/800319/Faamonitor/PL/')
    print(out_file)

para = AIMR.getParam()

main_window_search(int(para))

"""
[20170322,
 20170407,
 20170421,
 20170508,
 20170607,
 20170705,
 20170719,
 20170802,
 20170816,
 20170830,
 20170913,
 20170927,
 20171018,
 20171115,
 20171213,
 20180125,
 20180208,
 20180315,
 20180329,
 20180416,
 20180502,
 20180530,
 20180628,
 20180712,
 20180809,
 20180920,
 20181012,
 20181026,
 20181109,
 20181123,
 20181221]
"""