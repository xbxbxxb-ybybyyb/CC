# @Time : 2020/7/17 9:06
# @Author : Zhichen Lu
# @File : StockStrategyBase.py
import os
from abc import abstractmethod

import numpy as np
import pandas as pd
from xquant.factordata import FactorData

from conf.path_config import up_out_path, open_up_down_info_path
from dataApi.getData import get_date_range, get_minute_1stock, get_daily_1stock, get_minute_1factor
from dataApi.tradeDate import trade_minutes

s = FactorData()

class StockStrategyBase:

    def __init__(self, stk, start_date, end_date, price_rolling_window=10, amt_per_signal=5000000, available_flag=None, isin_pool_flag=None):
        """
        :param stk:股票代码 int
        :param start_date: int
        :param end_date: int
        :param price_rolling_window: int
        :param amt_per_signal: 每次买入金额 int/float
        :param available_flag: 每天可交易情况，默认剔除一字板、停牌、ST等, pd.Serise(index=date_list) False时不可买卖
        :param isin_pool_flag: 每天股票是否处于股票池中 pd.Series(index=date_list) False 时可卖不可买，False且无持仓不进入日内循环和 bar_handler
        """

        self.stk_id = stk
        self.stk_windcode = str(stk).zfill(6)+'.SZ' if stk<400000 else str(stk)+'.SH'
        self.record = [] #[交易日期,交易时间, falg, 成交量, 成交价,交易后持仓,可卖出持仓]
        self.dataflow = {}
        self.trading_day = None
        self.preday = None
        self.pre_i = None
        self.i = None
        self.datetime = None
        self.price_rolling_window = price_rolling_window
        self.amt_per_signal = amt_per_signal
        self.position = {'holding':0,'available':0}
        self.market_flow = get_minute_1stock(self.stk_id, start_date * 10000 + 925, end_date * 10000 + 1500, ['close'])
        self.market_flow['future_avg_price'] = self.market_flow['close'].rolling(self.price_rolling_window).mean().shift(-self.price_rolling_window).fillna(method='pad')
        #self.market_flow['future_avg_price'] = self.market_flow['close'].copy()
        if self.market_flow.shape[0] == 0:
            self.market_flow = None
        else:
            start_date = self.market_flow.index[0][0]
            end_date = self.market_flow.index[-1][0]
        if self.market_flow is None:
            return
        self.date_list = get_date_range(start_date, end_date)
        self.market_flow = self.market_flow.reindex(pd.MultiIndex.from_product([self.date_list, trade_minutes], names=["date", "time"]))
        self.market_flow_array = self.market_flow.values

        self.date_index = np.arange(len(self.date_list))
        self.daily_info = get_daily_1stock(stk, ['close', 'close_badj'], self.date_list)
        self.daily_info['close_padj'] = self.daily_info['close'].shift(-1) * self.daily_info['close_badj'] / self.daily_info['close_badj'].shift(-1)
        self.daily_info['adj_ratio'] = self.daily_info['close'] / self.daily_info['close_padj']
        self.pre_dail_info = self.daily_info.shift(1)
        if available_flag is None:
            available_info = s.get_factor_value("Basic_factor",[self.stk_windcode], s.tradingday(str(start_date), str(end_date)), ["trade_status"] )
            available_info = available_info.reset_index()
            available_info['mddate'] = available_info['mddate'].astype(int)
            available_info = available_info.set_index('mddate').reindex(self.date_list)
            self.available_info = available_info['trade_status'].isin(['交易', 'N', 'XD', 'XR', 'DR'])
            if os.path.exists(open_up_down_info_path + '%d.pkl' % stk):
                open_limit = pd.read_pickle(open_up_down_info_path + '%d.pkl' % stk)
                open_limit = open_limit.reindex(self.available_info.index)
                self.available_info = self.available_info & open_limit
            # if os.path.exists(down_out_path+'%d.pkl'%stk):
            #     down_info = pd.read_pickle(down_out_path+'%d.pkl'%stk)
            #     down_info = down_info.reindex(self.available_info.index)
            #     self.available_info = self.available_info & down_info.eq(1)
            #     del down_info
            # if os.path.exists(up_out_path+'%d.pkl'%stk):
            #     up_info = pd.read_pickle(up_out_path+'%d.pkl'%stk)
            #     up_info = up_info.reindex(self.available_info.index)
            #     self.available_info = self.available_info & up_info.eq(1)
            #     del up_info
        elif isinstance(available_flag,pd.Series):
            self.available_info = available_flag
        else:
            raise Exception('Wrong type for available_flag')
        self.available_info_list = self.available_info.tolist()
        if isin_pool_flag is None:
            self.inpool_info = pd.Series(False, index=self.date_list).values
        elif isinstance(isin_pool_flag, pd.Series):
            # isin_pool_flag_array = isin_pool_flag.values
            # isin_pool_flag_array[np.isnan(isin_pool_flag_array)] = 0
            # self.inpool_info = isin_pool_flag_array
            self.inpool_info = isin_pool_flag.reindex(self.date_list).fillna(False)
        else:
            raise Exception('Wrong type for isinpool flag')
        #self.inpool_info_list = self.inpool_info.tolist()
        self.inpool_info_list = list(self.inpool_info)
    @abstractmethod
    def daily_update(self):
        pass

    @abstractmethod
    def bar_handler(self):
        pass

    def istradable(self):
        #return self.available_info.loc[self.trading_day]
        return self.available_info_list[self.i]

    def isinpool(self):
        #return self.inpool_info.loc[self.trading_day]
        return self.inpool_info_list[self.i]

    def __daily_update(self,date,i,pre_close_padj,pre_close,pre_adj_ratio):
        # 数据更新
        self.preday = self.trading_day
        self.pre_i = self.i
        self.i = i
        self.trading_day = date
        # if date==20140613:
        #     print(111)
        # self.dataflow['pre_market'] = self.dataflow['market']
        self.dataflow['market'] = self.load_baisc_dataflow(self.trading_day,self.i)
        if not self.preday is None:
            #daily_info = self.daily_info.loc[self.preday]
            # flag 为‘H’的record中 vol,deal_price 两个字段用于存储 前复权今收 和 不复权今天收
            #self.record.append([self.preday, 1500, 'H', daily_info['close_padj'],daily_info['close'], self.position['holding'], self.position['available']])
            self.record.append(
                [self.preday, 1500, 'H', pre_close_padj, pre_close, self.position['holding'],
                 self.position['available']])
            # 权息更新
            if self.preday != self.trading_day:
                #adj_ratio = daily_info['adj_ratio']
                adj_ratio = pre_adj_ratio
                if abs(adj_ratio-1)>0.0001:
                    self.position['holding'] = self.position['holding']*adj_ratio
        self.record.append([self.trading_day,925, 'D', np.nan, np.nan,self.position['holding'],self.position['holding']])
        self.position['available'] = self.position['holding']
        # 自定义更新模块
        if self.istradable():
            self.daily_update()

    def backtest(self):
        #trade_i = 0
        if self.market_flow is None:
            return self.record
        self.max_value = None
        for date,i,pre_close_padj,pre_close,pre_adj_ratio in zip(self.date_list,self.date_index,self.pre_dail_info['close_padj'],self.pre_dail_info['close'],self.pre_dail_info['adj_ratio']):
            self.__daily_update(date,i,pre_close_padj,pre_close,pre_adj_ratio)
            if not self.istradable():
                """
                当日停牌、ST、一字板等不交易
                """
                continue
            if self.position['holding'] == 0 and not self.isinpool():
                """
                当日无持仓、且不在股票池里，则不进入日内bar_handler循环
                """
                continue
            for bar in trade_minutes[1:-1]:
                self.datetime = (date,bar)
                self.bar_handler()
            ########
            # trade_minutes_ = [1000,1030,1100,1300,1330,1400,1430]
            # for bar in trade_minutes_:
            #     self.datetime = (date,bar)
            #     self.bar_handler(trade_i)
            #     trade_i+=1
            # trade_i = 0
            #######
        self.record.append([self.trading_day, 1500, 'H', self.daily_info.at[self.trading_day, 'close_padj'],
                            self.daily_info.at[self.trading_day, 'close'], self.position['holding'], self.position['available']])
        return self.record

    def trade(self):
        return self.dataflow['market'].at[self.datetime[1],'future_avg_price']

    def buy(self,vol = None):
        if not self.isinpool():
            """
            不在股票池内时不可买
            """
            return
        deal_price = self.trade()
        if vol is None:
            vol = round(self.amt_per_signal/deal_price,-2)
        self.position['holding']+= vol
        self.record.append([self.datetime[0],self.datetime[1], 'B', vol, deal_price,self.position['holding'],self.position['available']])
        return vol

    def sell(self,vol=None):
        if vol is None:
            vol = self.position['available']
        else:
            vol = min(vol, self.position['available'])
        if vol==0:
            return
        deal_price = self.trade()
        self.position['holding'] -= vol
        self.position['available'] -= vol
        self.record.append([self.datetime[0],self.datetime[1], 'S', -vol, deal_price,self.position['holding'],self.position['available']])
        return vol

    def load_baisc_dataflow(self,date,i):
        if date not in self.market_flow.index:
            return None
        # if date>=20181225:
        #     print(1)
        data_array = self.market_flow_array[i*242:(i+1)*242]
        # mindex_products = pd.MultiIndex.from_product([[self.date_list[self.i]], trade_minutes], names=["date", "time"])
        # data = pd.DataFrame(data_array,index=mindex_products,columns=self.market_flow.columns)
        data = pd.DataFrame(data_array, index=trade_minutes, columns=self.market_flow.columns)
        #data = self.market_flow.loc[[date]]
        # data.loc[(date,trade_minutes[-self.price_rolling_window:]),'future_avg_price'] = np.nan#data.loc[trade_minutes[-self.price_rolling_window-1],'future_avg_price']
        # data['future_avg_price'] = data['future_avg_price'].fillna(method='pad')
        return data