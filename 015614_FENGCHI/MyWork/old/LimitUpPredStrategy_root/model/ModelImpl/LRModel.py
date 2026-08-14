# coding: utf-8
# Author：fengchi863
# Date ：2021/3/18 13:15

from LimitUpPredStrategy.model.ModelBase.ModelBaseClf import ModelBaseClf
from sklearn.linear_model import LogisticRegression

class LRModelClf(ModelBaseClf):
    def __init__(self, start_date=20140101, end_date=20191231, stock_pool_address=None):
        super().__init__(start_date, end_date, stock_pool_address)

    def train_model(self, X_train, y_train, params):
        model = LogisticRegression(n_jobs=-1)
        model.set_params(**params)
        model.fit(X_train, y_train)
        return model

    def predict(self, model, X_test):
        predict = model.predict(X_test)
        return predict
