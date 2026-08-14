# @Time : 2020/8/31 15:04
# @Author : Zhichen Lu
# @File : StockStrategyBySignal.py
# @File : StockStrategyBySignalMultyTrigger.py

import sys
import os
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from backtest.StrategyBackTest.StockStrategyBase import StockStrategyBase
import pandas as pd
import time
from backtest.StrategyBackTest.UniverseEvaluation import UniverseEvaluation
from dataApi import tradeDate, stockList, dividend, indName, getData
from StrongStockModel.conf.path_config import root_path
from multiprocessing import Manager
import itertools
from dataApi.stockList import clean_stock_list
import numpy as np


class StockStrategyBySignal(StockStrategyBase):

    def __init__(self, stk, start_date, end_date, price_rolling_window=10, amt_per_signal=5000000, available_flag=None,
                 isin_pool_flag=None):
        super().__init__(stk, start_date, end_date, price_rolling_window, amt_per_signal, available_flag,
                         isin_pool_flag)
        if stk in signal_global:
            self.signal = pd.DataFrame(signal_global[stk])
        else:
            self.signal = None
            self.market_flow = None
        self.stock = stk
        target_index = pd.MultiIndex.from_tuples(list(itertools.product(self.date_list, [1000, 1030, 1100, 1300, 1330, 1400, 1430])))
        self.signal = self.signal.reindex(target_index)
        self.last_buy_datetime = None
        self.over_24h = False

    def daily_update(self):
        # 每天基类会更新行情数据，此函数用于每天额外更新策略中需要使用的数据，如没有额外需要使用的数据，可不定义该函数
        # 每天额外更新数据
        if self.trading_day in self.signal.index:
            self.dataflow['signal'] = self.signal[self.i * 7:self.i * 7 + 7]
        else:
            self.dataflow['signal'] = None

    def bar_handler(self):
        # 每只股票每分钟信号逻辑定义
        if self.datetime == (20141216, 1000):
            print(1)
        if self.dataflow['signal'] is None:
            return
        # self.datetime (20170103,930)
        if not self.datetime in self.dataflow['signal'].index:
            return

        signal = self.dataflow['signal'].at[self.datetime, self.stk_id]
        if signal == 1 and self.position['holding'] == 0 and self.datetime[0] < self.date_list[-5]:
            # 买入函数可输入具体买入手数，该参数默认为 None, 如不输入，则默认买入self.amt_per_signal/均价 （四舍五入到手）
            self.buy()
            self.last_buy_datetime = self.datetime + (self.i,)
        if signal != 1 and self.position['available'] > 0:
            # 卖出函数可输入具体卖出手数，该参数默认为None, 如不输入，则默认卖出所有持仓
            if self.last_buy_datetime is None:
                raise Exception('Wrong situation')
            holding_days = self.i - self.last_buy_datetime[-1]
            if holding_days > 1 or (holding_days == 1 and self.last_buy_datetime[1] <= self.datetime[1]):
                self.sell()
                self.last_buy_datetime = None


def get_signal_by_val_pct_threshold_integration(pct, subset_path_list, signal_file_name_list):
    # subset_path_list, signal_file_name_list = [subpath,subpath.replace('lr','XGB')],[signal_file,signal_file.replace('lr','XGB')]
    point_set_list = [set(os.listdir(subset_path)) for subset_path in subset_path_list]
    for i in range(len(point_set_list)):
        for j in range(i + 1, len(point_set_list)):
            if point_set_list[i] != point_set_list[j]:
                raise Exception('Change point of Models are not match!!')

    point_list = os.listdir(subset_path_list[1])
    point_list = sorted([int(x[:-4]) for x in point_list])
    threshold_series = pd.DataFrame(columns=['threshold'], index=point_list)
    for date in point_list:
        subset = {}
        for subset_path in subset_path_list:
            subset[subset_path] = pd.read_pickle(subset_path + '%d.pkl' % date)
        subset = pd.Panel(subset)
        subset_sum = subset.sum(axis=0)
        subset_count = subset.count(axis=0)
        subset = subset_sum / subset_count
        th = (subset[0] < pct).sum() / subset.shape[0]
        threshold_series.loc[date, 'threshold'] = max(subset['prediction'].quantile(th), 0.005)
    threshold_series = threshold_series.reset_index()

    signal = {}
    for signal_file_name in signal_file_name_list:
        signal[signal_file_name] = pd.read_pickle(signal_file_name)
    signal = pd.Panel(signal)
    signal_count = signal.count(axis=0)
    signal_sum = signal.sum(axis=0)
    signal = signal_sum / signal_count
    signal[signal_count.eq(0)] = np.nan
    # signal['prediction'] = ((signal['prediction'] > th) * 1).replace(0, -1)
    signal = signal.reset_index()
    signal = signal.pivot_table(index=['level_0', 'level_2'], columns='level_1', values='prediction').replace(-1, 0).fillna(0).sort_index()

    signal['date'] = [x[0] for x in signal.index]
    signal['time'] = [x[1] for x in signal.index]
    signal['index'] = signal['date'].apply(lambda x: max(list(filter(lambda i: i < x, point_list))))
    signal = pd.merge(signal, threshold_series, 'left', 'index').set_index(['date', 'time'])

    signal = (signal.drop(['index', 'threshold'], axis=1).T - signal['threshold']).T
    signal = (signal > 0).replace(False, -1) * 1
    return signal

start = 20160101
end = 20181231



def main_beta():
    """
    示例2：一波全回测评估并输出
    :return:
    """
    #    strong_stock = pd.read_pickle('/data/group/800319/Faamonitor/强势个股2014-2019.pkl')
    #    strong_stock.index = strong_stock.index.map(lambda x: int(x))
    #    strong_stock.columns = strong_stock.columns.map(lambda x: stockList.trans_windcode2int(x))
    #    strong_stock = (strong_stock.shift(1).fillna(0)).astype(bool)

    #    is_valid = strong_stock

    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, start_date=start, end_date=end)

    stk_list = list(signal.keys())

    strats = UniverseEvaluation(StockStrategyBySignal, available_info=None, universe_info=stock_pool, buy_cost_ratio=cost, sell_cost_ratio=cost)
    # strats.backtest_one_stock(2989, 20130101, 20191231)
    e = time.time()
    # 并行回测
    file_name = '_'.join(signal_file[:-4].replace('all_mkt_', '').replace('all_mkt', '').split('/')[-3:][::-1]).strip('_') + '_beta'
    print(file_name)
    base_path = root_path + 'backtest_result_all_mkt_%dbp_cost_single_daily_signal/' % int(cost * 10000)
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    # output_path = root_path + base_path+'%s_%.2f.xlsx' % (file_name,th)
    output_path = base_path + '%s_%d_pct_val_threshold_single_daily_signal.xlsx' % (file_name, int(pct_threshold * 100))
    strats.one_wave_run(stk_list, start, end, kernel=40, output_path=output_path, mode='multi', signal_record_save=True)
    # pd.to_pickle(strats.record._getvalue(), '/data/group/800319/Faamonitor/factors/record_zxf_code_excute_by_lzc.pkl')
    # strats.one_wave_run(stk_list, 20100101, 20200728, kernel=10, output_path='/data/group/800319/Faamonitor/kdj_result_multi.xlsx', mode='multi')
    print('strategy time:', time.time() - e)
    print(output_path)


if __name__ == "__main__":
    pct_threshold = 0.05
    train_period = 200
    test_period = 10
    factor_num = 400
    cost = 0.001
    N = 40

    #    signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_ic_factor_selection/lr_train%d_test%d_factor_num%d.pkl' % (train_period, test_period, factor_num)
    # signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg/XGB_extra_v2_train%d_test%d.pkl' % (train_period, test_period)
    sp_list, fnm_list = [], []
    for md in ['lr', 'XGB']:
        signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/%s_train%d_test%d_factor_num%d_norm_window_%d.pkl' % \
                      (md, train_period, test_period, factor_num, N)
        subpath = signal_file.replace('.pkl', '_val_pred/')
        sp_list.append(subpath)
        fnm_list.append(signal_file)
    del subpath, signal_file
    signal_file = fnm_list[0].replace('lr', 'JustForTest')
    signal = pd.read_pickle('/data/user/015664/AFuckingTrigger/temp_signal.pkl')
    # signal = get_signal_by_val_pct_threshold_integration(pct_threshold,sp_list,fnm_list)
    # best_param_clf_xgb['train_pred_path'] = signal_file.replace('.pkl','_train_pred/')
    # signal = get_signal_by_val_pct_threshold(pct_threshold, signal_file.replace('.pkl', '_val_pred/'), signal_file)
    signal_dict = dict(signal)
    signal_global = Manager().dict(signal)
    main_beta()
    #
    # stat = {}
    # for th in [0.75,0.8,0.85,0.9,0.95]:
    #     signal = get_signal(th, signal_file.replace('.pkl', '_val_pred/'), signal_file)
    #     signal = signal.eq(1)
    #     trigger_count_daily = pd.DataFrame((signal.groupby('date').sum()>0).sum(axis=1))
    #     trigger_count_daily['year'] = [x//10000 for x in trigger_count_daily.index]
    #     stat[th] = trigger_count_daily.groupby('year').mean()
    #     print(th)
    #
    # stat = pd.DataFrame({x : stat[x][0] for x in stat})
