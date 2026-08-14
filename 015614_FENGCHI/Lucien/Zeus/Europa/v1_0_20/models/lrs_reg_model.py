# coding: utf-8
# Author：fengchi863
# Date ：2022/11/3 19:46

from Zeus.Europa.v1_0_20.ModelBase import ModelBase
from sklearn.linear_model import LogisticRegression
import random
random.seed(2022)

class LrRegModel(ModelBase):
    def __init__(self,
                 model_name: str = None,
                 date_config: dict = None,
                 factor_score_path=None,
                 factor_filter_path=None,
                 profit_path=None,
                 data_path=None,
                 factor_num=1e5,
                 label='label_pct_graded'
                 ):
        super().__init__(model_name=model_name,
                         date_config=date_config,
                         factor_score_path=factor_score_path,
                         factor_filter_path=factor_filter_path,
                         profit_path=profit_path,
                         data_path=data_path,
                         factor_num=factor_num,
                         label=label)

        self.score_threshold = 0
        self.best_score = None

    def train_model(self, X_train, y_train, X_valid, y_valid, param):
        model = LogisticRegression(**param)
        model.fit(X_train.values, y_train.values.ravel())
        self.model = model

    def model_predict(self, X_other):
        _y_pred = self.model.predict(X_other)
        return _y_pred
