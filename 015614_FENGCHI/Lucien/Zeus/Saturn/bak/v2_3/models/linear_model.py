# coding: utf-8
# Author：fengchi863
# Date ：2022/7/12 13:54

from Zeus.Saturn.v2_3.ModelBase import ModelBase
from sklearn.linear_model import LinearRegression


class LinearModel(ModelBase):
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
        model = LinearRegression(**param)
        model.fit(X_train.values, y_train.values.ravel())
        self.model = model

    def model_predict(self, X_other):
        _y_pred = self.model.predict(X_other)
        _y_pred = _y_pred > 0.2    # TODO:这个阈值可以是一个修改点，根据样本的变化情况修改这个阈值
        return _y_pred

