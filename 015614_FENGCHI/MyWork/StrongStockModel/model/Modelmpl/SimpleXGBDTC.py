# @Time : 2020/9/15 14:30
# @Author : Zhichen Lu
# @File : SimpleXGBDTC.py
import pandas as pd
import numpy as np
from scipy.stats import boxcox
from abc import abstractmethod
from sklearn.linear_model import LinearRegression
from types import MethodType
import bottleneck
from functools import partial
from tqdm import tqdm
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from model.nonFactorTest import NonFactorTest
from model.alphaDataPrepare import multiprocess
from model.metrics import top_ret, rmse
from hyperopt.pyll import scope
from hyperopt import fmin, tpe, hp, Trials, pyll
import xgboost as xgb
import os
import gc
import re


class DatasetTransform(object):

    def __init__(self, arr, orth=False, boxc=False, data_min=-1, data_max=1):

        self.orth = orth
        self.boxc = boxc
        self.data_min = data_min
        self.data_max = data_max

        if orth:
            corr = np.corrcoef(arr.T)
            u, d, v = np.linalg.svd(corr)
            m2 = u.dot(np.diag(1 / np.sqrt(d))).dot(v)
            arr = arr.dot(m2)
            self.m2 = m2

        self.mini = arr.min(axis=0)
        self.maxi = arr.max(axis=0)
        arr = (arr - self.mini) / (self.maxi - self.mini)

        if boxc:
            arr += 1
            arr1 = np.full_like(arr, np.nan)
            lmbda = np.full_like(arr[0], np.nan)
            for i in tqdm(range(arr.shape[1])):
                arr1[:, i], lmbda[i] = boxcox(arr[:, i])
            self.lmbda = lmbda
            self.minj = arr1.min(axis=0)
            self.maxj = arr1.max(axis=0)
            arr = (arr1 - self.minj) / (self.maxj - self.minj)

        arr *= data_max - data_min
        arr += data_min
        self.train_X = arr

    def __call__(self, pred):

        if self.orth:
            pred = pred.dot(self.m2)

        pred = (pred - self.mini) / (self.maxi - self.mini)

        if self.boxc:
            pred += 1
            pred[pred <= 0] = np.nan
            _min = np.nanmin(pred, axis=0)
            pred[np.isnan(pred)] = np.repeat(_min[None, :], pred.shape[0], axis=0)[np.isnan(pred)]
            pred1 = np.full_like(pred, np.nan)
            for i in range(pred.shape[1]):
                pred1[:, i] = boxcox(pred[:, i], self.lmbda[i])
            pred = (pred1 - self.minj) / (self.maxj - self.minj)

        pred *= self.data_max - self.data_min
        pred += self.data_min
        return pred


class AlphaBaseModelSimple(object):

    def __init__(self, middle_address, start_date=None, end_date=None, date_list=None, future_weight=5,
                 stock_pool_address=None, factor_list_address=None, load_address=None,
                 factor_type='factor_standardize', factor_address=None,
                 future_type='future_mv', future_address=None,
                 real_future_type='future_ZZ500', real_future_address=None):

        date_list = get_date_range(start_date, end_date) if date_list is None else date_list
        date_num = len(date_list)
        factor_address = ('%s/%s' % (middle_address, factor_type) if factor_address is None
                          else '%s/%s' % (factor_address, factor_type))

        factor_list_address = middle_address if factor_list_address is None else factor_list_address
        future_address = middle_address if future_address is None else future_address
        real_future_address = middle_address if real_future_address is None else real_future_address
        stock_pool_address = middle_address if stock_pool_address is None else stock_pool_address
        load_address = middle_address if load_address is None else load_address

        factor_list = list(np.load('%s/factor_list.npy' % factor_list_address))
        stock_pool = pd.read_hdf('%s/%s.h5' % (stock_pool_address, 'stock_pool'), 'stock_pool')

        assert set(date_list) - set(stock_pool.index.to_list()) == set()
        code_list = stock_pool.columns.to_list()
        stock_pool = stock_pool.reindex(date_list).values

        future = np.load('%s/%s.npy' % (future_address, future_type))
        real_future = np.load('%s/%s.npy' % (real_future_address, real_future_type))

        if isinstance(future_weight, int):
            future = future[future_weight - 1]
            real_future = real_future[future_weight - 1]
            future_days_max = future_weight
        else:
            future_weight = np.asanyarray(future_weight).astype(float)
            future_weight[~np.isfinite(future_weight)] = 0
            future_weight /= future_weight.sum()
            valid_future_weight = ~ np.isclose(future_weight, 0)
            future_days_max = (np.arange(valid_future_weight.shape[0]) * valid_future_weight).max() + 1
            future_weight = future_weight[valid_future_weight]
            future = future[valid_future_weight]
            real_future = real_future[valid_future_weight]
            future = future.transpose(tuple(range(1, future.ndim)) + (0,)).dot(future_weight)
            real_future = real_future.transpose(tuple(range(1, real_future.ndim)) + (0,)).dot(future_weight)

        self.date_list = date_list
        self.code_list = code_list
        self.factor_list = factor_list
        self.date_num = date_num
        self.future_days_max = future_days_max
        self.factor_address = factor_address
        self.stock_pool = stock_pool
        self.future = future
        self.real_future = real_future
        self.load_address = load_address

    def select_factor(self, select_factor_list, top_factor_num=None):

        if isinstance(select_factor_list, str):
            select_factor_list = list(np.load(select_factor_list))[:top_factor_num]

        factor_select = [self.factor_list.index(x) for x in select_factor_list][:top_factor_num]
        self.factor_select = factor_select

    def get_model_date_list(self, model_days):

        if model_days > 2e7:
            model_date = get_pre_trade_date(model_days, self.future_days_max, self.date_list)
            model_days = self.date_list.index(model_date) + 1
        else:
            model_date = self.date_list[model_days - 1]

        model_date_list = self.date_list[: model_days]
        predict_date = self.date_list[model_days + self.future_days_max]
        predict_date_list = self.date_list[self.date_list.index(predict_date):]
        predict_days = len(predict_date_list)

        self.model_days = model_days
        self.model_date = model_date
        self.model_date_list = model_date_list

        self.predict_days = predict_days
        self.predict_date = predict_date
        self.predict_date_list = predict_date_list

    def get_cv_date_list(self, cv_model_days, cv_predict_days, cv_folds_limit=10, long_policy=False):

        redo_cv_dates = sorted(self.model_date_list[- (
                cv_predict_days + self.future_days_max + 1): cv_model_days: - cv_predict_days])

        cv_dates_list = sorted(redo_cv_dates[-1:: - (len(redo_cv_dates) - 1 if len(redo_cv_dates) > 1 else 1) // (
            cv_folds_limit - 1 if cv_folds_limit > 1 else 1)])

        self.cv_model_days = cv_model_days
        self.cv_predict_days = cv_predict_days
        self.cv_date_list = cv_dates_list
        self.long_policy = long_policy

    def split_dataset(self, cv=False, date=None):

        date = date if cv else self.model_date
        day = self.date_list.index(date)
        if cv:
            train_days = day + 1 if self.long_policy else self.cv_model_days
            train_date_list = self.date_list[day - train_days + 1: day + 1]
            train_day_list = [self.date_list.index(x) for x in train_date_list]

            predict_days = self.cv_predict_days
            predict_date_list = self.date_list[day + self.future_days_max + 1: min(
                day + self.future_days_max + 1 + self.cv_predict_days, self.model_days)]
            predict_day_list = [self.date_list.index(x) for x in predict_date_list]
        else:
            train_days = self.model_days
            train_date_list = self.model_date_list
            train_day_list = [self.date_list.index(x) for x in train_date_list]

            predict_days = self.predict_days
            predict_date_list = self.predict_date_list
            predict_day_list = [self.date_list.index(x) for x in predict_date_list]

        train_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                     for x in train_date_list)].transpose(2, 0, 1)
        train_y = self.future[train_day_list].T
        train_ry = self.real_future[train_day_list].T
        train_pool = self.stock_pool[train_day_list].T

        predict_X = np.r_['0,3', tuple(np.load('%s %s.npy' % (self.factor_address, x))
                                       for x in predict_date_list)].transpose(2, 0, 1)
        predict_y = self.future[predict_day_list].T
        predict_ry = self.real_future[predict_day_list].T
        predict_pool = self.stock_pool[predict_day_list].T

        self.date = date
        self.day = day

        self.train_days = train_days
        self.train_date_list = train_date_list
        self.train_day_list = train_day_list
        self.train_X = train_X
        self.train_y = train_y
        self.train_ry = train_ry
        self.train_pool = train_pool

        self.predict_days = predict_days
        self.predict_date_list = predict_date_list
        self.predict_day_list = predict_day_list
        self.predict_X = predict_X
        self.predict_y = predict_y
        self.predict_ry = predict_ry
        self.predict_pool = predict_pool

    def clean_dataset(self, trans=False, orth=False, boxc=False):

        train_pool = self.train_pool & np.isfinite(self.train_y)
        train_X = self.train_X[train_pool][:, self.factor_select]
        train_y = self.train_y[train_pool]
        train_ry = self.train_ry[train_pool]

        predict_X = []
        predict_y = []
        predict_ry = []
        for j in range(self.predict_days):
            predict_X.append(self.predict_X[self.predict_pool[:, j], j][:, self.factor_select])

            temp_y = self.predict_y[self.predict_pool[:, j]][:, j].copy()
            temp_y[~ np.isfinite(temp_y)] = np.nanmean(temp_y)
            predict_y.append(temp_y)

            temp_ry = self.predict_ry[self.predict_pool[:, j]][:, j].copy()
            temp_ry[~ np.isfinite(temp_ry)] = np.nanmean(temp_ry)
            predict_ry.append(temp_ry)

        if trans:
            transform = DatasetTransform(train_X, orth=orth, boxc=boxc)
            train_X = transform.train_X
            for j in range(self.predict_days):
                predict_X[j] = transform(predict_X[j])
            self.transform = transform

        self.train_X = train_X
        self.train_y = train_y
        self.train_ry = train_ry

        self.predict_X = predict_X
        self.predict_y = predict_y
        self.predict_ry = predict_ry

    def store_dataset(self, save_address, trans=False, orth=False, boxc=False, whole=True, cv=True):

        if whole:
            self.split_dataset()
            self.clean_dataset(trans, orth, boxc)
            np.save('%s/predict_date_list' % save_address, self.predict_date_list)
            np.save('%s/predict_pool' % save_address, self.predict_pool)
            np.save('%s/train_X_whole' % save_address, self.train_X)
            np.save('%s/train_y_whole' % save_address, self.train_y)
            np.save('%s/train_ry_whole' % save_address, self.train_ry)
            np.save('%s/predict_X_whole' % save_address, self.predict_X)
            np.save('%s/predict_y_whole' % save_address, self.predict_y)
            np.save('%s/predict_ry_whole' % save_address, self.predict_ry)

        if cv:
            for date in self.cv_date_list:
                self.split_dataset(cv=True, date=date)
                self.clean_dataset(trans, orth, boxc)
                np.save('%s/train_X_cv%s' % (save_address, date), self.train_X)
                np.save('%s/train_y_cv%s' % (save_address, date), self.train_y)
                np.save('%s/train_ry_cv%s' % (save_address, date), self.train_ry)
                np.save('%s/predict_X_cv%s' % (save_address, date), self.predict_X)
                np.save('%s/predict_y_cv%s' % (save_address, date), self.predict_y)
                np.save('%s/predict_ry_cv%s' % (save_address, date), self.predict_ry)

        delattr(self, 'future')
        delattr(self, 'real_future')
        delattr(self, 'stock_pool')
        gc.collect()

    def load_dataset(self, date=None):

        suffix = 'whole' if date is None else 'cv' + str(date)
        self.train_X = np.load('%s/train_X_%s.npy' % (self.load_address, suffix))
        self.train_y = np.load('%s/train_y_%s.npy' % (self.load_address, suffix))
        self.train_ry = np.load('%s/train_ry_%s.npy' % (self.load_address, suffix))
        self.predict_X = list(np.load('%s/predict_X_%s.npy' % (self.load_address, suffix)))
        self.predict_y = list(np.load('%s/predict_y_%s.npy' % (self.load_address, suffix)))
        self.predict_ry = list(np.load('%s/predict_ry_%s.npy' % (self.load_address, suffix)))

        if date is None:
            self.predict_date_list = np.load('%s/predict_date_list.npy' % self.load_address)
            self.predict_pool = np.load('%s/predict_pool.npy' % self.load_address)

    def _set_model_dataset(self):

        self.train_y = (self.train_y > 0.7 - (0.2 - 0.1) * 1.7).astype(int)
        self.predict_y = [(x > 0.7 - (0.3 - 0.1) * 1.7).astype(int) for x in self.predict_y]
        self.train_X = xgb.DMatrix(self.train_X, label=self.train_y)
        self.predict_X = [xgb.DMatrix(self.predict_X[x], label=self.predict_y[x]) for x in range(len(self.predict_y))]

    def _set_params(self):

        config = [
            dict(
                eval1_weight=0,
                eval2_weight=1,
                process_type='default',
                boooster='gbtree',
                objective='binary:logistic',
                eval_metric='rmse',
                tree_method='gpu_hist',
                silent=True,
                nthread=-1,

                eta=0.1,
                max_depth=4,
                min_child_weight=10,
                gamma=0,
                subsample=1,
                colsample_bytree=1,
                reg_alpha=0,
                reg_lambda=1,
                scale_pos_weight=7 / 3,
                max_delta_step=0,
            ),
            dict(
                max_evals=10,
                eta=hp.uniform('eta', 0.01, 0.1),
                round_opt=True,
                num_boost_round=1000,
                min_boost_round=50,
            ),
            dict(
                max_evals=20,
                max_depth=hp.quniform('max_depth', 3, 10, 1),
                min_child_weight=hp.quniform('min_child_weight', 1, 10, 1),
                round_opt=False,

            ),
            dict(
                max_evals=20,
                gamma=hp.uniform('gamma', 0, 3),
                round_opt=False,
            ),
            dict(
                max_evals=10,
                subsample=hp.quniform('subsample', 0.5, 1, 0.1),
                colsample_bytree=hp.quniform('colsample_bytree', 0.5, 1, 0.1),
                round_opt=False,
            ),
        ]

        self.config = config
        self.params = config[0]

    def _train_model(self, params):

        params['max_depth'] = int(params['max_depth'])

        if self.params['round_opt']:

            def _feval(_y, dtrain):
                y = dtrain.get_label()
                metric2 = top_ret(_y, y)
                return 'top_ret', metric2

            evals_result = {}
            model = xgb.train(params, self.train_X, num_boost_round=self.params['num_boost_round'],
                              evals=[(self.predict_X[x], 'test%s' % x) for x in range(len(self.predict_X))],
                              feval=_feval, evals_result=evals_result, verbose_eval=False)
            rmse_result = np.r_['0,2', tuple(evals_result['test%s' % x]['rmse'] for x in range(len(
                self.predict_X)))].mean(axis=0)
            top_ret_result = np.r_['0,2', tuple(evals_result['test%s' % x]['top_ret'] for x in range(len(
                self.predict_X)))].mean(axis=0)

        else:
            model = xgb.train(params, self.train_X, num_boost_round=self.params['num_boost_round'])
            rmse_result = []
            top_ret_result = []
            for j in range(len(self.predict_ry)):
                predict_fit = model.predict(self.predict_X[j])
                rmse_result.append(rmse(predict_fit, self.predict_y[j]))
                top_ret_result.append(top_ret(predict_fit, self.predict_y[j]))
            rmse_result = np.array(rmse_result).mean()
            top_ret_result = np.array(top_ret_result).mean()

        self.model = model
        self.rmse_result.append(rmse_result)
        self.top_ret_result.append(top_ret_result)

    def train_model(self, params):

        self.rmse_result = []
        self.top_ret_result = []

        self._temp_opt = 1

        for date in self.cv_date_list:
            self.load_dataset(date)
            self._set_model_dataset()
            self._train_model(params)

        self.rmse_result = np.array(self.rmse_result).mean(axis=0)
        self.top_ret_result = np.array(self.top_ret_result).mean(axis=0)
        num_boost_round = self.params['num_boost_round'] - 1

        if params['round_opt']:
            num_boost_round = (bottleneck.nanrankdata(self.rmse_result) + bottleneck.nanrankdata(
                self.rmse_result)).argmin()
            if num_boost_round < self.params['min_boost_round'] - 1:
                num_boost_round = self.params['min_boost_round'] - 1
            self.rmse_result = self.rmse_result[num_boost_round]
            self.top_ret_result = self.top_ret_result[num_boost_round]

        if (self.params['eval1_weight'] * self.rmse_result + self.params['eval2_weight'] * self.top_ret_result
                < self._temp_opt):
            self._temp_opt = (self.params['eval1_weight'] * self.rmse_result +
                              self.params['eval2_weight'] * self.top_ret_result)
            self.num_boost_round = num_boost_round + 1

        print(params)
        print('rmse_result: ', self.rmse_result, '\ntop_ret_result: ', self.top_ret_result,
              '\n_temp_opt: ', self._temp_opt, '\nnum_boost_round: ', num_boost_round)

        return self.params['eval1_weight'] * self.rmse_result + self.params['eval2_weight'] * self.top_ret_result

    def search_hyper_parameters(self, search_round=2):

        if not hasattr(self, 'config'):
            self._set_params()

        while search_round > 0:
            search_round -= 1
            for j, params in enumerate(self.config[1:]):
                print('last %s round' % search_round, 'param group %s' % j)
                self.params.update(params)
                algo = partial(tpe.suggest)
                best = fmin(self.train_model, self.params, algo, self.params['max_evals'])
                best.update({'num_boost_round': self.num_boost_round})
                self.params.update(best)

    def _predict_model(self):

        self.load_dataset()
        self._set_model_dataset()
        self.params['max_depth'] = int(self.params['max_depth'])
        self.model = xgb.train(self.params, self.train_X, num_boost_round=self.params['num_boost_round'])

    def predict_model(self):

        self._predict_model()
        metrics = pd.DataFrame(index=['train'] + ['predict%s' % x for x in range(len(self.predict_ry))],
                               columns=['top_ret', 'rmse', 'top_ret_real', 'rmse_real'])

        train_fit = self.model.predict(self.train_X)
        metrics.loc['train', 'top_ret'] = top_ret(train_fit, self.train_y)
        metrics.loc['train', 'rmse'] = rmse(train_fit, self.train_y)
        metrics.loc['train', 'top_ret_real'] = top_ret(train_fit, self.train_ry)
        metrics.loc['train', 'rmse_real'] = rmse(train_fit, self.train_ry)

        predict = []
        for j in range(len(self.predict_ry)):
            predict_fit = self.model.predict(self.predict_X[j])
            predict.append(predict_fit)
            metrics.loc['predict%s' % j, 'top_ret'] = top_ret(predict_fit, self.predict_y[j])
            metrics.loc['predict%s' % j, 'rmse'] = rmse(predict_fit, self.predict_y[j])
            metrics.loc['predict%s' % j, 'top_ret_real'] = top_ret(predict_fit, self.predict_ry[j])
            metrics.loc['predict%s' % j, 'rmse_real'] = rmse(predict_fit, self.predict_ry[j])

        self.predict = predict
        self.metrics = metrics

    def get_compound_factor(self):

        compound = np.full((len(self.predict_date_list), len(self.code_list)), np.nan)
        for j in range(len(self.predict_date_list)):
            compound[j][self.predict_pool[:, j]] = self.predict[j]
        compound = pd.DataFrame(compound, self.predict_date_list, self.code_list)
        return compound


if __name__ == '__main__':
    start_date = 20140401
    end_date = 20181228
    date_list = None
    future_weight = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    middle_address = '/data/user/hanxu/model/temp20200706/'
    save_address = '/data/user/hanxu/model/temp20200706/model_temp/'
    stock_pool_address = None
    factor_list_address = None
    factor_type = 'factor_standardize'
    factor_address = '/data/user/hanxu/model/temp20200706/factor_standardize/'
    future_type = 'future_uniform10t30'
    future_address = None
    real_future_type = 'future_ZZ500'
    real_future_address = None

    cv_model_days = 120
    cv_predict_days = 20
    cv_folds_limit = 8
    long_policy = False

    model_days = 20171231

    trans = True
    orth = False
    boxc = False

    select_factor_list = [
        'MinVW',
        'MinuteLastTurn20std',
        'IndustryReverse',
        'RetMaxMinSum_Mean10',
        'Re300ReturnScore5D',
        'Tick_bsdiff_ret_skew_tail_ordervol_avg3_daily',
        'MarketTakerMu',
        'MedianDownAmtRatio',
        'RevDeal',
        'Tick_bsdiff_ret_skew_top_tradenum_corr3_daily',
        'Tick_bsdiff_ret_skew_top_passive_orderamt_corr3_daily',
        'RSI',
        'MedianDownVarRatio',
        'KNN30',
        'LongVolGrowthSharpe60d',
        'RankRoAIndustrialStability',
        'MarketTaker',
        'RTurnGainMin',
        'Tick_bsdiff_ret_std_top_active_ordervol_corr3_daily',
        'DailyGTJA27_max12',
        'MinCorW',
        'IVR_000300_20',
        'MeanTurn2RetDown5d',
        'CloseVolatility5d',
        'MinTradeKurt5d',
        'UpVolatilityRatio_20',
        'Vol30HHI_Mean2Std10',
        'Smartmoney_hlratio_ms0505_rolling1_daily',
        'VolPctMeanRankDiffInExtremeUpDownRet_Mean5',
        'AbnAmtRet',
        'DuoKongPV',
        'MinuteTurnoverStdSharpe',
        'MinUBS',
        'MinAmtKurt20d',
        'LargeSmallVolumeVWAPRatio_day',
        'CybzCorrClose',
        'Downward_volatility_20days',
        'MinuteRetVolMultSkewSharpe',
        'LiqRatioAS',
        'MildMoneyMaker',
        'RankinglistEffect',
        'MinAmtT',
        'dretvvolnew_msmean_20_10_daily',
        'CEMVstd',
        'IdioSkew5min10d',
        'MinutePVCorrMin',
        'CumretClseSlope_60',
        'OpenCapVolumeRR',
        'FM10_GTGTTM',
        'Smartmoney_amt_skew01505_rolling1_daily',
        'IdealSwing20',
        'MinAbnCorr',
        'dretvvolnew_skewmean_20_3_daily',
        'MinTradeMaxRatio5d',
        'UpSpeed',
        'ForecastEPDelta20d',
        'AbsRet2Deal',
        'MinBWskew',
        'MinMax',
        'MinuteDownVolatilityRatio20d',
        'EMVA',
        'AmtVolStdRankMean5d',
        'BuyAmtStd3Day',
        'QfaROE',
        'SeperateBeforehandRet_30',
        'MinPRRC',
        'MinWeightVolReSwing',
        'Min_amtavg_mktstate_mktskew_tailskew_5_3_daily',
        'InvSta',
        'VolRPriceRCorr20d',
        'VolRegIndexRsquare_20',
        'MinReSkewLast120_5d',
        'AmPmDiff',
        'ValueGrowthChange60d',
        'AvgClose2Vwap_Std_5_daily',
        'MarketHolderMu',
        'NI_SQ_IndustryRank',
        'ROEWin',
        'MinSkew40d',
        'HighActBuySellRatioSharp',
        'HighActBuyAmountMean',
        'dretvvolnew_msmean_60_10_daily',
        'MinPMAmpVolume5d',
        'MinuteTLSTRvs',
        'uretvvolnew_kurtmean_20_3_daily',
        'MinUBM',
        'RetSkewSharp',
        'SwingRateLongShort',
        'VolSurgeSharpe',
        'RTurnGainStd',
        'SellRtnSellMoneyDiffCorr',
        'UpVwap2LowWeightedByVolume_SR20',
        'VolPriceFlyerPlus',
        'Ret10Max_CS60_Mean2Std10',
        'MinAPDN',
        'AmtDealReDiff5d',
        'MinTTM',
        'SimpleVolume',
        'MinBap',
        'MinuteIlliqVwapClose5d',
        'RetVolProdSkewSharp_20',
        'SeperateBeforehandRet_Normolized20',
        'ShoutCutILLIQ_10',
        'TickFactor_DailyBuyOrderVwapStdRatio',
        'Profitability_IndZscore',
        'MinWAC',
        'DavisWin',
        'VwapTurnStdRatio',
        'RetMaxMinSum_SR5',
        'RankRetEPSIndustrialStability',
        'MinARC2VRCExcessSharpe5d',
        'Min_amtavg_selfstate_rawskew_5_3_daily',
        'GTJA36',
        'GTJA_064',
        'MinRetVolKurtRaw_5_5',
        'MinTopTailCost',
        'PVMax',
        'TickFactor_AccBuyKurt_daily',
        'MinHLS',
        'AmtEhdReverse',
        'ReCorr20',
        'MinVBR',
        'CsResidualSkew',
        'GTJA74',
        'BoolDW',
        'TickFactor_DailyPassBuyVwapStdRatio',
        'Netprofitmargin_q',
        'IndRankinglistEffect',
        'APB1m_Mean5d',
        'MinuteDCDVResistEWMA',
        'ForecastEPGChange60d',
        'MinuteCloseSmartGame',
        'NonstationaryPV',
        'DuoKongMix',
        'TickFactor_BuyOrderStd',
        'AmtPerTradeWeightedReturn5d',
        'CEMVsharpe',
        'SectorNotionalSharpe',
        'TickFactor_BuyOrderStdRatio',
        'MinRetVolMaxSr_1_1',
        'IlliqNeg60d',
        'MinPVRSD',
        'MinRetVolMaxSr_1_5',
        'TurnPEStd',
        'Smartmoney_hlratio_rdm01505_rolling3_daily',
        'RetMktDevCorr',
        'AmtStdBias',
        'OBCVPema_10',
        'TickFactor_DailySellTradeStdRatio',
        'DailyGTJA62',
        'ForecastPEGDelta5d',
        'CancelRateStd20d',
        'OperRevTTMStandardGrowth',
        'MinVRSI',
        'TurnoverSharpe',
        'MinuteliqSwingSharpe5d',
        'CorrRetVol_Mean_5',
        'WQ_027',
        'MinuteCloseTurnEWMA',
        'RetStdTurnCorr',
        'MinCloseReSkew5d',
        'CompoundMomSharpe10d',
        'MinVwapRV',
        'MinAC',
        'VwapRatioOnAmtPerTradeDay',
        'DailyGTJA7_mean5',
        'TickFactor_RawActBuyOrderStdRatio',
        'Tick_bsdiff_hl_top_active_ordervol_cov1_daily',
        'NomalToAmt',
        'BigOrderReturn20d',
        'MinTas',
        'EP_Hist2_120D',
        'ODPB_DIFF20',
        'APB5m_Mean5d',
        'Tick_bsdiff_ret_skew_tail_active_orderamt_cov3_daily',
        'VolUpDownStdRatio_Mean_5',
        'MinFW',
        'AgainstBeta',
        'Min10VolBurst5Wegihted5d',
        'MinWR_20_80_5d',
        'MomBigOrder3Day',
        'MinVVM',
        'Smartmoney_close_trb0505_rolling3_daily',
        'MinuteVolumeStdSharpe',
        'CPVDay',
        'MinuteCloseTurnRSharpe',
        'GTJA_042',
        'GTJA54',
        'MinuteUpVar',
        'MinTimeHighLow_20',
        'MinCloseCallAmt5maCorrSharpe',
        'ClosePercentSwing5d',
        'MinVVRankCorrStd',
        'DailyPriceVolume_10',
        'MinCM',
        'uretvvolnew_msmean_20_10_daily',
        'ODPEG_DIFF20',
        'MinuteLastVolumeRank5std',
        'MinuteCloseTurnREWMA',
        'RetRankStd10d',
        'C9_DIFF60',
        'AmtPerTradeWeightedReturn',
        'MinEMVA',
        'MinCorrVolumeRetUp5d',
        'FM2_YOYE',
        'VolitilityRelative',
        'RetCorrTurnDelayPure',
        'ExcessSkew5min10d',
        'MinRSTstd',
        'ValueDelay',
        'uretvvolnew_mstb_60_10_daily',
        'Tick_bsdiff_ret_std_top_orderamt_avg3_daily',
        'TickFactor_PassBuyVwapStdRatio',
        'NetProfitSurprise',
        'TickFactor_MinActBuyOrderStdRatio',
        'TickFactor_RawAccBuyKurt_daily',
        'Last30MinsVwapCloseRatio5d',
        'RetDiffStd_Mean2Std10',
        'LiquidityPure20Part2',
        'ZaoYinTrader',
        'GTJA16',
        'GTJA16_max5_1',
        'PVTTurn60d',
        'Min_amtavg_mktstate_indamtpctstd_tailskew_5_3_daily',
        'OpenPositionInHighLowWeightedByVol_Mean_5',
        'Min5VwapToClose20d',
        'dretvvolnew_skewmean_60_10_daily',
        'MinuteliqAmtRatioSharpe20d',
        'ForecastPE',
        'MinuteTurnoverVolSharpe',
        'Smartmoney_hlratio_rdm0505_rolling3_daily',
        'dretvolnew_skewmean_60_3_daily',
        'VolumeStdHigh2Low20d',
        'QfaYoyeps',
        'MinEMVANorm',
        'MinUBSR',
        'FM2_OTGR',
        'uretvolnew_stdstd_20_3_daily',
        'Min30TDis',
        'LowRtnVolSkew60d',
        'OperProfitTTMStandardGrowth',
        'ExtremeTurnStd',
        'RetBounceCorr',
        'MinTAW',
        'OCVPema_20',
        'IndustriesPBROE',
        'VolPriceCorr',
        'TurnoverSharpe100d',
        'AbnormalVolRaiseMom20d',
        'MinUBK',
        'AmihudLast120min10d',
        'AmtRet20d',
        'LowCandleBottom',
        'CloseVwapRetKurt_day',
        'SectorPESharpe',
        'ClosePercentSharpe5d',
        'VolaRatioOnBSlog3Day',
        'LowRtnVolGrowthSharpe60d',
        'CSTurnpureCorrRet',
        'MinuteLastHourMDDMCLIMBstd20d',
        'AmtStdMean60d',
        'dretvvolnew_msmean_60_3_daily',
        'ClosePercentRank5d',
        'dretvvolnew_skewmean_20_10_daily',
        'BeforehandRetResidual30',
        'ReverseMomentumDouble',
        'MinRVS',
        'dretvvolnew_scmmean_20_10_daily',
        'MinTradeSkew5d',
        'CorrPVTUpCloseSharpe20d',
        'PDPS_Hist2_120D',
        'UpDownVolatility',
        'Tick_bsdiffmktstate_amt_std_top_active_ordervol_corr3_daily',
        'DebtToAsset_std_3y',
        'CloseCorrTurnR2',
        'GTJA176',
        'GTJA16_min5_1',
        'IndustryMidBeta',
        'MinERRC',
        'VolPriceFlyer',
        'SmallPlayersTurnoverSharpe20d',
        'TwapVwapRet',
        'CorrCloseVol_Std10',
        'OverBuySell_Mean_5_daily',
        'VolumeStdHigh2Low5d',
        'MinuteALTKurt',
        'NIGrowthZscore1y',
        'CloseOpenDiffDrawdownCorr',
        'Tick_bsdiffmktstate_mktskew_tail_accamount_corr3_daily',
        'RetSkew_CS120_Mean2Std10',
        'RetSkew_Mean_5',
        'FM2_PTG',
        'MinHVSDis',
        'HighActSellRatioMean',
        'GTJA_032',
        'MinuteTWRSharpe20',
        'MinRetVolSkewRank_5_1',
        'SPPI',
        'MinuteVolumeHHISharpe',
        'Tick_bsdiff_ret_skew_tail_ordercanceledamt_avg3_daily',
        'MinuteRetSkewnessSharpe',
        'ForecastPEGRollChange40d',
        'MinBWstd',
        'LiqCorr',
        'MinHVSmin',
        'VolumeShortLongStdRatio',
        'FM5_YOYNP',
        'UpAmtKurt_Mean5',
        'MinVwapRVskew',
        'MomHigh2Low10d',
        'MinPVRSR',
        'GTJA_062',
        'MorVolAna',
        'FM10_GMTTM',
        'Min_amtavg_skewmean_60_3_daily',
        'Min_RelativeDownReturn',
        'uretvvolnew_kurtskew_20_10_daily',
        'MarketTakerSigma',
        'MoneyMaker',
        'MinTopVolRate',
        'CorrDelVolumePriceSharpe5d',
        'MinuteReturnAutocorr5d',
        'CorrCloseTurn10d_max',
        'ForecastPEGDelta20d',
        'RetSkew_Mean2Std10',
        'MinVVCorrRankStd',
        'IntradayAmountRatioDay',
        'MinVRCExcess5d',
        'CapVolume',
        'QualityGrowthIndRank',
        'MinuteDCDVR',
        'CorrTurnPrice10min5dSharpe',
        'uretvvolnew_skewmean_20_10_daily',
        'ROEStandardGrowth',
        'RelativeIndPEAS',
        'MinCorHighVolumeMax10d',
        'MinRetVolSkewMean_5_5',
        'CorrCloseTurn5d_max',
        'AmtPerDealRetCorr',
        'DailyCorrCloseVol_min5',
        'FM10_PROTTM',
        'Tick_bsdiff_raw_active_ordervol_corr3_daily',
        'MomHighExclMorn20d',
        'GTJA2TransRolling5',
        'MinStdW',
        'DailyVwapStdRatio_mean5',
        'LastTurn',
        'MinuteLastHourMaxClimb20dSR',
        'MinuteVolumeStabilitySharpe',
        'SwingHighLowPriceCorr',
        'MinVB10',
        'MinAmtMidStd',
        'Tick_bsdiffmktstate_ret_skew_top_active_orderamt_corr3_daily',
        'MinuteReturnDiffStdSharpe',
        'dretvolnew_kurtmean_20_10_daily',
        'FR10d_1001',
        'Tick_NewBuyOrderAmt',
        'MinuteEODRetDrawdownRatioSharpe',
        'FM9_GPM',
        'FM11_GPM',
        'Tick_bsdiff_amt_std_top_ordercanceledvol_skew3_daily',
        'Tick_bsdiff_illq_top_ordervol_cov3_daily',
        'RetSkew_CS60_Mean2Std10',
        'MinBum',
        'WQ016',
        'HighVolCorrStd',
        'FM2_GMA',
        'FM11_QOP',
        'MinVRSS',
        'GTJA_026',
        'AmtRet5d',
        'Min_amtavg_minskew_60_10_daily',
        'HighVolCorrMax',
        'Aktr',
        'MinVwapARC2VRCExcessSharpe20d',
        'Min_amtavg_mktstate_mktconsist_tailskew_5_3_daily',
        'VolPriceRunner',
        'HighCloseTurnSharpe20',
        'CorrDownVolumeSharpe',
        'CorrCloseVolumeSharpe',
        'MarketHolderSigma',
        'VolumeStdBias',
        'MinuteSwing',
        'GTJA179',
        'AmtStd_Mean2Std_5_daily',
        'FM9_YOYPRO',
        'MinRetVolSkewRank_5_5',
        'MinSmartFoolRatioMean',
        'MinuteRetVolMultSkew',
        'MinAmtMidSkew',
        'IndustryNeutralizedTurnoverStd',
        'HighVolumeCorr10d',
        'Tick_bsdiffmktstate_illq_top_active_orderamt_corr3_daily',
        'Min30CEMVbias',
        'DealnumSharpe',
        'RetSkew_CS180_Mean2Std30',
        'MarketHolder',
        'ReverseDistance',
        'CorrCloseVol_Std_5_daily',
        'MinWeightVolReSkew',
        'SwingToTurn',
        'Min_PredictReturnMean',
        'VolSwingRankCorr',
        'FM8_PTGTTM',
        'MinuteDCDVHoldEWMA',
        'MinuteMADistanceMA',
        'MinVolM',
        'MinuteDCDVH',
        'Tick_bsdiff_illq_tail_active_orderamt_avg3_daily',
        'AmtRet',
        'MomW',
        'EBITDev',
        'DailyCorrHighVol_max5',
        'MinuteRetLastHrSkew',
        'uretvvolnew_meanskew_60_10_daily',
        'Min_amtavg_selfstate_ret_topskew_5_3_daily',
        'IdioJump5min10d',
        'FM11_QOPYOY',
        'ReStdUp2Down5d',
        'Tick_bsdiffmktstate_idxmadiff_tail_accamount_corr3_daily',
        'MinWVRS',
        'Minute30CloseVolumeCorr',
        'uretvvolnew_stdskew_60_10_daily',
        'RetCutCorrTurnDelay',
        'RoeTTM_IndRank',
        'HighCapVolumeRR',
        'TargetReturnDelta5d',
        'Tick_bsdiff_illq_top_active_orderamt_cov3_daily',
        'MinRetVolKurtRank_5_1',
        'MinuteCloseCallAuctionTurnoverStdChange180d',
        'RangeRetCorr20',
        'AmtSkew3Day',
        'GPMarTTMStandardGrowth',
        'RankEBITPSChg',
        'GTJA_083',
        'MinuteTTLSStdRank',
        'Min_amtavg_mktstate_mktskew_topskew_5_3_daily',
        'MinuteCloseMomentumSharpe',
        'AmtPerTradeInOutflow5d',
        'ValueGrowthIndRank',
        'HighCloseTurnSharpe',
        'CEMV_CS30_SR20',
        'Tick_bsdiffmktstate_sizestyle_top_active_ordervol_corr3_daily',
        'MinuteRelativeUpVar',
        'StableRet',
        'TurnCloseLowSharpe',
        'DailyVwapStdRatio_min5',
        'StableVol',
        'BigOrderNetInflowRate5d',
        'MinuteVolVwapCorrCloseChg',
        'MinuteCloseTurnSharp',
        'MinuteDCDTA5d',
        'uretvvolnew_msstd_60_10_daily',
        'PVTTurn180d',
        'Min30HW',
        'Tick_bsdiffmktstate_idxmadiff_top_active_ordervol_corr3_daily',
        'CloseCapVolumeRRSharp',
        'ForecastPEGRoll',
        'CSTurnpureCorrRetSharp',
        'SwingW',
        'MinuteCloseTurn',
        'MinuteCloseUpVar',
        'TurnHighCloseSharpe',
        'MinuteTWRSkew20',
        'MinuteCorrRank',
        'MinLSV',
        'ProfitNoticeIndRank',
        'MinuteLast30mPriceVolRefineMean10d',
        'DeltaTurnSkew',
        'DownSpeed',
        'MinAmtSkew10d',
        'TickFactor_MinBuyOrderStdRatio',
        'TurnPEAS',
        'AmtPerTradeReSkew20d',
        'CEMV_Skew40',
        'DailyHLStdRatio_min5',
        'TurnCloseLowMP',
        'MinPVCS',
        'DailyHighStdRatio_min5',
        'FM18_PTG',
        'FM5_QG',
        'FM11_QGM',
        'CapVolumeRR',
        'GrahamValue',
        'MinBWS',
        'MinuteEODSortinoRatioSharpe',
        'Tick_NewSellOrderAmt_std',
        'TurnCloseLowSA',
        'VolRaiseMom5d',
        'Min_ACD',
        'Min10mRetUpVar',
        'TradeNumSkewDay',
        'TurnGain',
        'MinuteAmtStdSwing',
        'DivMulStaVol',
        'MinReSkewLast120_20d',
        'DailyCorrHighVol_std5',
        'DailyStdRatio_min5',
        'DailyHighStdRatio_max5',
        'RankP2UndistributedEPS',
        'Tick_NewBuyOrderAmt_std',
        'Min_amtavg_mktstate_ret_skew_tailskew_5_3_daily',
        'GTJA64',
        'MinuteCloseTurnRSharpe10',
        'Tick_bsdiffmktstate_mktconsist_top_active_ordervol_cov3_daily',
        'Tick_bsdiff_ret_tail_passive_ordervol_corr1_daily',
        'DownAmtPerkurt',
        'DailyStdRatio_max5',
        'DailyHighLowStdRatio_min5',
        'ReverseMomentumTriple',
        'FallTurnover',
        'MinuteCloseTurnR',
        'FM2_YOYTR',
        'CEMV_CS30_Skew40',
        'MinIdx500Corr',
        'RevSplit',
        'TurnHighClose',
        'CorrCloseRankTurn20d',
        'TurnNeuRetCorrSharp',
        'ForecastPERoll',
        'MinReSkewLast120_10d',
        'IdeaReverser5d',
        'MinuteliqSwingStd5',
        'OTC5std_daily',
        'UpHigh2VwapWeightedByVolume_SR20',
        'Min_amtavg_msstd_60_3_daily',
        'FR40d',
        'ExceedSwingCorAmt',
        'Min_cummaxdd_trbtb_20_10_daily',
        'MinRVM',
        'MinuteAmtCV3d',
        'HighCandleBottom',
        'WeightedDownUpSumRatio5d',
        'CompoundMomSharpe5d',
        'MinTopV',
        'ClosePercentRank10d_up',
        'MinWeightVolReRatio',
        'CloseOpenVolumeCorr',
        'PROFIT_UP60',
        'TurnHighCloseSigma',
        'BeforehandRetCut30',
        'SectorIlliquidity',
        'PriceDiff',
        'MinReturnVolUp2Down5d',
        'GrowthRefined',
        'MinRRCs',
        'Tick_bsdiffmktstate_ret_tail_active_ordervol_corr3_daily',
        'MinIndexCorr',
        'Min_amtavg_selfstate_hl_topskew_5_3_daily',
        'ODPB_DIFF120',
        'OpenAmt',
        'Min_cummaxdd_trbmean_20_10_daily',
        'RetVolMultSharp_30',
        'MinuteTPVDeltaCorr',
        'HighCloseTurnSharpe80',
        'TickFactor_AccBuyStd',
        'HighCloseTurnSigma',
        'FR20d_1130',
        'BeforehandRetCut20',
        'Min_amtavg_mktstate_mktconsist_tailskew_5_1_daily',
        'MinWVRSS',
        'FR40d_1001',
        'CloseCapVolumeRRBias',
        'Min_amtavg_mktstate_illq_topskew_5_3_daily',
        'ForecastEPChange60d',
        'MinuteLastHourSkewness40d',
        'Tick_bsdiff_ret_std_top_ordervol_corr3_daily',
        'Min_amtavg_selfstate_illq_topskew_5_3_daily',
        'uretvvolnew_skewmean_60_10_daily',
        'MinuteCloseTurnRev',
        'FM20_PTG',
        'VwapCloseAdj20d',
        'MinTTD',
        'Min_amtavg_skewmean_20_10_daily',
        'Tick_bsdiffmktstate_ret_std_top_active_ordervol_cov3_daily',
        'MinSkW',
        'VolitilityMax',
        'Tick_bsdiffmktstate_ret_std_tail_passive_orderamt_cov3_daily',
        'Min_amtavg_mktstate_sizestyle_topskew_5_3_daily',
        'MinBus',
        'Tick_bsdiff_hl_top_active_ordervol_cov3_daily',
        'FM8_GPM',
        'MinHVV',
        'MinAmtMidChg',
        'MinuteVolCVSkew10d',
        'Min_cummaxdd_rdmmean_20_3_daily',
        'PEAdj',
        'GTJA2TransRolling20',
        'CorrVolReturn5d',
        'Minute30m5dVolumeHHI',
        'Trade10minMax10dMin',
        'Min_amtavg_selfstate_hl_tailskew_5_3_daily',
        'GTJA_007',
        'Min_amtavg_mstb_60_10_daily',
        'Tick_bsdiffmktstate_timenearopen_tail_passive_orderamt_corr3_daily',
        'RankPBDev',
        'MinPVRSV',
        'MinuteAmtRetCor5d',
        'MinTradeStd10d',
        'Min60_RVstd',
        'Min_amtavg_msstd_60_10_daily',
        'FM5_OTG',
        'FM11_YOYOP',
        'MinSCS',
        'MinuteVMASkew',
        'MinuteEODVolumeWeightedReturnSharpe',
        'MinVRSR',
        'Min_amtavg_mktstate_timenearclose_topskew_5_3_daily',
        'MinRetVolMaxStd_1_1',
        'FM5_ROETTM',
        'FM13_PTG',
        'FM2_GPM',
        'PVTTurn5d',
        'MinRetVolStdSr_1_1',
        'FM15_EPS',
        'MinRRCDis',
        'uretvvolnew_msstd_60_3_daily',
        'MinuteVolofVolumeHHI',
        'DailyPrfLP_6',
        'MinuteCloseDiff',
        'TurnCorrSharp',
        'LiqRatioSA',
        'MinuteHighLowRtnVolDiff',
        'FM3_YOYOP',
        'MinVolRe',
        'Min_amtavg_msmean_20_3_daily',
        'MinuteValidRet',
        'MinVwapARC2VRCExcessChange60d',
        'TurnCV_10',
        'Min_amtavg_mktstate_sizestyle_tailskew_5_3_daily',
        'FM11_YOYTR',
        'FM8_OPYOY',
        'MinVRSV',
        'FM11_PTGTTM',
        'FM5_PTG',
        'MarketRec',
        'Min_amtavg_skewmean_60_10_daily',
        'FM11_QROE',
        'MinuteEODVolWeightedLongShortPowerSharpe',
        'FM5_OTE',
        'FR20d_1001',
        'MinuteGroupReBias5d',
        'MinuteIdioSkew5d',
        'Min_amtavg_selfstate_rawskew_5_1_daily',
        'MinVwapARC2VRCExcessChange20d',
        'RankPEChange',
        'RankEBIT2TRIndustrialStability',
        'FM9_ROATTM',
        'FM8_QOP',
        'ODPEG_DIFF120',
    ]
    top_factor_num = 100

    self = AlphaBaseModelSimple(middle_address, start_date, end_date, date_list, future_weight, stock_pool_address,
                                factor_list_address, save_address, factor_type, factor_address,
                                future_type, future_address, real_future_type, real_future_address)

    self.select_factor(select_factor_list, top_factor_num)
    self.get_model_date_list(model_days)
    self.get_cv_date_list(cv_model_days, cv_predict_days)
    # self.store_dataset(save_address, trans, orth, boxc)
    # self.load_dataset(save_address, date=20171117)
    # self.set_model_dataset()
    self._set_params()
    self.search_hyper_parameters()
    self.predict_model()
    self.metrics.to_hdf('%s/metrics_xgbc3.h5' % save_address, 'metrics_xgbc3')
    compound = self.get_compound_factor()
    compound.to_hdf('%s/compound_xgbc3.h5' % save_address, 'compound_xgbc3')

    stock_pool = pd.DataFrame(self.predict_pool.T, index=self.predict_date_list, columns=self.code_list)
    nft = NonFactorTest(self.predict_date_list[0], self.predict_date_list[-1], stock_pool, 5, pre_neutralize=False)
    nft.load_factor(compound, neutral=False)
    nft.test_factor()
