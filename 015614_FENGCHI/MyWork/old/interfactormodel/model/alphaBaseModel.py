import pandas as pd
import numpy as np
import bottleneck
from functools import partial
from tqdm import tqdm
from dataApi.tradeDate import get_date_range, get_pre_trade_date

class AlphaBaseModel(object):

    def __init__(self, start_date, end_date, future_days_max, future_index,
                 middle_address, stock_pool_address=None,
                 factor_type='factor_standardize', factor_address=None,
                 factor_rank_type='double', factor_rank_address=None,
                 future_type='future_mv', future_address=None):

        date_list = get_date_range(start_date, end_date)
        date_num = len(date_list)
        factor_address = ('%s/%s' % (middle_address, factor_type) if factor_address is None
                          else '%s/%s' % (factor_address, factor_type))

        future_address = middle_address if future_address is None else future_address
        factor_rank_address = middle_address if factor_rank_address is None else factor_rank_address
        stock_pool_address = middle_address if stock_pool_address is None else stock_pool_address

        stock_pool = pd.read_hdf('%s/%s.h5' % (stock_pool_address, 'stock_pool'), 'stock_pool')

        assert set(date_list) - set(stock_pool.index.to_list()) == set()
        code_list = stock_pool.columns.to_list()
        stock_pool = stock_pool.reindex(date_list).values

        future = np.load('%s/%s.npy' % (future_address, future_type))[future_index]
        factor_rank = np.load('%s/factor_rank_%s.npy' % (factor_rank_address, factor_rank_type))
        factor_weight = np.load('%s/factor_weight_%s.npy' % (factor_rank_address, factor_rank_type))

        self.date_list = date_list
        self.code_list = code_list
        self.date_num = date_num
        self.future_days_max = future_days_max
        self.factor_address = factor_address
        self.stock_pool = stock_pool
        self.future = future
        self.factor_rank = factor_rank
        self.factor_weight = factor_weight

    def get_model_date_list(self, model_days, predict_days):

        head_drop_days = max(model_days - 1, self.stock_pool.shape[0] - self.factor_rank.shape[0])
        tail_drop_days = self.future_days_max + 1
        model_date_list = self.date_list[head_drop_days: - tail_drop_days: predict_days]

        self.model_date_list = model_date_list
        self.model_days = model_days
        self.predict_days = predict_days

    def get_cv_date_list(self, cv_first_folds, cv_supports, cv_policy='long', cv_folds_limit=10):

        redo_cv_dates = self.model_date_list[cv_first_folds - 1 :: cv_supports]

        cv_rounds = len(redo_cv_dates)

        cv_dates_list = [self.model_date_list[(0 if cv_policy == 'long' else self.model_date_list.index(
            x) - cv_first_folds - self.future_days_max) : self.model_date_list.index(
            x) - self.future_days_max] for x in redo_cv_dates]

        cv_folds_limit = [(round(len(cv_dates_list[x]) * cv_folds_limit) if cv_folds_limit <= 1 else
                           min(cv_folds_limit, len(cv_dates_list[x]))) for x in range(cv_rounds)]

        cv_dates_list = [cv_dates_list[x][-1 :: - (len(cv_dates_list[x]) - 1 if len(cv_dates_list[x]) > 1 else 1) // (
            cv_folds_limit[x] - 1 if cv_folds_limit[x] > 1 else 1)] for x in range(cv_rounds)]

        cv_model_dates_list = [self.model_date_list[cv_first_folds - 1 + x * cv_supports : min(len(
            self.model_date_list), cv_first_folds - 1 + (x + 1) * cv_supports)] for x in range(cv_rounds)]

        self.cv_rounds = cv_rounds
        self.redo_cv_dates = redo_cv_dates
        self.cv_dates_list = cv_dates_list
        self.cv_model_dates_list = cv_model_dates_list

    def split_day_data(self, date):

        day = self.date_list.index(date)
        train_date_list = get_date_range(get_pre_trade_date(date, self.model_days - 1), date)
        predict_date_list = get_date_range(get_pre_trade_date(date, - self.future_days_max - 1), min(
            get_pre_trade_date(date, - self.future_days_max - self.predict_days), self.date_list[-1]))

        train_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                     for x in train_date_list)].transpose(2, 0, 1)
        train_y = self.future[day - self.model_days + 1: day + 1].T
        train_pool = self.stock_pool[day - self.model_days + 1: day + 1].T
        train_rank = self.factor_rank[day - self.date_num]
        train_weight = self.factor_weight[day - self.date_num]

        predict_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                       for x in predict_date_list)].transpose(2, 0, 1)
        predict_y = self.future[day + self.future_days_max + 1: min(
            day + self.future_days_max + 1 + self.predict_days, self.future.shape[1])].T
        predict_pool = self.stock_pool[day + self.future_days_max + 1: min(
            day + self.future_days_max + 1 + self.predict_days, self.future.shape[1])].T
        end_index = (day - self.date_num + self.future_days_max + 1 + self.predict_days
                     if day - self.date_num + self.future_days_max + 1 + self.predict_days < 0 else None)
        predict_rank = self.factor_rank[day - self.date_num + self.future_days_max + 1: end_index]
        predict_weight = self.factor_weight[day - self.date_num + self.future_days_max + 1: end_index]

        self.date = date
        self.day = day
        self.train_date_list = train_date_list
        self.predict_date_list = predict_date_list

        self.train_X = train_X
        self.train_y = train_y
        self.train_pool = train_pool
        self.train_rank = train_rank
        self.train_weight = train_weight

        self.predict_X = predict_X
        self.predict_y = predict_y
        self.predict_pool = predict_pool
        self.predict_rank = predict_rank
        self.predict_weight = predict_weight

    def clean_day_data(self):

        self.train_X = self.train_X[..., np.isfinite(self.train_rank)]
        self.train_X[~ np.isfinite(self.train_X)] = 0.

        _pool = self.train_pool & np.isfinite(self.train_y)

        self.train_X = self.train_X[_pool, :]
        self.train_y = self.train_y[_pool]

        self.predict_X = self.predict_X[..., np.isfinite(self.train_rank)]
        self.predict_X[~ np.isfinite(self.predict_X)] = 0.
        self.predict_X = tuple(self.predict_X[self.predict_pool[:, x], x, :] for x in range(self.predict_days))
        self.predict_y = tuple(self.predict_y[self.predict_pool[:, x], x] for x in range(self.predict_days))


if __name__ == '__main__':

    start_date = 20140102
    end_date = 20181228
    future_days_max = 5
    future_day_index = 4

    model_days = 120
    predict_days = 1

    cv_first_folds = 120
    cv_policy = 'long'
    cv_folds_limit = 10
    cv_supports = 120


    factor_type = 'factor_standardize'
    factor_rank_type = 'double'
    future_type = 'future'
    middle_address2 = '/data/user/015836/model/temp20200609/'
    middle_address = '/data/user/015836/model/temp20200527/'

    self = AlphaBaseModel(start_date, end_date, future_days_max, future_day_index, middle_address=middle_address,
                          factor_address=middle_address2, factor_rank_address=middle_address2,
                          factor_type=factor_type, factor_rank_type=factor_rank_type, future_type=future_type)

    self.get_model_date_list(model_days, predict_days)
    self.get_cv_date_list(cv_first_folds, cv_supports, cv_policy, cv_folds_limit)

    date = self.cv_dates_list[-1][-1]
    self.split_day_data(date)
    self.clean_day_data()

    import time
    t = time.time()
    date = self.model_date_list[1]
    self.split_day_data(date)
    #self.clean_day_data()
    time.time() - t