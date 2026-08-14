# coding: utf-8
# Author：fengchi863
# Date ：2021/3/8 21:07
from abc import abstractmethod
import pandas as pd, numpy as np
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare
from LimitUpPredStrategy.conf.path_conf import samples_path, samples_path_20210513, label_path
from sklearn.model_selection import StratifiedKFold
from sklearn import metrics

class ModelBaseReg:
    def __init__(self, start_date=20140101, end_date=20201231,
                 stock_pool_address=None):
        tdp = TickDataPrepare()
        if stock_pool_address:
            stock_pool = pd.read_pickle(stock_pool_address)
        else:
            stock_pool = tdp.get_data_by_date_list('LimitPool', start_date=start_date, end_date=end_date, return_idx=True)

        self.start_date = start_date
        self.end_date = end_date
        self.stock_pool = stock_pool

    def get_dataset(self, train_start_date=20140101, train_end_date=20191231,
                    predict_start_date=20200101, predict_end_date=20201231,
                    sample_type='all_board',
                    label_type='cls_当日收盘是否涨停'):
        train_samples = pd.read_pickle(samples_path_20210513 + sample_type + '.pkl')
        label = pd.read_pickle(label_path + label_type + '.pkl')
        label = label.reindex(index=train_samples.index)
        concat_samples = pd.concat([train_samples, label], axis=1)
        train_samples = concat_samples.loc[train_start_date: train_end_date]
        predict_samples = concat_samples.loc[predict_start_date: predict_end_date]
        return train_samples, predict_samples

    @abstractmethod
    def train_model(self, X_train, y_train, params, end_date=None):
        pass

    @abstractmethod
    def predict(self, model, X_test, end_date=None):
        pass

    def set_skf(self, n_splits=5):
        self.skf = StratifiedKFold(n_splits=n_splits)

    def train_and_test_CV(self, X_y_train_test_list, params=None):
        print('交叉验证开始，共分为%d折交叉验证' % len(X_y_train_test_list))
        model_list = []
        score_list = []
        for idx in range(len(X_y_train_test_list)):
            print('第%d轮训练' % (idx+1))
            cell = X_y_train_test_list[idx]
            X_train, X_test = cell[0], cell[1]
            y_train, y_test = cell[2], cell[3]

            model = self.train_model(X_train, y_train, params)
            y_pred = self.predict(model, X_test)
            mse = metrics.mean_squared_error(y_test, y_pred)
            print('MSE: %.4f' % mse)
            score_list.append(mse) # 使用精准率，正确预测为正占全部预测为正的比例，越高越好
            model_list.append(model)
        best_model = model_list[np.argmin(score_list)]
        return best_model

    def transfomer_scaler(self, factor_list, scaler, X_train, X_test):
        scaler.fit(X_train[factor_list])
        X_scaled_train = scaler.transform(X_train[factor_list])
        X_scaled_test = scaler.transform(X_test[factor_list])
        X_train_scaled = pd.DataFrame(X_scaled_train,\
                                     index=X_train.index,\
                                     columns=factor_list)
        X_test_scaled = pd.DataFrame(X_scaled_test,\
                                     index=X_test.index,
                                     columns=factor_list)
        return X_train_scaled, X_test_scaled, scaler

    def convert_data_4_train_and_test(self, train_samples, non_scaler_list, *factor_scaler_list):
        X_y_train_test_list = []
        X = train_samples.iloc[:, :-1]
        y = train_samples.iloc[:, -1]
        skf_data = self.skf.split(X, y)
        for train_index, test_index in skf_data:
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            X_train_list = []
            X_test_list = []
            for factor_list, scaler in factor_scaler_list:
                tmp_X_train, tmp_X_test, _ = self.transfomer_scaler(factor_list, scaler, X_train, X_test)
                X_train_list.append(tmp_X_train)
                X_test_list.append(tmp_X_test)

            if len(non_scaler_list) > 0:
                X_train_other, X_test_other = X_train[non_scaler_list], X_test[non_scaler_list]
                X_train_list.append(X_train_other)
                X_test_list.append(X_test_other)

            X_train_scaled = pd.concat(X_train_list, axis=1)
            X_test_scaled = pd.concat(X_test_list, axis=1)

            X_train_scaled = X_train_scaled.reindex(columns=sorted(X_train_scaled.columns.tolist()))
            X_test_scaled = X_test_scaled.reindex(columns=sorted(X_test_scaled.columns.tolist()))

            X_y_train_test_list.append((X_train_scaled, X_test_scaled, y_train, y_test))

        return X_y_train_test_list

    def convert_data_4_predict(self, train_samples, predict_samples, non_scaler_list, *factor_scaler_list):
        X_train = train_samples.iloc[:, :-1]
        X_test = predict_samples.iloc[:, :-1]
        y_train = train_samples.iloc[:, -1]
        y_test = predict_samples.iloc[:, -1]
        X_train_list = []
        X_test_list = []
        for factor_list, scaler in factor_scaler_list:
            tmp_X_train, tmp_X_test, _ = self.transfomer_scaler(factor_list, scaler, X_train, X_test)
            X_train_list.append(tmp_X_train)
            X_test_list.append(tmp_X_test)

        if len(non_scaler_list) > 0:
            X_train_other, X_test_other = X_train[non_scaler_list], X_test[non_scaler_list]
            X_train_list.append(X_train_other)
            X_test_list.append(X_test_other)

        X_train_scaled = pd.concat(X_train_list, axis=1)
        X_test_scaled = pd.concat(X_test_list, axis=1)

        X_train_scaled = X_train_scaled.reindex(columns=sorted(X_train_scaled.columns.tolist()))
        X_test_scaled = X_test_scaled.reindex(columns=sorted(X_test_scaled.columns.tolist()))

        X_y_train_test_list = (X_train_scaled, X_test_scaled, y_train, y_test)
        return X_y_train_test_list

    def test_predict(self, model, predict_samples):
        X_test = predict_samples.iloc[:, :-1]
        y_test = predict_samples.iloc[:, -1]
        y_pred = self.predict(model, X_test)
        mse = metrics.mean_squared_error(y_test, y_pred)
        return y_pred, mse