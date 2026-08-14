# coding: utf-8
# Author：fengchi863
# Date ：2025/2/27 13:52

import os
import json
import pickle
import numpy as np
import pandas as pd
import random
import xgboost as xgb
from sklearn.metrics import mean_squared_error, make_scorer
from sklearn.model_selection import GridSearchCV

class XGBRegModel:
    def __init__(self, **kwargs):
        super(XGBRegModel, self).__init__()
        self.model_name = 'XgbRegModel'
        self.params = {
            'learning_rate': 0.05,
            'objective': 'reg:linear',
            'eval_metric': 'rmse',
            'booster': 'gbtree',
            'n_estimators': 200,
            'random_state': 0,
            "seed": 0,
            "tree_method": 'gpu_hist'
        }
        self.param_grid = {
            'n_estimators': [200],
            "max_depth": [3, 5, 6, 7, 9, 12, 15, 17],
            "min_child_weight": [1, 5, 10, 20, 30],
            "subsample": [1],
            "colsample_bytree": [1],
            "reg_alpha": [0],
        }
        self.model = None

        for key, value in kwargs.items():
            self.params[key] = value

    def train_model(self, X_train, y_train, X_valid, y_valid):
        dtrain = xgb.DMatrix(X_train, y_train)
        dvalid = xgb.DMatrix(X_valid, y_valid)
        eval_result = {}
        num_boost_round = int(self.params.pop('num_boost_round'))
        # if 'roll' not in period:
        model = xgb.train(self.params, dtrain,
                          num_boost_round=num_boost_round,
                          evals=[(dtrain, 'train'), (dvalid, 'valid')],
                          evals_result=eval_result,
                          verbose_eval=0)
        self.model = model

    def fit(self, X_train, y_train, X_valid, y_valid, model_save_dir=None, model_save_name=None, model_name_suffix=None,
            scene_label=None, flag_task='reg', continue_path=None):
        print("参数：", self.params)
        if flag_task == "class":
            self.model = xgb.XGBClassifier(**self.params)
        else:
            self.model = xgb.XGBRegressor(**self.params)

        sample_weight = None
        if scene_label is not None:
            sample_weight = pd.DataFrame([1] * y_train.shape[0], index=y_train.index, columns=["weight"])
            sample_weight["weight"][scene_label["label"] == 1] = 3
            print(222222222222222222, sample_weight.shape, list(sample_weight["weight"])[:10])
            sample_weight = np.array(sample_weight)
            sample_weight = np.array(sample_weight)
            print(11111111111, sample_weight.dtype, sample_weight.shape, y_train.shape)
            a = [float(i) for i in sample_weight]
            print("训练权重集合：", set(a))
            for key_t in set(a):
                print(11111111, key_t, a.count(key_t))

        print("train sample_weight ================", sample_weight, X_train.shape)

        xgb_model_old = None
        # xgb_model_old = "/data/user/021012/code/FE_code/project_buy/model_output/europa/xgb_native/model/ceshi/FSRS/xgb_old1.txt"
        if continue_path:
            xgb_model_old = f"{continue_path}/xgb_{model_name_suffix}.txt"
            print(111111111111111111111111111111111111111111, xgb_model_old)

        self.model.fit(X_train, y_train, xgb_model=xgb_model_old)
        if model_save_dir:
            if model_save_name:
                save_modelname_temp = self.model_name + model_save_name
            else:
                save_modelname_temp = self.model_name

            if model_name_suffix:
                model_file = os.path.join(model_save_dir, "{}_{}.txt".format(save_modelname_temp, model_name_suffix))
            else:
                model_file = os.path.join(model_save_dir, "{}.txt".format(save_modelname_temp))
            self.my_save_model(model_file)