# @Time : 2020/7/28 11:36
# @Author : Zhichen Lu
# @File : TrainBase.py
import sys
sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/015614/BWorkHandOver')
sys.path.append('/data/user/015614/BWorkHandOver/ensemblemonitor-strategy-python')
sys.path.append('/data/user/015614/BWorkHandOver/StrongStockModel')

import datetime
import time
from abc import abstractmethod
from multiprocessing import Pool

import gc, os
import numpy as np
from tqdm import tqdm

# from StrongStockModel.System.LoadFactor.factor_utils import *
from StrongStockModel.conf.path_config import fix_factor_true_send_evaluation_path, strong_stock_path
from System.LoadFactor.FactorDataSet import FactorDataSet
from System.LoadLabel.LabelDataSet import LabelDataSet
from dataApi.stockList import clean_stock_list
from StrongStockModel.conf.path_config import root_path
import pandas as pd
from dataApi.tradeDate import get_date_range

stock_pool_path = root_path + 'stock_pool_without_limit_up_down.pkl'


def get_sample_days(sample_num, num):
    dataset_qualified = sample_num > num
    idx = dataset_qualified.values.argmax(axis=1)
    dataset_day = pd.Series(idx, index=sample_num.index).apply(lambda x: sample_num.columns[x])
    sample = []
    for idx, days in zip(dataset_day.index, dataset_day):
        sample.append(sample_num.loc[idx, days])
    dataset_day = pd.DataFrame(dataset_day)
    dataset_day['samples'] = sample
    return dataset_day


class ModelBase:

    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None):
        # self.fds = FactorDataSet()
        # self.lds = LabelDataSet()
        self.date_list = get_date_range(start, end)
        self.data_queue = {}
        self.feature_address = feature_address

    @abstractmethod
    def get_fix_factor_evaluation(self, num):
        factor_list = pd.read_pickle(fix_factor_true_send_evaluation_path)
        if num > len(factor_list):
            num = len(factor_list)
            print('the max length of fix_factor_list is %d' % (len(factor_list)))
        return factor_list[:num]

    @abstractmethod
    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        pass

    def get_rolling_index(self, period=10, period_predict=10):
        rolling_train_test_idx_list = []
        if len(self.date_list) == period:
            return [(0, (self.date_list[0], self.date_list[-1], self.date_list[-1], self.date_list[-1]))]
        elif (len(self.date_list) - period) % period_predict == 0:
            length = (len(self.date_list) - period) // period_predict
        else:
            length = (len(self.date_list) - period) // period_predict + 1
        for idx in range(length):
            train_start_idx = idx * period_predict
            train_end_idx = idx * period_predict + period - 1
            if idx == (len(self.date_list) - period) // period_predict:
                test_start_idx = idx * period_predict + period
                test_end_idx = len(self.date_list) - 1
            else:
                test_start_idx = idx * period_predict + period
                test_end_idx = test_start_idx + period_predict - 1
            train_start_date, train_end_date, test_start_date, test_end_date = [self.date_list[i] for i in
                                                                                [train_start_idx, train_end_idx,
                                                                                 test_start_idx, test_end_idx]]
            rolling_train_test_idx_list.append(
                (idx, (train_start_date, train_end_date, test_start_date, test_end_date)))
        return rolling_train_test_idx_list

    def get_rolling_index_by_sample(self, train_sample=40000, test_sample=10000, max_test_period=10, end_date=20181231):
        strong_stock = pd.read_pickle(strong_stock_path)
        strong_stock_sample_count = strong_stock.sum(axis=1) * 7
        sample_stat = pd.DataFrame({x: strong_stock_sample_count.rolling(x).sum() for x in list(range(1, 800))})
        training_day = get_sample_days(sample_stat, train_sample)
        sample_future_stat = pd.DataFrame({x: strong_stock_sample_count.rolling(x).sum().shift(-x) for x in list(range(1, 800))})
        test_day = get_sample_days(sample_future_stat, test_sample)

        training_day.columns = ['training_days', 'training_sample']
        test_day.columns = ['test_days', 'test_sample']
        info = pd.concat([training_day, test_day], axis=1)
        info.index = info.index.astype(int)
        info = info.loc[:end_date]
        train_start_date = info.index[0]
        train_end_date, test_start_date = info[info['training_sample'] > train_sample].index.tolist()[:2]
        info['judge'] = info['test_days'] / info['training_days'] <= 0.2

        if info.at[train_end_date, 'judge']:
            end_idx = info.index.tolist().index(train_end_date) + min(info.at[train_end_date, 'test_days'], max_test_period)
        else:
            end_idx = info.index.tolist().index(train_end_date) + min(max(1, int(info.loc[train_end_date, 'training_days'] * 0.2)), max_test_period)
        test_end_date = info.index[end_idx]
        rolling_train_test_idx_list = []
        rolling_train_test_idx_list.append((train_start_date, train_end_date, test_start_date, test_end_date))

        while end_idx < (info.shape[0] - 1):
            train_end_date = test_end_date
            train_start_date = info.index[end_idx - info.at[train_end_date, 'training_days']]
            test_start_date = info.index[end_idx + 1]
            if info.at[train_end_date, 'judge']:
                end_idx = end_idx + min(info.at[train_end_date, 'test_days'], max_test_period)
            else:
                end_idx = end_idx + min(max(1, int(info.loc[train_end_date, 'training_days'] * 0.2)), max_test_period)
            if end_idx >= info.shape[0]:
                end_idx = info.shape[0] - 1
            test_end_date = info.index[end_idx]
            rolling_train_test_idx_list.append((train_start_date, train_end_date, test_start_date, test_end_date))
        return rolling_train_test_idx_list

    @abstractmethod
    def feature_engineering(self, train_feature, train_label, test_feature, test_label):
        value_count = pd.Series((~np.isnan(train_feature.values)).sum(axis=1), index=train_feature.index)
        train_feature = train_feature[value_count > train_feature.shape[1] * 0.80]
        value_count = pd.Series((~np.isnan(test_feature.values)).sum(axis=1), index=test_feature.index)
        test_feature = test_feature[value_count > test_feature.shape[1] * 0.8]
        train_label, test_label = train_label.loc[train_feature.index].dropna(), test_label.loc[
            test_feature.index].dropna()
        train_feature, test_feature = train_feature.loc[train_label.index].fillna(0), test_feature.loc[
            test_label.index].fillna(0)

        train_arr = train_feature.values
        train_arr[train_arr == np.inf] = 0
        train_arr[train_arr == -np.inf] = 0
        train_feature = pd.DataFrame(train_arr, index=train_feature.index, columns=train_feature.columns)
        test_arr = test_feature.values
        test_arr[test_arr == np.inf] = 0
        test_arr[test_arr == -np.inf] = 0
        test_feature = pd.DataFrame(test_arr, index=test_feature.index, columns=test_feature.columns)
        del train_arr, test_arr
        return train_feature.clip(-5, 5), train_label, test_feature.clip(-5, 5), test_label

    @abstractmethod
    def train_model(self, X_train, y_train, params, end_date=None):
        pass

    @abstractmethod
    def predict(self, model, X_test, end_date=None):
        pass

    @abstractmethod
    def training_methodology(self, params, period=10, predict_period=10):
        pass

    @abstractmethod
    def rolling_train_and_predict(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = pd.DataFrame()
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, feature_engineering_time, training_sample = 0, 0, 0, 0
        model = None
        fix_factor_list = self.get_fix_factor_evaluation(factor_nums)
        for idx, cell_idx in bar:
            bar.set_description(
                "%s | %d | %d-%d || loading %.1f | feature engineering %.1f | training %.1f | training sample %d" % (
                    datetime.datetime.now().strftime('%H:%M:%S'),
                    os.getpid(), cell_idx[2], cell_idx[3], loading_time, feature_engineering_time,
                    training_time, training_sample))
            train_start_idx, train_end_idx, test_start_idx, test_end_idx = \
                cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3]
            e = time.time()
            print('check', cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3])
            # if test_end_idx!= 20170607:
            #     continue
            X_train, y_train, X_test, y_test, feature_engineering_time = \
                self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),
                                 fix_factor_list, None, label_methodology, label_param, kernel=kernel)
            gc.collect()
            loading_time = time.time() - e - feature_engineering_time
            e = time.time()

            print('re-train in this round')
            model = self.train_model(X_train, y_train, params, train_end_idx)
            if model is None:
                continue
            training_time = time.time() - e
            if len(X_test) == 0:
                print('zero sample')
                continue
            else:
                pred_label = self.predict(model, X_test, train_end_idx)
                y_test.columns = ['actual_label']
                y_test['prediction'] = pred_label
                print('test_ic', train_end_idx, y_test.corr())
                label = label.append(y_test)
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label

