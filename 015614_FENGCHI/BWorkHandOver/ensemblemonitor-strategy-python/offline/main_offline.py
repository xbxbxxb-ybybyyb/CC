# @Time : 2020/12/28 15:19
# @Author : Zhichen Lu
# @File : main_online.py
import sys
sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
import pandas as pd
from offline.ApplicationOffline import ApplicationOffline
import configparser
from online_conf import init_conf_path,local_config_path

offline_path ='/data/group/800002/alpha_factor/lib/x_factor_lib/'
def main(date_time, holding_info):
    date, time = date_time // 10000, date_time % 10000
    # 更新当前时间戳
    app.update_time(time)
    # 从对应的实盘文件夹加载和处理因子并预测
    factor_path = offline_path
    res = app.predict(time, factor_path)
    # 根据返回
    if not app.pre_time is None:
        last_buy, last_sell = app.buy_order_record[app.pre_time], app.sell_order_record[app.pre_time]
        traded_stk = sorted(list(set(last_buy.index).union(set(last_sell.index))))
        vol = app.get_realtime_dataflow('volume')[traded_stk]
        close = app.get_realtime_dataflow('close')[traded_stk]
        vwap = (vol.fillna(0) * close.fillna(method='pad')).sum() / vol.sum()
        holding_info = holding_info.set_index('Symbol')
        holding_info.loc[last_buy.index, 'NetPosition'] = holding_info.loc[last_buy.index, 'NetPosition'] + last_buy
        holding_info.loc[last_sell.index, 'NetPosition'] = holding_info.loc[last_sell.index, 'NetPosition'] - last_sell
        holding_info.loc[last_sell.index, 'SellAvailable'] = holding_info.loc[last_sell.index, 'SellAvailable'] - last_sell
        holding_info.loc[last_buy.index, 'TotalBuyAmount'] = holding_info.loc[last_buy.index, 'TotalBuyAmount'] + last_buy * vwap.loc[last_buy.index]
        holding_info.loc[last_sell.index, 'TotalSellAmount'] = holding_info.loc[last_sell.index, 'TotalSellAmount'] + last_sell * vwap.loc[last_sell.index]
        holding_info = holding_info.reset_index()
    if res:
        # 更新持仓
        app.holding_info_update(holding_info)
        # 根据当前持仓、现金、计算需要买入、卖出的股票
        order_lsit = app.bar_handler()
        return order_lsit
    else:
        buy_stk, sell_stk = pd.Series(), pd.Series()

    # 根据实际买入、卖出的情况更新持仓


if __name__ == "__main__":
    date = 20201026
    app = ApplicationOffline(date)
    holding_info = pd.DataFrame(index=app.stk_list)
    holding_info['PortfolioNO'] = '1'
    holding_info['NetPosition'] = pd.Series(app.holding)
    holding_info['SellAvailable'] = pd.Series(app.available)
    holding_info['TotalBuyAmount'] = 0
    holding_info['TotalSellAmount'] = 0
    holding_info = holding_info.reset_index().rename(columns={'index': 'Symbol'}).fillna(0)
    triggered_stk = {}
    for time_point in [1000, 1030, 1100, 1300, 1330, 1400, 1430]:
        triggered_stk[time_point] = main(date * 10000 + time_point, holding_info)
        print(time_point)
    app.output_daily_summary()
    pd.to_pickle(app.factor, f'{local_config_path}validation/factor_offline{str(date)}.pkl')
