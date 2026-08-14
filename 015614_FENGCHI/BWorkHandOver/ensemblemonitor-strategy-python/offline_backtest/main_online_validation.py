# @Time : 2020/12/28 15:19
# @Author : Zhichen Lu
# @File : main_online.py

import pandas as pd
from ApplicationNo930 import Application
import configparser
from online_conf import init_conf_path, local_config_path, realtime_path
from offline_backtest.dailyLastBarStat import main_stat
import os
import numpy as np


# realtime_path =

def main(date_time, app):
    date, time = date_time // 10000, date_time % 10000
    # 更新当前时间戳
    app.update_time(time)
    # 从对应的实盘文件夹加载和处理因子并预测
    factor_path = '%s/x_day_lib/%d/%d/' % (realtime_path, date, time)
    # factor_path = '/data/group/800319/fake_realtime_path/%d/%d/' % ( date, time)
    res = app.predict(time, factor_path)
    # 根据返回
    holding_info = pd.read_pickle(f'{local_config_path}校验股票池/1.pickle')
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
    for each in app.buy_time_info:
        if type(app.buy_time_info[each]) != tuple:
            print(each, type(app.buy_time_info[each]))
    for time_point in [1000, 1030, 1100, 1300, 1330, 1400, 1430]:
        triggered_stk[time_point], app = main(date * 10000 + time_point, app)
        print(time_point)
    app.output_daily_summary()
    import os

    if not os.path.exists(f'{local_config_path}validation/'):
        os.mkdir(f'{local_config_path}validation/')
    pd.to_pickle(app.factor, f'{local_config_path}validation/factor%d.pkl' % date)


# backtest_list = [(20210105, 20210106), (20210106, 20210107), (20210107, 20210108), (20210108, 20210111),
#                  (20210111, 20210112), (20210112, 20210113), (20210113, 20210114)]

# backtest_list = [(20210111, 20210112), (20210112, 20210113), (20210113, 20210114)]

# backtest_list = [(20210127, 20210128)]

# backtest_list = [(20210114, 20210115), (20210115, 20210118), (20210118, 20210119), (20210119, 20210120), (20210120, 20210121), (20210121, 20210122), (20210122, 20210125), (20210125, 20210126), (20210126, 20210127), (20210127, 20210128)]

backtest_list = [(20210423, 20210426)]

if __name__ == "__main__":
    # backtest_by_day(date=20210224)
    # main_stat(date=20210222, T_plus_1=20210223)
    for date, T_plust_1 in backtest_list:
        backtest_by_day(date=date)
        # main_stat(date=date, T_plus_1=T_plust_1)
        print(date, 'done')

