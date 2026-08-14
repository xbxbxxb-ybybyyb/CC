import pandas as pd
import numpy as np
import bottleneck
from functools import partial
import xgboost as xgb
from hyperopt.pyll import scope
from hyperopt import fmin, tpe, hp, Trials
from tqdm import tqdm
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from model.alphaBaseModel import AlphaBaseModel

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


class XGBDT(AlphaBaseModel):

    def __init__(self, start_date, end_date, future_days_max, future_day_index,
                 model_days, predict_days, cv_first_folds, cv_policy, cv_folds_limit, cv_supports,
                 middle_address, stock_pool_address=None,
                 factor_type='factor_standardize', factor_address=None,
                 factor_rank_type='double', factor_rank_address=None,
                 future_type='future_mv', future_address=None):

        super(XGBDT, self).__init__(
            start_date, end_date, future_days_max, future_day_index, middle_address, stock_pool_address,
            factor_type, factor_address, factor_rank_type, factor_rank_address, future_type, future_address)

        self.get_model_date_list(model_days, predict_days)
        self.get_cv_date_list(cv_first_folds, cv_supports, cv_policy, cv_folds_limit)

    def iterative_search(self):

    def traversal_search(self):

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

    self = XGBDT(start_date, end_date, future_days_max, future_day_index,
                 model_days, predict_days, cv_first_folds, cv_policy, cv_folds_limit, cv_supports,
                 middle_address=middle_address, factor_address=middle_address2, factor_rank_address=middle_address2,
                 factor_type=factor_type, factor_rank_type=factor_rank_type, future_type=future_type)

