# @Time : 2020/5/26 9:21
# @Author : Zhichen Lu
# @File : AdaBoost.py


import pandas as pd
from sklearn import metrics
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier

from TrainingModel.TrainBase import TrainBase


class AdaBoostModelNonTree(TrainBase):

    def __init__(self, start_date=20170103, end_date=20191231):
        super().__init__(start_date, end_date)

    def model_predict(self, model, X_test):
        test_pred = model.predict(X_test)
        pred_proba = model.predict_proba(X_test)
        return test_pred, pred_proba

    def model_train(self, X_train, y_train, param):
        clf_model = AdaBoostClassifier(param)
        param_self = clf_model.get_params()
        args_param = param.copy()
        for akey in param.keys():
            if akey not in param_self:
                args_param.pop(akey)
        if not isinstance(args_param['n_estimators'], int):
            args_param['n_estimators'] = int(args_param['n_estimators'])
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


class AdaBoostModelTree(AdaBoostModelNonTree):
    def __init__(self, start=20170103, end=20191231):
        super().__init__(start, end)

    def model_train(self, X_train, y_train, param):
        clf_model = AdaBoostClassifier(param)
        param_self = clf_model.get_params()
        args_param = param.copy()
        for akey in param.keys():
            if akey not in param_self:
                args_param.pop(akey)
        if not isinstance(args_param['n_estimators'], int):
            args_param['n_estimators'] = int(args_param['n_estimators'])
        base_model = DecisionTreeClassifier()
        tree_params = param.copy()
        for tkeys in param.keys:
            if tkeys not in base_model.get_params():
                tree_params.pop(tkeys)
        if not isinstance(tree_params['max_depth'], int):
            tree_params['max_depth'] = int(tree_params['max_depth'])
        base_model.set_params(**tree_params)
        args_param['base_estimator'] = base_model
        clf_model.set_params(**args_param)
        clf_model.fit(X_train, y_train)
        return clf_model
