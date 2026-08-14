# coding: utf-8
# Author：fengchi863
# Date ：2021/3/8 21:07
from abc import abstractmethod

import numpy as np
import pandas as pd
from sklearn import metrics
from ShortTermTrading.dataApi import tradeDate
from sklearn.model_selection import StratifiedKFold

from BombStockStrategy.conf.path_conf import samples_path, label_path


class ModelBaseClf:
    def __init__(self, start_date=20140701, end_date=20210531):

        self.start_date = start_date
        self.end_date = end_date

        # 交叉验证
        self.skf = None

    @staticmethod
    def get_dataset(filename='samples20211102', train_start_date=20140701, train_end_date=20191231,
                    predict_start_date=20200101, predict_end_date=20210731):
        samples = pd.read_pickle(samples_path + filename + '.pkl')
        train_samples = samples.loc[train_start_date: train_end_date]
        predict_samples = samples.loc[predict_start_date: predict_end_date]

        # 平移一天日期，供交易
        train_samples.index = train_samples.index.map(lambda x: (tradeDate.get_pre_trade_date(x[0], -1), x[1]))
        predict_samples.index = predict_samples.index.map(lambda x: (tradeDate.get_pre_trade_date(x[0], -1), x[1]))

        return train_samples, predict_samples

    @abstractmethod
    def train_model(self, x_train, y_train, params, end_date=None):
        pass

    @abstractmethod
    def predict(self, model, x_test, end_date=None):
        pass

    def set_skf(self, n_splits=5):
        self.skf = StratifiedKFold(n_splits=n_splits)

    def train_and_test_cv(self, x_y_train_test_list, params=None):
        print('交叉验证开始，共分为%d折交叉验证' % len(x_y_train_test_list))
        model_list = []
        score_list = []
        for idx in range(len(x_y_train_test_list)):
            print('第%d轮训练' % (idx+1))
            cell = x_y_train_test_list[idx]
            x_train, x_test = cell[0], cell[1]
            y_train, y_test = cell[2], cell[3]

            model = self.train_model(x_train, y_train, params)
            y_pred = self.predict(model, x_test)
            accuracy = metrics.accuracy_score(y_test, y_pred)
            precision = metrics.precision_score(y_test, y_pred)
            recall = metrics.recall_score(y_test, y_pred)
            f1_score = metrics.f1_score(y_test, y_pred)
            print('准确率：%.4f，精准率：%.4f，召回率：%.4f， F1分数：%.4f' %
                  (accuracy, precision, recall, f1_score))
            score_list.append(f1_score)
            model_list.append(model)
        best_model = model_list[np.argmax(score_list)]
        return best_model

    @staticmethod
    def _transformer_scaler(factor_list, scaler, x_train, x_test):
        scaler.fit(x_train[factor_list])
        x_scaled_train = scaler.transform(x_train[factor_list])
        x_scaled_test = scaler.transform(x_test[factor_list])
        x_train_scaled = pd.DataFrame(x_scaled_train,
                                      index=x_train.index,
                                      columns=factor_list)
        x_test_scaled = pd.DataFrame(x_scaled_test,
                                     index=x_test.index,
                                     columns=factor_list)
        return x_train_scaled, x_test_scaled, scaler

    def convert_data_4_train_and_test(self, train_samples, non_scaler_list, *factor_scaler_list):
        x_y_train_test_list = []
        x = train_samples.iloc[:, :-1]
        y = train_samples.iloc[:, -1]
        skf_data = self.skf.split(x, y)
        for train_index, test_index in skf_data:
            x_train, x_test = x.iloc[train_index], x.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            x_train_list = []
            x_test_list = []
            for factor_list, scaler in factor_scaler_list:
                tmp_x_train, tmp_x_test, _ = self._transformer_scaler(factor_list, scaler, x_train, x_test)
                x_train_list.append(tmp_x_train)
                x_test_list.append(tmp_x_test)

            if len(non_scaler_list) > 0:
                x_train_other, x_test_other = x_train[non_scaler_list], x_test[non_scaler_list]
                x_train_list.append(x_train_other)
                x_test_list.append(x_test_other)

            x_train_scaled = pd.concat(x_train_list, axis=1)
            x_test_scaled = pd.concat(x_test_list, axis=1)

            x_train_scaled = x_train_scaled.reindex(columns=sorted(x_train_scaled.columns.tolist()))
            x_test_scaled = x_test_scaled.reindex(columns=sorted(x_test_scaled.columns.tolist()))

            x_y_train_test_list.append((x_train_scaled, x_test_scaled, y_train, y_test))

        return x_y_train_test_list

    def convert_data_4_predict(self, train_samples, predict_samples, non_scaler_list, *factor_scaler_list):
        x_train = train_samples.iloc[:, :-1]
        x_test = predict_samples.iloc[:, :-1]
        y_train = train_samples.iloc[:, :-1]
        y_test = predict_samples.iloc[:, -1]
        x_train_list = []
        x_test_list = []
        for factor_list, scaler in factor_scaler_list:
            tmp_x_train, tmp_x_test, _ = self._transformer_scaler(factor_list, scaler, x_train, x_test)
            x_train_list.append(tmp_x_train)
            x_test_list.append(tmp_x_test)

        if len(non_scaler_list) > 0:
            x_train_other, x_test_other = x_train[non_scaler_list], x_test[non_scaler_list]
            x_train_list.append(x_train_other)
            x_test_list.append(x_test_other)

        x_train_scaled = pd.concat(x_train_list, axis=1)
        x_test_scaled = pd.concat(x_test_list, axis=1)

        x_train_scaled = x_train_scaled.reindex(columns=sorted(x_train_scaled.columns.tolist()))
        x_test_scaled = x_test_scaled.reindex(columns=sorted(x_test_scaled.columns.tolist()))

        x_y_train_test_list = (x_train_scaled, x_test_scaled, y_train, y_test)
        return x_y_train_test_list

    def test_predict(self, model, predict_samples):
        x_test = predict_samples.iloc[:, :-1]
        y_test = predict_samples.iloc[:, -1]
        y_pred = self.predict(model, x_test)
        conf_matrix = metrics.confusion_matrix(y_test, y_pred)
        return y_pred, conf_matrix