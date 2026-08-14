# coding: utf-8
# Author：fengchi863
# Date ：2021/6/17 10:25

import os, sys
sys.path.append('/data/user/015614/MyWork')
sys.path.append('/data/user/015614/MyWork/ShortTermTrading')
sys.path.append('/data/user/015614/MyWork/FaaMonitor')

from ShortTermTrading.dataApi import getData, tradeDate, stockList
from FaaMonitor.Util.DtUtil import DtUtil
from realtimeApi.getdata_from_open import get_stock_factor, data_prepare
from ShortTermTrading.Util.tools import get_stock_name
from xquant.factordata import FactorData
from ShortTermTrading.Util.tools import send_message
import pandas as pd
import time


class TrendStockMonitor:
    def __init__(self, buy_list:list, sell_list:list):

        today_date = DtUtil.get_today_date()
        yes_date = DtUtil.get_yesterday_date()
        shift_date = tradeDate.get_pre_trade_date(yes_date, 100)
        date_list = tradeDate.get_date_range(shift_date, yes_date)
        daily_st = stockList.clean_stock_list(no_pause=False, no_ST=True, least_live_days=0, start_date=shift_date,
                                    end_date=yes_date)
        stk_list = sorted(daily_st.columns.tolist())

        daily_close_badj = getData.get_daily_1factor('close_badj', code_list=stk_list, date_list=date_list)
        daily_ma5_badj = daily_close_badj.rolling(5).mean() # 用当天收盘价计算的ma5

        pre_close = data_prepare(str(today_date))['pre_close']
        pre_close = pre_close.droplevel(0)
        pre_close.index = pre_close.index.map(stockList.trans_windcode2int)

        fd = FactorData()
        s_trading_day = [str(today_date)]
        adjfactor = fd.get_factor_value('Basic_factor', mddate=s_trading_day, factor_names=['mdc_adjfactor'])
        adjfactor = adjfactor.loc[str(today_date)]

        self.today_date = today_date
        self.yes_date = yes_date
        self.date_list = date_list
        self.buy_list = buy_list
        self.sell_list = sell_list
        self.daily_st = daily_st
        self.daily_ma5_badj = daily_ma5_badj
        self.daily_close_badj = daily_close_badj
        self.pre_close = pre_close
        self.stk_list = stk_list
        self.daily_stock = list(set(buy_list + sell_list))
        self.adjfactor = adjfactor

    def start_intra_monitor(self):
        # 判断买入条件
        has_send_message = list()
        s_ma5 = self.daily_ma5_badj.loc[self.yes_date, self.daily_stock]
        s_ma5.index = s_ma5.index.map(stockList.trans_int2windcode)
        s_ma5_boost = s_ma5 * 1.005 # 这个数字能决定日内触发的多少
        while True:
            t1 = time.time()

            # 完善的退出机制
            if DtUtil.get_now_hm() > 1500:
                print('终于收盘了，辛劳的一天终于结束了，可以把资源释放出来了')
                break
            elif DtUtil.get_now_hm() < 930:
                continue

            daily_stock = list(map(stockList.trans_int2windcode, self.daily_stock))
            df = get_stock_factor(['ClosePx'], daily_stock)

            # 买入判断1
            self.pre_close.index = self.pre_close.index.map(stockList.trans_int2windcode)
            intra_pct = df['ClosePx'] / self.pre_close[daily_stock] - 1
            intra_close_expanding_min = df['ClosePx'].expanding().min() * self.adjfactor.loc[daily_stock].T.values
            intra_pct_expanding_min = intra_pct.expanding().min()
            low_pct_judge = intra_pct_expanding_min < -0.01 # 条件一
            ma5_judge = intra_close_expanding_min.iloc[-1] < s_ma5_boost # 条件二：此处要设置赋权因子
            ma5_boost_judge = (df['ClosePx'].iloc[-1] * self.adjfactor.loc[daily_stock, 'mdc_adjfactor'] / intra_close_expanding_min.iloc[-1] - 1) > 0.01 # 条件三
            ma5_judge2 = df['ClosePx'].iloc[-1] * self.adjfactor.loc[daily_stock, 'mdc_adjfactor'] > s_ma5_boost # 条件四：此处要设置赋权因子
            all_cond1 = low_pct_judge.iloc[-1] & ma5_judge & ma5_boost_judge & ma5_judge2

            # 买入判断2
            ma5_judge = intra_close_expanding_min.iloc[-1] < s_ma5  # 条件二：此处要设置赋权因子
            ma5_judge2 = df['ClosePx'].iloc[-1] * self.adjfactor.loc[daily_stock, 'mdc_adjfactor'] > s_ma5  # 条件四：此处要设置赋权因子
            all_cond2 = low_pct_judge.iloc[-1] & ma5_judge & ma5_boost_judge & ma5_judge2

            all_cond = all_cond1 | all_cond2
            buy_check = all_cond[all_cond]

            if len(buy_check) > 0:
                for stk_code in buy_check.index.tolist():
                    if stockList.trans_windcode2int(stk_code) in self.buy_list and \
                            stk_code not in has_send_message:
                        message = '趋势股T+N策略触发买入：' + \
                                  '个股为%s，' % get_stock_name(stk_code) + \
                                  '买入价格为%d' % self.get_latest_price(df['ClosePx'], stk_code)
                        send_message(['015614', '015624'], message)
                        has_send_message.append(stk_code)
                        print('已满足低吸条件，买入%s' % get_stock_name(stk_code))

            ma5_pct = df['ClosePx'].iloc[-1] * self.adjfactor.loc[daily_stock, 'mdc_adjfactor'] / s_ma5 - 1
            ma5_judge3 = (ma5_pct > 0.05) | (ma5_pct < -0.05) # 依靠ma5设置止盈点和止损点
            sell_check = ma5_judge3[ma5_judge3]

            if len(sell_check) > 0:
                for stk_code in sell_check.index.tolist():
                    if stockList.trans_windcode2int(stk_code) in self.sell_list and \
                            stk_code not in has_send_message:
                        message = '趋势股T+N策略触发卖出：' + \
                                  '个股为%s，' % get_stock_name(stk_code) + \
                                  '卖出价格为%d' % self.get_latest_price(df['ClosePx'], stk_code)
                        send_message(['015614', '015624'], message)
                        has_send_message.append(stk_code)
                        print('已满足卖出条件，卖出%s' % get_stock_name(stk_code))

            # print('一轮时间%d', time.time() - t1) # 2s

    @staticmethod
    def get_latest_price(df, stk_code):
        res = df.iloc[-1][stk_code]
        if type(res) == pd.Series:
            return res.values[0]
        else:
            return res

if __name__ == '__main__':
    daily_trade_prepare = pd.read_excel('/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/daily_trade_prepare/daily_trade_prepare.xlsx',
                  sheet_name='交易准备')
    buy_list = list(set(daily_trade_prepare['买入股票代码'].dropna().map(int).tolist()))
    sell_list = list(set(daily_trade_prepare['卖出股票代码'].dropna().map(int).tolist()))
    # buy_list = [300590, 603236, 300638, 603486, 688169, 688696, 600809, 600132, 600600, 600460, 300782, 2371, 300363,
    #             600763, 601127, 300077, 300223, 300782, 603260]
    # # buy_list = [600809] # 调试一只股票用
    # sell_list = []
    tsm = TrendStockMonitor(buy_list, sell_list)
    tsm.start_intra_monitor()