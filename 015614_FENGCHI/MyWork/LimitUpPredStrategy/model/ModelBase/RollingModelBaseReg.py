# coding: utf-8
# Author：fengchi863
# Date ：2021/3/8 21:07
from abc import abstractmethod
import pandas as pd
from LimitUpPredStrategy.conf.path_conf import samples_path, label_path, factor_evaluation_bt_path,strategy_pool_file_path,samples_path_20210809,factor_evaluation_bt_path_20210809
from sklearn import metrics
from LimitUpPredStrategy.dataApi import tradeDate

class RollingModelBaseReg:
    def __init__(self, start_date=20140701, end_date=20191231):

        date_list = tradeDate.get_date_range(start_date, end_date)

        self.start_date = start_date
        self.end_date = end_date
        self.date_list = date_list
        self.train_samples = None
        self.predict_samples = None

    def set_dataset(self, train_start_date=20140101, train_end_date=20191231,
                    predict_start_date=20200101, predict_end_date=20201231,
                    stock_pool_type='all_board',
                    label_type='reg_次日开盘溢价'):
        train_samples = pd.read_pickle(samples_path_20210809 + 'ApprovedFactor' + '.pkl')
        if stock_pool_type!='all_board':
            stock_pool = pd.read_hdf(samples_path_20210809, key=stock_pool_type)
            train_samples = train_samples.reindex(index=stock_pool.index)
        label = pd.read_pickle(label_path + label_type + '.pkl')
        label = label.reindex(index=train_samples.index)
        concat_samples = pd.concat([train_samples, label], axis=1)
        train_samples = concat_samples.loc[train_start_date: train_end_date]
        predict_samples = concat_samples.loc[predict_start_date: predict_end_date]
        self.train_samples = train_samples
        self.predict_samples = predict_samples

    # 给滚动训练调用
    def get_dataset(self, train_idx, test_idx, factor_num):
        factor_list = self.get_factor_evaluation(indicator='ret_tmr30_IC', early_date=train_idx[0], factor_num=factor_num)
        train_samples = self.train_samples.loc[train_idx[0]:train_idx[1]]
        test_samples = self.train_samples.loc[test_idx[0]:test_idx[1]]
        X_train = train_samples.iloc[:,:-1]
        y_train = train_samples.iloc[:,-1]
        X_test = test_samples.iloc[:,:-1]
        y_test = test_samples.iloc[:,-1]
        return X_train[factor_list], y_train, X_test[factor_list], y_test

    @abstractmethod
    def train_model(self, X_train, y_train, params):
        pass

    @abstractmethod
    def predict(self, model, X_test):
        pass

    def get_factor_evaluation(self, stock_pool='all_board', indicator='ret_tmr30_IC', factor_num=80, early_date=None):
        early_month = early_date // 100
        half_year_month_list = list(map(lambda x: x // 100, tradeDate.trade_half_years))
        last_month = max([i for i in half_year_month_list if i < early_month])
        factor_evaluation_bt_res = pd.read_pickle(factor_evaluation_bt_path_20210809 + 'reg_factor_std60_%d.pkl' % last_month)
        factor_evaluation_bt_res = factor_evaluation_bt_res.loc[self.train_samples.columns]
        s_indicator = factor_evaluation_bt_res[indicator].apply(abs)
        factor_list = s_indicator.sort_values(ascending=False)[:factor_num].index.tolist()
        return factor_list

    def test_predict(self, model, predict_samples):
        X_test = predict_samples.iloc[:, :-1]
        y_test = predict_samples.iloc[:, -1]
        y_pred = self.predict(model, X_test)
        mse = metrics.mean_squared_error(y_test, y_pred)
        return y_pred, mse

    def get_rolling_index(self, period=60, period_predict=10):
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

    @abstractmethod
    def rolling_train_and_predict(self, params={}, period=100000, predict_period=1000):
        pass