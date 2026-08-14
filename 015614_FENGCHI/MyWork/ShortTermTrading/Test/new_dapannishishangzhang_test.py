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

run_date = 20201111
run_datetime = 202011112100

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

    def __init__(self, signal, start=20140101, end=20181231, max_amt=100000000, per_amt=1000000, stock_pool=None,
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

    def buy_action(self, stk, vol=None, amt=None):
        deal_vol, deal_price = self.buy(stk, vol, amt)
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
                pd.Series(self.available).reindex(index=self.stk_list) * self.deal_price_record).sum()
        curr_holding_amt = (pd.Series(self.holding).reindex(index=self.stk_list) * self.deal_price_record).sum()
        if curr_available_amt >= 0 and curr_holding_amt >= curr_max_amt:
            can_buy_amt = curr_max_amt + min(curr_max_amt * 0.2, curr_available_amt) - curr_holding_amt
        elif curr_available_amt == 0 and curr_holding_amt >= curr_max_amt:
            can_buy_amt = 0
        elif curr_holding_amt < curr_max_amt:
            can_buy_amt = curr_max_amt - curr_holding_amt

        if can_buy_amt < 0:
            can_buy_amt = 0

        return can_buy_amt

    def get_stk_amt(self, date, time_point):
        tmp_mkt_stmt = self.mkt_stmt.loc[date, time_point].values[0]
        if tmp_mkt_stmt >= 8:
            stk_amt = 4000000
        elif 6 <= tmp_mkt_stmt < 8:
            stk_amt = 3000000
        elif 4 <= tmp_mkt_stmt < 6:
            stk_amt = 2000000
        elif 1 <= tmp_mkt_stmt < 4:
            stk_amt = 1000000
        elif 0 <= tmp_mkt_stmt < 1:
            stk_amt = 0
        return stk_amt

    def daily_update(self, idx, date):
        super().daily_update(idx, date)
        self.preday = getData.get_pre_trade_date(date)
        self.data_flow['signal'] = self.signal[self.date_idx * self.step:(self.date_idx + 1) * self.step][self.stk_list]
        if self.data_flow['signal'].index[0][0] != self.date or self.data_flow['signal'].index[-1][0] != self.date:
            raise Exception('Broadcast date and signal date are not matched!')
        if self.holding == {} and self.data_flow['signal'].sum().sum() == 0:
            return
        # 每天额外更新数据
        self.stk_minute_close = getData.get_minute_1factor('close', start_datetime=date * 10000 + 930,
                                                           end_datetime=date * 10000 + 1500,
                                                           code_list=self.stk_list)
        self.stk_minute_amt = getData.get_minute_1factor('amt', start_datetime=date * 10000 + 930,
                                                         end_datetime=date * 10000 + 1500,
                                                         code_list=self.stk_list)
        self.stk_minute_vol = getData.get_minute_1factor('vol', start_datetime=date * 10000 + 930,
                                                         end_datetime=date * 10000 + 1500,
                                                         code_list=self.stk_list)
        self.stk_pre_close = getData.get_daily_1factor('pre_close_badj', date_list=[date], code_list=self.stk_list)
        self.stk_minute_close_badj = getData.get_minute_1factor('close_badj', start_datetime=date * 10000 + 930,
                                                                end_datetime=date * 10000 + 1500,
                                                                code_list=self.stk_list)

        # 小于均线的比例
        self.stk_pctchg = self.stk_minute_close_badj / self.stk_pre_close.values - 1
        self.stk_minute_vwap = pd.DataFrame(self.stk_minute_amt.cumsum() / self.stk_minute_vol.cumsum())
        self.stk_minute_vwap_bool = self.stk_minute_close_badj < self.stk_minute_vwap
        self.stk_minute_vwap_bool['count'] = 1
        self.stk_minute_vwap_pct = (self.stk_minute_vwap_bool.expanding().sum().T / \
                                    self.stk_minute_vwap_bool['count'].expanding().sum().values).T

        # 相对大盘的超额收益
        self.mkt_pre_close = \
            getData.get_daily_1factor('close', [self.preday], code_list=['SZZZ'], type='bench').values[0][0]
        self.mkt_minute_close = getData.get_minute_1factor('close', code_list=['SZZZ'],
                                                           start_datetime=date * 10000 + 930,
                                                           end_datetime=date * 10000 + 1500,
                                                           base_date=20100101, type='bench')
        self.mkt_minute_pctchg = self.mkt_minute_close / self.mkt_pre_close - 1
        self.alpha = pd.DataFrame(self.stk_pctchg.sub(self.mkt_minute_pctchg['SZZZ'], axis=0))
        self.alpha_bool = self.alpha < 0
        self.alpha['count'] = 1
        self.alpha_pct = (self.alpha.expanding().sum().T / self.alpha['count'].expanding().sum().values).T

        # 今日涨停价
        self.up_limit_price = ((self.stk_pre_close * 100 * 1.1 + 0.5) / 100).apply(np.floor)
        self.stk_minute_limit_up_bool = self.stk_minute_close_badj == self.up_limit_price.values
        self.stk_minute_limit_up_bool_prod = self.stk_minute_limit_up_bool.cumprod()


    def bar_handler(self):
        date, time_point, date_idx, time_idx = self.datetime
        signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
        signal = signal[signal.eq(1)]
        buy_stk_list = []
        for stk in signal.index:
            if stk not in self.holding:
                # 只检查外部股票池下面的买入条件是否满足
                buy_stk_list.append(stk)
        curr_msmt_max_amt = self.get_curr_msmt_max_amt(date, time_point)
        can_buy_amt = self.get_can_buy_amt(curr_msmt_max_amt)
        can_stk_amt = self.get_stk_amt(date, time_point)
        if time_point == 930:
            print('\n%s可以买的金额' % str(date), str(can_buy_amt))

        if len(buy_stk_list) * can_stk_amt > can_buy_amt:
            if can_stk_amt == 0:
                can_buy_num = 0
            else:
                can_buy_num = can_buy_amt // can_stk_amt
            random.shuffle(buy_stk_list)
            print('\n买不起, 本可以买%d只，只能买%d只' % (len(buy_stk_list), can_buy_num))
            if len(buy_stk_list) == 0:
                buy_stk_list = []
            else:
                buy_stk_list = buy_stk_list[:int(can_buy_num)]

        for stk in buy_stk_list:
            self.buy_action(stk, amt=can_stk_amt)

        sell_list = [k for k, v in self.available.items() if v != 0]
        for stk in sell_list:
            # 卖出函数可输入具体卖出手数，该参数默认为None, 如不输入，则默认卖出所有持仓
            if self.stk_minute_limit_up_bool_prod.at[(date, time_point), stk] != 1 and \
                    self.stk_pctchg.at[(date, time_point), stk] > 0.07:  # 止盈条件
                # print(stk, date, time_point, '止盈卖出')
                if self.log_output:
                    self.logger.info(str(stk) + ',' + str(date) + ',' + str(time_point) + ',止盈卖出')
                self.sell_action(stk)
                continue
            # 早盘高开5%以上，9:40分涨跌幅小于4%就卖出
            if time_point >= 940 and (self.stk_pctchg.at[(date, 930), stk] > 0.05) and (
                    self.stk_pctchg.at[(date, time_point), stk] < 0.04):  # 止损条件
                # print(stk, date, time_point, '早盘高开回落卖出')
                if self.log_output:
                    self.logger.info(str(stk) + ',' + str(date) + ',' + str(time_point) + ',早盘高开回落卖出')
                self.sell_action(stk)
                continue
            # 低开幅度小于-4%，卖出
            if self.stk_pctchg.at[(date, time_point), stk] < -0.035:  # 止损条件
                # print(stk, date, time_point, '低开或下跌卖出')
                if self.log_output:
                    self.logger.info(str(stk) + ',' + str(date) + ',' + str(time_point) + ',低开或下跌卖出')
                self.sell_action(stk)
                continue
            # 9:50后如果个股当前涨跌幅小于0，且个股在均线下方的时间>60%，卖出
            if time_point >= 1030 and self.stk_minute_vwap_pct.at[(date, time_point), stk] > 0.6:
                # print(stk, date, time_point, '均线不满足卖出')
                if self.log_output:
                    self.logger.info(str(stk) + ',' + str(date) + ',' + str(time_point) + ',均线不满足卖出')
                self.sell_action(stk)
                continue
            # 9:50后个股相对于大盘的超额收益<0 且 时间占比超过50%，卖出
            if time_point >= 1030 and self.alpha_pct.at[(date, time_point), stk] > 0.5:
                # print(stk, date, time_point, '超额不满足卖出')
                if self.log_output:
                    self.logger.info(str(stk) + ',' + str(date) + ',' + str(time_point) + ',超额不满足卖出')
                self.sell_action(stk)
                continue
            if self.stk_minute_limit_up_bool_prod.at[(date, 930), stk] == 1 and \
                    self.stk_minute_limit_up_bool_prod.at[(date, time_point), stk] == 0:
                # print(stk, date, time_point, '涨停烂板卖出')
                if self.log_output:
                    self.logger.info(str(stk) + ',' + str(date) + ',' + str(time_point) + ',涨停烂板卖出')
                self.sell_action(stk)
                continue
            if time_point == 1455 and \
                    getData.get_trade_date_interval(date, base_date=self.last_buy_time[stk][0]) == holding_day - 1 and \
                    self.stk_minute_limit_up_bool.at[(date, 1454), stk] != 1:
                # print(stk, date, time_point, '强制平仓卖出')
                if self.log_output:
                    self.logger.info(str(stk) + ',' + str(date) + ',' + str(time_point) + ',强制平仓卖出')
                self.sell_action(stk)
                continue


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
