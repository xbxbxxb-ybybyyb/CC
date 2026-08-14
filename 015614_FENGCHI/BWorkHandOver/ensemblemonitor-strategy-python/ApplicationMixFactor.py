# @Time : 2020/12/28 15:18
# @Author : Zhichen Lu
# @File : Application.py

import pandas as pd
# from online_conf import realtime_path, local_config_path, holding_info_path, hyper_param_path, \
#     code_list_path, model_config_path, buy_time_info_path, vol_info_path, init_conf_path, daily_out_path, ratio_path
from online_conf import realtime_path
import xgboost as xgb
from sklearn.externals import joblib
import lightgbm as lgb
from catboost import CatBoostRegressor
from sklearn.linear_model import LinearRegression
import os, datetime
import datetime as dt
import numpy as np
import traceback
# from generateTimetable import generateTimetableAndTargetQtyInterval
import time as tm
import configparser
import tensorflow as tf
# import tensorflow.keras.backend as K
# from tensorflow.keras.models import load_model
from tensorflow.python.ops import math_ops
from Application930ForMix import Application930
from FactorCalculator_.RealTime import MinFactorCalculator
from ExtraTools import get_path_conf

os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'


path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
local_config_path, holding_info_path, hyper_param_path, code_list_path, model_config_path, buy_time_info_path, vol_info_path, init_conf_path, daily_out_path, ratio_path = \
    [path_conf[x] for x in
     ['local_config_path', 'holding_info_path', 'hyper_param_path', 'code_list_path', 'model_config_path', 'buy_time_info_path', 'vol_info_path', 'init_conf_path',
      'daily_out_path', 'ratio_path']]

market_data_path = realtime_path + 'market_data/'


def trans_int2windcode(code):
    if isinstance(code, str):
        return code
    elif isinstance(code, (float, int)):
        temp = str(int(code)).zfill(6)
        if temp[0] == '9' and len(temp) == 7:  # 指数
            if temp[1] == '3':
                result = temp[1:] + '.SZ'
            else:
                result = temp[1:] + '.SH'
        elif temp[0] == '0' or temp[0] == '3':
            result = temp + '.SZ'
        elif temp[0] == '6':
            result = temp + '.SH'
        else:
            result = temp + 'SH'
        return result
    else:
        raise Exception('input code type error')


def load_model_xgb(path, param={}):
    booster = xgb.Booster(param)
    booster.load_model(path)
    return booster


def load_model_sklearn(path):
    clf = joblib.load(path)
    return clf


def load_model_NN(path, param={}):
    def Network(param={}):
        # TODO:define your network structure and param
        return

    model = Network(param)
    model.load_weight(path)
    return model


def load_linear_v2(file):
    def ic_all(y_true, y_pred):
        yn_true = y_true - tf.keras.backend.mean(y_true)
        yn_true = yn_true / math_ops.maximum(tf.keras.backend.sqrt(tf.keras.backend.sum(tf.keras.backend.square(yn_true))), 1e-7)
        yn_pred = y_pred - tf.keras.backend.mean(y_pred)
        yn_pred = yn_pred / math_ops.maximum(tf.keras.backend.sqrt(tf.keras.backend.sum(tf.keras.backend.square(yn_pred))), 1e-7)
        return tf.keras.backend.sum(yn_true * yn_pred)

    def mae(y_true, y_pred):
        return tf.keras.backend.mean(tf.keras.backend.abs(y_pred - y_true))

    def mix_loss(y_true, y_pred):
        yn_true = y_true - tf.keras.backend.mean(y_true)
        yn_true = yn_true / math_ops.maximum(tf.keras.backend.sqrt(tf.keras.backend.sum(tf.keras.backend.square(yn_true))), 1e-7)
        yn_pred = y_pred / math_ops.maximum(tf.keras.backend.sqrt(tf.keras.backend.sum(tf.keras.backend.square(y_pred))), 1e-7)
        return - tf.keras.backend.sum(yn_true * yn_pred)

    def small_tanh(x):
        return tf.keras.backend.tanh(x) / 10

    custom_objects = {'ic_all': ic_all, 'mae': mae, 'mix_loss': mix_loss,
                      'small_tanh': small_tanh}

    model = tf.keras.models.load_model(file, custom_objects=custom_objects)
    return model


model_load_conf = {
    'Linear': load_model_sklearn,
    'XGB': load_model_xgb,
    'NN': load_model_NN,
    'LinearV2': load_linear_v2,
    'CatBoost': load_model_sklearn,
    'lightGBM': load_model_sklearn
}


# model = load_linear_v2('/data/group/800319/strategy_local_path//model/LinearV2_D/20201013.hdf5')

class Application:

    def __init__(self, date, log=print):

        self.log = log
        app930 = Application930(date, log=log)
        config = configparser.ConfigParser()
        config.read(init_conf_path + '%d.ini' % date)
        strategy_config = dict(config['strategy_init'])
        self.log(f'FIX:\n {strategy_config}')
        date, pre_date, barly_max_buy, stk_min_amt = map(int, [strategy_config[x] for x in
                                                               ['date', 'pre_date', 'barly_max_buy', 'stk_min_amt']])
        order_ratio = float(strategy_config['order_ratio'])
        per_amt = float(strategy_config['per_amt'])
        portfolio_id = eval(strategy_config['portfolio_id'])
        # 初始化输出路径
        if not os.path.exists(f'{daily_out_path}/{str(date)}'):
            os.mkdir(f'{daily_out_path}/{str(date)}')
        # 加载股票池，股票池文件命名为T-1日日期
        code_list = pd.read_pickle(code_list_path + '%d.pkl' % pre_date)
        # 加载模型配置文件,配置文件名称为模型更新日期名称
        file_list = sorted(list(filter(lambda x: x < 'model_conf%d.pkl' % date and x.endswith('.pkl'), os.listdir(model_config_path))))
        if not file_list:
            raise Exception('No available model config')
        log(f'loading model file {file_list[-1]}')
        model_conf, threshold = pd.read_pickle(model_config_path + file_list[-1])
        # 加载前一日收盘持仓信息,文件名为T-1日日期
        if not os.path.exists(holding_info_path + '%d.pkl' % pre_date):
            raise Exception('No available holding info file')
        holding_info = pd.read_pickle(holding_info_path + '%d.pkl' % pre_date)
        # 加载持仓股票的买入时间信息
        if not os.path.exists(buy_time_info_path + '%d.pkl' % pre_date):
            raise Exception('No available buy time info file')
        buy_time_info = pd.read_pickle(buy_time_info_path + '%d.pkl' % pre_date)

        # 因子方向、可用因子列表
        factor_direction = pd.read_pickle(local_config_path + 'factor_direction.pkl')
        available_factor_list = pd.read_pickle(local_config_path + 'using_fix_list.pkl')
        # 加载均值、标准差
        file_list = os.listdir(hyper_param_path)
        mean_file = 'mean%d.pkl' % pre_date
        if mean_file not in file_list:
            raise Exception('No available mean file')
        std_file = 'std%d.pkl' % pre_date
        if std_file not in file_list:
            raise Exception('No available std file')
        factor_mean = pd.read_pickle(hyper_param_path + mean_file)
        factor_std = pd.read_pickle(hyper_param_path + std_file)
        # 加载成交量
        vol_info = pd.read_pickle(vol_info_path + '%d.pkl' % pre_date)
        # 加载复权因子
        adj_factor = pd.read_pickle(f'{realtime_path}market_data/{date}/adjfactor.pkl')
        adj_factor = adj_factor.loc[adj_factor.index[-1]].reindex(vol_info.columns).fillna(1)
        self.adj_processed = False
        # 加载下单用的分布
        # if not os.path.exists(alog_trading_distr_path + '%d.pkl' % pre_date):
        #     raise Exception('No available Intraday Distr File')
        # intraDistr = pd.read_pickle(alog_trading_distr_path + '%d.pkl' % pre_date)
        # 加载模型、阈值、模型对应的因子
        model_list, factor_map = self.load_basic_conf(model_conf)
        factor_list_fix = set()
        factor_list_5min = set()
        for each in factor_map:
            if 'fix' in factor_map[each]:
                factor_list_fix = factor_list_fix.union(set(factor_map[each]['fix']))
            if '5min' in factor_map[each]:
                factor_list_5min = factor_list_5min.union(set(factor_map[each]['5min']))
        if factor_list_fix - set(available_factor_list):
            raise Exception(f'Using unsupported factors{factor_list_fix - set(available_factor_list)}')
        factor_list_fix = sorted(list(factor_list_fix))
        if portfolio_id is None:
            portfolio_id = -1

        ##########隔离池、黑名单
        unavailable_pool = pd.read_pickle(f'{local_config_path}restrict_list.pkl')
        ##########重合部分持仓在930 和 fix时点的比例
        ratio = pd.read_pickle(f'{ratio_path}{pre_date}.pkl')

        self.log = log
        self.portfolio_id = portfolio_id
        self.date = date
        self.pre_date = pre_date
        self.per_amt = per_amt
        self.barly_max_buy = barly_max_buy
        self.stk_min_amt = stk_min_amt
        self.order_ratio = order_ratio
        self.stk_list = sorted(list(set(code_list) - unavailable_pool))

        # self.intraDistr = intraDistr
        self.factor_list = factor_list_fix
        self.model_list = model_list
        self.threshold = threshold
        self.factor_map = factor_map
        self.buy_time_info = buy_time_info
        self.cash = holding_info.pop('cash')
        self.holding = holding_info
        self.available = holding_info.copy()
        self.pool_with_over_night_stk = sorted(list(set(self.stk_list).union(self.holding.keys())))
        self.involved_instance = set(self.pool_with_over_night_stk).union(set(app930.pool_with_over_night_stk))
        self.vol_info = vol_info[self.pool_with_over_night_stk]
        self.backup_adj_factor = adj_factor
        self.factor_direction = factor_direction[factor_list_fix]
        self.factor_mean = factor_mean.loc[factor_list_fix, self.pool_with_over_night_stk].T
        self.factor_std = factor_std.loc[factor_list_fix, self.pool_with_over_night_stk].T
        self.pred_ret = {}
        self.signal = {}
        self.factor = {}
        self.time = None
        self.pre_time = None
        self.buy_order_record = {}
        self.sell_order_record = {}
        self.total_buy_amt = 0
        self.total_sell_amt = 0
        # 截止至某个bar,近半小时买、卖的成交额
        self.barly_buy_amt, self.barly_sell_amt = {}, {}
        self.holding_info = {}
        self.holding_change = {}
        self.app930 = app930
        self.total_holding_info = {}
        self.ratio = ratio
        self.factor_calculator = MinFactorCalculator(date, log=self.log)
        if set(factor_list_5min) - set([x[0] for x in self.factor_calculator.factor_list]).union(set([x[0] for x in self.factor_calculator.desample_factor_list])):
            raise Exception(
                f'Wrong {set(factor_list_5min) - set([x[0] for x in self.factor_calculator.factor_list]).union(set([x[0] for x in self.factor_calculator.desample_factor_list]))}')
        self.factor_list_5min = factor_list_5min
        self.factor_5min = {}

    def get_first_target_plan(self):

        involved_stk = self.involved_instance
        holding_info = pd.DataFrame(index=involved_stk)
        holding_info['PortfolioNO'] = '1'
        holding_info['NetPosition'] = pd.Series(self.app930.holding).reindex(involved_stk).fillna(0)
        holding_info['SellAvailable'] = pd.Series(self.app930.available).reindex(involved_stk).fillna(0)
        holding_info['TotalBuyAmount'] = 0
        holding_info['TotalSellAmount'] = 0
        holding_info.loc[self.holding.keys(), 'NetPosition'] += pd.Series(self.holding).reindex(involved_stk).fillna(0)
        holding_info.loc[self.app930.holding.keys(), 'SellAvailable'] += pd.Series(self.app930.holding).reindex(involved_stk).fillna(0)
        holding_info['SellAvailable'] = holding_info['NetPosition']

        holding_info = holding_info.reset_index().rename(columns={'index': 'Symbol'}).fillna(0)

        self.total_holding_info[930] = holding_info.copy()
        holding_info = holding_info.set_index('Symbol')
        if self.ratio.shape[0] > 0:
            holding_info.loc[self.ratio.index, ['NetPosition', 'SellAvailable']] = (
                    holding_info.loc[self.ratio.index, ['NetPosition', 'SellAvailable']].T * self.ratio['bar_930']).T
        holding_info = holding_info.reset_index()
        res = self.app930.bar_handler(holding_info)
        return res

    def update_time(self, time):
        if self.time is None:
            self.pre_time = self.time
            self.time = time
            return
        if self.time < time:
            self.pre_time = self.time
            self.time = time
        elif self.time == time:
            return
        else:
            raise Exception('Target time is less than current time')

    def get_vol_info(self, stk_list):
        if self.time is None:
            raise Exception('Bar time is not define')
        return self.vol_info.T[self.time][stk_list]

    def feature_engineering(self, factor):
        # return factor.fillna(0)
        nan_count = factor.isnull().sum(axis=1)
        return factor[nan_count < 0.2 * factor.shape[1]].fillna(0)

    def load_basic_conf(self, model_conf):
        model_pack = {}
        factor_map = {}

        for each in model_conf:
            model_type, path, factor_list = model_conf[each]
            model_pack[each] = model_load_conf[model_type](path)
            factor_map[each] = factor_list
        return model_pack, factor_map

    def predict_by_multi_model(self, factor, factor_5min, time_point=None):
        if time_point is None:
            time_point = self.time
        if time_point in self.pred_ret or time_point in self.signal:
            raise Exception(
                f'Time point key {time_point} is already exist in predict result, maybe time point need to be update')
        factor_5min.index = factor_5min.index.map(trans_int2windcode)
        res = {}
        filtered_factor = {}
        for each in self.model_list:
            model = self.model_list[each]
            factor_list_fix = self.factor_map[each]['fix']
            if '5min' in self.factor_map[each]:
                factor_list_5min = self.factor_map[each]['5min']
            else:
                factor_list_5min = []
            factor_list = factor_list_fix + factor_list_5min
            tag = '_'.join(factor_list)
            if tag not in filtered_factor:
                filtered_factor[tag] = self.feature_engineering(pd.concat([factor[factor_list_fix], factor_5min.loc[self.involved_instance, factor_list_5min]], axis=1))
                if factor_list_5min:
                    filtered_factor[tag][factor_list_fix] = filtered_factor[tag][factor_list_fix] * self.factor_direction.loc[factor_list_fix]
            if isinstance(model, xgb.core.Booster):
                d_matrix = xgb.DMatrix(filtered_factor[tag])
                model.set_param('predictor', 'cpu_predictor')
                res[each] = pd.Series(model.predict(d_matrix), index=filtered_factor[tag].index)
            elif isinstance(model, LinearRegression):
                res[each] = pd.Series(model.predict(filtered_factor[tag])[:, 0], index=filtered_factor[tag].index)
            elif isinstance(model, tf.keras.models.Model):
                res[each] = pd.Series(model.predict(filtered_factor[tag].values)[:, 0], index=filtered_factor[tag].index)
            elif isinstance(model, lgb.sklearn.LGBMRegressor):
                res[each] = pd.Series(model.predict(filtered_factor[tag]), index=filtered_factor[tag].index)
            elif isinstance(model, CatBoostRegressor):
                res[each] = pd.Series(model.predict(filtered_factor[tag]), index=filtered_factor[tag].index)
            else:
                self.log(f'Undefined model type {each}')
            if len(set(res[each])) == 1:
                self.log(f'All prediction by model {each} are the same')
        self.pred_ret[time_point] = pd.DataFrame(res)
        integrated_pred_ret = self.pred_ret[time_point].mean(axis=1)
        trigger = integrated_pred_ret > self.threshold
        integrated_pred_ret[~trigger] = np.nan
        status = self.get_realtime_dataflow('limit_status')
        status = status.loc[status.index[-1], list(set(integrated_pred_ret.index).intersection(status.columns))]
        status = status[status.isin([1, -1])]
        integrated_pred_ret[status.index] = np.nan
        self.signal[time_point] = integrated_pred_ret.dropna()
        pd.to_pickle([self.pred_ret[time_point], self.signal[time_point]], f'{daily_out_path}/{str(self.date)}/pred_signal_{str(time_point)}.pkl')
        return self.signal[time_point]

    def load_factor(self, time_point, factor_path, backtest=False):
        factor = {}
        for each in self.factor_list:
            temp_factor = pd.read_pickle('%s/Fix%d_%s.pkl' % (factor_path, time_point, each))
            factor[each] = temp_factor.T[str(self.date)]
        factor = pd.DataFrame(factor)
        factor = factor.reindex(self.pool_with_over_night_stk, axis=0).reindex(self.factor_list, axis=1)
        self.log(f'backtest: {backtest}')
        # TODO Cahnge Bck
        if self.time == 1300:
            self.factor_calculator.calc_bar_data(1130, 0, False, back_test=backtest)
        else:
            self.factor_calculator.calc_bar_data(self.time, 0, False, back_test=backtest)

        self.factor[time_point] = self.factor_direction * (factor - self.factor_mean) / self.factor_std
        self.factor[time_point] = self.factor[time_point].clip(-6, 6)
        self.factor_5min[time_point] = self.factor_calculator.factor.loc[self.factor_list_5min].T
        pd.to_pickle(self.factor_calculator.factor, f'{daily_out_path}/{self.date}/5min_factor_{self.time}.pkl')


        return self.factor[time_point], self.factor_5min[time_point]

    def holding_another_round(self, stk):
        if stk not in self.buy_time_info or stk not in self.available or stk not in self.holding:
            self.log('Existing information of stock %s are not complete' % stk)
            return
        buy_date, buy_time = self.buy_time_info[stk][:2]
        if buy_date == self.pre_date and buy_time == self.time:
            self.buy_time_info[stk] = (self.date, self.time)

    def predict(self, time, factor_path, backtest=False):
        self.update_time(time)
        try:
            e = tm.time()
            factor, factor_5min = self.load_factor(time, factor_path, backtest)
            self.log(f'factor loading time: {tm.time() - e}')
            pd.to_pickle({'fix': factor, '5min': factor_5min}, f'{daily_out_path}{self.date}/factor_{self.time}.pkl')
            e = tm.time()
            self.predict_by_multi_model(factor, factor_5min, time)
            self.log(f'model prediction time: {tm.time() - e}')
            return True
        except Exception as e:

            self.log(f'Load and predict failed in time point {str(time)} \n {repr(e)}')
            self.log(f'{traceback.format_exc()}')

        # except:
        #     self.log('Factor load failed in bar %d' % time)
        #     return False

    def get_realtime_dataflow(self, factor, type='stock'):
        if self.time == 1300:
            time = 1130
        else:
            time = self.time
        return pd.read_pickle(market_data_path + '/%d/%d/%s/%s.pkl' % (self.date, time, type, factor))

    def bar_handler(self, signal=None):
        self.log(f'{self.time} bar_handler in')
        if not self.adj_processed:
            if os.path.exists(f'{realtime_path}/market_data/{self.date}/Data_adjfactor.h5'):
                adj_factor = pd.read_hdf(f'{realtime_path}/market_data/{self.date}/Data_adjfactor.h5').loc[self.date].reindex(self.vol_info.columns)
            else:
                self.log(f'Data_adjfactor.h5 is nor available in {self.time}')
                adj_factor = self.backup_adj_factor
            self.vol_info = self.vol_info * adj_factor
            self.adj_processed = True
        available_instance = self.holding_info[self.time]['Symbol'].tolist()
        # 剔除盘中涨跌停
        limit_status = self.get_realtime_dataflow('limit_status')
        limit_status = limit_status[-1:].T[limit_status.index[-1]]
        if signal is None:
            signal = self.signal[self.time]
        trigger_stk = set(signal.keys())
        # 当日可卖出股票 = 持仓股票剔除 盘中涨跌停
        avaliable_stk = set(self.available.keys()) - set(limit_status[limit_status.isin([1, -1])].index)
        avaliable_trigger_stk = avaliable_stk.intersection(trigger_stk)
        sell_stk = list(avaliable_stk - trigger_stk)
        # 截止当前持有超过240分钟的股票
        ######################
        # stk_hold_over_240 = set()
        # for stk in avaliable_stk:
        #     buy_date, buy_time = self.buy_time_info[stk][:2]
        #     if buy_date == self.pre_date and buy_time == self.time:
        #         stk_hold_over_240.add(stk)
        #
        # sell_stk = list(stk_hold_over_240 - trigger_stk)
        # avaliable_trigger_stk = set(stk_hold_over_240).intersection(trigger_stk)
        ##########################
        # 可买入股票 = 触发股票 剔除 不在股票池的股票 以及 有持仓个股
        trigger_stk = trigger_stk.intersection(set(self.stk_list))
        trigger_stk = trigger_stk - set(self.holding.keys())
        if trigger_stk - set(available_instance):
            self.log(f'Buy stock contain unavailable instance {trigger_stk - set(available_instance)}')
        trigger_stk = trigger_stk.intersection(set(available_instance))
        historical_future_vol = round(self.get_vol_info(self.pool_with_over_night_stk) * self.order_ratio, -2)
        for stk in avaliable_trigger_stk:
            self.holding_another_round(stk)

        close = self.get_realtime_dataflow('close')
        close = close[-1:].T[close.index[-1]]

        if sell_stk:
            limit_down_judge = limit_status.eq(-1).loc[sell_stk]
            sell_stk = limit_down_judge[~limit_down_judge].index.tolist()

        sell_vol = {}
        if self.cash < self.per_amt:
            # 如果当前现金不足买入一支股票，仅卖出
            target_vol = pd.Series()
        elif trigger_stk:
            # 处理买入股票
            limit_up_judge = limit_status.eq(1).loc[trigger_stk]  # pd.Series(limit_up_judge, index=trigger_stk)
            trigger_stk = limit_up_judge[~limit_up_judge].index.tolist()
            target_close = close.loc[trigger_stk]
            target_vol = round(self.per_amt / target_close, -2)
            target_vol = pd.concat([target_vol, historical_future_vol[list(trigger_stk)]], axis=1).min(axis=1)
            target_vol = target_vol // 100 * 100
            target_amt = target_vol * target_close
            target_amt = target_amt.loc[signal[trigger_stk].sort_values(ascending=False).index.tolist()]
            target_amt = target_amt[target_amt >= self.stk_min_amt]
            target_amt = target_amt[target_amt.cumsum() < self.cash]
            trigger_stk = target_amt.index.tolist()
            trigger_num = min(len(trigger_stk), int(self.cash // self.per_amt), self.barly_max_buy)
            trigger_stk = trigger_stk[:trigger_num]
            target_vol, target_amt = target_vol[trigger_stk], target_amt[trigger_stk]
        else:
            target_vol = pd.Series()
        # self.holding.rename({x:int(x[:-3]) for x in self.holding.index}).to_frame().astype(int).reset_index().values.tolist()
        if set(sell_stk) - set(available_instance):
            self.log(f'Sell stock contain stock not in available instance pool {set(sell_stk) - set(available_instance)}')
        sell_stk = list(set(sell_stk).intersection(set(available_instance)))
        for stk in sell_stk:
            buy_date, buy_time = self.buy_time_info[stk]
            if buy_date < self.pre_date or (buy_date == self.pre_date and buy_time <= self.time):
                sell_vol[stk] = min(historical_future_vol[stk] // 100 * 100, self.holding[stk])
        sell_vol = pd.Series(sell_vol)
        self.sell_order_record[self.time] = sell_vol.copy()
        self.buy_order_record[self.time] = target_vol.copy()
        e = tm.time()
        sell_vol = self.get_formated_order(sell_vol, 'S')
        target_vol = self.get_formated_order(target_vol, 'B')
        self.log(f'Timetable generation time in {self.time}: {tm.time() - e}')
        order_content = sell_vol + target_vol
        pd.to_pickle({
            'sell_vol': self.sell_order_record[self.time],
            'buy_vol': self.buy_order_record[self.time],
            'order_content': order_content
        }, f'{daily_out_path}/{str(self.date)}/order_info_{str(self.time)}.pkl')
        self.barly_output()
        if str(self.time) == '1430':
            self.output_daily_summary()

        return order_content

    def get_formated_order(self, target_vol, flag):
        if flag == 'S':
            target_vol = -1 * target_vol
        elif flag == 'B':
            pass
        else:
            raise Exception('Wrong Flag')
        content = []
        for stk in target_vol.index:
            # if stk in self.intraDistr:
            #     distr = self.intraDistr[stk]
            # else:
            #     self.log(f'---------------------intrDistr of {stk} does not exist------------------------')
            #     distr = {str(self.time).zfill(4): np.arange(1, 4)}
            # timetable = generateTimetableAndTargetQtyIntervalEqully(distr, target_vol[stk], self.date, 20,
            #                                                   str(self.time).zfill(4))
            start_time = datetime.datetime(self.date // 10000, self.date % 10000 // 100, self.date % 100, self.time // 100, self.time % 100)
            end_time = start_time + datetime.timedelta(0, 1800)
            target_form = {"StartTime": start_time.strftime('%H:%M:%S'), "EndTime": end_time.strftime('%H:%M:%S'), "TargetQty": str(target_vol[stk])}
            item = {
                'portfolio': str(self.portfolio_id),
                'symbol': stk,
                'target': target_form
            }
            content.append(item)
        return content  # {'command': 'TARGET', 'content': content}

    def holding_info_update(self, holding):
        self.total_holding_info[self.time] = holding.copy()
        holding = holding.set_index('Symbol')
        if self.time == 1000:
            # TODO 分离930和7个bar
            holding_change = holding.drop('PortfolioNO', axis=1) - self.total_holding_info[930].set_index('Symbol').drop('PortfolioNO', axis=1)
            holding_930_strategy = self.app930.holding_info[930].set_index('Symbol').drop('PortfolioNO', axis=1).reindex(self.involved_instance).fillna(0) + holding_change
            self.app930.time = 1000
            self.app930.pre_time = 930
            self.app930.holding_info_update(holding_930_strategy.fillna(0).reset_index())
            # self.app930.barly_output()
            self.app930.output_daily_summary()
        holding_930 = self.app930.holding_info[1000].set_index('Symbol')
        holding[holding_930.columns] -= holding_930
        ############################old
        self.holding_info[self.time] = holding.reset_index()
        holding_df = holding.copy()
        holding_df['NetPosition'] = holding_df['NetPosition'].astype(float)
        holding_df = holding_df[holding_df['NetPosition'] > 0]

        unioin_stk_list = list(set(holding_df.index).union(set(self.holding.keys())))
        current_holding = holding_df['NetPosition'].reindex(unioin_stk_list).fillna(0)
        pre_holding = pd.Series(self.holding).reindex(unioin_stk_list).fillna(0)
        holding_change = current_holding - pre_holding
        for each in holding_change.index:
            if holding_change[each] > 0 and each not in self.buy_time_info:
                self.buy_time_info[each] = (self.date, self.pre_time)
            if holding_change[each] < 0 and current_holding[each] == 0 and each in self.buy_time_info:
                self.buy_time_info.pop(each)
        # 在T-1个bar执行导致T个bar完成的仓位变化
        if not os.path.exists(f'{daily_out_path}{self.date}/'):
            os.mkdir(f'{daily_out_path}{self.date}/')
        pd.to_pickle(holding_change, f'{daily_out_path}{self.date}/holding_change_{self.time}.pkl')
        self.holding = holding_df['NetPosition']
        if set(self.holding.keys()) != set(self.buy_time_info.keys()).intersection(set(self.holding.keys())):
            self.log('Holding keys and buy time info are not match')
            raise Exception('Holding keys and buy time info are not match')
        self.available = holding_df['SellAvailable'][holding_df['SellAvailable'] > 0]
        total_buy_amt, total_sell_amt = holding[['TotalBuyAmount', 'TotalSellAmount']].sum().tolist()
        self.barly_buy_amt[self.time], self.barly_sell_amt[
            self.time] = total_buy_amt - self.total_buy_amt, total_sell_amt - self.total_sell_amt
        self.total_buy_amt, self.total_sell_amt = total_buy_amt, total_sell_amt
        self.cash += self.barly_sell_amt[self.time] - self.barly_buy_amt[self.time]
        return True

    def output_daily_summary(self):
        buy_time_info = {}
        for each in self.buy_time_info:
            date, time = self.buy_time_info[each][:2]
            if each in self.holding or date == self.date:
                buy_time_info[each] = self.buy_time_info[each]
        # pd.to_pickle(buy_time_info,buy_time_info_path+'%d.pkl'%self.date)
        res = {
            'stk_list': self.stk_list,
            'stk_list_with_over_night': self.pool_with_over_night_stk,
            'barly_holding_info': self.holding_info,
            'barly_total_holding_info': self.total_holding_info,
            'barly_sell_amt': self.barly_sell_amt,
            'barly_buy_amt': self.barly_buy_amt,
            'sell_order_record': self.sell_order_record,
            'buy_order_record': self.buy_order_record,
            'pred_ret': self.pred_ret,
            'signal': self.signal,
            'buy_time_info': buy_time_info,
            'fix_factor': self.factor[self.time],
            '5min_factor': self.factor_5min[self.time],
            'last_bar_initial_cash': self.cash,
        }
        pd.to_pickle(res, local_config_path + 'daily_output/%d.pkl' % self.date)

    def barly_output(self):
        res = {
            'stk_list': self.stk_list,
            'stk_list_with_over_night': self.pool_with_over_night_stk,
            'barly_holding_info': self.holding_info[self.time],
            'barly_total_holding_info': self.total_holding_info[self.time],
            'barly_sell_amt': self.barly_sell_amt[self.time],
            'barly_buy_amt': self.barly_buy_amt[self.time],
            'sell_order_record': self.sell_order_record[self.time],
            'buy_order_record': self.buy_order_record[self.time],
            'pred_ret': self.pred_ret[self.time],
            'signal': self.signal[self.time],
            'buy_time_info': self.buy_time_info,
            'bar_inital_cash': self.cash,
            'fix_factor': self.factor,
            '5min_factor': self.factor_5min
        }
        if not os.path.exists(f'{local_config_path}daily_output/{str(self.date)}/'):
            os.mkdir(f'{local_config_path}daily_output/{str(self.date)}/')
        pd.to_pickle(res, f'{local_config_path}daily_output/{str(self.date)}/{str(self.time)}_summary.pkl')

