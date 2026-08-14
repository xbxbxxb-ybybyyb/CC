# coding: utf-8
# Author：fengchi863
# Date ：2020/5/19 10:05

import os
import random
from abc import abstractmethod
from datetime import datetime

import gc
import numpy as np
import pandas as pd
from sklearn import preprocessing
from tqdm import tqdm

from conf.feature_config import *
from dataApi.stockList import clean_stock_list
from dataset_generation import FactorDataSet


class TrainBase:

    def __init__(self, start_date, end_date, factor_path=None, scale_list_=scale_list, non_scale_list_=non_scale_list):
        self.start_date = start_date
        self.end_date = end_date
        self.no_pause_stock_pool = clean_stock_list(no_pause=True, no_ST=False).loc[self.start_date:self.end_date]
        # self.no_pause_index = self.no_pause_stock_pool[self.no_pause_stock_pool].index
        if factor_path is None:
            self.fds = FactorDataSet(start=start_date, end=end_date)
        else:
            self.fds = FactorDataSet(start=start_date, end=end_date, root_path=factor_path)
        self.stk_id = None
        self.dataset = None
        self.scale_list = scale_list_
        self.non_scale_list = non_scale_list_

    def __load_dataset(self, stk_id, label):
        dataset = self.fds.get_dataset(stk_id, self.start_date, self.end_date, label)
        return dataset

    def get_no_pause_index(self, stk_id):
        no_pause_index = self.no_pause_stock_pool[stk_id]
        no_pause_index = no_pause_index[no_pause_index].index
        return no_pause_index

    def load_data(self, stk_id, train_idx, test_idx, dataset):

        no_pause_index = self.get_no_pause_index(stk_id)
        # self.__load_dataset(stk_id, label)
        Features = dataset[0].copy()
        Features = self.drop_feature(Features)
        Labels = dataset[1].copy()
        Labels.index = Features.index
        Features = Features.loc[no_pause_index]  # .copy()
        Labels = Labels.loc[no_pause_index]  # .copy()
        X_train = Features.iloc[train_idx[0] * 242:train_idx[1] * 242 + 242]
        y_train = Labels.iloc[train_idx[0] * 242:train_idx[1] * 242 + 242]

        X_test = Features.iloc[test_idx[0] * 242:test_idx[1] * 242 + 242]
        y_test = Labels.iloc[test_idx[0] * 242:test_idx[1] * 242 + 242]
        return X_train, y_train, X_test, y_test

    def drop_feature(self, X_data, drop_list=drop_list):
        return X_data.drop(drop_list, axis=1)

    def sort_x_data_cols(self, X_data):
        cols = X_data.columns
        X_data = X_data.reindex(columns=sorted(cols))
        return X_data

    def drop_nan_sample(self, X_data, y_data):
        drop_index = y_data[np.isnan(y_data)].index
        X_data.drop(drop_index, inplace=True, axis=0)
        y_data.drop(drop_index, inplace=True, axis=0)
        return X_data, y_data

    def fill_nan(self, X_train, X_test=None):
        X_data = pd.concat([X_train, X_test]).values
        X_data[np.isinf(X_data)] = np.nan
        X_data = X_data.reshape(X_data.shape[0] // 242, 242, X_data.shape[1])
        ##############################
        previous_day_mean = pd.DataFrame(np.nanmean(X_data, axis=1)).shift(1).fillna(method='pad', axis=0).values
        previous_day_mean[0, :] = 0
        for feature_idx in range(X_data.shape[2]):
            if np.nansum(X_data[:, 0, feature_idx]) == 0:
                X_data[:, 0, feature_idx] = previous_day_mean[:, feature_idx]
        X_data = pd.Panel(X_data).fillna(method='pad', axis=1).values
        X_data = X_data.reshape(X_data.shape[0] * X_data.shape[1], X_data.shape[2])
        if X_test is None:
            return pd.DataFrame(X_data[:X_train.shape[0], :], index=X_train.index, columns=X_train.columns).fillna(0)
        return pd.DataFrame(X_data[:X_train.shape[0], :], index=X_train.index, columns=X_train.columns).fillna(0), \
               pd.DataFrame(X_data[X_train.shape[0]:, :], index=X_test.index, columns=X_test.columns).fillna(0)

    def transformation_scaler(self, scaler_list, non_scaler_list, Scaler, X_train_data, X_test_data=None):
        Scaler.fit(X_train_data[scaler_list])
        X_scaled_train = Scaler.transform(X_train_data[scaler_list])
        df_X_scaled_train = pd.DataFrame(X_scaled_train,
                                         index=X_train_data.index,
                                         columns=scaler_list)
        df_X_train_non_scaler_list = X_train_data[non_scaler_list]
        X_train = pd.concat([df_X_scaled_train, df_X_train_non_scaler_list], axis=1)
        if X_test_data is None:
            return X_train
        X_scaled_test = Scaler.transform(X_test_data[scaler_list])

        df_X_scaled_test = pd.DataFrame(X_scaled_test,
                                        index=X_test_data.index,
                                        columns=scaler_list)
        df_X_test_non_scaler_list = X_test_data[non_scaler_list]
        X_test = pd.concat([df_X_scaled_test, df_X_test_non_scaler_list], axis=1)
        return X_train, X_test

    def check_label_and_remark(self, y_train, y_test=None, threshold=0.15):
        if np.sum(y_train == 0) / y_train.shape[0] < threshold:
            zero_index = y_train[y_train == 0].index
            new_zero_value = [1 for i in range(int(len(zero_index) / 2))] + [-1 for i in range(
                len(zero_index) - int(len(zero_index) / 2))]
            random.shuffle(new_zero_value)
            y_train.loc[zero_index] = new_zero_value
        if y_test is None:
            return y_train
        if np.sum(y_test == 0) / y_test.shape[0] < threshold:
            zero_index = y_test[y_test == 0].index
            new_zero_value = [1 for i in range(int(len(zero_index) / 2))] + [-1 for i in range(
                len(zero_index) - int(len(zero_index) / 2))]
            random.shuffle(new_zero_value)
            y_test.loc[zero_index] = new_zero_value
        return y_train, y_test

    def get_rolling_index(self, stk_id, period=120, period_predict=20):
        rolling_train_test_idx_list = []
        no_pause_index = self.get_no_pause_index(stk_id)
        for idx in range((len(no_pause_index) - period) // period_predict):
            train_start_idx = idx * period_predict
            train_end_idx = idx * period_predict + period - 1
            if idx == (len(no_pause_index) - period) // period_predict:
                test_start_idx = idx * period_predict + period
                test_end_idx = len(no_pause_index) - 1
            else:
                test_start_idx = idx * period_predict + period
                test_end_idx = test_start_idx + period_predict - 1
            rolling_train_test_idx_list.append((idx, (train_start_idx, train_end_idx,
                                                      test_start_idx, test_end_idx)))
        return rolling_train_test_idx_list

    def time_series_cross_validation(self, stk_id, label, hyper_params, train_period=120, predict_period=20):
        dataset = self.__load_dataset(stk_id, label)
        train_and_test_list = self.get_rolling_index(stk_id, period=train_period, period_predict=predict_period)
        predictions = pd.DataFrame()
        label = pd.DataFrame()
        bar = tqdm(train_and_test_list)
        for idx, cell_idx in bar:
            bar.set_description(
                "%s | %d | %d | %d-%d" % (datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S').split(" ")[1],
                                          os.getpid(), stk_id, cell_idx[2], cell_idx[3]))
            train_start_idx, train_end_idx, test_start_idx, test_end_idx = \
                cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3]

            # data processing
            X_train, y_train, X_test, y_test = self.load_data(stk_id, (train_start_idx, train_end_idx),
                                                              (test_start_idx, test_end_idx), dataset)

            # delete nan in factor matrix
            X_train, X_test = self.fill_nan(X_train, X_test)

            # delete nan in label
            X_train, y_train = self.drop_nan_sample(X_train, y_train)
            X_test, y_test = self.drop_nan_sample(X_test, y_test)

            # randomly change the label of zero if pct of zero less than a threshold
            y_train, y_test = self.check_label_and_remark(y_train, y_test, threshold=0.15)
            label = pd.concat([label, y_test])
            scaler = preprocessing.MinMaxScaler()
            X_train, X_test = self.transformation_scaler(self.scale_list, self.non_scale_list, scaler, X_train, X_test)
            clf_model = self.model_train(X_train, y_train, hyper_params)
            clf_predictions, _ = self.model_predict(clf_model, X_test)
            predictions = pd.concat([predictions, pd.DataFrame(clf_predictions, index=y_test.index)])
            del X_train, X_test
            gc.collect()
        del dataset
        gc.collect()
        return predictions, label

    def get_train_data(self, stk_id, label):
        dataset = self.__load_dataset(stk_id, label)
        X_train, y_train = dataset[0], dataset[1]
        X_train = self.fill_nan(X_train)
        X_train, y_train = self.drop_nan_sample(X_train, y_train)
        y_train = self.check_label_and_remark(y_train)
        scaler = preprocessing.MinMaxScaler()
        X_train = self.transformation_scaler(self.scale_list, self.non_scale_list, scaler, X_train)
        return X_train, y_train

    @abstractmethod
    def model_train(self):
        pass

    @abstractmethod
    def model_predict(self):
        pass

    @abstractmethod
    def training_methodology(self):
        pass
