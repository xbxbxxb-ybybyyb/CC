# coding: utf-8
# Author：fengchi863
# Date ：2020/8/12 15:14

import numpy as np
import pandas as pd
from sklearn import metrics
from xgboost import XGBClassifier

from StrongStockModel.model.ModelBase.ModelBase import ModelBase

class XGBModel(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None):
        super().__init__(start, end, stock_pool)

    def train_model(self, X_train, y_train, params):
        model = XGBClassifier()
        param_self = model.get_params()
        args_param = params.copy()
        for akey in params.keys():
            if akey not in param_self:
                args_param.pop(akey)
            else:
                if not isinstance(args_param[akey], type(param_self[akey])):
                    args_param[akey] = int(args_param[akey])
        model.set_params(**args_param)
        model.fit(X_train, y_train)
        return model

    def predict(self, model, X_test):
        pre_label = model.predict(X_test)
        return pre_label

    def training_methodology(self, params, period=10, predict_period=10):
        compare = self.rolling_train_and_predict(params=params, period=period, predict_period=predict_period)
        if len(compare) == 0:
            return pd.DataFrame(), {'acc': np.nan, 'precision': np.nan, 'recall': np.nan, 'f1': np.nan}
        acc = metrics.accuracy_score(y_true=compare['actual_label'], y_pred=compare['prediction'])
        precision = metrics.precision_score(y_true=compare['actual_label'], y_pred=compare['prediction'])
        recall = metrics.recall_score(y_true=compare['actual_label'], y_pred=compare['prediction'])
        f1 = metrics.f1_score(y_true=compare['actual_label'], y_pred=compare['prediction'])
        print({'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1})
        return compare, {'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1}