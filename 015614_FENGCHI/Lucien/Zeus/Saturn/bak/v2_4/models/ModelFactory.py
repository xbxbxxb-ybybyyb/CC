# coding: utf-8
# Author：fengchi863
# Date ：2022/7/12 14:39
"""
from Zeus.Saturn.v2_4.models.lr import LRModel
from Zeus.Saturn.v2_4.models.linear_model import LinearModel
from Zeus.Saturn.v2_4.models.xgb_clf_model import XGBClfModel
from Zeus.Saturn.v2_4.models.xgb_reg_model import XGBRegModel
from Zeus.Saturn.v2_4.ModelBase import ModelBase


class ModelFactory(ModelBase):
    def __init__(self,
                 model_name: str = None,
                 date_config: dict = None,
                 factor_score_path=None,
                 factor_filter_path=None,
                 data_path=None,
                 factor_num=1e5,
                 profit_path=None,
                 label='label_v2o10d1'
                 ):
        super().__init__(model_name=model_name,
                         date_config=date_config,
                         factor_score_path=factor_score_path,
                         factor_filter_path=factor_filter_path,
                         data_path=data_path,
                         factor_num=factor_num,
                         profit_path=profit_path,
                         label=label)
        self.model_name = model_name
        self.date_config = date_config

        self.model = None

    def train_model(self, X_train, y_train, param):
        if self.model_name is 'linear_model':
            model = LinearModel(date_config=self.date_config)
            model.train_model(X_train, y_train, param)
            self.model = model
        elif self.model_name is 'lr_model':
            model = LRModel(date_config=self.date_config)
            model.train_model(X_train, y_train, param)
            self.model = model
        elif self.model_name is 'xgb_clf_model':
            model = XGBClfModel(date_config=self.date_config)
            model.train_model(X_train, y_train, param)
            self.model = model
        elif self.model_name is 'xgb_reg_model':
            model = XGBRegModel(date_config=self.date_config)
            model.train_model(X_train, y_train, param)
            self.model = model

    def model_predict(self, X_other):
        _y_pred = self.model.model_predict(X_other)
        return _y_pred

"""