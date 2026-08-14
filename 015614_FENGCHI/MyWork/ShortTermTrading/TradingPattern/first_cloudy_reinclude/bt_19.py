# coding: utf-8
# Author：fengchi863
# Date ：2020/12/29 11:09

import os
import sys
import time
import logging

sys.path.append("/data/user/fengchi/MyWork/")
sys.path.append("/data/user/fengchi/MyWork/StrongStockModel/")
sys.path.append('/data/group/800319')
from backtest.StrategyBackTest.StockStrategyBase import StockStrategyBase
import pandas as pd, numpy as np
from backtest.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
from dataApi import stockList, getData


# def generate_logger(output_dir, file_name):
#     logger = logging.getLogger()
#     logger.setLevel(logging.INFO)
#     rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
#     log_name = output_dir + '%s.log' % file_name
#     fh = logging.FileHandler(log_name, mode='w')
#     fh.setLevel(logging.DEBUG)
#     formatter = logging.Formatter("%(levelname)s: %(message)s")
#     fh.setFormatter(formatter)
#     logger.addHandler(fh)
#     return logger


start_date = 20200101
end_date = 20201201

run_date = 20201229
run_datetime = 202012291500

pattern_name = '分歧转一致'
holding_day = 1

root_path = '/data/group/800319/fengchi/pattern_test/'

pickle_path = root_path + '/%s/%s/个股_%d_%d/' % (pattern_name, run_date, start_date, end_date)

stk_df_path = root_path + '%s/%s/外部股票池_%d_%d/stk_df.pkl' % (pattern_name, run_date, start_date, end_date)

output_dir = root_path + '%s/%s/结果_%d_%d_%d/' % (pattern_name, run_date, start_date, end_date, run_datetime)

output_path = output_dir + '回测结果_%d_%d_%d_%d.xlsx' % (holding_day, start_date, end_date, run_datetime)

log_path = output_dir + '回测日志_%d_%d_%d_%d.log' % (holding_day, start_date, end_date, run_datetime)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# logger = generate_logger(output_dir, '回测日志_%d_%d_%d_%d' % (holding_day, start_date, end_date, run_datetime))


class StockStrategyDemo(StockStrategyBase):

    def __init__(self, stk, start_date, end_date, price_rolling_window=10, amt_per_signal=5000000, available_flag=None,
                 isin_pool_flag=None):
        super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag,
                         isin_pool_flag)
        if self.market_flow is None:
            return
        self.signal = pd.read_pickle(pickle_path + ('%s.pkl' % stk)).loc[self.date_list]
        self.stock = stk
        self.last_buy_time = None

    def daily_update(self):
        # 每天基类会更新行情数据，此函数用于每天额外更新策略中需要使用的数据，如没有额外需要使用的数据，可不定义该函数
        # 每天额外更新数据
        self.stk_minute = getData.get_minute_1stock(self.stk_id, start_datetime=self.trading_day * 10000 + 925,
                                                    end_datetime=self.trading_day * 10000 + 1500,
                                                    factor_list=['close', 'amt', 'vol'])
        self.stk_adj_factor = getData.get_daily_1stock(self.stk_id, factor_list=['adjfactor'],
                                                       date_list=[self.trading_day]).values[0][0]
        self.stk_pre_close = getData.get_daily_1stock(self.stk_id, factor_list=['pre_close_badj'],
                                                      date_list=[self.trading_day]).values[0][0]
        self.stk_minute['close_badj'] = self.stk_minute['close'] * self.stk_adj_factor

        # 小于均线的比例
        self.stk_pctchg = self.stk_minute['close_badj'] / self.stk_pre_close - 1
        self.withdraw = self.stk_pctchg - self.stk_pctchg.expanding().max()
        self.stk_minute_vwap = pd.DataFrame(self.stk_minute['amt'].cumsum() / self.stk_minute['vol'].cumsum(),
                                            columns=['vwap'])
        self.stk_minute_vwap['less_vwap'] = self.stk_minute['close_badj'] < self.stk_minute_vwap['vwap']
        self.stk_minute_vwap['count'] = 1
        self.stk_minute_vwap['less_vwap_pct'] = self.stk_minute_vwap['less_vwap'].expanding().sum() / \
                                                self.stk_minute_vwap['count'].expanding().sum()

        # 相对大盘的超额收益
        self.mkt_pre_close = \
            getData.get_daily_1factor('close', [self.preday], code_list=['SZZZ'], type='bench').values[0][0]
        self.mkt_minute_close = getData.get_minute_1factor('close', code_list=['SZZZ'],
                                                           start_datetime=self.trading_day * 10000 + 925,
                                                           end_datetime=self.trading_day * 10000 + 1500,
                                                           base_date=20100101, type='bench')
        self.mkt_minute_pctchg = self.mkt_minute_close / self.mkt_pre_close - 1
        self.alpha = pd.DataFrame(self.stk_pctchg - self.mkt_minute_pctchg['SZZZ'], columns=['alpha'])
        self.alpha['count'] = 1
        self.alpha['less_alpha'] = self.alpha['alpha'] < 0
        self.alpha['alpha_pct'] = self.alpha['less_alpha'].expanding().sum() / self.alpha['count'].expanding().sum()

        # 今日涨停价
        self.up_limit_price = np.floor(self.stk_pre_close * 100 * 1.1 + 0.5) / 100
        self.stk_minute['is_limit_up'] = self.stk_minute['close_badj'] == self.up_limit_price
        self.stk_minute['continues_limit_up'] = self.stk_minute['is_limit_up'].cumprod()
        self.stk_minute['had_limit_up'] = self.stk_minute['is_limit_up'].expanding().max()

        return

    def bar_handler(self):
        # 每只股票每分钟信号逻辑定义
        if self.signal is None:
            return
        if not self.datetime in self.signal.index:
            return

        signal = self.signal.at[self.datetime, 'prediction']
        if signal == 1 and self.position['holding'] == 0:
            # 买入函数可输入具体买入手数，该参数默认为 None, 如不输入，则默认买入self.amt_per_signal/均价 （四舍五入到手）
            self.buy()
            self.last_buy_time = self.datetime[0]
        if self.position['available'] > 0:
            # 卖出函数可输入具体卖出手数，该参数默认为None, 如不输入，则默认卖出所有持仓
            # 低开幅度小于-4%，卖出
            if self.stk_pctchg.loc[self.datetime[0], 925] < -0.05:  # 止损条件
                print(self.stk_id, self.datetime, '开盘低开5个点卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',低开或下跌卖出')
                self.sell()
            if self.datetime[1] >= 940 and self.withdraw.loc[self.datetime[0], self.datetime[1]] < -0.04:  # 止盈条件
                print(self.stk_id, self.datetime, '日内回撤超限卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',止盈卖出')
                self.sell()
            if self.stk_minute['continues_limit_up'].loc[self.datetime[0], 930] == 1 and \
                    self.stk_minute['continues_limit_up'].loc[self.datetime[0], self.datetime[1]] == 0:
                print(self.stk_id, self.datetime, '涨停开盘盘中烂板卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',封板涨停卖出')
                self.sell()
            if self.stk_minute['had_limit_up'].loc[self.datetime[0], self.datetime[1]] == 1 and \
                    self.stk_minute['is_limit_up'].loc[self.datetime[0], self.datetime[1]] == 0:
                print(self.stk_id, self.datetime, '盘中涨停并烂板卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',盘中涨停并烂板卖出')
                self.sell()
            if self.datetime[1] == 1440 and \
                    getData.get_trade_date_interval(self.trading_day, base_date=self.last_buy_time) == holding_day - 1:
                print('强制平仓卖出')
                # logger.info(str(self.stk_id) + ',' + str(self.datetime) + ',强制平仓卖出')
                self.sell()


def start():
    """
    示例2：一波全回测评估并输出
    :return:
    """
    stock_pool = pd.read_pickle(stk_df_path)
    stock_pool.index = stock_pool.index.map(lambda x: int(x))
    stock_pool.columns = stock_pool.columns.map(lambda x: stockList.trans_windcode2int(x))
    stock_pool = (stock_pool.fillna(0)).astype(bool)

    is_valid = stock_pool
    file_list = os.listdir(pickle_path)
    file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
    stk_list = [int(x.strip('.pkl')) for x in file_list]

    strats = UniverseEvaluation(StockStrategyDemo, buy_cost_ratio=0.0005, sell_cost_ratio=0.001, available_info=None,
                                universe_info=is_valid)

    e = time.time()
    # 并行回测
    print('分歧转一致模式...回测开始')

    strats.one_wave_run(stk_list, start_date, end_date, kernel=24, output_path=output_path, mode='multi')

    print('strategy time:', time.time() - e)


if __name__ == "__main__":
    start()
