# @Time : 2020/10/8 9:34
# @Author : Zhichen Lu
# @File : train_linear_window.py

import sys
import os

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
import pandas as pd
from StrongStockModel.model.Modelmpl.Linear import LinearReg
from StrongStockModel.conf.path_config import strong_stock_path

def main():
    strong_pool = pd.read_pickle(strong_stock_path)
    # strong_pool = pd.read_pickle(ghost_stock_path)
    strong_pool.columns = [int(x[:-3]) for x in strong_pool.columns]
    strong_pool.index = strong_pool.index.astype(int)
    # best_param_clf_xgb['weight'] = {1: 0.4, -1: 0.6}

    # lr = LR(20140101, 20181231, strong_pool.loc[20140101:20181231], feature_address=all_mkt_preprocessed_ts_norm_by_date_path)
    # label = lr.rolling_train_and_predict_fix_dataset_scale(params=best_param_clf_lr, train_set_num=40000, test_set_num=10000, max_test_day=1, label_methodology='fix_window', label_param={'threshold': 0.02},
    #                                             factor_nums=200, kernel=10)
    # lr.check_dataset(params=best_param_clf_lr, period=240, predict_period=20, label_param={'threshold': 0.02}, kernel=10)
    train_period = 200
    test_period = 10
    factor_num = 400
    N = 40
    all_mkt_preprocessed_ts_norm_by_date_path = '/data/group/800319/junkData/StrongStock/processed_factor_all_pool_by_date/ts_norm_%d/' % N
    model = LinearReg(20150101, 20181231, None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path)
    out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/XGB_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
    train_period, test_period, factor_num, N)
    best_param = {'n_jobs':-1}
    best_param['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param['train_pred_path'] = out_file.replace('.pkl', '_train_pred/')
    label = model.rolling_train_and_predict(params=best_param, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=10, factor_nums=factor_num)
    pd.to_pickle(label, out_file)
    # os.mkdir('/data/group/800319/Faamonitor/PL/')

main()