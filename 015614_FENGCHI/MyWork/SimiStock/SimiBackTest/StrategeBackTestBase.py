# coding: utf-8
# Author：fengchi863
# Date ：2022/4/15 15:03
from abc import abstractmethod
from SimiStock.dataApi import getData, stockList, tradeDate
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData

s = FactorData()


class StrategyBackTestBase:
    def __init__(self, stk_id, start_date, end_date, price_rolling_len=5, amt_per_signal=10000000, available_flag=None,
                 isin_pool_flag=None):
        self.stk_id = stk_id
        self.stk_code = stockList.trans_int2windcode(stk_id)
        self.record = []
        self.dataflow = {}
        self.trade_date = None
        self.pre_day = None
        self.datetime = None
        self.amt_per_signal = amt_per_signal
        self.price_rolling_len = price_rolling_len
        self.position = {'holding': 0, 'available': 0}

        self.date_list = tradeDate.get_date_range(start_date, end_date)
        self.date_index = list(np.arange(len(self.date_list)))

        # 更新权息因子
        self.daily_info = getData.get_daily_1stock(stk_id, ['close', 'open', 'low', 'high', 'close_badj'],
                                                   self.date_list)
        self.daily_info['close_padj'] = self.daily_info['close'].shift(-1) * self.daily_info['close_badj'] / \
                                        self.daily_info['close_badj'].shift(-1)
        self.daily_info['adj_ratio'] = self.daily_info['close'] / self.daily_info['close_padj']
        self.pre_daily_info = self.daily_info.shift(1)

        # 读取日内数据
        self.market_flow = getData.get_minute_1stock(self.stk_id, start_date * 10000 + 925, end_date * 10000 + 1500,
                                                    ['close', 'amt', 'vol'])
        self.market_flow['future_avg_buy_price'] = self.market_flow['close'].rolling(
            self.price_rolling_len).mean().shift(-self.price_rolling_len).fillna(method='pad')
        self.market_flow['future_avg_sell_price'] = self.market_flow['amt'] / self.market_flow['vol']
        if len(self.market_flow) == 0:
            self.market_flow = None
            return
        else:
            start_date = self.market_flow.index[0][0]
            end_date = self.market_flow.index[-1][0]
        self.market_flow = self.market_flow.reindex(
            pd.MultiIndex.from_product([self.date_list, tradeDate.trade_minutes], names=["date", "time"]))
        self.market_flow_array = self.market_flow.values

        if available_flag is None:
            available_info = s.get_factor_value("Basic_factor", [self.stk_code],
                                                s.tradingday(str(start_date), str(end_date)), ["trade_status"])
            available_info = available_info.reset_index()
            available_info['mddate'] = available_info['mddate'].astype(int)
            available_info = available_info.set_index('mddate').reindex(self.date_list)
            self.available_info = available_info['trade_status'].isin(['交易', 'N', 'XD', 'XR', 'DR'])
        elif isinstance(available_flag, pd.Series):
            self.available_info = available_flag
        else:
            raise Exception('Wrong type for available_flag')
        self.available_info_list = self.available_info.tolist()

        if isin_pool_flag is None:
            self.inpool_info = pd.Series(False, index=self.date_list).values
        elif isinstance(isin_pool_flag, pd.Series):
            self.inpool_info = isin_pool_flag.reindex(self.date_list).fillna(False)
        else:
            raise Exception('Wrong type for isinpool flag')
        self.inpool_info_list = list(self.inpool_info)

    @abstractmethod
    def daily_update(self):
        pass

    @abstractmethod
    def bar_handler(self):
        pass

    def istradable(self):
        return self.available_info_list[self.date_list.index(self.trade_date)]

    def isinpool(self):
        try:
            return self.inpool_info_list[self.date_list.index(self.trade_date)]
        except:
            print(1)

    def __daily_update(self, trade_date):
        self.pre_day = self.trade_date
        self.trade_date = trade_date

        pre_close_padj = self.pre_daily_info['close_padj'][trade_date]
        pre_close = self.pre_daily_info['close'][trade_date]
        pre_adj_ratio = self.pre_daily_info['adj_ratio'][trade_date]

        if self.position['holding'] == 0 and not self.isinpool():
            return
        self.dataflow['market'] = self.load_basic_dataflow(self.trade_date)
        if self.pre_day is not None:
            self.record.append(
                [self.pre_day, 1500, 'H', pre_close_padj, pre_close, self.position['holding'],
                 self.position['available']])
            # 权息更新
            if self.pre_day != self.trade_date:
                adj_ratio = pre_adj_ratio
                if abs(adj_ratio - 1) > 0.0001:
                    self.position['holding'] = self.position['holding'] * adj_ratio
        self.record.append(
            [self.trade_date, 925, 'D', np.nan, np.nan, self.position['holding'], self.position['holding']])
        self.position['available'] = self.position['holding']
        # 自定义更新模块
        if self.istradable():
            self.daily_update()

    def load_basic_dataflow(self, date):
        date_idx = self.date_list.index(date)
        if date not in self.market_flow.index:
            return None
        data_array = self.market_flow_array[date_idx * 242:(date_idx + 1) * 242]
        data = pd.DataFrame(data_array, index=tradeDate.trade_minutes, columns=self.market_flow.columns)
        return data

    def backtest(self):
        for date in self.date_list:
            self.__daily_update(date)
            if not self.istradable():
                # 当日停牌、ST、一字板等不交易
                continue
            if self.position['holding'] == 0 and not self.isinpool():
                # 当日无持仓、且不在股票池里，则不进入日内bar_handler循环
                continue
            for bar in tradeDate.trade_minutes[0:-1]:
                self.datetime = (date, bar)
                self.bar_handler()
        self.record.append([self.trade_date, 1500, 'H', self.daily_info.at[self.trade_date, 'close_padj'],
                            self.daily_info.at[self.trade_date, 'close'], self.position['holding'],
                            self.position['available']])
        return self.record

    def get_buy_price(self):
        return self.dataflow['market'].at[self.datetime[1], 'future_avg_buy_price']

    def get_sell_price(self):
        return self.dataflow['market'].at[self.datetime[1], 'future_avg_sell_price']

    def buy_action(self, vol=None, direction='Long'):
        if not self.isinpool():
            return
        deal_price = self.get_buy_price()
        if vol is None:
            vol = round(self.amt_per_signal / deal_price, -2)
        self.position['holding'] += vol
        self.record.append([self.datetime[0], self.datetime[1], 'B', vol, deal_price, self.position['holding'],
                            self.position['available'], direction])
        return vol

    def sell_action(self, vol=None, direction='Long'):
        if vol is None:
            vol = self.position['available']
        else:
            vol = min(vol, self.position['available'])
        if vol == 0:
            return
        deal_price = self.get_sell_price()
        self.position['holding'] -= vol
        self.position['available'] -= vol
        self.record.append([self.datetime[0], self.datetime[1], 'S', -vol, deal_price, self.position['holding'],
                            self.position['available'], direction])
        return vol
