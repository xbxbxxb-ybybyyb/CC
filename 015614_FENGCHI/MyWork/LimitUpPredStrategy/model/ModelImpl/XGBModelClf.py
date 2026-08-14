# coding: utf-8
# Author：fengchi863
# Date ：2021/3/26 11:19

from LimitUpPredStrategy.model.ModelBase.ModelBaseClf import ModelBaseClf
import xgboost as xgb

class XGBModelClf(ModelBaseClf):
    def __init__(self, start_date=20140101, end_date=20191231, stock_pool_address=None):
        super().__init__(start_date, end_date, stock_pool_address)

    def train_model(self, X_train, y_train, params):
        clf_model = xgb.XGBClassifier()
        param_self = clf_model.get_params()
        args_param = params.copy()
        for akey in params.keys():
            if akey not in param_self:
                args_param.pop(akey)
            else:
                if not isinstance(args_param[akey], type(param_self[akey])):
                    args_param[akey] = int(args_param[akey])
        # if tf.test.gpu_device_name():
        #     args_param['tree_method'] = 'gpu_hist'
        clf_model.set_params(**args_param)
        clf_model.fit(X_train, y_train, verbose=True)
        return clf_model

    def predict(self, model, X_test):
        predict = model.predict(X_test)
        return predict