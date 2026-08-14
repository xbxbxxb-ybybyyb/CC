# coding: utf-8
# Author：fengchi863
# Date ：2022/7/16 16:10

from Zeus.Saturn.v2_2.ModelBase import ModelBase
from xgboost import XGBRegressor
import random
import numpy as np
np.random.seed(2022)
random.seed(2022)

class XGBRegModel(ModelBase):
    def __init__(self,
                 model_name: str = None,
                 date_config: dict = None,
                 factor_score_path=None,
                 factor_filter_path=None,
                 profit_path=None,
                 data_path=None,
                 factor_num=1e5,
                 label='label_v2o10d1'
                 ):
        super().__init__(model_name=model_name,
                         date_config=date_config,
                         factor_score_path=factor_score_path,
                         factor_filter_path=factor_filter_path,
                         profit_path=profit_path,
                         data_path=data_path,
                         factor_num=factor_num,
                         label=label)

    def train_model(self, X_train, y_train, param):
        if 'early_stopping_rounds' in param:
            early_stopping_rounds = param.pop('early_stopping_rounds')
        else:
            early_stopping_rounds = None
        model = XGBRegressor(**param)
        model.fit(X_train.values, y_train.values.ravel(), early_stopping_rounds=early_stopping_rounds)
        self.model = model

    def model_predict(self, X_other):
        _y_pred = self.model.predict(X_other)
        return _y_pred
