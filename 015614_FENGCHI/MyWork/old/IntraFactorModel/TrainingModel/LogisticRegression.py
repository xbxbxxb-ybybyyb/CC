# @Time : 2020/5/22 9:46
# @Author : Zhichen Lu
# @File : LogisticRegression.py

import numpy as np
# from tqdm import tqdm
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LogisticRegression

from TrainingModel.TrainBase import TrainBase


class RollingLRModel(TrainBase):

    def __init__(self, start_date=20140102, end_date=20191231, factor_path=None, scare_list=None, non_scare_list=None):
        super(RollingLRModel, self).__init__(start_date, end_date, factor_path, scale_list_=scare_list, non_scale_list_=non_scare_list)

    def model_train(self, X_train, y_train, param):
        lr_model = LogisticRegression()
        lr_model.set_params(**param)
        lr_model.fit(np.array(X_train), np.array(y_train))
        return lr_model

    def model_predict(self, lr_model, X_test):
        clf_predictions = lr_model.predict(np.array(X_test))
        clf_proba = lr_model.predict_proba(np.array(X_test))
        return clf_predictions, clf_proba

    def training_methodology(self, stk_id, label, params):
        # print(params)
        prediction, actual_label = super(RollingLRModel, self).time_series_cross_validation(stk_id, label,
                                                                                            hyper_params=params)
        if len(prediction) == 0:
            return pd.DataFrame(), {'acc': np.nan, 'precision': np.nan, 'recall': np.nan, 'f1': np.nan}
        compare = pd.concat([prediction, actual_label], axis=1, join_axes=[prediction.index])
        compare.columns = ['prediction', 'actual']
        acc = metrics.accuracy_score(y_true=compare['actual'], y_pred=compare['prediction'])
        precision = metrics.precision_score(y_true=compare['actual'], y_pred=compare['prediction'], average='micro')
        recall = metrics.recall_score(y_true=compare['actual'], y_pred=compare['prediction'], average='micro')
        f1 = metrics.f1_score(y_true=compare['actual'], y_pred=compare['prediction'], average='micro')
        # print(params, {'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1})
        return compare, {'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1}

# def optimization(self):
#
# trade_months = list(filter(lambda x: 20170104 <= x & x <= 20191231, trade_months))
# start_date = 20170103
# end_date = 20191231
# print(1)
# date_list = get_date_range(start_date, end_date)
# stock_pool = clean_stock_list('COMMON',no_limit_down=True,no_limit_up=True).loc[20170103:20191231]
# isin_judge = stock_pool.sum()
# stock_pool = stock_pool[isin_judge[isin_judge!=0].index]
# stock_list = stock_pool.columns.tolist()
# print(2)
# rolling_model = RollingLRModel(start_date,end_date)
#
# def optimization(param):
