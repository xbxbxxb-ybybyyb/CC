# coding: utf-8
# Author：fengchi863
# Date ：2021/3/23 14:26

import warnings

import numpy as np
from sklearn import metrics
from sklearn.preprocessing import MinMaxScaler

from BombStockStrategy.conf.factor_config import del_factor_list, factor_name_list
from BombStockStrategy.conf.model_param_config import best_param_clf_lr
from BombStockStrategy.model.ModelImpl.LRModelClf import LRModelClf

warnings.filterwarnings('ignore')

if __name__ == '__main__':
    lr_model = LRModelClf(start_date=20140101, end_date=20201231)
    lr_model.set_skf(n_splits=5)
    train_samples, predict_samples = lr_model.get_dataset(filename='samples_Label2_20211102',
                                                          train_start_date=20140101,
                                                          train_end_date=20191231,
                                                          predict_start_date=20200101,
                                                          predict_end_date=20201231)

    # 剔除掉前后有停牌的个股，因为label中这部分计算出来是nan
    train_samples = train_samples[~np.isnan(train_samples['label'])]
    predict_samples = predict_samples[~np.isnan(predict_samples['label'])]

    factor_scaler_list = []
    need_scaler_list = list(set(factor_name_list).difference(set(del_factor_list)))   # 不进行归一化
    factor_scaler_list.append((need_scaler_list, MinMaxScaler()))
    non_scaler_list = []
    X_y_train_test_list = lr_model.convert_data_4_train_and_test(train_samples, non_scaler_list, *factor_scaler_list)
    best_model = lr_model.train_and_test_cv(X_y_train_test_list, best_param_clf_lr)
    _, X_test, _, y_test = lr_model.convert_data_4_predict(train_samples, predict_samples, non_scaler_list,
                                                           *factor_scaler_list)
    # 在样本外预测
    y_pred = lr_model.predict(best_model, X_test)
    confuse_metrics = metrics.confusion_matrix(y_test, y_pred)

    print(confuse_metrics)
