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

from dataApi.FixFactorRollPrepare import load_fix_data

s = FactorData()


class StockEnv(gym.Env):

    def __init__(self, start=20190101, end=20190630, stock_pool=None, target_point=[1000, 1030, 1100, 1300, 1330, 1400, 1430],
                 buy_cost=0.001, sell_cost=0.001, per_amt_ratio=0.0025, append_param={}, initial_cash=200000000, barly_max_buy=100,
                 deal_percent=0.1, stk_min_amt=None):
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

        stk_list = stock_pool.columns.tolist()

        close = get_minute_pickle('close', date_list=get_date_range(date_list[0], date_list[-1]), code_list=stock_pool.columns.tolist())
        pause = get_daily_1factor('pause', date_list=date_list, code_list=stk_list).fillna(False)
        flatten = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/DataForTplusN/open_flatten.pkl').loc[date_list, stk_list]

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
        self.episode = 0
        self.reset()
        if stk_min_amt is None:
            self.stk_min_amt = self.per_amt * 0.2
        else:
            self.stk_min_amt = stk_min_amt
        print('min_stk_amt', self.stk_min_amt)

    def reset(self):
        self.start = True
        self.episode += 1
        self.last_buy_time = {}
        self.cash = self.initial_money
        self.accout_value = [self.initial_money]
        self.account_index = []
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
        historical_future_vol = pd.Series(np.inf, index=signal.index)
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
        if np.isnan(vol) or vol == 0:
            return 0, deal_price
        vol = min(vol, int(self.bar_actual_future_vol[stk] // 100 * 100))

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

    def step(self, action):

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
        print(f'{next_point}|cash:{self.cash}|equity:{cap}|total:{self.cash + cap}|step profit:{((self.cash + cap) / self.accout_value[-1] - 1) * 100:.2f}')
        self.accout_value.append(self.cash + cap)
        self.account_index.append((self.date, self.trading_point[self.bar_idx]))
        print('account_vol:', self.accout_value[-1])
        return (self.cash + cap) / self.accout_value[-1] - 1

    def render(self, mode='human'):
        pass


import time


def main():
    e = time.time()
    test_env = StockEnv(end=20190130)
    init_time = time.time() - e
    print('init_time:', init_time)
    account_memory = []
    actions_memory = []
    test_env.reset()
    signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_lightGBM_CatBoostWithMax5threshold_0.05.pkl')
    signal = signal.loc[test_env.date_list[0]:test_env.date_list[-1]]
    pred_ret = pred_ret.loc[test_env.date_list[0]:test_env.date_list[-1]]
    pred_ret[~signal] = np.nan
    for idx, cell in enumerate(signal.index.tolist()):
        day, point = cell
        action = signal.iloc[idx]
        reward = test_env.step(action)



# git config –-global http.postBuffer 524288000
main()

