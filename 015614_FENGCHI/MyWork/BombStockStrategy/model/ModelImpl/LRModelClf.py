# coding: utf-8
# Author：fengchi863
# Date ：2021/3/18 13:15

from BombStockStrategy.model.ModelBase.ModelBaseClf import ModelBaseClf
from sklearn.linear_model import LogisticRegression


class LRModelClf(ModelBaseClf):
    def __init__(self, start_date=20140101, end_date=20191231):
        super().__init__(start_date, end_date)

    @staticmethod
    def train_model(x_train, y_train, params):
        model = LogisticRegression(n_jobs=-1)
        model.set_params(**params)
        model.fit(x_train, y_train)
        return model

    @staticmethod
    def predict(model, x_test):
        predict = model.predict(x_test)
        return predict
