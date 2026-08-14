# coding: utf-8
# Author：fengchi863
# Date ：2020/11/11 15:14

# coding: utf-8
# Author：fengchi863
# Date ：2020/11/4 15:32

import logging
import os
import sys
import time

sys.path.append("/data/user/fengchi/MyWork/")
sys.path.append("/data/user/fengchi/MyWork/StrongStockModel/")
sys.path.append('/data/group/800319')

from StrongStockModel.backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, EvaluationHelper
from StrongStockModel.dataApi import getData
import pandas as pd, numpy as np
import random

random.seed(2020)


def generate_logger(output_dir, file_name):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    log_name = output_dir + '%s.log' % file_name
    fh = logging.FileHandler(log_name, mode='w')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


start_date = 20140101
end_date = 20161231

run_date = 20201105
run_datetime = 202011111100

pattern_name = '大盘逆势上涨'
holding_day = 1

root_path = '/data/group/800319/fengchi/pattern_test/'

pickle_path = root_path + '/%s/%s/个股_%d_%d/' % (pattern_name, run_date, start_date, end_date)
mkt_stmt_path = '/data/group/800319/市场情绪与概念板块/历史EMA市场情绪.h5'

stk_df_path = '/data/group/800319/fengchi/pattern_test/%s/%s/股票池_%d_%d/stk_df.pkl' % (
    pattern_name, run_date, start_date, end_date)

output_dir = root_path + '%s/%s/结果_%d_%d_%d/' % (pattern_name, run_date, start_date, end_date, run_datetime)

output_path = output_dir + '回测结果_%d_%d_%d_%d.xlsx' % (holding_day, start_date, end_date, run_datetime)

log_path = output_dir + '回测日志_%d_%d_%d_%d.log' % (holding_day, start_date, end_date, run_datetime)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

class SignalPortfolio(PortfolioStrategyBase):

    def __init__(self, signal, start=20140101, end=20181231, max_amt=400000000, per_amt=1000000, stock_pool=None,
                 target_point=None,
                 buy_cost=0.001, sell_cost=0.001, log_output=False):
        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost, per_amt)
        self.log_output = log_output
        if log_output:
            self.logger = generate_logger(output_dir,
                                          '回测日志_%d_%d_%d_%d' % (holding_day, start_date, end_date, run_datetime))
        self.mkt_stmt = pd.read_hdf(mkt_stmt_path, '历史EMA市场情绪')
        self.signal = signal.reindex(self.close.index).fillna(0)
        self.stk_list = list(set(self.signal.columns.tolist()).intersection(set(self.stock_pool.columns.tolist())))
        self.data_flow['signal'] = None
        self.last_buy_time = {}
        self.max_amt = max_amt
        self.deal_price_record = pd.Series(index=self.stk_list)

    def sell_action(self, stk, vol=None):
        if stk not in self.last_buy_time:
            raise Exception('Last buy time is not recorded')
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) >= 1:
            _, deal_price = self.sell(stk, vol)
            self.deal_price_record[stk] = np.nan

    def buy_action(self, stk, vol=None):
        deal_vol, deal_price = self.buy(stk, vol)
        if deal_vol > 0:
            self.last_buy_time[stk] = self.datetime
            self.deal_price_record[stk] = deal_price

    def get_curr_msmt_max_amt(self, date, time_point):
        tmp_mkt_stmt = self.mkt_stmt.loc[date, time_point].values[0]
        if tmp_mkt_stmt >= 8:
            coef = 1.0
        elif 6 <= tmp_mkt_stmt < 8:
            coef = 0.75
        elif 4 <= tmp_mkt_stmt < 6:
            coef = 0.5
        elif 1 <= tmp_mkt_stmt < 4:
            coef = 0.25
        elif 0 <= tmp_mkt_stmt < 1:
            coef = 0.0
        return coef * self.max_amt

    def get_can_buy_amt(self, curr_max_amt):
        curr_available_amt = (
                    pd.Series(self.available).reindex(index=self.stk_list) * pd.Series(self.deal_price_record)).sum()
        curr_holding_amt = (pd.Series(self.holding) * pd.Series(self.deal_price_record)).sum()
        if curr_available_amt >= 0 and curr_holding_amt >= curr_max_amt:
            can_buy_amt = min(curr_max_amt * 0.2, curr_available_amt)
        elif curr_available_amt == 0 and curr_holding_amt >= curr_max_amt:
            can_buy_amt = 0
        elif curr_holding_amt < curr_max_amt:
            can_buy_amt = curr_max_amt - curr_holding_amt
        return can_buy_amt

    def daily_update(self, idx, date):
        super().daily_update(idx, date)
        self.preday = getData.get_pre_trade_date(date)
        self.data_flow['signal'] = self.signal[self.date_idx * self.step:(self.date_idx + 1) * self.step][self.stk_list]
        if self.data_flow['signal'].index[0][0] != self.date or self.data_flow['signal'].index[-1][0] != self.date:
            raise Exception('Broadcast date and signal date are not matched!')
        if self.holding == {} and self.data_flow['signal'].sum().sum() == 0:
            return

    def bar_handler(self):
        date, time_point, date_idx, time_idx = self.datetime
        signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
        signal = signal[signal.eq(1)]
        buy_stk_list = []
        for stk in signal.index:
            if stk not in self.holding:
                # TODO: 获取当前分钟内满足条件的股票池列表，存入buy_stk_list
                buy_stk_list.append(stk)
        curr_msmt_max_amt = self.get_curr_msmt_max_amt(date, time_point)
        can_buy_amt = self.get_can_buy_amt(curr_msmt_max_amt)
        if time_point == 930:
            print('\n%s可以买的金额' % str(date), str(can_buy_amt))
        if len(buy_stk_list) * self.per_amt > can_buy_amt:
            can_buy_num = can_buy_amt // self.per_amt
            random.shuffle(buy_stk_list)
            print('\n买不起, 本可以买%d只，只能买%d只' % (len(buy_stk_list), can_buy_num))
            if len(buy_stk_list) == 0:
                buy_stk_list = []
            else:
                buy_stk_list = buy_stk_list[:int(can_buy_num)]

        for stk in buy_stk_list:
            self.buy_action(stk)

        sell_list = [k for k, v in self.available.items() if v != 0]
        for stk in sell_list:
            # 卖出函数可输入具体卖出手数，该参数默认为None, 如不输入，则默认卖出所有持仓
            # TODO: 卖出股票
            self.sell_action(stk)


def main():
    signal = pd.read_pickle(stk_df_path)
    sp_inst = SignalPortfolio(signal, start_date, end_date, per_amt=1000000, log_output=True)
    helper = EvaluationHelper()

    e = time.time()
    record = sp_inst.run_backtest(24)
    helper.one_wave_run(record, kernel=24, output_path=output_path, signal_record_save=True)
    print(time.time() - e)


if __name__ == "__main__":
    main()
