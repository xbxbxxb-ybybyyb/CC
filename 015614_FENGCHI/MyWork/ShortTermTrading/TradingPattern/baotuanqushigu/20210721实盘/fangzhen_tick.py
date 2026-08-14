# coding: utf-8
# Author：fengchi863
# Date ：2021/7/21 10:17
'''
用于仿真
'''

from xquant.marketdata import MarketData
from xquant.factordata import FactorData
from datetime import datetime,timedelta
from FaaMonitor.Util.DtUtil import DtUtil
from dataApi import stockList
import pandas as pd, numpy as np

class Simulator:
    def __init__(self):
        today_date = DtUtil.get_today_date()
        yes_date = DtUtil.get_yesterday_date()

        fd = FactorData()
        mdp = MarketData()

        self.fd = fd
        self.mdp = mdp
        self.today_date = today_date
        self.yes_date = yes_date

        # 买入侧参数
        self.buy_list = None
        self.rolling_min_dict = dict()
        self.ma5 = dict()
        self.ma5_boost = dict()
        self.pre_close = dict()
        self.per_amt = dict()

        # 卖出侧参数
        self.sell_list = None
        self.buy_price = dict()
        self.vol = dict()
        self.gain_closeout = dict()
        self.loss_closeout = dict()

    def daily_reset(self):
        buy_profile = pd.read_excel('20210723.xlsx', sheet_name='买入股票池', index_col=0)
        sell_profile = pd.read_excel('20210723.xlsx', sheet_name='卖出股票池', index_col=0)
        self.buy_list = buy_profile.index.tolist()
        self.sell_list = sell_profile.index.tolist()

        for stk in buy_profile.index:
            self.ma5[stk] = buy_profile.loc[stk, 'ma']
            self.ma5_boost[stk] = buy_profile.loc[stk, 'ma_boost']
            self.pre_close[stk] = buy_profile.loc[stk, 'pre_close']
            self.per_amt[stk] = buy_profile.loc[stk, 'per_amt']

        for stk in sell_profile.index:
            self.buy_price[stk] = sell_profile.loc[stk, 'buy_price']
            self.ma5[stk] = sell_profile.loc[stk, 'ma']
            self.vol[stk] = sell_profile.loc[stk, 'vol']
            self.gain_closeout[stk] = sell_profile.loc[stk, 'gain_closeout']
            self.loss_closeout[stk] = sell_profile.loc[stk, 'loss_closeout']

    # 更新最低价
    def update_rolling_min(self, stk, last_px):
        if stk not in self.rolling_min_dict:
            self.rolling_min_dict[stk] = last_px
        else:
            if last_px < self.rolling_min_dict[stk]:
                self.rolling_min_dict[stk] = last_px
            else:
                return

    def generate_buy_signal(self, stk, last_px):
        if self.rolling_min_dict[stk] / self.pre_close[stk] - 1 > -0.01:
            return False

        cond1 = last_px / self.rolling_min_dict[stk] - 1 > 0.01

        cond11 = self.rolling_min_dict[stk] < self.ma5[stk]
        cond12 = last_px > self.ma5[stk]

        cond21 = self.rolling_min_dict[stk] < self.ma5_boost[stk]
        cond22 = last_px > self.ma5_boost[stk]

        all_cond = (cond1 & cond11 & cond12) | (cond1 & cond21 & cond22)
        return all_cond

    def generate_sell_signal(self, stk, last_px):
        pctchg = last_px / self.buy_price[stk] - 1
        if pctchg < -0.08:
            return True # 强制平仓8%
        if last_px > self.ma5[stk] * (1 + self.gain_closeout[stk]):
            return True
        if last_px > self.ma5[stk] * (1 - self.gain_closeout[stk]):
            return True
        return False

    def intra_monitor(self):

        while True:
            for stk in self.buy_list:
                # df = self.mdp.get_data_by_date("Kline1M4ZT", stockList.trans_int2windcode(stk), str(self.today_date)).set_index('MDTime')
                df = self.mdp.get_data_by_date('Stock', stockList.trans_int2windcode(stk), str(self.today_date), ["3"])
                last_px = df.iloc[-1]['LastPx']

                self.update_rolling_min(stk, last_px)
                buy_signal = self.generate_buy_signal(stk, last_px)

                if buy_signal:
                    order_dict = dict()
                    order_dict['portfolio'] = '20100'
                    order_dict['symbol'] = stockList.trans_int2windcode(stk)
                    target_dict = dict()
                    target_dict['StartTime'] = DtUtil.get_standard_HMS()
                    target_dict['EndTime'] = DtUtil.get_standard_HMS(delta=10)
                    target_dict['TargetQty'] = np.floor(self.per_amt[stk] / last_px / 100)
                    order_dict['target'] = target_dict
                    print(order_dict)

            for stk in self.sell_list:
                df = self.mdp.get_data_by_date('Stock', stockList.trans_int2windcode(stk), str(self.today_date), ["3"])
                last_px = df.iloc[-1]['LastPx']
                sell_signal = self.generate_sell_signal(stk, last_px)
                if sell_signal:
                    order_dict = dict()
                    order_dict['portfolio'] = '20100'
                    order_dict['symbol'] = stockList.trans_int2windcode(stk)
                    target_dict = dict()
                    target_dict['StartTime'] = DtUtil.get_standard_HMS()
                    target_dict['EndTime'] = DtUtil.get_standard_HMS(delta=10)
                    target_dict['TargetQty'] = -self.vol[stk]
                    order_dict['target'] = target_dict
                    print(order_dict)

if __name__ == '__main__':
    sim = Simulator()
    sim.daily_reset()
    sim.intra_monitor()