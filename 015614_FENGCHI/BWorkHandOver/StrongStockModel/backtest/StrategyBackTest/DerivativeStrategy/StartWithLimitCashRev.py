# @Time : 2020/12/15 9:19
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py

from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, InitailCashBasedEvaluationHelper
from tqdm import tqdm
import gc
import pandas as pd
import numpy as np

class StartWithLimitCash(PortfolioStrategyBase):
    def __init__(self, signal, start=20140101, end=20181231, stock_pool=None, target_point=None,
                 buy_cost=0.001, sell_cost=0.001, per_amt_ratio=0.0025, append_param={}, initial_cash=200000000,barly_max_buy=100):
        per_amt = round(initial_cash*per_amt_ratio,-5)
        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost, per_amt, append_param=append_param)
        self.signal = signal.reindex(self.close.index)
        self.data_flow['signal'] = None
        self.last_buy_time = {}
        self.cash = initial_cash
        self.accout_value = initial_cash
        self.per_amt_ratio = per_amt_ratio
        self.barly_max_buy = barly_max_buy
        self.cash_series = pd.Series(np.nan,index=self.date_list)
        self.holding_value = pd.Series(np.nan,index=self.date_list)


    def sell_action(self, stk, vol=None):
        if stk not in self.last_buy_time:
            raise Exception('Last buy time is not recorded')
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) > 1 or ((bar_date_idx - date_idx) == 1 and bar_time == time_point):
            vol, deal_price = self.sell(stk, vol)
            if vol>0:
                if not np.isnan(deal_price):
                    self.cash += vol*deal_price*(1-self.sell_cost)
                else:
                    raise Exception('Unexpected')
    def buy_action(self, stk, vol=None):
        deal_vol,deal_price = self.buy(stk, vol)
        if deal_vol > 0:
            if not np.isnan(deal_price):
                self.last_buy_time[stk] = self.datetime
                self.cash -= deal_vol*deal_price*(1+self.buy_cost)
            else:
                raise Exception('Unexpected')
        return deal_vol

    def holding_another_round(self,stk):
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) == 1 and bar_time == time_point:
            self.last_buy_time[stk] = self.datetime

    def daily_update(self, idx, date):
        super().daily_update(idx, date)
        self.data_flow['signal'] = self.signal[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        date_pool = self.stock_pool[self.date_idx:self.date_idx + 1].T[date]
        date_pool = date_pool[~date_pool]
        self.data_flow['not_available'] = set(date_pool.index.tolist())
        if self.data_flow['signal'].index[0][0] != self.date or self.data_flow['signal'].index[-1][0] != self.date:
            raise Exception('Broadcast date and signal date are not match!')

    def bar_handler(self):
        date, time_point, date_idx, time_idx = self.datetime
        signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
        signal = signal.dropna()
        trigger_stk = set(signal.index)
        avaliable_stk = set(self.available.keys()) - self.data_flow['not_available']
        avaliable_trigger_stk = avaliable_stk.intersection(trigger_stk)
        sell_stk = avaliable_stk - trigger_stk
        trigger_stk = trigger_stk - self.data_flow['not_available']

        for stk in avaliable_trigger_stk:
            self.holding_another_round(stk)

        if self.cash<self.per_amt:
            for stk in sell_stk:
                self.sell_action(stk)
            return

        for stk in sell_stk:
            self.sell_action(stk)

        if self.cash<self.per_amt:
            return

        trigger_num = min(len(trigger_stk),int(self.cash//self.per_amt),self.barly_max_buy)
        trigger_stk = signal[list(trigger_stk)].sort_values(ascending=False).index.tolist()[:trigger_num]

        for stk in trigger_stk:
            if stk not in self.holding:
                _ = self.buy_action(stk)

    def run_backtest(self, kernel=10):
        self.re_initial()
        bar = tqdm(self.date_list)
        for date_idx, date in enumerate(bar):
            bar.set_description('%d | holding:%d'%(date,len(self.holding)))
            self.daily_update(date_idx, date)
            for time_idx, time_point in enumerate(self.trading_point):
                try:
                    self.bar_dealprice = self.data_flow['deal_price'][time_idx:time_idx + 1].T[(date, time_point)]
                except:
                    raise Exception(' ')
                self.datetime = (date, time_point, date_idx, time_idx)
                self.bar_point = date_idx * self.step + time_idx
                self.bar_handler()
                # print(self.datetime)
            self.cash_series[self.date] = self.cash
            daily_close = self.daily_info['close'][self.date_idx:self.date_idx+1].T[self.date][list(self.holding.keys())]
            self.accout_value = (daily_close*pd.Series(self.holding)).sum() + self.cash
            self.holding_value[self.date] = self.accout_value
            self.per_amt = round(self.accout_value*self.per_amt_ratio,-5)
        record = list(self.record.keys())
        for each in record:
            self.record[each] = pd.DataFrame(self.record[each], columns=['date', 'time', 'flag', 'vol', 'deal_price', 'holding', 'available']).set_index(['date', 'time'])
        gc.collect()
        return self.record._getvalue()


