import pandas as pd
import numpy as np
import bottleneck
from functools import partial
import xgboost as xgb
from hyperopt.pyll import scope
from hyperopt import fmin, tpe, hp, Trials
from tqdm import tqdm
from dataApi.tradeDate import get_date_range, get_pre_trade_date

trials = Trials()

@scope.define
def add_func(a, b):
    return a + b


@scope.define
def mul_func(a, b):
    return a * b


def search_best_params(func, space, max_evals=100, n_startup_jobs=20):

    algo = partial(tpe.suggest, n_startup_jobs=n_startup_jobs)
    best = fmin(func, space, algo, max_evals)
    return best


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

def metric_ret(preds, dtrain):

    label = dtrain.get_label()
    if len(np.unique(preds)) / np.isfinite(label).sum() < 0.75:
        ret = -1.
    else:
        ret = np.nanmean((label - np.nanmean(label))[bottleneck.nanrankdata(preds) / np.isfinite(preds).sum() > 0.9])
    return 'top_ret', - ret

def train(params, cv_train, cv_test, num_boost_round=1000, early_stopping_rounds=30, model=None):
    evals_result = {}
    model1 = xgb.train(params, cv_train, evals=cv_test,
                       num_boost_round=num_boost_round, early_stopping_rounds=early_stopping_rounds,
                       xgb_model=model, verbose_eval=True,
                       feval=metric_ret, evals_result=evals_result)

    return model1, evals_result

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

    def get_model_date_list(self, model_days, ny_days):

        head_drop_days = max(model_days - 1, self.stock_pool.shape[0] - self.factor_rank.shape[0])
        tail_drop_days = self.future_days_max + 1
        model_date_list = self.date_list[head_drop_days: - tail_drop_days: ny_days]

        self.model_date_list = model_date_list
        self.model_days = model_days
        self.ny_days = ny_days

    def split_day_data(self, date):

        day = self.date_list.index(date)
        train_date_list = get_date_range(get_pre_trade_date(date, self.model_days - 1), date)
        predict_date_list = get_date_range(get_pre_trade_date(date, - self.future_days_max - 1), min(
            get_pre_trade_date(date, - self.future_days_max - self.ny_days), self.date_list[-1]))

        train_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                     for x in train_date_list)].transpose(2, 0, 1)
        train_y = self.future[:, day - self.model_days + 1: day + 1].transpose(2, 1, 0)
        train_pool = self.stock_pool[day - self.model_days + 1: day + 1].T
        train_rank = self.factor_rank[day - self.date_num]
        train_weight = self.factor_weight[day - self.date_num]

        predict_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                       for x in predict_date_list)].transpose(2, 0, 1)
        predict_y = self.future[:, day + self.future_days_max + 1: min(
            day + self.future_days_max + 1 + self.ny_days, self.future.shape[1])].transpose(2, 1, 0)
        predict_pool = self.stock_pool[day + self.future_days_max + 1: min(
            day + self.future_days_max + 1 + self.ny_days, self.future.shape[1])].T
        end_index = (day - self.date_num + self.future_days_max + 1 + self.ny_days
                     if day - self.date_num + self.future_days_max + 1 + self.ny_days < 0 else None)
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

    def get_ts_cv_days(self, cv_train_days, cv_validation_days, cv_days_limit):

        self.cv_train_days = cv_train_days
        self.cv_validation_days = cv_validation_days
        self.cv_days = np.arange(self.train_X.shape[1])[
                       cv_train_days + self.future_days_max:: cv_validation_days + self.future_days_max]
        cv_days_limit = round(len(self.cv_days) * cv_days_limit) if cv_days_limit < 1 else min(
            cv_days_limit, len(self.cv_days))
        self.cv_days = self.cv_days[-1:: - (len(self.cv_days) - 1 if len(self.cv_days) > 1 else 1) //
                                         (cv_days_limit - 1 if cv_days_limit > 1 else 1)]

    def split_day_cv_data(self, cv_day):

        self.cv_train_X = self.train_X[:, cv_day - self.future_days_max - self.cv_train_days:
                                          cv_day - self.future_days_max].copy()

        self.cv_train_y = self.train_y[:, cv_day - self.future_days_max - self.cv_train_days:
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

        return self.cv_train_X, self.cv_train_y, self.cv_predict_X, self.cv_predict_y

    def pack_cv_data(self):

        self.cv_data = []
        for cv_day in self.cv_days:
            self.split_day_cv_data(cv_day)
            cv_train = xgb.DMatrix(self.cv_train_X, label=self.cv_train_y)
            cv_test = [(xgb.DMatrix(self.cv_predict_X[x], label=self.cv_predict_y[x]), str(x + 1))
                       for x in range(len(self.cv_predict_y))]
            self.cv_data.append((cv_train, cv_test))

    def search_best_round(self, params, num_boost_round=1000, early_stopping_rounds=30):

        Model = []
        Eval_result = []
        Rounds = []
        for j in range(len(self.cv_days)):
            cv_train, cv_test = self.cv_data[j]
            model, evals_result = train(params, cv_train, cv_test, num_boost_round, early_stopping_rounds)
            evals_result = np.r_['0,2', tuple(evals_result[str(x + 1)]['top_ret'] for x in range(len(cv_test)))]
            rounds = evals_result.shape[1]
            Model.append(model)
            Eval_result.append(evals_result)
            Rounds.append(rounds)

        max_round = max(Rounds)
        for j in range(len(self.cv_days)):
            add_round = max_round - Rounds[j]
            if add_round > 0:
                cv_train, cv_test = self.cv_data[j]
                model, evals_result = train(params, cv_train, cv_test, add_round, add_round, Model[j])
                evals_result = np.r_['0,2', tuple(evals_result[str(x + 1)]['top_ret'] for x in range(len(cv_test)))]
                Eval_result[j] = np.c_[Eval_result[j], evals_result]

        Eval_result = np.nanmean(np.r_[tuple(Eval_result)], axis=0)
        best_round = np.nanargmin(Eval_result)
        min_eval = np.nanmin(Eval_result)

        return best_round, min_eval

    def algo_search(self, param_space, best_round, max_evals=100, n_startup_jobs=20):

        def _func(params):

            print(params)
            Eval_result = []
            for j in range(len(self.cv_days)):
                cv_train, cv_test = self.cv_data[j]
                model, evals_result = train(params, cv_train, cv_test, best_round, best_round)
                evals_result = np.array([evals_result[str(x + 1)]['rmse'][-1] for x in range(len(cv_test))])
                Eval_result.append(evals_result)
            Eval_result = np.nanmean(np.r_[tuple(Eval_result)])
            return Eval_result

        algo = partial(tpe.suggest, n_startup_jobs=n_startup_jobs)
        best = fmin(_func, param_space, algo, max_evals, verbose=1)
        return best

    def eta_search(self, param_space, max_evals=100, n_startup_jobs=20):

        self.best_round = []
        self.eta = []

        def _func(params):

            print(params)
            best_round, min_eval = self.search_best_round(params, early_stopping_rounds=100)
            self.best_round.append(best_round)
            self.eta.append(params['learning_rate'])
            return min_eval

        algo = partial(tpe.suggest, n_startup_jobs=n_startup_jobs)
        best = fmin(_func, param_space, algo, max_evals)
        best_round = self.best_round[self.eta.index(best['learning_rate'])]
        return best, best_round

    def predict(self, params, predict_address):

        all_train = xgb.DMatrix(self.all_train_X, label=self.all_train_y)
        model = xgb.train(params, all_train, num_boost_round=params['n_estimators'])
        for j, dt in enumerate(self.predict_date_list):
            _pool = self.predict_pool[:, j]
            predict = np.full(_pool.shape, np.nan)
            predict[_pool] = model.predict(xgb.DMatrix(self.predict_X[j]))
            np.save('%s/predict %s' % (predict_address, dt), predict)



params = dict(process_type='default', boooster='gbtree', objective='reg:linear', silent=True,
              nthread=24,
              learning_rate=0.1, n_estimators=100,
              max_depth=4, min_child_weight=1,
              gamma=0, subsample=1, colsample_bytree=1,
              reg_alpha=0, reg_lambda=1,
              scale_pos_weight=1, max_delta_step=0)

params1 = dict(process_type='default', boooster='gbtree', objective='reg:linear', silent=True,
               nthread=24,
               learning_rate=0.1,
               n_estimators=33,
               max_depth=scope.add_func(hp.randint('max_depth', 10), 1),
               min_child_weight=scope.add_func(hp.randint('min_child_weight', 10), 1),
               gamma=hp.quniform('gamma', 0, 1, 0.1),
               subsample=hp.quniform('subsample', 0.5, 1, 0.1),
               colsample_bytree=hp.quniform('colsample_bytree', 0.5, 1, 0.1),
               reg_alpha=hp.qloguniform('reg_alpha', np.log(0.01), np.log(100), 0.01),
               reg_lambda=hp.qloguniform('reg_lambda', np.log(0.01), np.log(100), 0.01),
               scale_pos_weight=1,
               max_delta_step=0)




if __name__ == '__main__':

    start_date = 20140102
    end_date = 20181228
    future_days_max = 5
    model_days = 36
    predict_days = 1
    future_day_index = 4
    cv_train_days = 30
    cv_validation_days = 1
    cv_days_limit = 1
    factor_type = 'factor_standardize'
    factor_rank_type = 'double'
    future_type = 'future'
    middle_address = '/data/user/015836/model/temp20200527/'

    params = dict(process_type='default', boooster='gbtree', objective='reg:linear', silent=True,
                  nthread=24,
                  learning_rate=0.1, n_estimators=100,
                  max_depth=4, min_child_weight=1,
                  gamma=0, subsample=1, colsample_bytree=1,
                  reg_alpha=0, reg_lambda=1,
                  scale_pos_weight=1, max_delta_step=0)

    self = AlphaBaseModel(start_date, end_date, future_days_max, middle_address=middle_address,
                          factor_type=factor_type, factor_rank_type=factor_rank_type, future_type=future_type)

    self.get_model_date_list(model_days, predict_days)

    model_date_list = [x for x in self.model_date_list if 20151223 < x <= 20161222]

    error_date = []
    for date in tqdm(model_date_list):

        try:
            self.split_day_data(date)
            self.clean_day_data()
            self.get_ts_cv_days(cv_train_days, cv_validation_days, cv_days_limit)
            self.pack_cv_data()
            best_round, min_eval = self.search_best_round(params)
            params.update(
                dict(max_depth=scope.add_func(hp.randint('max_depth', 5), 3),
                     min_child_weight=scope.add_func(hp.randint('min_child_weight', 10), 1),
                     gamma=hp.quniform('gamma', 0, 0.1, 0.01),
                     subsample=hp.quniform('subsample', 0.5, 1, 0.1),
                     colsample_bytree=hp.quniform('colsample_bytree', 0.5, 1, 0.1),
                     reg_lambda=1,
                     reg_alpha=0)
            )
            best = self.algo_search(params, best_round, max_evals=20, n_startup_jobs=20)
            best['max_depth'] += 3
            params.update(best)
            params.update(dict(learning_rate=hp.quniform('learning_rate', 0.01, 0.1, 0.01)))
            best, best_round = self.eta_search(params, max_evals=5, n_startup_jobs=20)
            params.update(best)
            self.predict(params, '/data/user/015836/model/xgbr20200607/')
            params.update(dict(learning_rate=0.1))

        except:
            error_date.append(date)

            params = dict(process_type='default', boooster='gbtree', objective='reg:linear', silent=True,
                          nthread=24,
                          learning_rate=0.1, n_estimators=100,
                          max_depth=4, min_child_weight=1,
                          gamma=0, subsample=1, colsample_bytree=1,
                          reg_alpha=0, reg_lambda=1,
                          scale_pos_weight=1, max_delta_step=0)


    params = dict(process_type='default', boooster='gbtree', objective='reg:linear', silent=True,
                  nthread=24,
                  learning_rate=0.1, n_estimators=100,
                  max_depth=4, min_child_weight=5,
                  gamma=0.7, subsample=0.5, colsample_bytree=0.5,
                  reg_alpha=12, reg_lambda=12,
                  scale_pos_weight=1, max_delta_step=0)

dl = get_date_range(20160101, 20181231)
compound = np.r_['0,2', tuple(np.load('%s%s %s.npy' % ('/data/user/015836/model/xgbr20200607/', 'predict', x))
                              for x in dl)]
compound = pd.DataFrame(compound, index=dl, columns=self.code_list)
compound.to_hdf('/data/user/015836/model/compound/compound115.h5', 'compound115', format='t')
compound = pd.read_hdf('/data/user/015836/model/compound/compound115.h5', 'compound115')
from dataApi.nonFactorTest import NonFactorTest
nft = NonFactorTest(20160101, 20181231)
nft.load_factor(compound, neutral=False)
zzz = nft.test_factor(period='Y',
                      output=False, file='/data/user/015836/model/xgbr20200607/aaa.xlsx')

strategy_mdd=False, top_mdd=False, long_short_mdd=False,

if not hasattr(self, 'train_factors_dict'):
    self.train_factors_dict = {}
add_train_dates = list(set(train_date_list) - set(self.train_factors_dict.keys()))
for x in add_train_dates:
    self.train_factors_dict[x] = np.load('%s %s.npy' % (self.factor_address, x))
self.train_factors_dict = {x: self.train_factors_dict[x] for x in train_date_list}

train_X = np.r_['0,3', tuple(self.train_factors_dict[x] for x in train_date_list)].transpose(2, 0, 1)

if not hasattr(self, 'predict_factors_dict'):
    self.predict_factors_dict = {}
add_predict_dates = list(set(predict_date_list) - set(self.predict_factors_dict.keys()))
for x in add_predict_dates:
    self.predict_factors_dict[x] = np.load('%s %s.npy' % (self.factor_address, x))
self.predict_factors_dict = {x: self.predict_factors_dict[x] for x in predict_date_list}

predict_X = np.r_['0,3', tuple(self.predict_factors_dict[x] for x in predict_date_list)].transpose(2, 0, 1)


(np.abs((df - (df * (1 + share_ratio)).shift(1))) * twap).sum(axis=1) / (np.abs((df + (df * (1 + share_ratio)).shift(1))) * twap).sum(axis=1)