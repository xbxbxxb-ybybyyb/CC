# coding: utf-8
# Author：fengchi863
# Date ：2021/3/31 10:17

import random
random.seed(2021)
from LimitUpPredStrategy.conf.path_conf import *
from LimitUpPredStrategy.model.ModelImpl.XGBModelClf import XGBModelClf
from LimitUpPredStrategy.conf.factor_conf import factor_name_list, del_factor_list
from LimitUpPredStrategy.conf.model_param_config import best_param_clf_xgboost
from sklearn.preprocessing import MinMaxScaler
from LimitUpPredStrategy.Util.ml_util import calc_metrics
import warnings
import pandas as pd
import pickle
import gc
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    xgb_model = XGBModelClf(start_date=20140101, end_date=20191231, stock_pool_address=None)
    xgb_model.set_skf(n_splits=5)
    train_samples, predict_samples = xgb_model.get_dataset(train_start_date=20140101,
                                            train_end_date=20191231,
                                            predict_start_date=20200101,
                                            predict_end_date=20201231)
    print('共使用因子%d个' % (train_samples.shape[1] - 1))
    factor_scaler_list = []
    need_scaler_list = list(set(factor_name_list).difference(set(del_factor_list)))
    factor_scaler_list.append((need_scaler_list, MinMaxScaler()))
    non_scaler_list = []
    X_y_train_test_list = xgb_model.convert_data_4_train_and_test(train_samples, non_scaler_list, *factor_scaler_list)
    best_model = xgb_model.train_and_test_CV(X_y_train_test_list, best_param_clf_xgboost)
    _, X_test, _, y_test = xgb_model.convert_data_4_predict(train_samples, predict_samples, non_scaler_list, *factor_scaler_list)
    # 在样本外预测
    y_pred = xgb_model.predict(best_model, X_test)
    y_pred = pd.DataFrame(y_pred, index=predict_samples.index, columns=['y_pred'])
    pred_res = pd.concat([y_test, y_pred], axis=1)
    pred_res.to_pickle(pred_output_path + 'xgb_pred_signal.pkl')

    # 统计效果
    y_balance = y_test.sum() / len(y_test)
    y_pred_balance = y_pred.sum() / len(y_pred)

    print('样本外预测结果：')
    calc_metrics(y_test, y_pred)

    print('真实值样本平衡度：%.4f' % y_balance)
    print('预测值样本平衡度：%.4f' % y_pred_balance)