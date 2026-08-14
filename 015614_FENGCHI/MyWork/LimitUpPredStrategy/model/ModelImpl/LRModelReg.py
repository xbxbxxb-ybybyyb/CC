# coding: utf-8
# Author：fengchi863
# Date ：2021/4/1 14:25

from LimitUpPredStrategy.model.ModelBase.ModelBaseReg import ModelBaseReg
from sklearn.linear_model import LogisticRegression
import pandas as pd

class LRModelReg(ModelBaseReg):
    def __init__(self, start_date=20140101, end_date=20191231, stock_pool_address=None):
        super().__init__(start_date, end_date, stock_pool_address)

    def train_model(self, X_train, y_train, params):
        model = LogisticRegression(n_jobs=-1)
        model.set_params(**params)
        model.fit(X_train, y_train)
        return model

    def predict(self, model, X_test, true_pct=0.5):
        predict = model.predict_proba(X_test)
        predict = pd.DataFrame(predict[:, 1].reshape(-1,1), index=X_test.index)
        return predict