# @Time : 2020/12/28 15:19
# @Author : Zhichen Lu
# @File : main_online.py

import pandas as pd
from ApplicationNo930 import Application
import configparser
from online_conf import init_conf_path, realtime_path, local_config_path
from offline_backtest.dailyLastBarStat import main_stat
import os
import numpy as np


def main(date_time, app):
    date, time = date_time // 10000, date_time % 10000
    # 更新当前时间戳
    app.update_time(time)
    # 从对应的实盘文件夹加载和处理因子并预测
    factor_path = '%s/x_day_lib/%d/%d/' % (realtime_path, date, time)
    res = app.predict(time, factor_path)
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
        last_buy = last_buy[~np.isclose(last_buy, 0)]
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
    else:
        involved_stk = sorted(list(set(app.stk_list).union(set(app.holding.keys()))))
        holding_info = pd.DataFrame(index=involved_stk)
        holding_info['PortfolioNO'] = '1'
        holding_info['NetPosition'] = pd.Series(app.holding)
        holding_info['SellAvailable'] = pd.Series(app.available)
        holding_info['TotalBuyAmount'] = 0
        holding_info['TotalSellAmount'] = 0
        holding_info = holding_info.reset_index().rename(columns={'index': 'Symbol'}).fillna(0)
    if not os.path.exists(f'{local_config_path}fake_barly_info/{app.date}/'):
        os.mkdir(f'{local_config_path}fake_barly_info/{app.date}/')

    pd.to_pickle(holding_info, f'{local_config_path}fake_barly_info/{app.date}/{app.time}.pkl')
    if res:
        # 更新持仓
        app.holding_info_update(holding_info)
        # 根据当前持仓、现金、计算需要买入、卖出的股票
        order_lsit = app.bar_handler()
        return order_lsit, app
    else:
        raise Exception

    # 根据实际买入、卖出的情况更新持仓


def backtest_by_day(date):
    app = Application(date)

    triggered_stk = {}
    for time_point in [1000, 1030, 1100, 1300, 1330, 1400, 1430]:
        if time_point == 1430:
            print(1)
        triggered_stk[time_point], app = main(date * 10000 + time_point, app)
        print(time_point)
    app.output_daily_summary()
    import os

    if not os.path.exists(f'{local_config_path}validation/'):
        os.mkdir(f'{local_config_path}validation/')
    pd.to_pickle(app.factor, f'{local_config_path}validation/factor%d.pkl' % date)


backtest_list = [(20210112, 20210113), (20210113, 20210114)]

# backtest_list = [(20210114, 20210115), (20210115, 20210118), (20210118, 20210119), (20210119, 20210120), (20210120, 20210121), (20210121, 20210122), (20210122, 20210125), (20210125, 20210126), (20210126, 20210127), (20210127, 20210128)]

# backtest_list = [(20210112, 20210113), (20210113, 20210114), (20210114, 20210115)]
if __name__ == "__main__":
    # backtest_by_day(date=20210111)
    # main_stat(date=20210111, T_plus_1=20210112)
    for date, T_plust_1 in backtest_list:
        backtest_by_day(date=date)
        main_stat(date=date, T_plus_1=T_plust_1)
        print(date, 'done')
