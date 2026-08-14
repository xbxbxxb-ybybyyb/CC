# @Time : 2020/12/28 15:19
# @Author : Zhichen Lu
# @File : main_online.py
import sys

sys.path.extend(
    ['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python',
     '/data/user/015664/TriggeredTrading/StrongStockModel',
     '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master',
     '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic',
     '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading'])

import pandas as pd
from ApplicationMixFactorAndMatrixIntegrationWithExtraCondition import Application
import configparser
from online_conf import realtime_path
from offline_backtest.dailyLastBarStat import main_stat, main_stat_930
import os
import numpy as np
from dataApi.getData import get_minute_1factor, trans_int2windcode
import traceback

local_config_path = '/data/group/800319/strategy_local_path3/'


FACTOR_PATH =  '/data/group/800002/realtime/alpha/x_day_lib/'
# FACTOR_PATH =  '/data/group/800442/SimFixFactor/'

def main(date_time, app, holding_info=None):
    date, time = date_time // 10000, date_time % 10000
    # 更新当前时间戳
    app.update_time(time)
    # 从对应的实盘文件夹加载和处理因子并预测
    factor_path = f'{FACTOR_PATH}{date}/{time}/' #% (realtime_path, date, time)
    # factor_path = '/data/group/800319/fake_realtime_path/%d/%d/' % ( date, time)
    res = app.predict(time, factor_path, backtest=True)
    # 根据返回
    if not app.pre_time is None:
        holding_info = pd.read_pickle(f'{local_config_path}fake_barly_info/{app.date}/{app.pre_time}.pkl')
        last_buy, last_sell = app.buy_order_record[app.pre_time], app.sell_order_record[app.pre_time]
        traded_stk = sorted(list(set(last_buy.index).union(set(last_sell.index))))
        vol = app.get_realtime_dataflow('volume')[traded_stk].loc[str(app.date) + str(app.pre_time):str(app.date) + str(app.time)]
        close = app.get_realtime_dataflow('close')[traded_stk].loc[str(app.date) + str(app.pre_time):str(app.date) + str(app.time)]
        vwap = (vol.fillna(0) * close.fillna(method='pad')).sum() / vol.sum()
        vol_up = (vol.sum() * 0.1) // 100 * 100
        last_buy = pd.DataFrame({'target': last_buy, 'up': vol_up.reindex(last_buy.index).fillna(0)}).min(axis=1)
        last_sell = pd.DataFrame({'target': last_sell, 'up': vol_up.reindex(last_sell.index).fillna(0)}).min(axis=1)
        last_buy = last_buy[~np.isclose(last_buy, 0)]  # print({int(x[:-3]) for x in last_sell.index})
        last_sell = last_sell[~np.isclose(last_sell, 0)]
        holding_info = holding_info.set_index('Symbol')
        holding_info.loc[last_buy.index, 'NetPosition'] = holding_info.loc[last_buy.index, 'NetPosition'] + last_buy
        holding_info.loc[last_sell.index, 'NetPosition'] = holding_info.loc[last_sell.index, 'NetPosition'] - last_sell
        holding_info.loc[last_sell.index, 'SellAvailable'] = holding_info.loc[last_sell.index, 'SellAvailable'] - last_sell
        holding_info.loc[last_buy.index, 'TotalBuyAmount'] = holding_info.loc[last_buy.index, 'TotalBuyAmount'] + last_buy * vwap.loc[last_buy.index] * (1 + 0.001)
        holding_info.loc[last_sell.index, 'TotalSellAmount'] = holding_info.loc[last_sell.index, 'TotalSellAmount'] + last_sell * vwap.loc[last_sell.index] * (1 - 0.001)

        if holding_info.loc[last_buy.index, 'TotalBuyAmount'].isnull().sum() > 0:
            raise Exception('Buy amount exist NaN in %d %d' % (app.date, app.time))

        if holding_info.loc[last_sell.index, 'TotalSellAmount'].isnull().sum() > 0:
            raise Exception('Sell amount exist NaN in %d %d' % (app.date, app.time))
        holding_info = holding_info.reset_index()
    elif holding_info is None:
        involved_stk = sorted(list(set(app.stk_list).union(set(app.holding.keys()))))
        holding_info = pd.DataFrame(index=involved_stk)
        holding_info['PortfolioNO'] = '1'
        holding_info['NetPosition'] = pd.Series(app.holding)
        holding_info['SellAvailable'] = pd.Series(app.available)
        holding_info['TotalBuyAmount'] = 0
        holding_info['TotalSellAmount'] = 0
        holding_info = holding_info.reset_index().rename(columns={'index': 'Symbol'}).fillna(0)
    else:
        holding_info = holding_info.reset_index().rename(columns={'index': 'Symbol'}).fillna(0)
    if not os.path.exists(f'{local_config_path}fake_barly_info/{app.date}/'):
        os.makedirs(f'{local_config_path}fake_barly_info/{app.date}/')

    pd.to_pickle(holding_info, f'{local_config_path}fake_barly_info/{app.date}/{app.time}.pkl')
    if res:
        # 更新持仓
        app.holding_info_update(holding_info)
        # 根据当前持仓、现金、计算需要买入、卖出的股票
        order_lsit = app.bar_handler()
        return order_lsit, app
    else:
        print(traceback.format_exc())
        raise Exception

    # 根据实际买入、卖出的情况更新持仓


def backtest_by_day(date):
    app = Application(date)

    triggered_stk = {}
    print(f'930 holding {len(app.app930.holding)}')
    res_list = app.get_first_target_plan()

    holding_info = app.total_holding_info[930].set_index('Symbol')
    last_buy = app.app930.buy_order_record[930]
    last_sell = app.app930.sell_order_record[930]
    close = get_minute_1factor('close', start_datetime=date * 10000 + 930, end_datetime=date * 10000 + 959)
    vol = get_minute_1factor('vol', start_datetime=date * 10000 + 930, end_datetime=date * 10000 + 959)
    vol.columns, close.columns = vol.columns.map(trans_int2windcode), close.columns.map(trans_int2windcode)
    vol, close = vol[app.app930.pool_with_over_night_stk], close[app.app930.pool_with_over_night_stk]

    vwap = (vol.fillna(0) * close.fillna(method='pad')).sum() / vol.sum()
    vol_up = (vol.sum() * 0.1) // 100 * 100

    last_buy = pd.DataFrame({'target': last_buy, 'up': vol_up.reindex(last_buy.index).fillna(0)}).min(axis=1)
    last_sell = pd.DataFrame({'target': last_sell, 'up': vol_up.reindex(last_sell.index).fillna(0)}).min(axis=1)
    last_buy = last_buy[~np.isclose(last_buy, 0)]  # print({int(x[:-3]) for x in last_sell.index})
    last_sell = last_sell[~np.isclose(last_sell, 0)]
    holding_info.loc[last_buy.index, 'NetPosition'] = holding_info.loc[last_buy.index, 'NetPosition'] + last_buy
    holding_info.loc[last_sell.index, 'NetPosition'] = holding_info.loc[last_sell.index, 'NetPosition'] - last_sell
    holding_info.loc[last_sell.index, 'SellAvailable'] = holding_info.loc[last_sell.index, 'SellAvailable'] - last_sell
    holding_info.loc[last_buy.index, 'TotalBuyAmount'] = holding_info.loc[last_buy.index, 'TotalBuyAmount'] + last_buy * vwap.loc[last_buy.index] * (1 + 0.001)
    holding_info.loc[last_sell.index, 'TotalSellAmount'] = holding_info.loc[last_sell.index, 'TotalSellAmount'] + last_sell * vwap.loc[last_sell.index] * (1 - 0.001)

    for each in app.buy_time_info:
        if type(app.buy_time_info[each]) != tuple:
            print(each, type(app.buy_time_info[each]))
    for time_point in [1000, 1030, 1100, 1300, 1330, 1400, 1430]:
        triggered_stk[time_point], app = main(date * 10000 + time_point, app, holding_info)
        # send_message(['015664'], f'{time_point} done')
        print(time_point)
    app.output_daily_summary()

    if not os.path.exists(f'{local_config_path}validation/'):
        os.mkdir(f'{local_config_path}validation/')
    pd.to_pickle(app.factor, f'{local_config_path}validation/factor%d.pkl' % date)
    pd.to_pickle(app.factor_5min, f'{local_config_path}validation/factor%d_5min.pkl' % date)


import shutil
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.sendInfo import send_message

# backtest_list = [(20210803, 20210804)]
backtest_list = [(x, get_pre_trade_date(x, -1)) for x in [20220106]]

if __name__ == "__main__":
    # backtest_by_day(date=20210224)
    # main_stat(date=20210222, T_plus_1=20210223)
    for date, T_plust_1 in backtest_list:
        # if not os.path.exists(f'/data/group/800319/strategy_local_path3_for_930//FolderFor930/{date}/StrategyIn/signal{date}.pkl'):
        #     shutil.copy(f'/data/group/800319/strategy_local_path3_for_930/morning_model/val_sign/{date}.pkl'
        # ,f'/data/group/800319/strategy_local_path3_for_930//FolderFor930/{date}/StrategyIn/signal{date}.pkl')
        if os.path.exists(f'{local_config_path}vol_info/{get_pre_trade_date(date)}_backup.pkl'):
            shutil.copy(f'{local_config_path}vol_info/{get_pre_trade_date(date)}_backup.pkl', f'{local_config_path}vol_info/{get_pre_trade_date(date)}.pkl')
        backtest_by_day(date=date)
        # break
        main_stat(date=date, T_plus_1=T_plust_1)
        main_stat_930(date=date, T_plus_1=T_plust_1)
        send_message(['015664'], f'{date} done')

#
# import shutil
# from  online_conf import local_config_path
# from dataApi.tradeDate import get_date_range,get_pre_trade_date
#
#
# for date in get_date_range(20201102,20210104):
#     pre_date = get_pre_trade_date(date)
#     # shutil.copy(f'/data/group/800319/strategy_local_path/code_list/{pre_date}.pkl',f'/data/group/800319/strategy_local_path3/code_list/{pre_date}.pkl')
#     # shutil.copy(f'/data/group/800319/strategy_local_path/factor_hyper_param/mean{pre_date}.pkl',f'/data/group/800319/strategy_local_path3/factor_hyper_param/mean{pre_date}.pkl')
#     # shutil.copy(f'/data/group/800319/strategy_local_path/factor_hyper_param/mean{pre_date}.pkl',f'/data/group/800319/strategy_local_path3/factor_hyper_param/std{pre_date}.pkl')
#     shutil.copy(f'/data/group/800319/strategy_local_path/vol_info/{pre_date}.pkl',f'/data/group/800319/strategy_local_path3/vol_info/{pre_date}.pkl')

# from online_conf import holding_info_path
#
# old_model_holding = pd.read_pickle(holding_info_path+'20210526_with_old_model.pkl')
# new_model_holding = pd.read_pickle(holding_info_path+'20210526_with_new_update_model.pkl')
#
# set(old_model_holding.keys()) - set(new_model_holding.keys())
# set(old_model_holding.keys()).intersection(set(new_model_holding.keys()))
#
# len(set(old_model_holding.keys()).intersection(set(new_model_holding.keys())))
