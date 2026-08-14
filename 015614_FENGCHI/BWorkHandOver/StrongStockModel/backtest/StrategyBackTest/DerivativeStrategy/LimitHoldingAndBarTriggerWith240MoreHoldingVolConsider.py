# @Time : 2020/12/2 21:15
# @Author : Zhichen Lu
# @File : LimitHoldingAndBarTriggerWith240MoreHoldingVolConsider.py

from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, EvaluationHelper
import pandas as pd
from StrongStockModel.conf.path_config import deal_price_path
from dataApi.getData import get_daily_1factor
import numpy as np
import gc
from tqdm import tqdm

class LimitHoldingAndBarTriggerWith240MoreHoldingVolConsider(PortfolioStrategyBase):

    def __init__(self, signal, start=20140101, end=20181231, stock_pool=None, target_point=None, buy_cost=0.001, sell_cost=0.001, per_amt=500000, append_param={}, max_holding=600,
                 barly_max_buy=400, deal_percent=0.1,stk_min_amt=200000):
        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost, per_amt, append_param=append_param)
        self.signal = signal.reindex(self.close.index)
        self.data_flow['signal'] = None
        self.last_buy_time = {}
        self.max_holding_num = max_holding
        self.barly_max_buy_num = barly_max_buy
        self.past_5day_future_30min_vol = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl').reindex(self.close.index)
        self.future_30_min_vol = pd.read_pickle(deal_price_path + 'vol_future_rolling_30_sum.pkl').reindex(self.close.index)
        self.daily_info['pre_close'] = self.daily_info['close'] * self.daily_info['close_badj'].shift(1) / self.daily_info['close_badj']
        self.deal_percent = deal_percent
        self.stk_min_amt = stk_min_amt
        self.holding_num = {}
        self.daily_high = get_daily_1factor('high', self.date_list, self.stk_list)
        self.daily_low = get_daily_1factor('low', self.date_list, self.stk_list)

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
        vol = min(vol,int(self.bar_actual_future_vol[stk]//100*100))

        holding += vol
        self.holding[stk], self.available[stk] = holding, available
        if stk not in self.record:
            self.record[stk] = [[self.datetime[0], self.datetime[1], 'B', vol, deal_price, holding, available]]
        else:
            record = self.record[stk]
            record.append([self.datetime[0], self.datetime[1], 'B', vol, deal_price, holding, available])
            self.record[stk] = record
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
        if stk not in self.record:
            raise Exception('Sell without record')
        else:
            record = self.record[stk]
            record.append([self.datetime[0], self.datetime[1], 'S', -vol, deal_price, holding, available])
            self.record[stk] = record
        return vol, deal_price



    def sell_action(self, stk, vol=None):
        if stk not in self.last_buy_time:
            raise Exception('Last buy time is not recorded')
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) > 1 or ((bar_date_idx - date_idx) == 1 and bar_time >= time_point):
            vol, deal_price = self.sell(stk, vol)

    def buy_action(self, stk, vol=None):
        deal_vol, deal_price = self.buy(stk, vol)
        if deal_vol > 0:
            if not np.isnan(deal_price):
                self.last_buy_time[stk] = self.datetime
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
        self.data_flow['past_future_vol'] = self.past_5day_future_30min_vol[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        self.data_flow['actual_future_vol'] = self.future_30_min_vol[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        #不在股票池里的股票
        date_pool = self.stock_pool[self.date_idx:self.date_idx + 1].T[date]
        date_pool = pd.Series(date_pool.tolist(),index=date_pool.index.tolist())
        date_pool = date_pool[~date_pool]
        #停牌、一字板的股票
        not_tradable = self.untradable_pool[self.date_idx:self.date_idx + 1].T[self.date]

        self.data_flow['not_tradable'] = set(not_tradable[not_tradable].index.tolist())
        self.data_flow['not_available'] = set(date_pool.index.tolist())
        self.data_flow['daily_high'] = self.daily_high[self.date_idx:self.date_idx + 1].T[self.date]
        self.data_flow['daily_low'] = self.daily_low[self.date_idx:self.date_idx + 1].T[self.date]
        self.data_flow['pre_close'] = self.daily_info['pre_close'][self.date_idx:self.date_idx + 1].T[self.date]

        if self.data_flow['signal'].index[0][0] != self.date or self.data_flow['signal'].index[-1][0] != self.date:
            raise Exception('Broadcast date and signal date are not match!')

    def bar_handler(self):
        date, time_point, date_idx, time_idx = self.datetime
        signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
        signal = signal.dropna()
        trigger_stk = set(signal.index)
        # 可卖出股票 = 持仓股票剔除 停牌and一字板
        avaliable_stk = set(self.available.keys()) - self.data_flow['not_tradable']
        avaliable_trigger_stk = avaliable_stk.intersection(trigger_stk)
        sell_stk = list(avaliable_stk - trigger_stk)
        # 可买入股票 = 触发股票 剔除 不在股票池的股票 以及 有持仓个股
        trigger_stk = trigger_stk - self.data_flow['not_available']
        trigger_stk = list(trigger_stk - set(self.holding.keys()))
        historical_future_vol = round(self.data_flow['past_future_vol'][time_idx:time_idx + 1].T[(date, time_point)] * self.deal_percent, -2)
        for stk in avaliable_trigger_stk:
            self.holding_another_round(stk)

        bar_close = self.data_flow['close'][time_idx:time_idx + 1].T[(date, time_point)]
        if sell_stk:
            sell_close = bar_close[sell_stk]
            limit_down_judge = ((sell_close.values / self.data_flow['pre_close'][sell_stk].values - 1) <= -0.098) & (
                    sell_close.values == self.data_flow['daily_low'][sell_stk].values)
            limit_down_judge = pd.Series(limit_down_judge, index=sell_stk)
            sell_stk = limit_down_judge[~limit_down_judge].index.tolist()
        try:
            sell_info = pd.DataFrame({'up': historical_future_vol.loc[sell_stk],
                                               'target': pd.Series({stk:self.holding[stk] for stk in sell_stk})})
        except:
            print(1)
        sell_info['actual_order_vol'] = sell_info.min(axis=1)
        sell_info['over_half'] = sell_info['actual_order_vol'] / sell_info['target'] >= 0.5
        assumption_soldout_num = sell_info['over_half'].sum()

        if (len(self.holding) - assumption_soldout_num)>=self.max_holding_num:
            sell_order_vol = sell_info['actual_order_vol']
            for stk in sell_stk:
                sell_vol = sell_order_vol[stk]
                self.sell_action(stk, sell_vol)
            return
        elif trigger_stk:
            target_close = bar_close[trigger_stk]
            limit_up_judge = ((target_close.values / self.data_flow['pre_close'][trigger_stk].values - 1) >= 0.098) & (
                        target_close.values == self.data_flow['daily_high'][trigger_stk].values)
            limit_up_judge = pd.Series(limit_up_judge, index=trigger_stk)
            trigger_stk = limit_up_judge[~limit_up_judge].index.tolist()
            target_vol = round(self.per_amt / target_close, -2)
            target_vol = pd.concat([target_vol, historical_future_vol[list(trigger_stk)]], axis=1).min(axis=1)
            target_vol = target_vol // 100 * 100
            target_amt = target_vol * target_close
            target_amt = target_amt.loc[signal[trigger_stk].sort_values(ascending=False).index.tolist()]
            target_amt = target_amt[target_amt >= self.stk_min_amt]
            trigger_stk = target_amt.index.tolist()

            trigger_num = min(len(trigger_stk), self.max_holding_num - len(self.holding) + assumption_soldout_num, self.barly_max_buy_num)
            trigger_stk = trigger_stk[:trigger_num]
            target_vol = target_vol[trigger_stk]
        else:
            target_vol = pd.Series()

        sell_order_vol = sell_info['actual_order_vol']
        for stk in sell_stk:
            sell_vol = sell_order_vol[stk]
            self.sell_action(stk, sell_vol)

        for stk in target_vol.index:
            if stk in self.holding:
                raise Exception('Buying a holding stock')
            _ = self.buy_action(stk, target_vol[stk])

    def run_backtest(self, kernel=10):
        self.re_initial()
        bar = tqdm(self.date_list)
        for date_idx, date in enumerate(bar):
            bar.set_description('%d | holding:%d' % (date, len(self.holding)))
            self.daily_update(date_idx, date)
            for time_idx, time_point in enumerate(self.trading_point):
                self.bar_dealprice = self.data_flow['deal_price'][time_idx:time_idx + 1].T[(date, time_point)]
                self.bar_actual_future_vol = self.data_flow['actual_future_vol'][time_idx:time_idx + 1].T[(date, time_point)]*self.deal_percent
                self.datetime = (date, time_point, date_idx, time_idx)
                self.bar_point = date_idx * self.step + time_idx
                self.bar_handler()
                # print(self.datetime)
            daily_close = self.daily_info['close'][self.date_idx:self.date_idx + 1].T[self.date][list(self.holding.keys())]
            self.holding_num[self.date] = len(self.holding)

        record = list(self.record.keys())
        for each in record:
            self.record[each] = pd.DataFrame(self.record[each], columns=['date', 'time', 'flag', 'vol', 'deal_price', 'holding', 'available']).set_index(['date', 'time'])
        gc.collect()
        return self.record._getvalue()

