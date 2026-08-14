# @Time : 2020/12/2 21:23
# @Author : Zhichen Lu
# @File : LimitHoldingAndAssignedDistribut.py

from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, EvaluationHelper
import pandas as pd

class LimitHoldingAndAssignedDistribut(PortfolioStrategyBase):
    def __init__(self, signal, start=20140101, end=20181231, stock_pool=None, target_point=None, buy_cost=0.001, sell_cost=0.001, per_amt=500000, append_param={}, max_holding=600,
                 distribution=None):
        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost, per_amt, append_param=append_param)
        self.signal = signal.reindex(self.close.index)
        self.data_flow['signal'] = None
        self.last_buy_time = {}
        self.max_holding_num = max_holding
        if distribution is None:
            distribution = pd.DataFrame(1,index=self.date_list,columns=self.trading_point)
        elif isinstance(distribution,pd.DataFrame):
            distribution = distribution.reindex(self.date_list,axis=0).reindex(self.trading_point,axis=1)
            col_sum = distribution.sum(axis=1)
            distribution = (distribution.T/col_sum).T
            distribution.loc[col_sum[col_sum.eq(0)].index] = 1./len(self.trading_point)
        else:
            raise Exception('Wrong distribution type')
        self.distribution = distribution

    def sell_action(self, stk, vol=None):
        if stk not in self.last_buy_time:
            raise Exception('Last buy time is not recorded')
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) > 1 or ((bar_date_idx - date_idx) == 1 and bar_time == time_point):
            self.sell(stk, vol)

    def buy_action(self, stk, vol=None):
        deal_vol,_ = self.buy(stk, vol)
        if deal_vol > 0:
            self.last_buy_time[stk] = self.datetime
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
        self.data_flow['distribution'] = self.distribution[self.date_idx:self.date_idx + 1].T[date]
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

        for stk in sell_stk:
            self.sell_action(stk)
        holding_num = len(self.holding)
        if holding_num >= self.max_holding_num:
            return
        trigget_num = min(len(trigger_stk),int(self.max_holding_num*self.data_flow['distribution'][time_point]))
        if (holding_num + trigget_num) > self.max_holding_num:
            trigget_num = self.max_holding_num - holding_num

        bough_num = 0
        trigger_stk = signal[list(trigger_stk)].sort_values(ascending=False).index.tolist()
        for stk in trigger_stk:
            if stk not in self.holding:
                _ = self.buy_action(stk)
                bough_num += 1
            if bough_num >= trigget_num:
                break
