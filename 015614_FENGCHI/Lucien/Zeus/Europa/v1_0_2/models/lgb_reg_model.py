# coding: utf-8
# Author：fengchi863
# Date ：2022/8/19 10:32

from Zeus.Europa.v1_0_2.ModelBase import ModelBase
from lightgbm import LGBMRegressor
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
                 label='label_TN_o2ul'
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

    def train_model(self, X_train, y_train, X_valid, y_valid, param):
        if 'early_stopping_rounds' in param:
            early_stopping_rounds = param.pop('early_stopping_rounds')
        else:
            early_stopping_rounds = None

        if 'score_threshold' in param:
            self.score_threshold = param.pop('score_threshold')

        model = LGBMRegressor(**param)
        model.fit(X_train.values, y_train.values.ravel())
        self.model = model

    def model_predict(self, X_other):
        _y_pred = self.model.predict(X_other)
        return _y_pred