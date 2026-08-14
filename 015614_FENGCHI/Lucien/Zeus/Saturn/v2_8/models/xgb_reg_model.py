# coding: utf-8
# Author：fengchi863
# Date ：2022/7/16 16:10

from Zeus.Saturn.v2_8.ModelBase import ModelBase
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
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

    @staticmethod
    def my_eval(preds, dtrain):
        label = dtrain.get_label()
        # 由于sklearn中的xgb都是最小化这个值，所以这里加负号
        pos_ratio = (label > 0).sum() / len(label)
        perc_value = np.percentile(preds, pos_ratio * 100)
        score = -roc_auc_score(label > 0, preds > perc_value)
        return 'my_eval', score

    def train_model(self, X_train, y_train, param):
        param_copy = param.copy()
        if 'early_stopping_rounds' in param_copy:
            early_stopping_rounds = int(param_copy.pop('early_stopping_rounds'))
        else:
            early_stopping_rounds = None

        X_train, X_valid, y_train, y_valid = train_test_split(X_train, y_train, test_size=0.2, shuffle=False)
        valid = [X_valid.values, y_valid.values.ravel()]
        eval_set = [valid]

        model = XGBRegressor(**param_copy)
        model.fit(X_train.values, y_train.values.ravel(),
                  eval_metric='rmse',
                  early_stopping_rounds=early_stopping_rounds,
                  eval_set=eval_set,
                  verbose=False)
        print(f'最佳轮次为{model.best_iteration}，最佳树个数为{model.best_ntree_limit}, 最佳得分为{model.best_score}')
        self.model = model

    def model_predict(self, X_other):
        _y_pred = self.model.predict(X_other)
        return _y_pred
