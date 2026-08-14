# coding: utf-8
# Author：fengchi863
# Date ：2020/11/4 15:32

import logging
import os
import sys
import time

sys.path.append("/data/user/015614/MyWork/")
sys.path.append("/data/user/015614/MyWork/StrongStockModel/")
sys.path.append('/data/group/800319')

from StrongStockModel.backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, EvaluationHelper
from StrongStockModel.dataApi import getData
import pandas as pd, numpy as np


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


start_date = 20170101
end_date = 20191231

run_date = 20201105
run_datetime = 202011021935

pattern_name = '大盘逆势上涨'
holding_day = 3

root_path = '/data/group/800319/fengchi/pattern_test/'

pickle_path = root_path + '/%s/%s/个股_%d_%d/' % (pattern_name, run_date, start_date, end_date)

stk_df_path = '/data/group/800319/fengchi/pattern_test/%s/%s/股票池_%d_%d/stk_df.pkl' % (
    pattern_name, run_date, start_date, end_date)

output_dir = root_path + '%s/%s/结果_%d_%d_%d/' % (pattern_name, run_date, start_date, end_date, run_datetime)

output_path = output_dir + '回测结果_%d_%d_%d_%d.xlsx' % (holding_day, start_date, end_date, run_datetime)

log_path = output_dir + '回测日志_%d_%d_%d_%d.log' % (holding_day, start_date, end_date, run_datetime)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# logger = generate_logger(output_dir, '回测日志_%d_%d_%d_%d' % (holding_day, start_date, end_date, run_datetime))

class SignalPortfolio(PortfolioStrategyBase):

    def __init__(self, signal, start=20140101, end=20181231, stock_pool=None, target_point=None, buy_cost=0.001,
                 sell_cost=0.001):
        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost)
        self.signal = signal.reindex(self.close.index).fillna(0)
        self.stk_list = self.signal.columns.tolist()
        self.data_flow['signal'] = None
        self.last_buy_time = {}
        self.buy_amt = pd.Series()
        self.profit = pd.Series()

    def sell_action(self, stk, vol=None):
        if stk not in self.last_buy_time:
            raise Exception('Last buy time is not recorded')
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) > 1 or ((bar_date_idx - date_idx) == 1 and bar_time >= time_point):
            self.sell(stk, vol)

    def buy_action(self, stk, vol=None):
        deal_vol = self.buy(stk, vol)
        if deal_vol > 0:
            self.last_buy_time[stk] = self.datetime

    def daily_update(self, idx, date):
        super().daily_update(idx, date)
        self.preday = getData.get_pre_trade_date(date)
        self.data_flow['signal'] = self.signal[self.date_idx * self.step:(self.date_idx + 1) * self.step]
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

        # 涨速
        self.pctchg_speed_1m = self.stk_minute_close_badj.pct_change(1)
        self.pctchg_speed_2m = self.stk_minute_close_badj.pct_change(2)
        self.pctchg_speed_3m = self.stk_minute_close_badj.pct_change(3)
        self.pctchg_speed_4m = self.stk_minute_close_badj.pct_change(4)
        self.pctchg_speed_5m = self.stk_minute_close_badj.pct_change(5)

        self.stk_amt_rolling10 = self.stk_minute_amt.shift(1).rolling(10).mean()
        self.stk_amt_rolling_1m_mean = self.stk_minute_amt.shift(1).rolling(1).mean()
        self.stk_amt_rolling_2m_mean = self.stk_minute_amt.shift(1).rolling(2).mean()
        self.stk_amt_rolling_3m_mean = self.stk_minute_amt.shift(1).rolling(3).mean()
        self.stk_amt_rolling_4m_mean = self.stk_minute_amt.shift(1).rolling(4).mean()
        self.stk_amt_rolling_5m_mean = self.stk_minute_amt.shift(1).rolling(5).mean()

    def bar_handler(self):
        date, time_point, date_idx, time_idx = self.datetime
        signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
        signal = signal[signal.eq(1)]
        for stk in signal.index:
            if stk not in self.holding:
                # 只检查外部股票池下面的买入条件是否满足
                sort_dict = {1: self.pctchg_speed_1m.at[(date, time_point), stk],
                             2: self.pctchg_speed_2m.at[(date, time_point), stk],
                             3: self.pctchg_speed_3m.at[(date, time_point), stk],
                             4: self.pctchg_speed_4m.at[(date, time_point), stk],
                             5: self.pctchg_speed_5m.at[(date, time_point), stk]}
                sort_dict = sorted(sort_dict.items(), key=lambda x: x[1], reverse=True)
                if sort_dict[0][1] > 0.02:
                    if time_point < 940:
                        self.buy_action(stk)
                        return
                    max_up_minute_window = sort_dict[0][0]
                    if max_up_minute_window == 1:
                        if (self.stk_amt_rolling_1m_mean.at[(date, time_point), stk] /
                            self.stk_amt_rolling10.loc[(date, time_point), stk]) < 0.8:
                            return
                    if max_up_minute_window == 2:
                        if (self.stk_amt_rolling_2m_mean.at[(date, time_point), stk] /
                            self.stk_amt_rolling10.loc[(date, time_point), stk]) < 0.8:
                            return
                    if max_up_minute_window == 3:
                        if (self.stk_amt_rolling_3m_mean.at[(date, time_point), stk] /
                            self.stk_amt_rolling10.loc[(date, time_point), stk]) < 0.8:
                            return
                    if max_up_minute_window == 4:
                        if (self.stk_amt_rolling_4m_mean.at[(date, time_point), stk] /
                            self.stk_amt_rolling10.loc[(date, time_point), stk]) < 0.8:
                            return
                    if max_up_minute_window == 5:
                        if (self.stk_amt_rolling_5m_mean.at[(date, time_point), stk] /
                            self.stk_amt_rolling10.loc[(date, time_point), stk]) < 0.8:
                            return
                    self.buy_action(stk)
                else:
                    return
        for stk in list(self.available.keys()):
            # 卖出函数可输入具体卖出手数，该参数默认为None, 如不输入，则默认卖出所有持仓
            if self.stk_minute_limit_up_bool_prod.at[(date, time_point), stk] != 1 and \
                    self.stk_pctchg.loc[(date, time_point), stk] > 0.07:  # 止盈条件
                print(stk, date, time_point, '止盈卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',止盈卖出')
                self.sell_action(stk)
            # 低开幅度小于-4%，卖出
            if self.stk_pctchg.at[(date, time_point), stk] < -0.04:  # 止损条件
                print(stk, date, time_point, '低开或下跌卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',低开或下跌卖出')
                self.sell_action(stk)
            # 早盘高开5%以上，9:40分涨跌幅小于5%就卖出
            if time_point == 940 and (self.stk_pctchg.at[(date, 930), stk] > 0.05) and (
                    self.stk_pctchg.at[(date, 940), stk] < 0.05):  # 止损条件
                print(stk, date, time_point, '早盘高开回落卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',早盘高开回落卖出')
                self.sell_action(stk)
            # 9:50后如果个股当前涨跌幅小于0，且个股在均线下方的时间>60%，卖出
            if time_point > 1030 and self.stk_minute_vwap_pct.at[(date, time_point), stk] > 0.6:
                print(stk, date, time_point, '均线不满足卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',均线不满足卖出')
                self.sell_action(stk)
            # 9:50后个股相对于大盘的超额收益<0 且 时间占比超过50%，卖出
            if time_point > 1030 and self.alpha_pct.at[(date, time_point), stk] > 0.5:
                print(stk, date, time_point, '超额不满足卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',超额不满足卖出')
                self.sell_action(stk)
            if self.stk_minute_limit_up_bool_prod.at[(date, 930), stk] == 1 and \
                    self.stk_minute_limit_up_bool_prod.loc[(date, time_point), stk] == 0:
                print(stk, date, time_point, '封板涨停卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',封板涨停卖出')
                self.sell_action(stk)
            if getData.get_trade_date_interval(date, base_date=self.last_buy_time[stk][0]) == holding_day - 1:
                print(stk, date, time_point, '强制平仓卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',强制平仓卖出')
                self.sell_action(stk)


def main():
    signal = pd.read_pickle(stk_df_path)
    sp_inst = SignalPortfolio(signal, start_date, end_date)
    helper = EvaluationHelper()

    e = time.time()
    record = sp_inst.run_backtest(24)
    helper.one_wave_run(record, kernel=24, output_path=output_path, signal_record_save=True)
    print(time.time() - e)


if __name__ == "__main__":
    main()
