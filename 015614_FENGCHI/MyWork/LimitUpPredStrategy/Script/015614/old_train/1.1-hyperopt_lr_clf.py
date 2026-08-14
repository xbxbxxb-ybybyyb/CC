# coding: utf-8
# Author：fengchi863
# Date ：2021/3/29 13:47

from LimitUpPredStrategy.model.ModelImpl.LRModelClf import LRModelClf
from LimitUpPredStrategy.Util.hyperopt_util import hyperopt_wrapper
from LimitUpPredStrategy.conf.model_param_config import param_space_clf_lr
from LimitUpPredStrategy.conf.factor_conf import factor_name_list, del_factor_list
from sklearn.preprocessing import MinMaxScaler
from sklearn import metrics

lr_model = LRModelClf(start_date=20140101, end_date=20191231, stock_pool_address=None)
train_samples, predict_samples = lr_model.get_dataset(train_start_date=20140101,
                                            train_end_date=20191231,
                                            predict_start_date=20200101,
                                            predict_end_date=20201231)
print('共使用因子%d个' % (train_samples.shape[1] - 1))
factor_scaler_list = []
need_scaler_list = list(set(factor_name_list).difference(set(del_factor_list)))
factor_scaler_list.append((need_scaler_list, MinMaxScaler()))
non_scaler_list = []
X_train, X_test, y_train, y_test = lr_model.convert_data_4_predict(train_samples, predict_samples, non_scaler_list, *factor_scaler_list)

def hyperopt_objective(params):
    model = lr_model.train_model(X_train, y_train, params)
    y_pred = model.predict(X_test)
    f1_score = metrics.f1_score(y_test, y_pred)
    # print(f1_score)
    return -f1_score

best_param = hyperopt_wrapper(hyperopt_objective, param_space_clf_lr, verbose=True, max_evals=10)
print(best_param)
