# coding: utf-8
# Author：fengchi863
# Date ：2022/8/19 10:32

from Zeus.Saturn.v3_0_35.ModelBase import ModelBase
from lightgbm import LGBMRegressor
import lightgbm as lgb
import numpy as np
import random
from scipy import stats
random.seed(2022)

class LGBRegModel(ModelBase):
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

    @staticmethod
    def my_eval(preds, dtrain):
        label = dtrain.get_label()
        # 由于sklearn中的xgb都是最小化这个值，所以这里加负号
        ic = -1 * stats.pearsonr(label, preds)[0]
        return 'my_eval', ic

    @staticmethod
    def my_obj(preds, dtrain):
        def transfer_label(preds2, level):
            preds_copy = preds2.copy()
            for idx in range(len(level) - 1):
                min_ = level[idx]
                max_ = level[idx + 1]
                preds_copy = np.where((min_ <= abs(preds_copy)) & (abs(preds_copy) < max_), np.sign(preds_copy) * min_, preds_copy)
            return preds_copy
        label = dtrain.get_label()
        level = np.hstack([np.arange(0, 100) / 1000, np.arange(100, 200, 10) / 1000, np.arange(200, 300, 20) / 1000, np.arange(3, 197, 97) / 10])
        preds2 = preds.copy()
        preds2 = transfer_label(preds2, level)
        residual = (label - preds2).astype("float")
        grad = np.where(residual < 0, -2 * residual / (label + 1), -10 * 2 * residual / (label + 1))
        hess = np.where(residual < 0, 2 / (label + 1), 10 * 2 / (label + 1))
        return grad, hess

    def train_model(self, X_train, y_train, X_valid, y_valid, param):
        if 'early_stopping_rounds' in param:
            early_stopping_rounds = param.pop('early_stopping_rounds')
        else:
            early_stopping_rounds = None

        if 'score_threshold' in param:
            self.score_threshold = param.pop('score_threshold')

        param.pop('silent')
        n_estimators = param.pop('n_estimators')
        param['verbose'] = -1
        lgb_train = lgb.Dataset(X_train.values, y_train.values.ravel())
        model = lgb.train(param, lgb_train, num_boost_round=n_estimators, fobj=self.my_obj)

        # model = LGBMRegressor(**param)
        # model.fit(X_train.values, y_train.values.ravel())
        self.model = model

    def model_predict(self, X_other):
        _y_pred = self.model.predict(X_other)
        return _y_pred