# @Time : 2020/12/15 9:19
# @Author : Zhichen Lu
# @File : run_StartWithLimitCashVolConsider.py

from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, InitailCashBasedEvaluationHelper
from tqdm import tqdm
import gc
import pandas as pd
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path, root_path
from dataApi.getData import get_daily_1factor, get_minute_1factor
import itertools

class StartWithLimitCashVolConsiderChangingCash(PortfolioStrategyBase):
    def __init__(self, signal, start=20140101, end=20181231, stock_pool=None, target_point=None,
                 buy_cost=0.001, sell_cost=0.001, per_amt_ratio=0.0025, append_param={}, initial_cash=200000000, barly_max_buy=100,
                 deal_percent=0.1, stk_min_amt=None, discount_ratio_series={}, per_ratio_change={}, max_trigger_num={}, intra_discount_ratio={}):
        per_amt = round(initial_cash * per_amt_ratio, -4)

        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost, per_amt, append_param=append_param)

        # close = get_minute_pickle('close', date_list=get_date_range(self.date_list[0], self.date_list[-1]), code_list=self.stock_pool.columns.tolist())
        close = get_minute_1factor('close', start_datetime=self.date_list[0], end_datetime=self.date_list[-1], code_list=self.stock_pool.columns.tolist())
        # get_minute_pickle('close', date_list=get_date_range(self.date_list[0], self.date_list[-1]), code_list=self.stock_pool.columns.tolist())
        close = close.shift(1).swaplevel(0, 1).loc[self.trading_point].swaplevel(0, 1)
        self.close = close
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
        self.holding_value = pd.Series(np.nan, index=pd.MultiIndex.from_tuples(list(itertools.product(self.date_list, self.trading_point))))
        self.holding_num = pd.Series(np.nan, index=self.date_list)
        # self.vol_cumsum = pd.read_pickle(deal_price_path + 'vol_rolling_30_sum.pkl').reindex(self.close.index)
        self.past_5day_future_30min_vol = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl').reindex(self.close.index)
        self.past_5day_future_30min_vol.columns = [int(str(x)[:6]) for x in self.past_5day_future_30min_vol.columns]
        self.future_30_min_vol = pd.read_pickle(deal_price_path + 'vol_future_rolling_30_sum.pkl').reindex(self.close.index)
        self.daily_info['pre_close'] = self.daily_info['close'] * self.daily_info['close_badj'].shift(1) / self.daily_info['close_badj']
        self.deal_percent = deal_percent
        if stk_min_amt is None:
            self.stk_min_amt = int(min(0.2 * per_amt, 500000))
        else:
            self.stk_min_amt = stk_min_amt
        self.discount_ratio_series = discount_ratio_series
        self.per_ratio_change = per_ratio_change
        self.sell_order_record = {}
        self.buy_order_record = {}
        self.max_triger_num = max_trigger_num
        self.discount_ratio = 1
        self.intra_discount_ratio = pd.Series(intra_discount_ratio).reindex(self.close.index).fillna(1)
        self.loaded_cash = 0

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
        if (bar_date_idx - date_idx) > 1 or ((bar_date_idx - date_idx) == 1 and bar_time >= time_point):
            vol, deal_price = self.sell(stk, vol)
            if vol > 0:
                if not np.isnan(deal_price):
                    self.cash += vol * deal_price * (1 - self.sell_cost)
                else:
                    raise Exception('Unexpected')
            return True, vol, deal_price
        else:
            return False, np.nan, np.nan

    def buy_action(self, stk, vol=None):
        deal_vol, deal_price = self.buy(stk, vol)
        if deal_vol > 0:
            if not np.isnan(deal_price):
                self.last_buy_time[stk] = self.datetime
                self.cash -= deal_vol * deal_price * (1 + self.buy_cost)
            else:
                raise Exception('Unexpected')
        return deal_vol, deal_price

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
        self.data_flow['intra_discount_ratio'] = self.intra_discount_ratio.iloc[self.date_idx * self.step:(self.date_idx + 1) * self.step]

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

    def bar_handler(self, bar_close):
        date, time_point, date_idx, time_idx = self.datetime
        signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
        signal = signal.dropna()
        trigger_stk = set(signal.index)
        # 盘中涨跌停

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
        avaliable_cash = self.cash + self.loaded_cash
        if avaliable_cash < self.per_amt:
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
            target_vol = pd.concat([target_vol, historical_future_vol[list(trigger_stk)]], axis=1).min(axis=1)
            target_vol = target_vol // 100 * 100
            target_amt = target_vol * target_close
            target_amt = target_amt.loc[signal[trigger_stk].sort_values(ascending=False).index.tolist()]
            target_amt = target_amt[target_amt >= self.stk_min_amt]
            target_amt = target_amt[target_amt.cumsum() < avaliable_cash]
            trigger_stk = target_amt.index.tolist()
            trigger_num = min(len(trigger_stk), int(avaliable_cash // self.per_amt), self.barly_max_buy)
            trigger_stk = trigger_stk[:trigger_num]
            target_vol = target_vol[trigger_stk]
        else:
            target_vol = pd.Series()

        sold_record = []
        for stk in sell_stk:  # to_sell = set(sell_stk)
            sell_vol = min(historical_future_vol[stk], self.holding[stk])
            signal_sent, vol, price = self.sell_action(stk, sell_vol)
            if signal_sent:
                sold_record.append([stk, signal_sent, vol, price])
        if date not in self.sell_order_record:
            self.sell_order_record[date] = {}
        self.sell_order_record[date][time_point] = sold_record

        bought_order = []
        # sold = to_sell - {x for x in self.holding}
        for stk in target_vol.index:
            if stk in self.holding:
                raise Exception('Buying a holding stock')
            deal_vol, deal_price = self.buy_action(stk, target_vol[stk])
            bought_order.append([stk, deal_vol, deal_price])
        if date not in self.buy_order_record:
            self.buy_order_record[date] = {}
        self.buy_order_record[date][time_point] = bought_order

    def run_backtest(self, kernel=10):
        self.holding_series = {}
        self.re_initial()
        bar = tqdm(self.date_list)
        for date_idx, date in enumerate(bar):
            bar.set_description('%d | holding:%d' % (date, len(self.holding)))
            self.daily_update(date_idx, date)
            if date == 20170105:
                print(1)
            for time_idx, time_point in enumerate(self.trading_point):
                self.bar_dealprice = self.data_flow['deal_price'][time_idx:time_idx + 1].T[(date, time_point)]
                self.bar_actual_future_vol = self.data_flow['actual_future_vol'][time_idx:time_idx + 1].T[(date, time_point)] * self.deal_percent
                self.datetime = (date, time_point, date_idx, time_idx)
                self.bar_point = date_idx * self.step + time_idx
                self.holding_series[(date, time_point)] = self.holding.copy()

                bar_close = self.data_flow['close'][time_idx:time_idx + 1].T[(date, time_point)]
                # if target_ratio<=1:
                # self.cash 自有资金
                # self.loaed_mony 杠杆资金
                # 可用账户市值 = 持仓市值+自由资金+杠杆资金
                # 计算净值的账户市值 = 持仓市值+自由资金+杠杆资金
                target_ratio = self.data_flow['intra_discount_ratio'].iloc[[time_idx]][(date, time_point)]
                if target_ratio != self.discount_ratio:
                    current_value_account = (bar_close * pd.Series(self.holding)).sum() + self.cash
                    target_value_account = target_ratio * current_value_account
                    self.loaded_cash = target_value_account - current_value_account
                    self.discount_ratio = target_ratio

                    self.holding_value[(self.date, time_point)] = current_value_account
                    self.available_accout_value = current_value_account + self.loaded_cash
                    self.per_amt = max(self.available_accout_value * self.per_amt_ratio // 10000 * 10000, 10000)
                    self.stk_min_amt = int(min(0.2 * self.per_amt, 500000))

                    if np.isnan(self.cash):
                        print('nan cash')


                self.holding_series[(date, time_point)]['init_cash'] = self.cash
                self.bar_handler(bar_close)

                # print(self.datetime)
            if date in self.per_ratio_change:
                self.per_amt_ratio = self.per_ratio_change[date]
            if date in self.max_triger_num:
                self.barly_max_buy = self.max_triger_num[date]
            self.cash_series[self.date] = self.cash
            self.holding_num[self.date] = len(self.holding)
            daily_close = self.daily_info['close'][self.date_idx:self.date_idx + 1].T[self.date][list(self.holding.keys())]
            self.accout_value = (daily_close * pd.Series(self.holding)).sum() + self.cash
            self.holding_value[(self.date, 1500)] = self.accout_value
            self.available_accout_value = self.accout_value + self.loaded_cash
            self.per_amt = max(self.available_accout_value * self.per_amt_ratio // 10000 * 10000, 10000)
            self.stk_min_amt = int(min(0.2 * self.per_amt, 500000))

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
