# coding: utf-8
# Author：fengchi863
# Date ：2022/7/12 13:54

from Zeus.Saturn.v1_1.ModelBase import ModelBase
from sklearn.linear_model import LinearRegression


class LinearModel(ModelBase):
    def __init__(self,
                 model_name='linear_model',
                 train_start_date=20160104,
                 train_end_date=20181231,
                 valid_start_date=20191008,
                 valid_end_date=20200630,
                 pred_start_date=20200701,
                 pred_end_date=20201231,
                 factor_score_path=None,
                 factor_filter_path=None,
                 profit_path=None,
                 label='label_v2o10d1'):
        super().__init__(model_name=model_name,
                         train_start_date=train_start_date,
                         train_end_date=train_end_date,
                         valid_start_date=valid_start_date,
                         valid_end_date=valid_end_date,
                         pred_start_date=pred_start_date,
                         pred_end_date=pred_end_date,
                         factor_score_path=factor_score_path,
                         factor_filter_path=factor_filter_path,
                         profit_path=profit_path,
                         label=label)

    def train_model(self, X_train, y_train, param):
        model = LinearRegression(param)
        model.fit(X_train, y_train)
        self.model = model

    def model_predict(self, X_other):
        y_pred = self.model.predict(X_other)
        return y_pred
