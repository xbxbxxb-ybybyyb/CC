# coding: utf-8
# Author：fengchi863
# Date ：2020/5/25 17:46

from sklearn.ensemble import GradientBoostingClassifier
from TrainingModel.TrainBase import TrainBase
from sklearn import metrics
import pandas as pd


class GBDTModel(TrainBase):

    def __init__(self, start_date=20170103, end_date=20191231):
        super().__init__(start_date, end_date)

    def model_predict(self, model, X_test):
        test_pred = model.predict(X_test)
        pred_proba = model.predict_proba(X_test)
        return test_pred, pred_proba

    def model_train(self, X_train, y_train, param):
        clf_model = GradientBoostingClassifier()
        param_self = clf_model.get_params()
        args_param = param.copy()
        for akey in param.keys():
            if akey not in param_self:
                args_param.pop(akey)
            else:
                if not isinstance(args_param[akey], type(param_self[akey])):
                    args_param[akey] = int(args_param[akey])
        clf_model.set_params(**args_param)
        clf_model.fit(X_train, y_train)
        return clf_model

    def training_methodology(self, stk_id, label, params):
        prediction, actual_label = super().time_series_cross_validation(stk_id, label, hyper_params=params)
        compare = pd.concat([prediction, actual_label], axis=1, join_axes=[prediction.index])
        compare.columns = ['prediction', 'actual']
        acc = metrics.accuracy_score(y_true=compare['actual'], y_pred=compare['prediction'])
        precision = metrics.precision_score(y_true=compare['actual'], y_pred=compare['prediction'], average='micro')
        recall = metrics.recall_score(y_true=compare['actual'], y_pred=compare['prediction'], average='micro')
        f1 = metrics.f1_score(y_true=compare['actual'], y_pred=compare['prediction'], average='micro')
        return compare, {'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1}
