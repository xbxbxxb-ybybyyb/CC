# @Time : 2020/10/28 9:04
# @Author : Zhichen Lu
# @File : SignalPortfolioStrategyDemo.py
from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, EvaluationHelper
import pandas as pd
import os


class SignalBasedPortfolio(PortfolioStrategyBase):

    def __init__(self, signal, start=20140101, end=20181231, stock_pool=None, target_point=None, buy_cost=0.001, sell_cost=0.001):
        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost)
        self.signal = signal.reindex(self.close.index).fillna(0)
        self.data_flow['signal'] = None
        self.last_buy_time = {}

    def sell_action(self, stk, vol=None):
        if stk not in self.last_buy_time:
            raise Exception('Last buy time is not recorded')
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) > 1 or ((bar_date_idx - date_idx) == 1 and bar_time >= time_point):
            sold_vol, sold_price = self.sell(stk, vol)

    def buy_action(self, stk, vol=None):
        deal_vol, dea_price = self.buy(stk, vol)
        if deal_vol > 0:
            self.last_buy_time[stk] = self.datetime

    def daily_update(self, idx, date):
        super().daily_update(idx, date)
        self.data_flow['signal'] = self.signal[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        if self.data_flow['signal'].index[0][0] != self.date or self.data_flow['signal'].index[-1][0] != self.date:
            raise Exception('Broadcast date and signal date are not match!')

    def bar_handler(self):
        date, time_point, date_idx, time_idx = self.datetime
        signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
        signal = signal[signal.eq(1)]
        trigger_stk = set(signal.index)
        for stk in trigger_stk:
            if stk not in self.holding:
                self.buy_action(stk)
        sell_stk = set(self.available.keys()) - trigger_stk
        for stk in sell_stk:
            self.sell_action(stk)


def get_signal_by_val_pct_threshold(pct, subset_path, signal_file_name):
    """
    在验证集上计算pct处于多少分位数，然后用分位数在预测值上的阈值作为分类阈值
    :param pct:
    :param subset_path:
    :param signal_file_name:
    :return:
    """
    point_list = os.listdir(subset_path)
    point_list = sorted([int(x[:-4]) for x in point_list])
    threshold_series = pd.DataFrame(columns=['threshold'], index=point_list)
    for date in point_list:
        subset = pd.read_pickle(subset_path + '%d.pkl' % date)
        # date_list = sorted(list(set([x[0] for x in subset.index])))
        # subset = subset.loc[date_list[:-1]]
        th = (subset[0] < pct).sum() / subset.shape[0]
        threshold_series.loc[date, 'threshold'] = max(subset['prediction'].quantile(th), 0.005)
    threshold_series = threshold_series.reset_index()
    signal = pd.read_pickle(signal_file_name)
    # signal['prediction'] = ((signal['prediction'] > th) * 1).replace(0, -1)
    signal = signal.reset_index()
    signal = signal.pivot_table(index=['level_0', 'level_2'], columns='level_1', values='prediction')  # .replace(-1, 0).fillna(0).sort_index()

    signal['date'] = [x[0] for x in signal.index]
    signal['time'] = [x[1] for x in signal.index]
    signal['index'] = signal['date'].apply(lambda x: max(list(filter(lambda i: i < x, point_list))))
    signal = pd.merge(signal, threshold_series, 'left', 'index').set_index(['date', 'time'])

    signal = (signal.drop(['index', 'threshold'], axis=1).T - signal['threshold']).T
    signal = (signal > 0).replace(False, -1) * 1
    return signal


def main():
    pct_threshold = 0.05
    train_period = 200
    test_period = 10
    factor_num = 400
    cost = 0.001
    N = 40
    signal_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/XGB_train%d_test%d_factor_num%d_norm_window_%d.pkl' % \
                  (train_period, test_period, factor_num, N)
    # signal = get_signal_by_val_pct_threshold(pct_threshold, signal_file.replace('.pkl', '_val_pred/'), signal_file)
    # pd.to_pickle(signal,'/data/user/015664/AFuckingTrigger/temp_signal.pkl')
    signal = pd.read_pickle('/data/user/015664/AFuckingTrigger/temp_signal.pkl')
    instance = SignalBasedPortfolio(signal, 20160101, 20181231, target_point=[1000, 1030, 1100, 1300, 1330, 1400, 1430])
    helper = EvaluationHelper()
    import time
    e = time.time()
    record = instance.run_backtest(48)  # pd.read_pickle('/data/user/015664/AFuckingTrigger/port_record.pkl')
    pd.to_pickle(record, '/data/user/015664/AFuckingTrigger/port_record3.pkl')
    helper.one_wave_run(record, kernel=48, output_path='/data/user/015664/AFuckingTrigger/PortfolioFrameRes20201028.xlsx', signal_record_save=True)
    print(time.time() - e)


if __name__ == "__main__":
    main()
