"""
from HANXU.Timing.hyper_param_search.models import timing_xgb_model, train_xgb_model, train_xgb_model_dc
from sklearn.metrics import mean_absolute_error as mae_func
from sklearn.metrics import mean_squared_error as mse_func
import time
from Timing.hyper_param_search.MyLogger import my_logger
import os
import pandas as pd

search_times = 0
hyper_search_path = ''


def fmin_xgb_func(param):
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


def fmin_xgb_func_with_backtest(param):
    global search_times
    t1 = time.time()
    my_logger.info(f'第{search_times}轮超参数为: {param}')
    total_long_pred, total_short_pred, total_long_true, total_short_true = \
        train_xgb_model(timing_xgb_model, param, search_times=search_times)
    # 接入回测框架
    os.system(f'python3 /data/user/015614/BWorkHandOver/R2D2/ChangingCash/run_backtestFC.py {search_times}')   # 执行命令，输入文件夹以及文件路径
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


def fmin_xgb_dc_func_with_backtest(param):
    global search_times
    t1 = time.time()
    my_logger.info(f'第{search_times}轮超参数为: {param}')
    total_long_pred, total_short_pred, total_long_true, total_short_true = \
        train_xgb_model_dc(timing_xgb_model, param, search_times=search_times)

    # 判断是否提前停止
    allow_search_time = pd.read_excel()

    # 接入回测框架
    os.system(f'python3 /data/user/015614/BWorkHandOver/R2D2/ChangingCash/run_backtestFC.py {search_times}')   # 执行命令，输入文件夹以及文件路径
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


def fmin_lstm(param):
    t1 = time.time()
    print(param)
    return
"""