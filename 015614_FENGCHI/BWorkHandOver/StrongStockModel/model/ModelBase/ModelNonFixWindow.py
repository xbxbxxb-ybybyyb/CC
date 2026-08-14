# @Time : 2020/12/29 9:54
# @Author : Zhichen Lu
# @File : ModelNewLoading.py
import os, gc, time, datetime

from dataApi.FixFactorRollPrepare import load_fix_data_selfdefined_label, feature_engineering
import numpy as np
from dataApi.tradeDate import get_recent_trade_date, get_pre_trade_date, get_date_range
import pandas as pd
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelBase
from tqdm import tqdm


class ModelNonFixWindow(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
                 label_path='/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5/data/', future_bar_num=None):
        if future_bar_num is None:
            raise Exception('Future bar num must be defined')
        super().__init__(start, end, stock_pool, feature_address)
        self.using_factor_list = pd.read_pickle('/data/group/800442/800319/strategy_local_path/available_factor_list.pkl')
        self.feature_address = feature_address
        self.date_list = get_date_range(start, end)
        if label_path is None or future_bar_num is None:
            self.label_path = None
        else:
            self.label_path = f'{label_path}/future_{future_bar_num}_bar.npy'
        self.future_bar_num = future_bar_num

    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        gc.collect()
        e = time.time()
        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time, y_1day_train = load_fix_data_selfdefined_label(train_idx[0],
                                                                                                                                                      get_pre_trade_date(
                                                                                                                                                          train_idx[-1]),
                                                                                                                                                      fix_factor_list,
                                                                                                                                                      address=self.feature_address,
                                                                                                                                                      label_path=self.label_path,
                                                                                                                                                      return_1day_label=True)
        else:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time, y_1day_train = load_fix_data_selfdefined_label(train_idx[0], train_idx[-1],
                                                                                                                                                      fix_factor_list,
                                                                                                                                                      address=self.feature_address,
                                                                                                                                                      label_path=self.label_path,
                                                                                                                                                      return_1day_label=True)
        train_feature, train_label, train_idx_date, train_idx_time, train_idx_code, y_1day_train = feature_engineering(train_feature, train_label, nolimit_train, train_idx_date,
                                                                                                                       train_idx_time, train_idx_code, y_1day_train)
        train_feature = train_feature
        index_train = pd.MultiIndex.from_tuples(list(zip(train_idx_date.tolist(), train_idx_time.tolist(), train_idx_code.tolist())))
        train_feature, train_label = pd.DataFrame(train_feature, index=index_train, columns=fix_factor_list), \
                                     pd.DataFrame({'actual_label': train_label, '1_day_label': y_1day_train}, index=index_train)

        today = get_pre_trade_date(int(datetime.date.today().strftime('%Y%m%d')))
        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            test_feature, test_label = pd.DataFrame(columns=fix_factor_list), pd.DataFrame(columns=fix_factor_list)
        else:
            if test_idx[-1] > today:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time, y_1day = load_fix_data_selfdefined_label(start_date=test_idx[0],
                                                                                                                                              end_date=today,
                                                                                                                                              factor_list=fix_factor_list,
                                                                                                                                              return_idx=True,
                                                                                                                                              address=self.feature_address,
                                                                                                                                              label_path=self.label_path,
                                                                                                                                              return_1day_label=True)
            else:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time, y_1day = load_fix_data_selfdefined_label(start_date=test_idx[0],
                                                                                                                                              end_date=test_idx[-1],
                                                                                                                                              factor_list=fix_factor_list,
                                                                                                                                              return_idx=True,
                                                                                                                                              address=self.feature_address,
                                                                                                                                              label_path=self.label_path,
                                                                                                                                              return_1day_label=True)

            if today <= test_idx[-1]:
                test_label[np.isnan(test_label) & (test_idx_date == today)] = 0
                test_nolimit[(test_label == 0) & (test_idx_date == today)] = True
                print('-----------new update-----------')
            test_feature, test_label, test_idx_date, test_idx_time, test_idx_code, y_1day = feature_engineering(test_feature, test_label, test_nolimit, test_idx_date,
                                                                                                                test_idx_time, test_idx_code, y_1day)

            index_test = pd.MultiIndex.from_tuples(list(zip(test_idx_date.tolist(), test_idx_time.tolist(), test_idx_code.tolist())))

            test_feature, test_label = pd.DataFrame(test_feature, index=index_test, columns=fix_factor_list), \
                                       pd.DataFrame({'actual_label': test_label, '1_day_label': y_1day}, index=index_test)
        return train_feature, train_label, test_feature, test_label, time.time() - e

    def rolling_train_and_predict(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = pd.DataFrame()
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, feature_engineering_time, training_sample = 0, 0, 0, 0
        model = None

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

            if os.path.exists(params['feature_path'] + '%d.pkl' % train_end_idx):
                fix_factor_list = pd.read_pickle(params['feature_path'] + '%d.pkl' % train_end_idx)
                X_train, y_train, X_test, y_test, feature_engineering_time = \
                    self.get_dataset((get_pre_trade_date(train_end_idx, 12), train_end_idx), (test_start_idx, test_end_idx),
                                     fix_factor_list, None, label_methodology, label_param, kernel=kernel)
            else:
                fix_factor_list = self.get_fix_factor_evaluation(factor_nums, train_end_idx)
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
                y_test['prediction'] = pred_label
                print('test_ic', train_end_idx, y_test.corr())
                label = label.append(y_test)
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label
