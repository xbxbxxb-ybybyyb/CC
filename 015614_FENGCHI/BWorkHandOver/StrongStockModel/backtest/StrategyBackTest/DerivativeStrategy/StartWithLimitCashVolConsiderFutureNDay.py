# @Time : 2020/12/15 9:19
# @Author : Zhichen Lu
# @File : StartWithLimitCashVolConsiderFutureNDay.py

from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, InitailCashBasedEvaluationHelper
from tqdm import tqdm
import gc
import pandas as pd
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path, root_path
from dataApi.getData import get_daily_1factor


class StartWithLimitCashVolConsiderFutureNDay(PortfolioStrategyBase):
    def __init__(self, signal,window:int, start=20140101, end=20181231, stock_pool=None, target_point=None,
                 buy_cost=0.001, sell_cost=0.001, per_amt_ratio=0.0025, append_param={}, initial_cash=200000000, barly_max_buy=100,
                 deal_percent=0.1, stk_min_amt=None):
        per_amt = round(initial_cash * per_amt_ratio, -5)
        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost, per_amt, append_param=append_param)
        self.daily_high = get_daily_1factor('high', self.date_list, self.stk_list)
        self.daily_low = get_daily_1factor('low', self.date_list, self.stk_list)
        self.signal = signal.reindex(self.close.index)
        self.data_flow['signal'] = None
        self.last_buy_time = {}
        self.cash = initial_cash
        self.accout_value = initial_cash
        self.per_amt_ratio = per_amt_ratio
        self.barly_max_buy = barly_max_buy
        self.cash_series = pd.Series(np.nan, index=self.date_list)
        self.holding_value = pd.Series(np.nan, index=self.date_list)
        self.holding_num = pd.Series(np.nan, index=self.date_list)
        # self.vol_cumsum = pd.read_pickle(deal_price_path + 'vol_rolling_30_sum.pkl').reindex(self.close.index)
        if 'past_vol_path' in append_param:
            self.past_5day_future_30min_vol = pd.read_pickle(append_param['past_vol_path']).reindex(self.close.index)
        else:
            self.past_5day_future_30min_vol = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl').reindex(self.close.index)
        self.past_5day_future_30min_vol.columns = [int(str(x)[:6]) for x in self.past_5day_future_30min_vol.columns]
        if 'future_deal_vol' in append_param:
            self.future_30_min_vol = pd.read_pickle(append_param['future_deal_vol']).reindex(self.close.index)
        else:
            self.future_30_min_vol = pd.read_pickle(deal_price_path + 'vol_future_rolling_30_sum.pkl').reindex(self.close.index)
        self.daily_info['pre_close'] = self.daily_info['close'] * self.daily_info['close_badj'].shift(1) / self.daily_info['close_badj']
        self.deal_percent = deal_percent
        if stk_min_amt is None:
            self.stk_min_amt = self.per_amt * 0.2
        else:
            self.stk_min_amt = stk_min_amt
        print('min_stk_amt', self.stk_min_amt)
        self.order_info = {}
        self.window = window

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
        if (bar_date_idx - date_idx) > self.window or ((bar_date_idx - date_idx) == self.window and bar_time >= time_point):
            vol, deal_price = self.sell(stk, vol)
            if vol > 0:
                if not np.isnan(deal_price):
                    self.cash += vol * deal_price * (1 - self.sell_cost)
                else:
                    raise Exception('Unexpected')
            return vol,deal_price
        else:
            return None

    def buy_action(self, stk, vol=None):
        deal_vol, deal_price = self.buy(stk, vol)
        if deal_vol > 0:
            if not np.isnan(deal_price):
                self.last_buy_time[stk] = self.datetime
                self.cash -= deal_vol * deal_price * (1 + self.buy_cost)
            else:
                raise Exception('Unexpected')
        return deal_vol

    def holding_another_round(self, stk):
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) == 1 and bar_time == time_point:
            self.last_buy_time[stk] = self.datetime

    def daily_update(self, idx, date):
        super().daily_update(idx, date)
        self.data_flow['signal'] = self.signal[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        self.data_flow['past_future_vol'] = self.past_5day_future_30min_vol[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        self.data_flow['actual_future_vol'] = self.future_30_min_vol[self.date_idx * self.step:(self.date_idx + 1) * self.step]
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

        if self.data_flow['signal'].index[0][0] != self.date or self.data_flow['signal'].index[-1][0] != self.date:
            raise Exception('Broadcast date and signal date are not match!')

    def bar_handler(self):
        date, time_point, date_idx, time_idx = self.datetime
        signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
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
        historical_future_vol = round(self.data_flow['past_future_vol'][time_idx:time_idx + 1].T[(date, time_point)] * self.deal_percent, -2)
        for stk in avaliable_trigger_stk:
            self.holding_another_round(stk)

        sell_signal = []
        if self.cash < self.per_amt:
            not_buy = True
            for stk in sell_stk:
                sell_vol = min(historical_future_vol[stk], self.holding[stk])
                sold_res = self.sell_action(stk, sell_vol)
                if sold_res:
                    sell_signal.append([stk]+list(sold_res))

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
            sold_res = self.sell_action(stk, sell_vol)
            if sold_res:
                sell_signal.append([stk] + list(sold_res))

        # sold = to_sell - {x for x in self.holding}

        deal_list = []
        for stk in target_vol.index:
            if stk in self.holding:
                raise Exception('Buying a holding stock')
            deal_vol = self.buy_action(stk, target_vol[stk])
            deal_list.append(deal_vol)
        orderable_vol['deal_vol'] = deal_list
        self.order_info[self.datetime[:2]] = orderable_vol


    def run_backtest(self, kernel=10):
        self.re_initial()
        self.daily_holding = {}
        self.daily_buy_time_info = {}
        self.daily_conf = {}
        bar = tqdm(self.date_list)
        for date_idx, date in enumerate(bar):
            bar.set_description('%d | holding:%d' % (date, len(self.holding)))
            self.daily_update(date_idx, date)
            self.daily_conf[date] = {
                'date': date,
                'pre_date': self.pre_date,
                'barly_max_buy': self.barly_max_buy,
                'stk_min_amt': self.stk_min_amt,
                'per_amt': self.per_amt,
                'cash': self.cash,
                'portfolio_id': '201001',
                'order_ratio': 0.1
            }
            for time_idx, time_point in enumerate(self.trading_point):
                self.bar_dealprice = self.data_flow['deal_price'][time_idx:time_idx + 1].T[(date, time_point)]
                self.bar_actual_future_vol = self.data_flow['actual_future_vol'][time_idx:time_idx + 1].T[(date, time_point)] * self.deal_percent
                self.datetime = (date, time_point, date_idx, time_idx)
                self.bar_point = date_idx * self.step + time_idx
                self.bar_handler()
                # print(self.datetime)
            self.cash_series[self.date] = self.cash
            self.holding_num[self.date] = len(self.holding)
            daily_close = self.daily_info['close'][self.date_idx:self.date_idx + 1].T[self.date][list(self.holding.keys())]
            self.accout_value = (daily_close * pd.Series(self.holding)).sum() + self.cash
            self.holding_value[self.date] = self.accout_value
            self.per_amt = max(self.accout_value * self.per_amt_ratio // 10000 * 10000, 10000)

            self.daily_holding[date] = self.holding.copy()
            self.daily_buy_time_info[date] = self.last_buy_time

        pre_close_padj, pre_close, pre_adj_ratio = self.daily_info['close_padj'][self.date_idx:self.date_idx + 1].T[date], \
                                                   self.daily_info['close'][self.date_idx:self.date_idx + 1].T[date], \
                                                   self.daily_info['adj_ratio'][self.date_idx:self.date_idx + 1].T[date]
        for stk in self.holding:
            holding = self.holding[stk]
            stk_close_padj, stk_close, stk_adj_ratio = pre_close_padj[stk], pre_close[stk], pre_adj_ratio[stk]
            available = self.available[stk] if stk in self.available else 0
            if holding > 0:
                record = self.record[stk]
                record.append([self.date, 1500, 'H', stk_close_padj, stk_close, holding, available])
                self.record[stk] = record

        record = list(self.record.keys())
        for each in record:
            self.record[each] = pd.DataFrame(self.record[each], columns=['date', 'time', 'flag', 'vol', 'deal_price', 'holding', 'available']).set_index(['date', 'time'])
        gc.collect()
        return self.record._getvalue()

# import os
# import pandas as pd
#
# file_list = os.listdir('/data/group/800319/strategy_local_path/buy_time_info_old/')
# for each in file_list:
#     buy_time_info_origin = pd.read_pickle('/data/group/800319/strategy_local_path/buy_time_info_old/%s'%each)
#     buy_time_info = {}
#     for stk in buy_time_info_origin:
#         code = str(stk).zfill(6) + '.SZ' if stk < 400000 else str(stk) + '.SH'
#         buy_time_info[code] = buy_time_info_origin[stk]
#     pd.to_pickle(buy_time_info,'/data/group/800319/strategy_local_path/buy_time_info/%s'%each)
