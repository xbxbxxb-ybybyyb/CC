# @Time : 2021/6/4 10:36
# @Author : Zhichen Lu
# @File : FixEnv.py
import numpy as np
import pandas as pd
from gym.utils import seeding
import gym
from gym import spaces
import matplotlib
from StrongStockModel.conf.path_config import root_path, deal_price_path
from StrongStockModel.dataApi.getData import get_date_range, get_daily_1stock, get_minute_1factor, get_daily_1factor, get_minute_pickle
from StrongStockModel.dataApi.stockList import clean_stock_list
from StrongStockModel.dataApi.tradeDate import trade_minutes, get_trade_date_interval, get_date_range
from tqdm import tqdm
from multiprocessing import Pool, Manager
import gc, os
import time, datetime
from xquant.factordata import FactorData
from copy import deepcopy
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv

from dataApi.FixFactorRollPrepare import load_fix_data, feature_engineering

s = FactorData()


def load_factor(date, factor_list):
    X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(date, date, factor_list=factor_list)
    X, y, idx_date, idx_time, idx_code = feature_engineering(X, y, nolimit, idx_date, idx_time, idx_code)
    index = pd.MultiIndex.from_tuples(list(zip(idx_date.tolist(), idx_time.tolist(), idx_code.tolist())))
    factor = pd.DataFrame(X, index=index, columns=factor_list)
    return factor, pd.Series(y, index=index)


class StockEnv(gym.Env):

    def __init__(self, start=20170101, end=20191231, stk_list=None, stock_pool=None, target_point=[1000, 1030, 1100, 1300, 1330, 1400, 1430],
                 buy_cost=0.001, sell_cost=0.001, per_amt_ratio=0.0025, append_param={}, initial_cash=200000000, barly_max_buy=100,
                 deal_percent=0.1, stk_min_amt=None, eval_indicator='ic_t', reward_type='total_return'):
        date_list = list(map(int, s.tradingday(str(start), str(end))))
        start, end = date_list[0], date_list[-1]
        if stock_pool is None:
            stock_pool = pd.read_pickle(root_path + 'stock_pool_without_limit_up_down.pkl').shift(1)
            if start >= stock_pool.index[0] and end <= stock_pool.index[-1]:
                stock_pool = stock_pool.loc[start:end]
            else:
                raise Exception('No Available Stock Pool')
        if set(date_list) != set(stock_pool.index):
            stock_pool = stock_pool.reindex(date_list)
        if stk_list is None:
            stk_list = stock_pool.columns.tolist()
        else:
            stock_pool = stock_pool.reindex(stk_list, axis=1)
        close = get_minute_1factor('close', date_list[0], date_list[-1], code_list=stock_pool.columns.tolist())
        pause = get_daily_1factor('pause', date_list=date_list, code_list=stk_list).fillna(False)
        flatten = 0  # pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/DataForTplusN/open_flatten.pkl').loc[date_list, stk_list]

        if os.path.exists(deal_price_path + 'deal_price%d_%d.pkl' % (start, end)) and 'deal_price_path' not in append_param:
            deal_price = pd.read_pickle(deal_price_path + 'deal_price%d_%d.pkl' % (start, end))
        elif 'deal_price_path' in append_param:
            print('load from', append_param['deal_price_path'])
            deal_price = pd.read_pickle(append_param['deal_price_path']).loc[start:end]
        else:
            deal_price = close.rolling(10).mean().shift(-10)
            deal_price.to_pickle(deal_price_path + 'deal_price%d_%d.pkl' % (start, end))
        deal_price = deal_price.shift(1).swaplevel(0, 1).loc[target_point].swaplevel(0, 1)
        close = close.shift(1).swaplevel(0, 1).loc[target_point].swaplevel(0, 1)
        factor_evaluation = pd.read_pickle(f'{root_path}external_data/moon_v2/{eval_indicator}.pkl')
        using_fix_list = pd.read_pickle('/data/group/800319/strategy_local_path3/available_factor_list.pkl')
        inter_col = list(set(factor_evaluation.columns.tolist()).intersection(set(using_fix_list)))
        factor_evaluation = factor_evaluation[inter_col]
        target_date = max(list(filter(lambda x: x < start, factor_evaluation.index.tolist())))
        if 'ret' in eval_indicator:
            print('ret')
            factor_evaluation = factor_evaluation.loc[target_date].sort_values(ascending=False)
        elif 'ic' in eval_indicator:
            print('ic')
            factor_evaluation = factor_evaluation.loc[target_date].apply(abs).sort_values(ascending=False)
        else:
            raise Exception('')
        factor_list = factor_evaluation.index.tolist()[:100]

        self.factor_list = factor_list
        self.date_list = date_list
        self.stock_pool = stock_pool
        self.trading_point = target_point
        self.stk_list = stk_list
        self.daily_info = {x: get_daily_1factor(x, date_list=self.date_list, code_list=self.stk_list) for x in
                           ['close', 'close_badj']}  # get_daily_1stock(stk, ['close', 'close_badj'], self.date_list)
        self.daily_info['close_padj'] = self.daily_info['close'].shift(-1) * self.daily_info['close_badj'] / self.daily_info['close_badj'].shift(-1)
        self.daily_info['adj_ratio'] = self.daily_info['close'] / self.daily_info['close_padj']
        self.pre_dail_info = {x: self.daily_info[x].shift(1) for x in self.daily_info}
        self.untradable_pool = (pause + flatten) > 0

        self._step = len(self.trading_point)
        self.close = close
        self.deal_price = deal_price
        self.data_flow = {'close': None, 'deal_price': None}
        self.buy_cost = buy_cost
        self.sell_cost = sell_cost

        self.daily_high = get_daily_1factor('high', self.date_list, self.stk_list)
        self.daily_low = get_daily_1factor('low', self.date_list, self.stk_list)
        self.initial_money = initial_cash
        self.per_amt_ratio = per_amt_ratio
        self.barly_max_buy = barly_max_buy
        self.future_30_min_vol = pd.read_pickle(deal_price_path + 'vol_future_rolling_30_sum.pkl').reindex(self.close.index)
        self.daily_info['pre_close'] = self.daily_info['close'] * self.daily_info['close_badj'].shift(1) / self.daily_info['close_badj']
        self.deal_percent = deal_percent
        #############

        #############Gym Parameter
        self.episode = 0
        self.state_space = (len(self.stk_list), len(self.factor_list))
        self.action_space = spaces.Box(low=-0.1, high=0.1, shape=(self.stk_list.__len__(),))
        self.observation_space = spaces.Box(
            low=-6, high=6, shape=self.state_space)
        self.reset()

        if stk_min_amt is None:
            self.stk_min_amt = self.per_amt * 0.2
        else:
            self.stk_min_amt = stk_min_amt
        self.reward_type = reward_type

    def get_multiproc_env(self, n=10):
        def get_self():
            return deepcopy(self)

        e = SubprocVecEnv([get_self for _ in range(n)], start_method="fork")
        obs = e.reset()
        return e, obs

    def reset(self):
        self.start = True
        self.episode += 1
        self.last_buy_time = {}
        self.cash = self.initial_money
        self.accout_value = [self.initial_money]
        self.account_index = [(self.date_list[0], 1000)]
        self.day_end = [self.initial_money]
        self.daily_profit = [np.nan]
        self.cash_series = pd.Series(np.nan, index=self.date_list)
        self.holding_value = pd.Series(np.nan, index=self.date_list)
        self.holding_num = pd.Series(np.nan, index=self.date_list)
        self.per_amt = round(self.initial_money * self.per_amt_ratio, -5)
        self.holding = {}
        self.available = {}
        self.evaluation_result = {}
        self.order_info = {}

        self.daily_holding = {}
        self.daily_buy_time_info = {}
        self.daily_conf = {}

        self.pre_date_idx, self.pre_date = None, None
        self.date, self.date_idx = None, None
        self.bar_idx = None
        self.datetime = ()
        self.update_state((self.date_list[0], 1000))

        return self.state

    def base_daily_update(self, idx, date):
        self.pre_date_idx, self.pre_date = self.date_idx, self.date
        self.date_idx, self.date = idx, date
        self.data_flow['close'] = self.close[self.date_idx * self._step:(self.date_idx + 1) * self._step]
        self.data_flow['deal_price'] = self.deal_price[self.date_idx * self._step:(self.date_idx + 1) * self._step]

        if self.pre_date is None:
            return
        pre_close_padj, pre_close, pre_adj_ratio = self.pre_dail_info['close_padj'][self.date_idx:self.date_idx + 1].T[date], \
                                                   self.pre_dail_info['close'][self.date_idx:self.date_idx + 1].T[date], \
                                                   self.pre_dail_info['adj_ratio'][self.date_idx:self.date_idx + 1].T[date]
        for stk in self.holding:
            holding = self.holding[stk]
            stk_close_padj, stk_close, stk_adj_ratio = pre_close_padj[stk], pre_close[stk], pre_adj_ratio[stk]
            available = self.available[stk] if stk in self.available else 0
            if holding > 0:
                if abs(1 - stk_adj_ratio) > 0.0001:
                    holding = holding * stk_adj_ratio
                    self.holding[stk] = holding
                self.available[stk] = holding

    def daily_update(self, idx, date):
        self.base_daily_update(idx, date)
        # VolConsider
        ####################
        self.data_flow['actual_future_vol'] = self.future_30_min_vol[self.date_idx * self._step:(self.date_idx + 1) * self._step]
        # 不在股票池里的股票
        date_pool = self.stock_pool[self.date_idx:self.date_idx + 1].T[date]
        date_pool = pd.Series(date_pool.tolist(), index=date_pool.index.tolist())
        date_pool = date_pool[~date_pool]
        # 停牌、一字板的股票
        not_tradable = self.untradable_pool[self.date_idx:self.date_idx + 1].T[self.date]

        self.data_flow['not_tradable'] = set(not_tradable[not_tradable].index.tolist())
        self.data_flow['not_available'] = set(date_pool.index.tolist())
        self.data_flow['daily_high'] = self.daily_high[self.date_idx:self.date_idx + 1].T[self.date]
        self.data_flow['daily_low'] = self.daily_low[self.date_idx:self.date_idx + 1].T[self.date]
        self.data_flow['pre_close'] = self.daily_info['pre_close'][self.date_idx:self.date_idx + 1].T[self.date]

    def bar_handler(self, signal):
        date, time_point, date_idx, time_idx = self.datetime
        signal = signal.dropna()
        trigger_stk = set(signal.index)
        # 盘中涨跌停
        bar_close = self.data_flow['close'][time_idx:time_idx + 1].T[(date, time_point)]
        # 可卖出股票 = 持仓股票剔除 停牌and一字板
        avaliable_stk = set(self.available.keys())
        #############
        available_close = bar_close[list(avaliable_stk)]
        limit_down_judge = ((available_close.values / self.data_flow['pre_close'][list(avaliable_stk)].values - 1) <= -0.098) & (
                available_close.values == self.data_flow['daily_low'][list(avaliable_stk)].values)
        limit_down_judge = pd.Series(limit_down_judge, index=list(avaliable_stk))
        limit_up_judge = ((available_close.values / self.data_flow['pre_close'][list(avaliable_stk)].values - 1) >= 0.098) & (
                available_close.values == self.data_flow['daily_high'][list(avaliable_stk)].values)
        limit_up_judge = pd.Series(limit_up_judge, index=list(avaliable_stk))
        avaliable_stk = set(limit_down_judge[~(limit_down_judge | limit_up_judge)].index.tolist())
        ##########
        avaliable_stk = avaliable_stk - self.data_flow['not_tradable']
        avaliable_trigger_stk = avaliable_stk.intersection(trigger_stk)
        sell_stk = list(avaliable_stk - trigger_stk)
        # 可买入股票 = 触发股票 剔除 不在股票池的股票 以及 有持仓个股
        trigger_stk = trigger_stk - self.data_flow['not_available']  # print({str(x).zfill(6)+'.SZ' if x <400000 else str(x)+'.SH' for x in trigger_stk})
        trigger_stk = list(trigger_stk - set(self.holding.keys()))
        # historical_future_vol = round(self.data_flow['past_future_vol'][time_idx:time_idx + 1].T[(date, time_point)] * self.deal_percent, -2)
        historical_future_vol = pd.Series(np.inf, index=self.stk_list)
        for stk in avaliable_trigger_stk:
            self.holding_another_round(stk)

        if self.cash < self.per_amt:
            not_buy = True
            for stk in sell_stk:
                sell_vol = min(historical_future_vol[stk], self.holding[stk])
                self.sell_action(stk, sell_vol)
            return
        elif trigger_stk:
            not_buy = False
            target_close = bar_close[trigger_stk]
            limit_up_judge = ((target_close.values / self.data_flow['pre_close'][trigger_stk].values - 1) >= 0.098) & (
                    target_close.values == self.data_flow['daily_high'][trigger_stk].values)
            limit_up_judge = pd.Series(limit_up_judge, index=trigger_stk)
            trigger_stk = limit_up_judge[~limit_up_judge].index.tolist()
            target_vol = round(self.per_amt / target_close, -2)
            orderable_vol = pd.concat([target_vol, historical_future_vol[list(trigger_stk)]], axis=1).min(axis=1)
            orderable_vol = pd.DataFrame({'target': target_vol, 'orderable': orderable_vol})
            target_vol = orderable_vol['orderable']
            target_vol = target_vol // 100 * 100
            orderable_vol['sent_order'] = target_vol
            target_amt = target_vol * target_close
            target_amt = target_amt.loc[signal[trigger_stk].sort_values(ascending=False).index.tolist()]
            target_amt = target_amt[target_amt >= self.stk_min_amt]
            target_amt = target_amt[target_amt.cumsum() < self.cash]
            trigger_stk = target_amt.index.tolist()
            trigger_num = min(len(trigger_stk), int(self.cash // self.per_amt), self.barly_max_buy)
            trigger_stk = trigger_stk[:trigger_num]
            target_vol = target_vol[trigger_stk]
            orderable_vol = orderable_vol.T[target_vol.index].T
        else:
            target_vol = pd.Series()
            orderable_vol = pd.DataFrame()

        for stk in sell_stk:  # to_sell = set(sell_stk)
            sell_vol = min(historical_future_vol[stk], self.holding[stk])
            self.sell_action(stk, sell_vol)
        # sold = to_sell - {x for x in self.holding}

        deal_list = []
        for stk in target_vol.index:
            if stk in self.holding:
                raise Exception('Buying a holding stock')
            deal_vol = self.buy_action(stk, target_vol[stk])
            deal_list.append(deal_vol)
        orderable_vol['deal_vol'] = deal_list
        self.order_info[self.datetime[:2]] = orderable_vol

    def holding_another_round(self, stk):
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) == 1 and bar_time == time_point:
            self.last_buy_time[stk] = self.datetime

    def trade(self, stk):
        return self.bar_dealprice[stk]

    def isinpool(self, stk):
        bool_val = self.stock_pool[self.date_idx:self.date_idx + 1][stk].tolist()[0]
        return bool_val

    def sell_action(self, stk, vol=None):
        if stk not in self.last_buy_time:
            raise Exception('Last buy time is not recorded')
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) > 1 or ((bar_date_idx - date_idx) == 1 and bar_time >= time_point):
            vol, deal_price = self.sell(stk, vol)
            if vol > 0:
                if not np.isnan(deal_price):
                    self.cash += vol * deal_price * (1 - self.sell_cost)
                else:
                    raise Exception('Unexpected')

    def buy_action(self, stk, vol=None):
        deal_vol, deal_price = self.buy(stk, vol)
        if deal_vol > 0:
            if not np.isnan(deal_price):
                self.last_buy_time[stk] = self.datetime
                self.cash -= deal_vol * deal_price * (1 + self.buy_cost)
            else:
                raise Exception('Unexpected')
        if (stk in self.holding) and (stk not in self.last_buy_time):
            raise Exception('Wrong')
        return deal_vol

    def buy(self, stk, vol=None, amt=None):
        if not self.isinpool(stk):
            """
            不在股票池内时不可买
            """
            return 0, np.nan
        if stk in self.holding:
            holding = self.holding[stk]
        else:
            holding = 0

        if stk in self.available:
            available = self.available[stk]
        else:
            available = 0
        deal_price = self.trade(stk)  # self.bar_dealprice[stk]
        if deal_price == 0 or np.isnan(deal_price):
            return 0, np.nan
        if vol is None and amt is None:
            vol = round(self.per_amt / deal_price, -2)
        elif vol is None:
            vol = round(amt / deal_price, -2)
        elif amt is None:
            pass
        else:
            raise Exception('One of amt and vol must be not None')

        vol = min(vol, int(self.bar_actual_future_vol[stk] // 100 * 100))
        if np.isnan(vol) or vol == 0:
            return 0, deal_price
        holding += vol
        self.holding[stk], self.available[stk] = holding, available
        # if stk not in self.record:
        #     self.record[stk] = [[self.datetime[0], self.datetime[1], 'B', vol, deal_price, holding, available]]
        # else:
        #     record = self.record[stk]
        #     record.append([self.datetime[0], self.datetime[1], 'B', vol, deal_price, holding, available])
        #     self.record[stk] = record
        return vol, deal_price

    def sell(self, stk, vol=None):
        available = self.available[stk]
        holding = self.holding[stk]
        if vol is None:
            vol = available
        else:
            vol = min(vol, available)
        if vol == 0 or np.isnan(vol):
            return 0, np.nan
        deal_price = self.trade(stk)
        if deal_price == 0 or np.isnan(deal_price):
            return 0, np.nan
        vol = min(vol, int(self.bar_actual_future_vol[stk] // 100 * 100))
        holding -= vol
        available -= vol
        if holding > 0:
            self.holding[stk] = holding
        else:
            del self.holding[stk]
        if available > 0:
            self.available[stk] = available
        else:
            del self.available[stk]
        # if stk not in self.record:
        #     raise Exception('Sell without record')
        # else:
        #     record = self.record[stk]
        #     record.append([self.datetime[0], self.datetime[1], 'S', -vol, deal_price, holding, available])
        #     self.record[stk] = record
        return vol, deal_price

    def step(self, action_pred_ret):
        # print(f'action {action}')
        # print(list(action))
        action = action_pred_ret.copy()
        action[action < 0.05] = np.nan
        if isinstance(action, pd.Series):
            pass
        elif isinstance(action, np.ndarray):
            action = pd.Series(action, index=self.stk_list)
        else:
            raise Exception('Unexpected action type')
        if self.start:
            self.bar_idx = 0
        else:
            self.bar_idx = (self.bar_idx + 1) % 7

        if self.bar_idx == 0:
            if self.start:
                date_idx = 0
            else:
                date_idx = self.date_idx + 1
            date = self.date_list[date_idx]
            self.daily_update(date_idx, date)
        self.start = False
        time_point = self.trading_point[self.bar_idx]
        self.terminal = self.date == self.date_list[-1] and time_point == 1430

        self.bar_dealprice = self.data_flow['deal_price'][self.bar_idx:self.bar_idx + 1].T[(self.date, time_point)]
        self.bar_actual_future_vol = self.data_flow['actual_future_vol'][self.bar_idx:self.bar_idx + 1].T[(self.date, time_point)] * self.deal_percent
        self.datetime = (self.date, time_point, self.date_idx, self.bar_idx)
        self.bar_point = self.date_idx * self._step + self.bar_idx
        self.bar_handler(action)

        holding = pd.Series(self.holding)

        if self.bar_idx == (len(self.trading_point) - 1):
            close = self.daily_info['close'].iloc[self.date_idx][holding.index]
            next_point = (self.date, 1500)
        else:
            close = self.data_flow['close'][self.bar_idx + 1:self.bar_idx + 2].T[(self.date, self.trading_point[self.bar_idx + 1])][holding.index]
            next_point = (self.date, self.trading_point[self.bar_idx + 1])
        cap = (close * holding).sum()
        self.accout_value.append(self.cash + cap)
        self.account_index.append(next_point)
        # print('account_vol:', self.accout_value[-1])
        label_reward = self.update_reward()
        infos = {'future_label': label_reward}
        print(f'episode:{self.episode}|{next_point}|cash:{self.cash}|equity:{cap}|'
              f'reward:{self.reward}|total:{self.cash + cap}|step profit:{((self.cash + cap) / self.accout_value[-2] - 1) * 100:.2f}')

        if not self.terminal:
            self.update_state(next_point)

        days = (self.accout_value.__len__() - 1) // 7
        if (self.accout_value.__len__() - 1) % 7 > 0:
            days += 1
            if len(self.day_end) == days:
                self.day_end.append(self.accout_value[-1])
                self.daily_profit.append(self.day_end[-1] / self.day_end[-2] - 1)
        self.day_end[days] = self.accout_value[-1]
        self.daily_profit[days] = self.day_end[-1] / self.day_end[-2] - 1

        # print(self.total_return(), self.annual_return(), self.volatility(), self.sharpe())

        return self.state, self.reward, self.terminal, infos

    def total_return(self):
        total_return = self.accout_value[-1] / self.accout_value[0] - 1
        return total_return

    def annual_return(self):
        return (self.accout_value[-1] / self.accout_value[0]) ** (244. / len(self.day_end[:-1])) - 1

    def sharpe(self):
        daily_ret = np.array(self.daily_profit)
        std_ = np.nanstd(daily_ret)
        if std_ == 0:
            std_ += 0.01
        return (np.nanmean(daily_ret) / (std_)) * (244 ** 0.5)

    def volatility(self):
        return -np.nanstd(self.daily_profit) * (244 ** 0.5)

    def update_reward(self):
        if self.reward_type == 'volatility':
            reward = self.volatility()
        elif self.reward_type == 'sharpe':
            reward = self.sharpe()
        elif self.reward_type == 'annual_return':
            reward = self.annual_return()
        elif self.reward_type == 'total_return':
            reward = self.total_return()
        else:
            raise Exception('Unexpected Reward Function')
        self.reward = reward.copy()
        return self.reward_label.copy()

    def update_factor(self, date):
        self.factor, self.label = load_factor(date=date, factor_list=self.factor_list)
        self.factor = self.factor.loc[date]
        self.label = self.label.loc[date]

    def update_state(self, date_time):
        date, time_point = date_time
        if time_point == 1500:
            date = self.date_list[self.date_list.index(date) + 1]
            time_point = 1000
        if date != self.date:
            self.update_factor(date)
        self.state = self.factor.loc[time_point].reindex(self.stk_list).fillna(0)
        self.reward_label = self.label.loc[time_point].reindex(self.stk_list).fillna(0)

    def render(self, mode='human'):
        return self.state


import time


def main():
    e = time.time()
    test_env = StockEnv(start=20170101, end=20170130)
    init_time = time.time() - e
    print('init_time:', init_time)
    account_memory = []
    actions_memory = []
    test_env.reset()
    signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_lightGBM_CatBoostWithMax5threshold_0.05.pkl')
    signal = signal.loc[test_env.date_list[0]:test_env.date_list[-1]]
    pred_ret = pred_ret.loc[test_env.date_list[0]:test_env.date_list[-1]]
    pred_ret[~signal] = np.nan
    for idx, cell in enumerate(pred_ret.index.tolist()):
        day, point = cell
        action = pred_ret.iloc[idx]
        state, reward, terminal, _ = test_env.step(action)
    print(terminal)

#
# start = time.time()
# main()
# total = time.time() - start
# print(f'sample one time take {total} second')
