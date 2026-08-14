# coding: utf-8
# Author：fengchi863
# Date ：2022/6/20 13:11.

from hyperopt import fmin, tpe, Trials
from Timing.hyper_param_search.hyper_param_space import xgb_hyper_param_space
from HANXU.Timing.hyper_param_search.models import timing_xgb_model, train_xgb_model, train_xgb_model_dc
from HANXU.Timing.StrategyTest import test_signal_np, date_list, wf1d1000
from sklearn.metrics import mean_absolute_error as mae_func
from sklearn.metrics import mean_squared_error as mse_func
import time
from Timing.hyper_param_search.MyLogger import my_logger
import os
import pandas as pd
import numpy as np
import random
from xquant.xqutils.helper import link

lm = link.LinkMessage()
random.seed(2022)

search_times = 0
hyper_search_path = ''


class HyperParamSearch:
    def __init__(self, model_name=None):
        self.model_name = model_name
        self.model_func = None
        self._model_param_space = None
        self.best_param = None

    @property
    def model_param_space(self):
        return self._model_param_space

    @model_param_space.setter
    def model_param_space(self, value):
        my_logger.info(f'{self.model_name}超参数寻优空间已设置...')
        self._model_param_space = value

    def launch_search(self, fmin_func=None, algo=tpe.suggest, max_evals=100):
        my_logger.info('开始进行超参数寻优...')
        trials = Trials()
        best_param = fmin(fmin_func, self._model_param_space, algo=algo,
                          trials=trials, max_evals=max_evals, verbose=True, rstate=np.random.RandomState(2022))
        my_logger.info(f'阶段性超参数训练结束，本次最优超参数为:{best_param}')

        for idx, trial in enumerate(trials.trials[:max_evals]):
            my_logger.info(f'第{idx}次: {trial}')
        my_logger.info()
        return best_param

    def fmin_xgb_func(self, param):
        global search_times
        t1 = time.time()
        my_logger.info(f'第{search_times}轮超参数为: {param}')
        total_long_pred, total_short_pred, total_long_true, total_short_true = \
            train_xgb_model(timing_xgb_model, param, search_times=search_times)
        mae_mean = (mae_func(total_long_true, total_long_pred) +
                    mae_func(total_short_true, total_short_pred)) / 2
        mse_mean = (mse_func(total_long_true, total_long_pred) +
                    mse_func(total_short_true, total_short_pred)) / 2
        my_logger.info(f'此轮耗时{round(time.time() - t1, 2)}秒: {round(mae_mean, 6)}, {round(mse_mean, 6)}')
        search_times += 1
        return mae_mean

    def fmin_xgb_func_with_backtest(self, param):
        global search_times
        t1 = time.time()
        my_logger.info(f'第{search_times}轮超参数为: {param}')
        total_long_pred, total_short_pred, total_long_true, total_short_true = \
            train_xgb_model(timing_xgb_model, param, search_times=search_times)
        # 接入回测框架
        os.system(
            f'python3 /data/user/015614/BWorkHandOver/R2D2/ChangingCash/run_backtestFC.py {search_times} {self.model_name}')  # 执行命令，输入文件夹以及文件路径
        # 读取回测结果，包括最终净值、最大回撤等，返回最终净值
        out_path = f'/data/group/800442/800319/Timing/BackTest/Signal/hyper_search/bt_result_{search_times}.xlsx'
        net_value = pd.read_excel(out_path, sheet_name='每日持仓统计', index_col=0)['账户净值'].iloc[-1]
        profit_per_deal = pd.read_excel(out_path, sheet_name='逐笔持仓综合统计', index_col=0)['全时段'].iloc[0]
        mae_mean = (mae_func(total_long_true, total_long_pred) +
                    mae_func(total_short_true, total_short_pred)) / 2
        mse_mean = (mse_func(total_long_true, total_long_pred) +
                    mse_func(total_short_true, total_short_pred)) / 2
        my_logger.info(f'此轮耗时{round(time.time() - t1, 2)}秒: '
                       f'{round(mae_mean, 6)}, {round(mse_mean, 6)}, {round(net_value, 6)}, {round(profit_per_deal, 6)}')
        search_times += 1
        del total_long_pred, total_long_true, total_short_true, total_short_pred
        return -net_value

    def fmin_xgb_dc_func_with_backtest(self, param):
        global search_times
        t1 = time.time()
        my_logger.info(f'第{search_times}轮超参数为: {param}')
        # 判断是否提前停止
        allow_search_time = pd.read_pickle(
            '/data/group/800442/800319/Timing/BackTest/Signal/hyper_search_setting/hyper_search_ini.pkl').loc[
            self.model_name, 'max_evals']

        if allow_search_time < search_times:
            my_logger.info('提前终止')
            return 0

        total_long_pred, total_short_pred, total_long_true, total_short_true = \
            train_xgb_model_dc(timing_xgb_model, param, search_times=search_times, signal_name=self.model_name)

        # 测试信号多空表现
        signal_address = f'/data/group/800442/800319/Timing/BackTest/Signal/hyper_search_{self.model_name}/{search_times}/'
        signal_name = self.model_name

        signal = pd.read_pickle(f'{signal_address}{signal_name}.pkl')
        signal = signal.reindex(date_list).fillna(0).values
        signal_res, _, _ = test_signal_np(signal, future=wf1d1000, freq='Y', signal_months=12)
        ins_long_profit, ins_short_profit, oos_long_profit, oos_short_profit = \
            signal_res.loc['多头收益', 'ins'], signal_res.loc['空头收益', 'ins'], signal_res.loc['多头收益', 'oos'], signal_res.loc['空头收益', 'oos']
        print('纯信号回测已完成，接下来接入日内触发信号进行回测...')

        # 接入回测框架
        os.system(
            f'python3 /data/user/015614/BWorkHandOver/R2D2/ChangingCash/run_backtestFC.py {search_times} {self.model_name}')  # 执行命令，输入文件夹以及文件路径
        # 读取回测结果，包括最终净值、最大回撤等，返回最终净值
        out_path = f'/data/group/800442/800319/Timing/BackTest/Signal/hyper_search_{self.model_name}/bt_result_{search_times}.xlsx'
        net_value = pd.read_excel(out_path, sheet_name='每日持仓统计', index_col=0)['账户净值'].iloc[-1]
        profit_per_deal = pd.read_excel(out_path, sheet_name='逐笔持仓综合统计', index_col=0)['全时段'].iloc[0]
        mae_mean = (mae_func(total_long_true, total_long_pred) +
                    mae_func(total_short_true, total_short_pred)) / 2
        mse_mean = (mse_func(total_long_true, total_long_pred) +
                    mse_func(total_short_true, total_short_pred)) / 2
        my_logger.info(f'此轮耗时{round(time.time() - t1, 2)}秒: ' +
                       f'{round(mae_mean, 6)}, {round(mse_mean, 6)}, {round(net_value, 6)}, {round(profit_per_deal, 6)}, '
                       f'{round(ins_long_profit, 6)}, {round(ins_short_profit, 6)}, {round(oos_long_profit, 6)}, {round(oos_short_profit, 6)}')
        lm.sendMessage(f'此轮耗时{round(time.time() - t1, 2)}秒: ' +
                       f'{round(mae_mean, 6)}, {round(mse_mean, 6)}, {round(net_value, 6)}, {round(profit_per_deal, 6)}, '
                       f'{round(ins_long_profit, 6)}, {round(ins_short_profit, 6)}, {round(oos_long_profit, 6)}, {round(oos_short_profit, 6)}')
        search_times += 1
        del total_long_pred, total_long_true, total_short_true, total_short_pred,
        return -net_value

    def fmin_lstm(self, param):
        t1 = time.time()
        print(param)
        return


if __name__ == '__main__':
    # hps = HyperParamSearch(model_name='XGB', model_func=fmin_xgb_func)
    # hps = HyperParamSearch(model_name='XGB400', model_func=fmin_xgb_func_with_backtest)
    hps = HyperParamSearch(model_name='XGB400_dc')
    hps.model_param_space = xgb_hyper_param_space
    hps.launch_search(fmin_func=hps.fmin_xgb_dc_func_with_backtest)
    print(hps.best_param)


