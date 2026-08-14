# @Time : 2020/11/30 08:45
# @Author : Zhichen Lu
# @File : LimitPortfolioRev240Concept.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, EvaluationHelper
import pandas as pd
import os
import numpy as np
from dataApi.ConceptApi import get_basic_values
from xquant.compute.aimr import AIMR


class SignalBasedPortfolioLimitUp(PortfolioStrategyBase):

    def __init__(self, signal, start=20140101, end=20181231, stock_pool=None, target_point=None, buy_cost=0.001, sell_cost=0.001, per_amt=500000, append_param={}, max_holding=600,
                 daily_max_buy=400):
        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost, per_amt, append_param=append_param)
        self.signal = signal.reindex(self.close.index)
        self.data_flow['signal'] = None
        self.last_buy_time = {}
        self.max_holding_num = max_holding
        self.daily_max_buy_num = daily_max_buy
        self.active_stock = get_basic_values('Active_Stock').shift(1).reindex(self.date_list, axis=0).reindex(self.signal.columns.tolist(), axis=1)
        self.active_stock = self.active_stock.reindex(self.date_list,axis=0).reindex(self.stk_list,axis=1)
        self.daily_active_stk = None

    def sell_action(self, stk, vol=None):
        if stk not in self.last_buy_time:
            raise Exception('Last buy time is not recorded')
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) > 1 or ((bar_date_idx - date_idx) == 1 and bar_time == time_point):
            self.sell(stk, vol)

    def buy_action(self, stk, vol=None):
        deal_vol,_ = self.buy(stk, vol)
        if deal_vol > 0:
            self.last_buy_time[stk] = self.datetime
        return deal_vol

    def holding_another_round(self,stk):
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) == 1 and bar_time == time_point:
            self.last_buy_time[stk] = self.datetime

    def daily_update(self, idx, date):
        super().daily_update(idx, date)
        self.data_flow['signal'] = self.signal[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        date_pool = self.stock_pool[self.date_idx:self.date_idx + 1].T[date]
        date_pool = date_pool[~date_pool]
        self.data_flow['not_available'] = set(date_pool.index.tolist())
        self.daily_active_stk = self.active_stock[self.date_idx:self.date_idx + 1].T[date]
        self.daily_active_stk = self.daily_active_stk[self.daily_active_stk].index.tolist()
        print(self.daily_active_stk)
        if self.data_flow['signal'].index[0][0] != self.date or self.data_flow['signal'].index[-1][0] != self.date:
            raise Exception('Broadcast date and signal date are not match!')

    def bar_handler(self):
        date, time_point, date_idx, time_idx = self.datetime
        signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
        signal = signal.dropna()
        trigger_stk = set(signal.index)
        avaliable_stk = set(self.available.keys()) - self.data_flow['not_available']
        avaliable_trigger_stk = avaliable_stk.intersection(trigger_stk)
        sell_stk = avaliable_stk - trigger_stk
        trigger_stk = trigger_stk - self.data_flow['not_available']

        for stk in avaliable_trigger_stk:
            self.holding_another_round(stk)

        for stk in sell_stk:
            self.sell_action(stk)
        holding_num = len(self.holding)
        if holding_num >= self.max_holding_num:
            return
        trigget_num = min(len(trigger_stk), self.daily_max_buy_num)
        if (holding_num + trigget_num) > self.max_holding_num:
            trigget_num = self.max_holding_num - holding_num

        bough_num = 0
        signal.loc[list(set(self.daily_active_stk).intersection(set(signal.index)))] += 100000000
        trigger_stk = signal[list(trigger_stk)].sort_values(ascending=False).index.tolist()
        for stk in trigger_stk:
            if stk not in self.holding:
                _ = self.buy_action(stk)
                bough_num += 1
            if bough_num >= trigget_num:
                break


"""
def get_signal_by_val_pct_threshold(pct, subset_path, signal_file_name):

    # 在验证集上计算pct处于多少分位数，然后用分位数在预测值上的阈值作为分类阈值
    # :param pct:
    # :param subset_path:
    # :param signal_file_name:
    # :return:

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
    pred_ret = pd.read_pickle(signal_file_name)
    # signal['prediction'] = ((signal['prediction'] > th) * 1).replace(0, -1)
    pred_ret = pred_ret.reset_index()
    pred_ret = pred_ret.pivot_table(index=['level_0', 'level_2'], columns='level_1', values='prediction')  # .replace(-1, 0).fillna(0).sort_index()

    pred_ret['date'] = [x[0] for x in pred_ret.index]
    pred_ret['time'] = [x[1] for x in pred_ret.index]
    pred_ret['index'] = pred_ret['date'].apply(lambda x: max(list(filter(lambda i: i < x, point_list))))
    signal = pd.merge(pred_ret, threshold_series, 'left', 'index').set_index(['date', 'time'])

    signal = (signal.drop(['index', 'threshold'], axis=1).T - signal['threshold']).T
    signal = (signal > 0).replace(False, -1) * 1
    return signal, pred_ret.set_index(['date', 'time']).drop('index', axis=1)

"""


def get_signal_by_val_pct_threshold_integration(pct, subset_path_list, signal_file_name_list,start):
    # subset_path_list, signal_file_name_list = [subpath,subpath.replace('lr','XGB')],[signal_file,signal_file.replace('lr','XGB')]
    point_set_list = [set(os.listdir(subset_path)) for subset_path in subset_path_list]
    point_list = os.listdir(subset_path_list[0])
    for i in range(len(point_set_list)):
        for j in range(i + 1, len(point_set_list)):
            if point_set_list[i] != point_set_list[j]:
                inter_set = point_set_list[i].intersection(point_set_list[j])
                if inter_set in [point_set_list[i] ,point_set_list[j]]:
                    point_list = sorted(list(inter_set))
                else:
                    raise Exception('Change point of models are not match!!')


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
    signal = signal.loc[start:]
    signal['date'] = [x[0] for x in signal.index]
    signal['time'] = [x[1] for x in signal.index]
    pred_ret = signal.set_index(['date', 'time'])
    signal['index'] = signal['date'].apply(lambda x: max(list(filter(lambda i: i < x, point_list))))

    signal = pd.merge(signal, threshold_series, 'left', 'index').set_index(['date', 'time'])

    signal = (signal.drop(['index', 'threshold'], axis=1).T - signal['threshold']).T
    signal = signal > 0
    return signal, pred_ret

def main(max_holding, daily_max_buy):
    pct_threshold = 0.05
    cost = 0.001
    sp_list, fnm_list = [], []
    # XGB
    file_list_xgb = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
                        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
                        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl']
    # Linear
    file_list_linear = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
     '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
     '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl']
    # NN
    file_list_nn = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/NNCorrStd_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
                 '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/NNCorrStdGPU_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
                 '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/NNCorrStdGPU_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl']

    for signal_file in file_list_linear+file_list_xgb:
        subpath = signal_file.replace('.pkl', '_val_pred/')
        sp_list.append(subpath)
        fnm_list.append(signal_file)
    del subpath, signal_file
    # signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, sp_list, fnm_list, 20160101)
    # pd.to_pickle([signal,pred_ret],'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_DTC.pkl')
    signal,pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_DTC.pkl')
    pred_ret[~signal] = np.nan
    # pd.to_pickle(signal,'/data/user/015664/AFuckingTrigger/temp_signal.pkl')
    #  = pd.read_pickle('/data/user/015664/AFuckingTrigger/temp_signal.pkl')

    instance = SignalBasedPortfolioLimitUp(pred_ret, 20160101, 20181231, target_point=[1000, 1030, 1100, 1300, 1330, 1400, 1430],
                                           buy_cost=cost, sell_cost=cost, max_holding=max_holding, daily_max_buy=daily_max_buy)
    helper = EvaluationHelper(buy_cost_ratio=cost, sell_cost_ratio=cost)
    import time
    e = time.time()
    record = instance.run_backtest(48)  # pd.read_pickle('/data/user/015664/AFuckingTrigger/port_record.pkl')
    # pd.to_pickle(record, '/data/user/015664/AFuckingTrigger/限制买入和持仓/敏感性分析/record/twap10min_record_insample_lr_XGB_NN.pkl')
    out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/Rev240DTC/XGBWithConceptZXF_SeperateEnsemble_UpHolding%d_UpBuy%d_%dbp_cost.xlsx' % (
    max_holding, daily_max_buy, int(10000 * cost))
    helper.one_wave_run(record, kernel=24, output_path=out_file,
                        signal_record_save=True)
    print(time.time() - e)
    print(out_file)

if __name__ == "__main__":
    # para = int(AIMR.getParam())
    # main(*para_list[para])
    main(300,100)