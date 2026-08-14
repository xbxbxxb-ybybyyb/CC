# coding: utf-8
# Author：fengchi863
# Date ：2022/7/13 9:50

from Zeus.Saturn.v2_15.ModelBase import ModelBase
from xgboost import XGBClassifier
import random
import numpy as np
np.random.seed(2022)

class XGBClfModel(ModelBase):
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
        model = XGBClassifier(**param)
        model.fit(X_train.values, y_train.values.ravel())
        self.model = model

    def model_predict(self, X_other):
        _y_pred = self.model.predict(X_other)
        return _y_pred

