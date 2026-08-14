import pandas as pd
import numpy as np
import bottleneck
from functools import partial
from hyperopt import fmin, tpe
from xgboost import XGBRegressor
from dataApi.tradeDate import get_date_range, get_pre_trade_date

def rolling_windows(a, window):

    if window > a.shape[0]:
        raise ValueError(
            "Specified `window` length of {0} exceeds length of"
            " `a`, {1}.".format(window, a.shape[0])
        )
    if isinstance(a, (pd.Series, pd.DataFrame)):
        a = a.values
    if a.ndim == 1:
        a = a.reshape(-1, 1)
    shape = (a.shape[0] - window + 1, window) + a.shape[1:]
    strides = (a.strides[0],) + a.strides
    windows = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    if windows.ndim == 1:
        windows = np.atleast_2d(windows)
    return windows

def search_best_params(func, space, max_evals=100, n_startup_jobs=1):

    algo = partial(tpe.suggest, n_startup_jobs=n_startup_jobs)
    best = fmin(func,space, algo, max_evals)
    return best

class AlphaBaseModel(object):


    def __init__(self, start_date, end_date, future_days_max, middle_address, stock_pool_address=None,
                 factor_type='factor_standardize', factor_address=None,
                 factor_rank_type='double', factor_rank_address=None,
                 future_type='future_mv', future_address=None):

        date_list = get_date_range(start_date, end_date)
        date_num = len(date_list)
        factor_address = ('%s/%s' % (middle_address, factor_type) if factor_address is None
                          else '%s/%s ' % (factor_address, factor_type))

        future_address = middle_address if future_address is None else future_address
        factor_rank_address = middle_address if factor_rank_address is None else factor_rank_address
        stock_pool_address = middle_address if stock_pool_address is None else stock_pool_address

        stock_pool = pd.read_hdf('%s/%s.h5' % (stock_pool_address, 'stock_pool'), 'stock_pool')

        assert set(date_list) - set(stock_pool.index.to_list()) == set()
        code_list = stock_pool.columns.to_list()
        stock_pool = stock_pool.reindex(date_list).values

        future = np.load('%s/%s.npy' % (future_address, future_type))
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

    def get_model_date_list_1x1y(self, model_days):

        head_drop_days = max(model_days - 1, self.stock_pool.shape[0] - self.factor_rank.shape[0])
        tail_drop_days = self.future_days_max + 1
        model_date_list = self.date_list[head_drop_days : - tail_drop_days]

        self.model_date_list = model_date_list
        self.model_days = model_days

    def get_model_date_list_1xny(self, model_days, ny_days):

        head_drop_days = max(model_days - 1, self.stock_pool.shape[0] - self.factor_rank.shape[0])
        tail_drop_days = self.future_days_max + 1
        model_date_list = self.date_list[head_drop_days : - tail_drop_days : ny_days]

        self.model_date_list = model_date_list
        self.model_days = model_days
        self.ny_days = ny_days

    def get_model_date_list_mx1y(self, model_days, mx_days):

        head_drop_days = max(model_days + mx_days - 2, self.stock_pool.shape[0] - self.factor_rank.shape[0])
        tail_drop_days = self.future_days_max + 1
        model_date_list = self.date_list[head_drop_days : - tail_drop_days]

        self.model_date_list = model_date_list
        self.model_days = model_days
        self.mx_days = mx_days

    def get_model_date_list_mxny(self, model_days, mx_days, ny_days):

        head_drop_days = max(model_days + mx_days - 2, self.stock_pool.shape[0] - self.factor_rank.shape[0])
        tail_drop_days = self.future_days_max + 1
        model_date_list = self.date_list[head_drop_days : - tail_drop_days : ny_days]

        self.model_date_list = model_date_list
        self.model_days = model_days
        self.mx_days = mx_days
        self.ny_days = ny_days

    def split_day_data_1x1y(self, date):

        day = self.date_list.index(date)
        train_date_list = get_date_range(get_pre_trade_date(date, self.model_days - 1), date)
        predict_date = get_pre_trade_date(date, - self.future_days_max - 1)

        train_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                     for x in train_date_list)].transpose(2, 0, 1)
        train_y = self.future[:, day - self.model_days + 1 : day + 1].transpose(2, 1, 0)
        train_pool = self.stock_pool[day - self.model_days + 1 : day + 1].T
        train_rank = self.factor_rank[day - self.date_num]
        train_weight = self.factor_weight[day - self.date_num]

        predict_X = np.load('%s %s.npy' % (self.factor_address, predict_date)).T
        predict_y = self.future[:, day + self.future_days_max + 1].T
        predict_pool = self.stock_pool[day + self.future_days_max + 1].T
        predict_rank = self.factor_rank[day - self.date_num + self.future_days_max + 1]
        predict_weight = self.factor_weight[day - self.date_num + self.future_days_max + 1]

        self.date = date
        self.day = day
        self.train_date_list = train_date_list
        self.predict_date = predict_date

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

    def split_day_data_1xny(self, date):

        day = self.date_list.index(date)
        train_date_list = get_date_range(get_pre_trade_date(date, self.model_days - 1), date)
        predict_date_list = get_date_range(get_pre_trade_date(date, - self.future_days_max - 1), min(
            get_pre_trade_date(date, - self.future_days_max - self.ny_days), self.date_list[-1]))

        train_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                     for x in train_date_list)].transpose(2, 0, 1)
        train_y = self.future[:, day - self.model_days + 1 : day + 1].transpose(2, 1, 0)
        train_pool = self.stock_pool[day - self.model_days + 1 : day + 1].T
        train_rank = self.factor_rank[day - self.date_num]
        train_weight = self.factor_weight[day - self.date_num]

        predict_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                     for x in predict_date_list)].transpose(2, 0, 1)
        predict_y = self.future[:, day + self.future_days_max + 1 : min(
            day + self.future_days_max + 1 + self.ny_days, self.future.shape[1])].transpose(2, 1, 0)
        predict_pool = self.stock_pool[day + self.future_days_max + 1 : min(
            day + self.future_days_max + 1 + self.ny_days, self.future.shape[1])].T
        end_index = (day - self.date_num + self.future_days_max + 1 + self.ny_days
                     if day - self.date_num + self.future_days_max + 1 + self.ny_days < 0 else None)
        predict_rank = self.factor_rank[day - self.date_num + self.future_days_max + 1 : end_index]
        predict_weight = self.factor_weight[day - self.date_num + self.future_days_max + 1 : end_index]

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

    def split_day_data_mx1y(self, date):

        day = self.date_list.index(date)
        train_date_list = get_date_range(get_pre_trade_date(date, self.model_days + self.mx_days - 2), date)
        predict_date = get_pre_trade_date(date, - self.future_days_max - 1)
        predict_load_list = get_date_range(get_pre_trade_date(date, - self.future_days_max + self.mx_days - 2),
                                           get_pre_trade_date(date, - self.future_days_max - 1))

        train_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                     for x in train_date_list)].transpose(2, 0, 1)
        train_y = self.future[:, day - self.model_days - self.mx_days + 2 : day + 1].transpose(2, 1, 0)
        train_pool = self.stock_pool[day - self.model_days - self.mx_days + 2 : day + 1].T
        train_rank = self.factor_rank[day - self.date_num]
        train_weight = self.factor_weight[day - self.date_num]

        predict_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                                     for x in predict_load_list)].transpose(2, 0, 1)
        predict_y = self.future[:, day + self.future_days_max + 1].T
        predict_pool = self.stock_pool[day + self.future_days_max + 1].T
        predict_rank = self.factor_rank[day - self.date_num + self.future_days_max + 1]
        predict_weight = self.factor_weight[day - self.date_num + self.future_days_max + 1]

        self.date = date
        self.day = day
        self.train_date_list = train_date_list
        self.predict_load_list = predict_load_list
        self.predict_date = predict_date

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

    def split_day_data_mxny(self, date):

        day = self.date_list.index(date)
        train_date_list = get_date_range(get_pre_trade_date(date, self.model_days + self.mx_days - 2), date)
        predict_load_list = get_date_range(get_pre_trade_date(date, - self.future_days_max + self.mx_days - 2), min(
            get_pre_trade_date(date, - self.future_days_max - self.ny_days), self.date_list[-1]))
        predict_date_list = get_date_range(get_pre_trade_date(date, - self.future_days_max - 1), min(
            get_pre_trade_date(date, - self.future_days_max - self.ny_days), self.date_list[-1]))


        train_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                     for x in train_date_list)].transpose(2, 0, 1)
        train_y = self.future[:, day - self.model_days - self.mx_days + 2 : day + 1].transpose(2, 1, 0)
        train_pool = self.stock_pool[day - self.model_days - self.mx_days + 2 : day + 1].T
        train_rank = self.factor_rank[day - self.date_num]
        train_weight = self.factor_weight[day - self.date_num]

        predict_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                     for x in predict_load_list)].transpose(2, 0, 1)
        predict_y = self.future[:, day + self.future_days_max + 1 : min(
            day + self.future_days_max + 1 + self.ny_days, self.future.shape[1])].transpose(2, 1, 0)
        predict_pool = self.stock_pool[day + self.future_days_max + 1 : min(
            day + self.future_days_max + 1 + self.ny_days, self.future.shape[1])].T
        predict_rank = self.factor_rank[day - self.date_num + self.future_days_max + 1 : min(
            day - self.date_num + self.future_days_max + 1 + self.ny_days, self.future.shape[1])]
        predict_weight = self.factor_weight[day - self.date_num + self.future_days_max + 1 : min(
            day - self.date_num + self.future_days_max + 1 + self.ny_days, self.future.shape[1])]

        self.date = date
        self.day = day
        self.train_date_list = train_date_list
        self.predict_load_list = predict_load_list
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

class XGBTR(AlphaBaseModel):

    def __init__(self, start_date, end_date, future_days_max, middle_address, stock_pool_address=None,
                 factor_type='factor_standardize', factor_address=None,
                 factor_rank_type='double', factor_rank_address=None,
                 future_type='future_mv', future_address=None):

        super().__init__(start_date, end_date, future_days_max, middle_address, stock_pool_address,
                 factor_type, factor_address, factor_rank_type, factor_rank_address, future_type, future_address)

    def clean_day_data(self):

        self.train_y = self.train_y[..., future_day_index]
        self.train_X = self.train_X[..., np.isfinite(self.train_rank)]
        self.train_X[~ np.isfinite(self.train_X)] = 0.

        _pool = self.train_pool & np.isfinite(self.train_y)
        self.train_X[~ _pool] = np.nan

        self.all_train_X = self.train_X[_pool, :]
        self.all_train_y = self.train_y[_pool]

        self.predict_X = self.predict_X[..., np.isfinite(self.train_rank)]
        self.predict_X[~ np.isfinite(self.predict_X)] = 0.
        self.predict_X = tuple(self.predict_X[self.predict_pool[:, x], x, :] for x in range(self.ny_days))
        self.predict_y = tuple(self.predict_y[self.predict_pool[:, x], x] for x in range(self.ny_days))

    def get_ts_cv_days(self, cv_train_days, cv_validation_days):

        self.cv_train_days = cv_train_days
        self.cv_validation_days = cv_validation_days
        self.cv_days = np.arange(self.train_X.shape[1])[
                       cv_train_days + self.future_days_max :: cv_validation_days + self.future_days_max]

    def split_day_cv_data(self, cv_day):

        self.cv_train_X = self.train_X[:, cv_day - self.future_days_max - self.cv_train_days :
                                          cv_day - self.future_days_max].copy()

        self.cv_train_y = self.train_y[:, cv_day - self.future_days_max - self.cv_train_days :
                                          cv_day - self.future_days_max].copy()

        _pool = np.all(np.isfinite(self.cv_train_X), axis=2)
        self.cv_train_X = self.cv_train_X[_pool, :]
        self.cv_train_y = self.cv_train_y[_pool]

        self.cv_predict_X = tuple(self.train_X[:, cv_day + x].copy()
                                  for x in range(min(self.model_days - cv_day, self.cv_validation_days)))

        self.cv_predict_y = tuple(self.train_y[:, cv_day + x].copy()
                                  for x in range(min(self.model_days - cv_day, self.cv_validation_days)))

        _pool = tuple(np.all(np.isfinite(self.cv_predict_X[x]), axis=1) for x in range(len(self.cv_predict_X)))
        self.cv_predict_X = tuple(self.cv_predict_X[x][_pool[x], :] for x in range(len(self.cv_predict_X)))
        self.cv_predict_y = tuple(self.cv_predict_y[x][_pool[x]] for x in range(len(self.cv_predict_y)))

    def train_model(self):

        model = XGBRegressor(process_type='default', boooster='gbtree', objective='reg:linear',
                             eval_metric='rmse', nthread=24,
                             learning_rate=0.1, n_estimators=100,
                             max_depth=4, min_child_weight=1,
                             gamma=0, subsample=1, colsample_bytree=1,
                             reg_alpha=0, reg_lambda=1,
                             scale_pos_weight=1, max_delta_step=0)

        model.fit(self.cv_train_X, self.cv_train_y)
        y_hat = tuple(model.predict(self.cv_predict_X[x]) for x in range(len(self.cv_predict_X)))
        metric = tuple(np.sqrt(np.nanmean((y_hat[x] - self.cv_predict_y[x]) ** 2)) for x in range(len(y_hat)))
        gain = tuple(- np.nanmean((self.cv_predict_y[x] - np.nanmean(self.cv_predict_y[x]))[
                                      bottleneck.nanrankdata(y_hat[x]) > 0.9]) for x in range(len(y_hat)))
        self.metric = metric
        self.gain = gain

    def train_cv1_model(args):




        global self
        model = XGBRegressor(process_type='default', boooster='gbtree', objective='reg:linear',
                             eval_metric=args['eval_metric'], nthread=24,
                             learning_rate=args['learning_rate'], n_estimators=args['n_estimators'],
                             max_depth=args['max_depth'], min_child_weight=args['min_child_weight'],
                             gamma=args['gamma'], subsample=args['subsample'], colsample_bytree=args['colsample_bytree'],
                             reg_lambda=args['reg_lambda'], reg_alpha=args['reg_alpha'],
                             scale_pos_weight=args['scale_pos_weight'], max_delta_step=args['max_delta_step'])

        model.fit(self.cv_train_X, self.cv_train_y)
        y_hat = tuple(model.predict(self.cv_predict_X[x]) for x in range(len(self.cv_predict_X)))
        rmse = np.mean(tuple(np.sqrt(np.nanmean((y_hat[x] - self.cv_predict_y[x]) ** 2)) for x in range(len(y_hat))))
        ret = np.mean(tuple(np.nanmean((self.cv_predict_y[x] - np.nanmean(self.cv_predict_y[x]))[
                                           bottleneck.nanrankdata(y_hat[x]) > 0.9]) for x in range(len(y_hat))))
        print(rmse, ret)
        return rmse

search_best_params(train_model, scope, max_evals=100, n_startup_jobs=20)

model = XGBRegressor(process_type='default', boooster='gbtree', objective='reg:linear',
                     eval_metric='rmse', nthread=24,
                     learning_rate=0.1, n_estimators=100,
                     max_depth=4, min_child_weight=1,
                     gamma=0, subsample=1, colsample_bytree=1,
                     reg_alpha=0, reg_lambda=1,
                     scale_pos_weight=1, max_delta_step=0)

model.fit(self.cv_train_X, self.cv_train_y)
y_hat = tuple(model.predict(self.cv_predict_X[x]) for x in range(len(self.cv_predict_X)))
rmse = np.mean(tuple(np.sqrt(np.nanmean((y_hat[x] - self.cv_predict_y[x]) ** 2)) for x in range(len(y_hat))))
ret = np.mean(tuple(np.nanmean((self.cv_predict_y[x] - np.nanmean(self.cv_predict_y[x]))[bottleneck.nanrankdata(
    y_hat[x]) / np.isfinite(y_hat[x]).sum() > 0.9]) for x in range(len(y_hat))))

eta_search(self, params2, max_evals=10, n_startup_jobs=20)

params2 = dict(process_type='default', boooster='gbtree', objective='reg:linear', silent=True,
               nthread=24,
               learning_rate=hp.quniform('learning_rate', 0.01, 0.1, 0.01),
               n_estimators=33,
               max_depth=6,
               min_child_weight=8,
               gamma=0.9,
               subsample=0.9,
               colsample_bytree=0.7,
               reg_alpha=0,
               reg_lambda=1,
               scale_pos_weight=1,
               max_delta_step=0)




params = dict(process_type='default', boooster='gbtree', objective='reg:linear', silent=True,
              nthread=24,
              learning_rate=0.1, n_estimators=100,
              max_depth=4, min_child_weight=1,
              gamma=0, subsample=1, colsample_bytree=1,
              reg_alpha=0, reg_lambda=1,
              scale_pos_weight=1, max_delta_step=0)

cv_train = xgb.DMatrix(self.cv_train_X, label=self.cv_train_y)
cv_test = [(xgb.DMatrix(self.cv_predict_X[x], label=self.cv_predict_y[x]), str(x + 1))
           for x in range(len(self.cv_predict_y))]

model1 = None
model1 = xgb.train(params, cv_train, evals=cv_test,
                   num_boost_round=1000, early_stopping_rounds=30, xgb_model=model1, verbose_eval=True,
                   feval=metric_ret)



if __name__ == '__main__':

    start_date = 20140102
    end_date = 20181228
    future_days_max = 5
    model_days = 120
    predict_days = 5
    future_day_index = 4
    cv_train_days = 40
    cv_validation_days = 2
    factor_type = 'factor_standardize'
    factor_rank_type = 'double'
    future_type = 'future_mv'
    middle_address = '/data/user/015836/model/temp20200527/'

    self = AlphaBaseModel(start_date, end_date, future_days_max, middle_address=middle_address,
                          factor_type=factor_type, factor_rank_type=factor_rank_type, future_type=future_type)

    self.get_model_date_list_1xny(model_days, predict_days)
    date = self.model_date_list[0]
    self.split_day_data_1xny(date)

