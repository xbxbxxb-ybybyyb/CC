# @Time : 2020/7/28 11:36
# @Author : Zhichen Lu
# @File : TrainBase.py
import datetime
import time
from abc import abstractmethod
from multiprocessing import Pool

import gc, os
import numpy as np
from tqdm import tqdm

from StrongStockModel.System.LoadFactor.factor_utils import *
from StrongStockModel.conf.path_config import fix_factor_true_send_evaluation_path, strong_stock_path
from System.LoadFactor.FactorDataSet import FactorDataSet
from System.LoadLabel.LabelDataSet import LabelDataSet
from dataApi.stockList import clean_stock_list
from StrongStockModel.conf.path_config import root_path
import pandas as pd

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
        self.fds = FactorDataSet()
        self.lds = LabelDataSet()
        if stock_pool is None:
            if os.path.exists(stock_pool_path):
                self.stock_pool = pd.read_pickle(stock_pool_path)
                self.stock_pool = self.stock_pool.loc[start:end]
            else:
                # self.stock_pool = clean_stock_list('ALL', no_pause=True, start_date=start, end_date=end)
                stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                              no_pause=True, least_recover_days=1,
                                              no_pause_limit=0.5, no_pause_stats_days=120,
                                              no_limit_up=False, no_limit_down=False,
                                              other_limit=None, start_date=20140101, end_date=20191231)
                h5_path = "/data/group/wdb_h5/WIND/universe_complete/universe_complete.h5"
                limit_info = {}
                limit_info['OPENUPLIMIT'] = pd.read_hdf(h5_path, 'OPENUPLIMIT')
                limit_info['OPENDOWNLIMIT'] = pd.read_hdf(h5_path, 'OPENDOWNLIMIT')
                for k in limit_info:
                    limit_info[k] = limit_info[k].reset_index()
                    limit_info[k]['dt'] = limit_info[k]['dt'].apply(lambda x: int(x.strftime('%Y%m%d')))
                    limit_info[k]['Ticker'] = limit_info[k]['Ticker'].apply(lambda x: int(x[:-3]))
                    limit_info[k] = limit_info[k].pivot_table(index='dt', columns='Ticker', values=k).reindex(stock_pool.index, axis=0).reindex(stock_pool.columns, axis=1).fillna(
                        0) > 0
                self.stock_pool = stock_pool & limit_info['OPENUPLIMIT'] & limit_info['OPENDOWNLIMIT']
                pd.to_pickle(self.stock_pool, stock_pool_path)
        elif isinstance(stock_pool, pd.DataFrame):
            isin = stock_pool.sum()
            in_list = isin[isin > 0].index.tolist()
            in_list = list(set(in_list).intersection(set(self.fds.stk_list)))
            self.stock_pool = stock_pool[in_list].loc[start:end]
        self.date_list = self.stock_pool.index.tolist()
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

        period_pool = self.stock_pool.loc[train_idx[0]:test_idx[1]]
        isin = period_pool.sum()
        union_stk_list = isin[isin > 0].index.tolist()
        date_list = period_pool.index.tolist()
        target_date_list = sorted(list(set(date_list) - set(self.data_queue.keys())))
        remove_date_list = sorted(list(set(self.data_queue.keys()) - set(date_list)))
        print('in_%d_%d | out_%d_%d' % (target_date_list[0], target_date_list[-1],
                                        remove_date_list[0] if len(remove_date_list) > 0 else 0,
                                        remove_date_list[-1] if len(remove_date_list) > 0 else 0))
        for date in remove_date_list:
            _ = self.data_queue.pop(date)
        gc.collect()
        pool = Pool(kernel)
        res_dict = {}
        e = time.time()
        for date in target_date_list:
            temp_stk_list = period_pool.loc[date]
            temp_stk_list = temp_stk_list[temp_stk_list].index.tolist()
            if len(temp_stk_list) == 0:
                continue
            # res_dict[date] = pool.apply_async(self.fds.load_fix_factor_h5, (*(temp_stk_list, fix_factor_list, date),))
            if self.feature_address is None:
                res_dict[date] = pool.apply_async(self.fds.load_strong_stk_date, (*(date, fix_factor_list),))
            else:
                res_dict[date] = pool.apply_async(self.fds.load_strong_stk_date, (*(date, fix_factor_list, self.feature_address),))

        pool.close()
        pool.join()
        load_time = time.time() - e

        for date in res_dict:
            self.data_queue[date] = res_dict[date].get()
        fix_factor = pd.concat([self.data_queue[x] for x in self.data_queue])
        fix_factor = fix_factor.sort_index()
        e = time.time()

        if label_method == 'fix_window':
            if 'kind' not in label_param:
                label_param['kind'] = 'clf'
            label = self.lds.calc_pctchg_N(union_stk_list, train_idx[0], test_idx[-1], **label_param)
        else:
            raise Exception('Wrong label type')
        label = label.loc[list(filter(lambda x: x[1] in [1000, 1030, 1100, 1300, 1330, 1400, 1430],
                                      label.index.tolist()))]
        label = label.stack(dropna=False).to_frame()
        if type(label.index) == pd.core.indexes.multi.MultiIndex:
            label.index = [(x[0], x[2], x[1]) for x in label.index]
        else:
            label.index = [(x[0][0], x[1], x[0][1]) for x in label.index]
        label.index = pd.MultiIndex.from_tuples(label.index)
        print(train_idx, test_idx)
        # if test_idx[-1]==20170607:
        #     print(1)
        label = label.loc[fix_factor.index]
        # fix_factor.index.levels[0]
        train_feature = fix_factor.loc[train_idx[0]:train_idx[-1]]
        train_label = label.loc[train_idx[0]:train_idx[-1]]
        test_feature = fix_factor.loc[test_idx[0]:test_idx[-1]]
        test_label = label.loc[test_idx[0]:test_idx[-1]]
        print('load %d | label %d' % (load_time, time.time() - e))
        e = time.time()
        train_feature, train_label, test_feature, test_label = \
            self.feature_engineering(train_feature, train_label, test_feature, test_label)
        self.data_queue.clear()
        del fix_factor
        gc.collect()
        return train_feature, train_label, test_feature, test_label, time.time() - e

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
            training_sample = X_train.shape[0]
            loading_time = time.time() - e - feature_engineering_time
            e = time.time()

            if len(X_train) > 2000 and len(set(y_train[y_train.columns[0]])) > 1:
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

