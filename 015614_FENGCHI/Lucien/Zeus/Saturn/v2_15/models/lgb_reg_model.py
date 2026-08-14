# coding: utf-8
# Author：fengchi863
# Date ：2022/7/20 10:40

from Zeus.Saturn.v2_15.ModelBase import ModelBase
from lightgbm import LGBMRegressor
import random
import numpy as np
np.random.seed(2022)
random.seed(2022)

class CatRegModel(ModelBase):
    def __init__(self,
                 model_name: str = None,
                 date_config: dict = None,
                 factor_score_path=None,
                 factor_filter_path=None,
                 profit_path=None,
                 label='label_v2o10d1'
                 ):
        super().__init__(model_name=model_name,
                         date_config=date_config,
                         factor_score_path=factor_score_path,
                         factor_filter_path=factor_filter_path,
                         profit_path=profit_path,
                         label=label)

    def train_model(self, X_train, y_train, param):
        if 'early_stopping_rounds' in param:
            early_stopping_rounds = param.pop('early_stopping_rounds')
        else:
            early_stopping_rounds = None
        model = LGBMRegressor(**param)
        model.fit(X_train.values, y_train.values.ravel(), early_stopping_rounds=early_stopping_rounds)
        self.model = model

    def model_predict(self, X_other):
        _y_pred = self.model.predict(X_other)
        return _y_pred
