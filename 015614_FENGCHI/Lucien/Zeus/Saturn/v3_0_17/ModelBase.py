# coding: utf-8
# Author：fengchi863

from dataApi import tradeDate, sendInfo
from Zeus.Saturn.v3_0_17.DataPrepare import DataPrepare
from abc import abstractmethod
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score, explained_variance_score
import pandas as pd
import numpy as np
import random
random.seed(2022)

class ModelBase:
    def __init__(self,
                 model_name: str = None,
                 date_config: dict = None,
                 factor_score_path=None,
                 factor_filter_path=None,
                 data_path=None,
                 profit_path=None,
                 label='label_v2o10d1',
                 factor_num=1e5):
        self.model_name = model_name
        self.train_start_date = date_config['train_start_date']
        self.train_end_date = date_config['train_end_date']
        self.valid_start_date = date_config['valid_start_date']
        self.valid_end_date = date_config['valid_end_date']
        self.test_start_date = date_config['test_start_date']
        self.test_end_date = date_config['test_end_date']

        self.factor_score_path = factor_score_path
        self.factor_filter_path = factor_filter_path
        self.profit_path = profit_path
        self.saturn_data_path = data_path
        self.label = label
        self.factor_num = factor_num

        dp = DataPrepare()
        self.samples = dp.get_samples(self.saturn_data_path)
        self.y = None

        self.model = None

    def get_dateset(self):
        samples = self.samples.copy()
        samples['trade_date'] = samples.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()

        # 处理数据集，这里要根据数据集进行变化
        y = samples.filter(regex='label*')
        X = samples.drop(y.columns.tolist(), axis=1)
        y = y[[self.label]]

        # 针对这个特定样本集，剔除那个这个标签为空的样本
        y = y.drop(np.isnan(y)[self.label][np.isnan(y)[self.label]].index)
        X = X.reindex(index=y.index)

        y['trade_date'] = y.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
        X['trade_date'] = X.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()

        # 这里要保证样本文件中存在这几天的数据
        X_train = X.query(f'trade_date >= {self.train_start_date} & trade_date <= {self.train_end_date}')
        y_train = y.query(f'trade_date >= {self.train_start_date} & trade_date <= {self.train_end_date}')
        X_valid = X.query(f'trade_date >= {self.valid_start_date} & trade_date <= {self.valid_end_date}')
        y_valid = y.query(f'trade_date >= {self.valid_start_date} & trade_date <= {self.valid_end_date}')
        X_test = X.query(f'trade_date >= {self.test_start_date} & trade_date <= {self.test_end_date}')
        y_test = y.query(f'trade_date >= {self.test_start_date} & trade_date <= {self.test_end_date}')

        y_train = y_train[[self.label]]
        y_valid = y_valid[[self.label]]
        y_test = y_test[[self.label]]

        X_train = X_train.drop('trade_date', axis=1)
        X_valid = X_valid.drop('trade_date', axis=1)
        X_test = X_test.drop('trade_date', axis=1)

        if hasattr(self, 'factor_list') and len(self.factor_list) > 0:
            X_train = X_train[self.factor_list]
            X_valid = X_valid[self.factor_list]
            X_test = X_test[self.factor_list]

        assert len(self.factor_list) == X_train.shape[1]
        assert len(self.factor_list) == X_valid.shape[1]
        assert len(self.factor_list) == X_test.shape[1]
        # print('数据长度校验通过')
        #
        # print('各个数据集的大小：\n', f'X_train：{X_train.shape}\n', f'y_train：{y_train.shape}\n',
        #       f'X_valid：{X_valid.shape}\n', f'y_valid：{y_valid.shape}\n', f'X_test：{X_test.shape}\n',
        #       f'y_test：{y_test.shape}')
        # print('整体正负样本的平衡度: ', f'正样本比例：{round(((y > 0).sum() / len(y))[self.label], 4)}')
        # print('*' * 30)

        return X_train, y_train, X_valid, y_valid, X_test, y_test

    @abstractmethod
    def train_model(self, X_train, y_train, X_valid, y_valid, param):
        pass

    @abstractmethod
    def model_predict(self, X_other):
        pass

    def set_factor_list(self, factor_list):
        if self.factor_num <= len(factor_list):
            self.factor_list = factor_list[:self.factor_num]
        else:
            self.factor_list = factor_list

    def check_and_set_factor_list(self, factor_list):
        assert self.factor_list == factor_list
        self.factor_list = factor_list

    @staticmethod
    def calc_model_score(true_label, pred_label):
        acc = accuracy_score(true_label, pred_label)
        rec = recall_score(true_label, pred_label)
        prec = precision_score(true_label, pred_label)
        f1 = f1_score(true_label, pred_label)
        auc = roc_auc_score(true_label, pred_label)
        return acc, rec, prec, f1, auc

    @staticmethod
    def calc_model_reg_score(true_label, pred_label):
        mse = mean_squared_error(true_label, pred_label)
        mae = mean_absolute_error(true_label, pred_label)
        mae2 = median_absolute_error(true_label, pred_label)
        r2 = r2_score(true_label, pred_label)
        return mse, mae, mae2, r2