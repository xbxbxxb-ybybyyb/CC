# coding: utf-8
# Author：fengchi863

from dataApi import tradeDate, sendInfo
from Zeus.Saturn.v1_1.DataPrepare import DataPrepare
from abc import abstractmethod
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import pandas as pd
from sklearn.model_selection import StratifiedKFold


class ModelBase:
    def __init__(self,
                 model_name: str = None,
                 train_start_date=20160104,
                 train_end_date=20181231,
                 valid_start_date=20191008,
                 valid_end_date=20200630,
                 pred_start_date=20200701,
                 pred_end_date=20201231,
                 factor_score_path=None,
                 factor_filter_path=None,
                 profit_path=None,
                 label='label_v2o10d1'):
        self.model_name = model_name
        self.train_start_date = train_start_date
        self.train_end_date = train_end_date
        self.valid_start_date = valid_start_date
        self.valid_end_date = valid_end_date
        self.pred_start_date = pred_start_date
        self.pred_end_date = pred_end_date

        self.factor_score_path = factor_score_path
        self.factor_filter_path = factor_filter_path
        self.profit_path = profit_path
        self.label = label

        if factor_filter_path:
            raw_factor_list = pd.read_excel(factor_filter_path, index_col=0)
            factor_list = raw_factor_list.query('corr_selected==1')['factor_name'].tolist()
            print(f'使用已筛选因子，原有因子{len(raw_factor_list)}个，筛选后为{len(factor_list)}个')
            self.factor_list = factor_list

        self.model = None

    def get_dateset(self):
        dp = DataPrepare()
        samples = dp.get_samples()
        samples['trade_date'] = samples.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()

        # 处理数据集，这里要根据数据集进行变化
        y = samples.filter(regex='label*')
        X = samples.drop(y.columns.tolist(), axis=1)
        y = y[[self.label]]
        y['trade_date'] = samples.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
        X['trade_date'] = samples.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()

        # 这里要保证样本文件中存在这几天的数据
        X_train = X.query(f'trade_date >= {self.train_start_date} & trade_date <= {self.train_end_date}')
        y_train = y.query(f'trade_date >= {self.train_start_date} & trade_date <= {self.train_end_date}')
        X_valid = X.query(f'trade_date >= {self.valid_start_date} & trade_date <= {self.valid_end_date}')
        y_valid = y.query(f'trade_date >= {self.valid_start_date} & trade_date <= {self.valid_end_date}')

        y_train = y_train[[self.label]]
        y_valid = y_valid[[self.label]]

        X_train = X_train.drop('trade_date', axis=1)
        X_valid = X_valid.drop('trade_date', axis=1)

        if hasattr(self, 'factor_list'):
            X_train = X_train[self.factor_list]
            X_valid = X_valid[self.factor_list]

        assert len(self.factor_list) == X_train.shape[1]
        assert len(self.factor_list) == X_valid.shape[1]

        return X_train, y_train, X_valid, y_valid

    @abstractmethod
    def train_model(self, X_train, y_train, param):
        pass

    @abstractmethod
    def model_predict(self, X_other):
        pass

    @staticmethod
    def calc_model_score(true_label, pred_label):
        acc = accuracy_score(true_label, pred_label)
        rec = recall_score(true_label, pred_label)
        prec = precision_score(true_label, pred_label)
        f1 = f1_score(true_label, pred_label)
        auc = roc_auc_score(true_label, pred_label)
        return acc, rec, prec, f1, auc

    def get_skf(self, kfold=5):
        return
