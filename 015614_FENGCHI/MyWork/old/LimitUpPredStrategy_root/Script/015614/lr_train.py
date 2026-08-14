# coding: utf-8
# Author：fengchi863
# Date ：2021/3/23 14:26

from LimitUpPredStrategy.model.ModelImpl.LRModelClf import LRModel
from LimitUpPredStrategy.conf.factor_conf import factor_name_list, del_factor_list
from LimitUpPredStrategy.conf.model_param_config import best_param_clf_lr
from sklearn.preprocessing import MinMaxScaler
from sklearn import metrics
import warnings
import pickle
import gc
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    lr_model = LRModel(start_date=20140101, end_date=20191231, stock_pool_address=None)
    lr_model.set_skf(n_splits=5)
    train_samples, predict_samples = lr_model.get_dataset(train_start_date=20140101,
                                            train_end_date=20191231,
                                            predict_start_date=20200101,
                                            predict_end_date=20201231)
    factor_scaler_list = []
    need_scaler_list = list(set(factor_name_list).difference(set(del_factor_list)))
    factor_scaler_list.append((need_scaler_list, MinMaxScaler()))
    non_scaler_list = []
    X_y_train_test_list = lr_model.convert_data_4_train_and_test(train_samples, non_scaler_list, *factor_scaler_list)
    best_model = lr_model.train_and_test_cv(X_y_train_test_list, best_param_clf_lr)
    _, X_test, _, y_test = lr_model.convert_data_4_predict(train_samples, predict_samples, non_scaler_list, *factor_scaler_list)
    # 在样本外预测
    y_pred, confuse_metrics = lr_model.predict(best_model, X_test)
    confuse_metrics = metrics.confusion_matrix(y_test, y_pred)
    print(confuse_metrics)

