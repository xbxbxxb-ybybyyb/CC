# coding: utf-8
# Author：fengchi863

from dataApi import tradeDate, sendInfo
from Zeus.Saturn.v2_9.DataPrepare import DataPrepare
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

        if factor_filter_path:
            raw_factor_list = pd.read_excel(factor_filter_path, index_col=0)
            factor_list = raw_factor_list.query('corr_selected==1')['factor_name'].tolist()
            # print(f'使用已筛选因子，原有因子{len(raw_factor_list)}个，筛选后为{len(factor_list)}个')
            # print('*' * 30)
            self.factor_list = sorted(factor_list)

        if factor_score_path:
            factor_list = self.select_factor()  # 返回排过序的因子列表
            if factor_num < len(factor_list):
                self.factor_list = sorted(factor_list[:factor_num])
            else:
                self.factor_list = factor_list
                # print('factor_num没有起作用!')

            # print(f'经过打分筛选，还剩{len(self.factor_list)}个')
            # print('*' * 30)

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
    def train_model(self, X_train, y_train, param):
        pass

    @abstractmethod
    def model_predict(self, X_other):
        pass

    def set_factor_list(self, factor_list):
        self.factor_list = factor_list

    def check_and_set_factor_list(self, factor_list):
        assert self.factor_list == factor_list
        self.factor_list = factor_list

    def rolling_train_and_predict(self, len_train=4000, len_test=1000, rolling_type='valid', param=None,
                                  pct_threshold=0.06, refer_num=1000):
        y_pred_prob_list = list()
        y_pred_clf_list = list()

        score_threshold = 0.0

        if 'score_threshold' in param.keys():
            score_threshold = param.pop('score_threshold')
        if 'pct_threshold' in param.keys():
            pct_threshold = param.pop('pct_threshold')
        if 'refer_num' in param.keys():
            refer_num = int(param.pop('refer_num'))
        if 'len_train' in param.keys():
            len_train = int(param.pop('len_train'))
        if 'len_test' in param.keys():
            len_test = int(param.pop('len_test'))

        samples = self.samples.copy()
        y = samples.filter(regex='label*')
        X = samples.drop(y.columns.tolist(), axis=1)
        y = y[[self.label]]
        y = y.drop(np.isnan(y)[self.label][np.isnan(y)[self.label]].index)  # 剔除样本
        X = X.reindex(index=y.index)
        self.y = y
        if hasattr(self, 'factor_list') and len(self.factor_list) > 0:
            X = X[self.factor_list]

        rolling_train_test_list = self.get_rolling_index_by_samples(len_train, len_test, rolling_type)
        for idx, train_test_idx_list in enumerate(rolling_train_test_list):
            train_start_idx, train_end_idx, test_start_idx, test_end_idx = train_test_idx_list
            X_train = X.iloc[train_start_idx:train_end_idx]
            y_train = y.iloc[train_start_idx:train_end_idx]
            X_test = X.iloc[test_start_idx:test_end_idx]

            y_train[y_train > 0.2] = 0.1
            y_train[y_train < -0.2] = -0.1

            self.train_model(X_train, y_train, param)
            y_test_prob_pred = self.model_predict(X_test.values)
            y_train_prob_pred = self.model_predict(X_train.values)
            score_threshold = self.get_score_threshold(y_train, y_train_prob_pred, threshold=pct_threshold, refer_num=refer_num)
            y_pred_prob_list.append(pd.DataFrame(y_test_prob_pred, index=X_test.index))
            y_pred_clf_list.append(pd.DataFrame(y_test_prob_pred > score_threshold, index=X_test.index))

        y_pred_prob_all = pd.concat(y_pred_prob_list, axis=0)
        y_pred_clf_all = pd.concat(y_pred_clf_list, axis=0)
        return y_pred_prob_all, y_pred_clf_all

    def get_rolling_index_by_samples(self, len_train=4000, len_test=1000, rolling_type='valid'):
        rolling_train_test_list = list()

        y = self.y.copy()
        y['trade_date'] = self.y.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
        if rolling_type is 'valid':
            end_date = self.valid_end_date  # 这里设置为test_end_date可以开启cheat模式
            y = y.query(f'trade_date <= {end_date}')
        elif rolling_type is 'test' or 'fit':
            end_date = self.test_end_date
            y = y.query(f'trade_date <= {end_date}')
        else:
            raise Exception('rolling_type is given incorrect')

        samples_len = y.shape[0]
        if samples_len <= len_train:
            raise Exception(f'整体数据集的长度不足以切分，len_train必须小于等于样本训练集长度{samples_len}')

        # 首轮
        train_start_idx = 0
        train_end_idx = len_train
        test_start_idx = train_end_idx
        test_end_idx = test_start_idx + len_test

        while test_end_idx < samples_len:
            rolling_train_test_list.append([train_start_idx, train_end_idx, test_start_idx, test_end_idx])
            train_start_idx = train_start_idx + len_test
            train_end_idx = train_start_idx + len_train
            test_start_idx = train_end_idx
            test_end_idx = test_start_idx + len_test

        if rolling_train_test_list[-1][-1] < samples_len:
            rolling_train_test_list.append([train_start_idx, train_end_idx, test_start_idx, samples_len])

        return rolling_train_test_list

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
        evs = explained_variance_score(true_label, pred_label)
        return mse, mae, mae2, r2, evs

    def load_factor_score(self):
        factor_score = None
        if self.factor_score_path:
            factor_score = pd.read_excel(self.factor_score_path, index_col=0)
        return factor_score

    def select_factor(self):
        if self.factor_score_path:
            # 剔除
            factor_filter = self.load_factor_score().set_index('factor_name')['区间1-out-mic'].dropna()
            factor_filter = factor_filter[factor_filter >= 0.07].index.tolist()

            # 排序
            factor_s = self.load_factor_score().set_index('factor_name')['区间1-out-value'].dropna()
            factor_s2 = factor_s[factor_s > 0]
            factor_s2 = factor_s2.loc[list(set(factor_s2.index).intersection(set(factor_filter)))]
            factor_s3 = factor_s2[list(set(factor_s2.index).intersection(self.factor_list))]

            factor_list = pd.DataFrame(factor_s3).reset_index().sort_values(['区间1-out-value', 'factor_name'], ascending=False)
            return factor_list['factor_name'].tolist()
        else:
            return self.factor_list

    @staticmethod
    def get_score_threshold(y_train, y_train_prob_pred, threshold=0.06, refer_num=1000):
        _threshold = (y_train.iloc[-refer_num:, 0].values > threshold).sum() / refer_num
        pred_threshold = np.percentile(y_train_prob_pred[:-refer_num], (1 - _threshold) * 100)
        return pred_threshold