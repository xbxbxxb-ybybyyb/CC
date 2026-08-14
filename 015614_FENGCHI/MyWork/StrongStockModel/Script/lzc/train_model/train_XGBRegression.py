import sys
import os

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
import pandas as pd
from StrongStockModel.model.Modelmpl.XGBRegression import XGBRegression
from StrongStockModel.conf.path_config import strong_stock_path, all_mkt_preprocessed_ts_maxmin_by_date_path, all_mkt_preprocessed_ts_norm_by_date_path, \
    all_mkt_preprocessed_ts_pct_by_date_path
from StrongStockModel.conf.model_param_config import best_param_clf_xgb

def main_window_search():
    train_period = 100
    test_period = 10
    factor_num = 400
    N = 40
    all_mkt_preprocessed_ts_norm_by_date_path = '/data/group/800319/junkData/StrongStock/processed_factor_all_pool_by_date/ts_norm_%d_and_binary/' % N
    model = XGBRegression(20150309, 20181231, None, feature_address=all_mkt_preprocessed_ts_norm_by_date_path)
    out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/XGBNewPara_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
    train_period, test_period, factor_num, N)
    print(out_file)
    best_param_clf_xgb['objective'] = 'reg:squarederror'
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param_clf_xgb['train_pred_path'] = out_file.replace('.pkl', '_train_pred/')
    label = model.rolling_train_and_predict(params=best_param_clf_xgb, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, out_file)
    # os.mkdir('/data/group/800319/Faamonitor/PL/')
    print(out_file)

main_window_search()