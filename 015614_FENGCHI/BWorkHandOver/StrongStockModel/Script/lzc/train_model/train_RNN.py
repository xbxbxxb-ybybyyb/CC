# @Time : 2020/11/4 9:01
# @Author : Zhichen Lu
# @File : train_RNN.py


import sys
import os

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
import pandas as pd
from StrongStockModel.model.Modelmpl.RNNBase import RNNBase
from StrongStockModel.conf.path_config import strong_stock_path,root_path
from xquant.compute.aimr import AIMR


def main_window_search():
    train_period = 10
    test_period = 5
    factor_num = 312
    N = 40
    all_mkt_preprocessed_ts_norm_by_date_path = '/data/group/800319/JunkSmallFactor/'#root_path + 'processed_factor_all_pool_by_date_5min/ts_norm_%d_append/'%N
    model = RNNBase(20150101, 20181231, None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path)
    # model = XGBRegression5min(20150309, 20181231, None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path) #200
    out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/RNNTest/RNN_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
    train_period, test_period, factor_num, N)
    print(out_file)
    best_param_clf_xgb = {}
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    # best_param_clf_xgb['train_pred_path'] = out_file.replace('.pkl', '_train_pred/')
    best_param_clf_xgb['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    # best_param_clf_xgb['load local model'] = True
    label = model.rolling_train_and_predict(params=best_param_clf_xgb, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=10, factor_nums=factor_num)
    pd.to_pickle(label, out_file)
    # os.mkdir('/data/group/800319/Faamonitor/PL/')
    print(out_file)

# idx = int(AIMR.getParam())
main_window_search()