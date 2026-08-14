# @Time : 2020/10/28 9:09
# @Author : Zhichen Lu
# @File : LimitedPorfolio.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, EvaluationHelper
import pandas as pd
import os
from dataApi.tradeDate import get_desample_minute_dict
import numpy as np
from xquant.compute.aimr import AIMR


class SignalBasedPortfolioLimitUp(PortfolioStrategyBase):

    def __init__(self, signal, start=20140101, end=20181231, stock_pool=None, target_point=None, buy_cost=0.001, sell_cost=0.001, max_holding=600, daily_max_buy=400):
        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost)
        self.signal = signal.reindex(self.close.index)
        self.data_flow['signal'] = None
        self.last_buy_time = {}
        self.max_holding_num = max_holding
        self.daily_max_buy_num = daily_max_buy

    def sell_action(self, stk, vol=None):
        if stk not in self.last_buy_time:
            raise Exception('Last buy time is not recorded')
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) > 1 or ((bar_date_idx - date_idx) == 1 and bar_time >= time_point):
            self.sell(stk, vol)

    def buy_action(self, stk, vol=None):
        deal_vol, _ = self.buy(stk, vol)
        if deal_vol > 0:
            self.last_buy_time[stk] = self.datetime
        return deal_vol

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
        sell_stk = set(self.available.keys()) - trigger_stk - self.data_flow['not_available']
        trigger_stk = trigger_stk - self.data_flow['not_available']
        for stk in sell_stk:
            self.sell_action(stk)
        holding_num = len(self.holding)
        if holding_num >= self.max_holding_num:
            return
        trigget_num = min(len(trigger_stk), self.daily_max_buy_num)
        if (holding_num + trigget_num) > self.max_holding_num:
            trigget_num = self.max_holding_num - holding_num

        bough_num = 0
        for stk in trigger_stk:
            if stk not in self.holding:
                _ = self.buy_action(stk)
                bough_num += 1
            if bough_num >= trigget_num:
                break


def main(max_holding, daily_max_buy):
    pct_threshold = 0.05
    cost = 0.001
    # signal, pred_ret = pd.read_pickle('/data/group/800319/signal/MixFreq_signal_%d_threshold.pkl' % (int(pct_threshold * 100)))
    pred_ret = pd.read_pickle('/data/group/800319/pred_signal/OLS_5min_f100_ic_all_t')
    # pred_ret.index = pd.MultiIndex.from_tuples(pred_ret.index.tolist())
    # pred_ret[~signal] = np.nan
    bar_list = get_desample_minute_dict(5)
    bar_list = [bar_list[x] for x in bar_list]
    bar_list = sorted(list(set(bar_list)))
    instance = SignalBasedPortfolioLimitUp(pred_ret, 20160101, 20181231, target_point=bar_list[4:-1],
                                           buy_cost=cost, sell_cost=cost, max_holding=max_holding, daily_max_buy=daily_max_buy)
    helper = EvaluationHelper()
    import time
    e = time.time()
    record = instance.run_backtest(48)
    helper.one_wave_run(record, kernel=24,
                        output_path='/data/user/015664/AFuckingTrigger/限制买入和持仓/5min/OLSMultiIndex_UpHolding%d_UpBuy%d_threshold_%dpct.xlsx' % (
                        max_holding, daily_max_buy, int(pct_threshold * 100)),
                        signal_record_save=True)
    print(time.time() - e)


if __name__ == "__main__":
    main(300, 100)
