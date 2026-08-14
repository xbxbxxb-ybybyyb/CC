# @Time : 2020/6/17 15:30
# @Author : Zhichen Lu
# @File : TimeSeriesTrainBase.py
import os
from abc import abstractmethod
from multiprocessing import Pool

import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn import metrics
from sklearn import preprocessing

from TrainingModel.TrainBase import TrainBase
from conf.feature_config import *
from conf.path_config import model_file_path
from dataApi.tradeDate import get_date_range


class TimeSeriesTrainBase(TrainBase):

    def __init__(self, start_date, end_date, factor_path=None, scale_list_=scale_list, non_scale_list_=non_scale_list, lag=30):
        super().__init__(start_date, end_date, factor_path, scale_list_, non_scale_list_)
        self.lag = lag

    def load_data_one_stk(self, stk, label_method, period_info, for_universe=False):
        train_start, train_end, test_start, test_end = period_info[1]
        dataset = self.fds.get_dataset(stk, train_start, test_end, label_method)
        no_pause_index = self.get_no_pause_index(stk)
        X_train, X_test = dataset[0].loc[no_pause_index].loc[(train_start, 925):(train_end, 1500)], \
                          dataset[0].loc[no_pause_index].loc[(test_start, 925):(test_end, 1500)]
        y_train, y_test = dataset[1].loc[X_train.index], dataset[1].loc[X_test.index]
        if len(X_train) < 242 * 5:
            return pd.Panel(), pd.Series(), pd.Panel(), pd.Series()
        # fillna
        X_train, X_test = self.fill_nan(X_train, X_test)
        # delete nan in label
        X_train, y_train = self.drop_nan_sample(X_train, y_train)
        X_test, y_test = self.drop_nan_sample(X_test, y_test)
        # preprocessing
        scaler = preprocessing.Normalizer()  # MinMaxScaler()
        if len(X_test) > 0:
            X_train, X_test = self.transformation_scaler(self.scale_list, self.non_scale_list, scaler, X_train, X_test)
        else:
            X_train = self.transformation_scaler(self.scale_list, self.non_scale_list, scaler, X_train)
            X_test = pd.DataFrame()
        Features_train = {}
        Features_test = {}
        for i in list(range(self.lag))[::-1]:
            Features_train[i] = X_train.shift(i)
            Features_test[i] = X_test.shift(i)
        Features_train = pd.Panel(Features_train)
        Features_test = pd.Panel(Features_test)
        Features_train = Features_train.swapaxes(0, 1)
        Features_test = Features_test.swapaxes(0, 1)
        if for_universe:
            Features_train.items = ['%d_%d' % (stk, x[0] * 10000 + x[1]) for x in Features_train.items]
            Features_test.items = ['%d_%d' % (stk, x[0] * 10000 + x[1]) for x in Features_test.items]
            y_train.index = Features_train.items
            y_test.index = Features_test.items
        return Features_train, y_train, Features_test, y_test

    def get_rolling_index_by_fixed_interval(self, start, end, period=60, period_predict=20):

        rolling_train_test_idx_list = []
        date_list = get_date_range(start, end)
        for idx in range((len(date_list) - period) // period_predict):
            train_start_idx = idx * period_predict
            train_end_idx = idx * period_predict + period - 1
            if idx == (len(date_list) - period) // period_predict:
                test_start_idx = idx * period_predict + period
                test_end_idx = len(date_list) - 1
            else:
                test_start_idx = idx * period_predict + period
                test_end_idx = test_start_idx + period_predict - 1
            rolling_train_test_idx_list.append((idx, [date_list[x] for x in [train_start_idx, train_end_idx, test_start_idx, test_end_idx]]))
        return rolling_train_test_idx_list

    def load_data_universe(self, stk_list, label_method, period_info):
        training_set, test_set, label_train, label_test = [], [], [], []
        pool = Pool(10)
        dataset_dict = {}
        for stk in stk_list:
            # self.load_data_one_stk(*(stk, label_method, period_info, True))
            # Features_train, y_train, Features_test, y_test = self.load_data_one_stk(stk,label_method, period_info,True)
            dataset_dict[stk] = pool.apply_async(self.load_data_one_stk, (*(stk, label_method, period_info, True),))
            # print(stk)
        pool.close()
        pool.join()
        for stk in stk_list:
            Features_train, y_train, Features_test, y_test = dataset_dict[stk].get()
            training_set.append(Features_train)
            test_set.append(Features_test)
            label_train.append(y_train)
            label_test.append(y_test)

        training_set = pd.concat(training_set, axis='items')
        test_set = pd.concat(test_set, axis='items')
        label_train = pd.concat(label_train)
        label_test = pd.concat(label_test)
        return training_set, label_train, test_set, label_test

    def train_base_universe(self, stk_list, label_method, period=60, period_predict=20, tag=None, model_path=model_file_path):
        out_path = '%s/%s/' % (model_path, tag)
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        rolling_index = self.get_rolling_index_by_fixed_interval(self.start_date, self.end_date, period, period_predict)
        model_set = {}
        predict_label = pd.Series()
        true_label = pd.Series()
        for period_info in rolling_index[9:]:
            print(period_info)
            Features_train, y_train, Features_test, y_test = self.load_data_universe(stk_list, label_method, period_info)
            print(Features_train.shape, Features_test.shape)
            model = self.feed_model_with_universe(Features_train, y_train, model_file_path + tag)
            prediction = model.predict(Features_test.values.reshape(Features_test.shape + (1,)))
            model_set['_'.join(list(map(str, period_info)))] = out_path + 'model_train_%d_%d_test_%d_%d.h5' % tuple(period_info[1])
            model.save(model_set['_'.join(list(map(str, period_info)))])
            true_label = pd.concat([true_label, y_test])
            predict_label = pd.concat([predict_label, pd.Series(np.argmax(prediction, axis=1), index=y_test.index)])
        compare = pd.DataFrame({'label': true_label, 'prediction': predict_label})
        pd.to_pickle(compare, out_path + 'label_compare.pkl')
        pd.to_pickle(model_set, out_path + 'model_set.pkl')
        print(out_path + 'label_compare.pkl')
        print(out_path + 'model_set.pkl')
        return model_set, compare

    def evaluate_basse_model(self, stk_list, label_method, period=60, period_predict=20, tag=None, model_path=model_file_path):
        out_path = '%s/%s/' % (model_path, tag)
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        rolling_index = self.get_rolling_index_by_fixed_interval(self.start_date, self.end_date, period, period_predict)
        model_set = {}
        predict_label = pd.Series()
        true_label = pd.Series()
        for period_info in rolling_index[9:]:
            print(period_info)
            Features_train, y_train, Features_test, y_test = self.load_data_universe(stk_list, label_method, period_info)
            print(Features_train.shape, Features_test.shape)
            model_set['_'.join(list(map(str, period_info)))] = out_path + 'model_train_%d_%d_test_%d_%d.h5' % tuple(period_info[1])
            model = load_model(model_set['_'.join(list(map(str, period_info)))])
            prediction = model.predict(Features_test.values.reshape(Features_test.shape + (1,)))
            true_label = pd.concat([true_label, y_test])
            temp_prediction = pd.Series(np.argmax(prediction, axis=1), index=y_test.index)
            predict_label = pd.concat([predict_label, temp_prediction])
            print('period:', metrics.accuracy_score(y_test + 1, temp_prediction))
            print('all_until_now:', metrics.accuracy_score(true_label + 1, predict_label))
            print('max_label:', pd.DataFrame(y_test).groupby(0).size().max() / len(y_test))
            print('max_label_until:', pd.DataFrame(true_label).groupby(0).size().max() / len(true_label))
            if len(true_label) != len(predict_label):
                print('Wrong Length')
        compare = pd.DataFrame({'label': true_label, 'prediction': predict_label})
        pd.to_pickle(compare, out_path + 'label_compare.pkl')
        print('all:', metrics.accuracy_score(compare['label'], compare['prediction']))

        return compare

    def tuning_for_stk(self, label_method, period=60, period_predict=20, tag=None, model_path=model_file_path):
        # TODO
        out_path = '%s/%s/' % (model_path, tag)
        rolling_index = self.get_rolling_index_by_fixed_interval(self.start_date, self.end_date, period, period_predict)
        pass

    @abstractmethod
    def feed_model_with_universe(self, Features_train, y_train, path):
        pass


"""
def main():
    TSTB = TimeSeriesTrainBase(start_date=20170103, end_date=20181231, factor_path='/data/group/800319/junkData/IntraFactorModel/FactorByStock_new/',
                               scale_list_=scale_list_5min, non_scale_list_=non_scale_list_5min)
    rolling_index = TSTB.get_rolling_index_by_fixed_interval(20180102, 20181231)
    stk_list = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/best_model_hyper_params/para_optimization_pool.pkl')
    # Features_train, y_train, Features_test, y_test = TSTB.load_data_one_stk(1, 'rise_down_zero_5min', rolling_index[0])
    training_set, label_train, test_set, label_test = TSTB.load_data_universe(stk_list, 'rise_down_zero_5min', rolling_index[0])


if __name__ == "__main__":
    main()
"""
