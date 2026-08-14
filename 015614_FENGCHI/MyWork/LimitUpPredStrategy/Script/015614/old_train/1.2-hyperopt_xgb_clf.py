# coding: utf-8
# Author：fengchi863
# Date ：2021/3/31 13:42

from LimitUpPredStrategy.model.ModelImpl.XGBModelClf import XGBModelClf
from LimitUpPredStrategy.Util.hyperopt_util import hyperopt_wrapper
from LimitUpPredStrategy.conf.model_param_config import param_space_clf_xgboost
from LimitUpPredStrategy.conf.factor_conf import factor_name_list, del_factor_list
from sklearn.preprocessing import MinMaxScaler
from sklearn import metrics

xgb_model = XGBModelClf(start_date=20140101, end_date=20191231, stock_pool_address=None)
train_samples, predict_samples = xgb_model.get_dataset(train_start_date=20140101,
                                            train_end_date=20191231,
                                            predict_start_date=20200101,
                                            predict_end_date=20201231)
print('共使用因子%d个' % (train_samples.shape[1] - 1))
factor_scaler_list = []
need_scaler_list = list(set(factor_name_list).difference(set(del_factor_list)))
factor_scaler_list.append((need_scaler_list, MinMaxScaler()))
non_scaler_list = []
X_train, X_test, y_train, y_test = xgb_model.convert_data_4_predict(train_samples, predict_samples, non_scaler_list, *factor_scaler_list)

def hyperopt_objective(params):
    model = xgb_model.train_model(X_train, y_train, params)
    y_pred = model.predict(X_test)
    precision = metrics.precision_score(y_test, y_pred)
    # print(f1_score)
    return -precision

best_param = hyperopt_wrapper(hyperopt_objective, param_space_clf_xgboost, verbose=True, max_evals=30)
print(best_param)