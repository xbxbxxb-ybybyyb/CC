# @Time : 2021/7/1 19:00
# @Author : Zhichen Lu
# @File : BackTest.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
import pandas as pd
import numpy as np
from dataApi.tradeDate import get_date_range,get_pre_trade_date,get_recent_trade_date
from dataApi.stockList import trans_windcode2int
import datetime
from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, InitailCashBasedEvaluationHelper
from StrongStockModel.conf.path_config import deal_price_path, root_path
from online_conf import local_config_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderChangablePerRatio import  StartWithLimitCashVolConsiderChangablePerRatio
from Tool930.OnlineCompare930 import calc_930_compare
backtest_start_date = 20220112
today = get_recent_trade_date()#int(datetime.date.today().strftime('%Y%m%d'))
date_list = get_date_range(backtest_start_date, today)
df = pd.concat([pd.read_pickle(f'/data/group/800319/strategy_local_path3/morning_model/val_sign/{x}.pkl')
                for x in date_list], axis=1, keys=date_list)
df.index = df.index.map(trans_windcode2int)
df = df.T
alpha_pool = df.copy()
df.index = pd.MultiIndex.from_product([df.index, [930]])

bar_list = [930]
cost = 0.001
per_amt_ratio = 0.005
initial_cash = 7000000
per_ratio_change = {

}
max_trigger_num = {20220113:0,20220117:100,20220125:0,20220208:100,20220307:0,20220309:100,20220314:0}
tag = 'Back930'
deal_ratio = 0.1

start = backtest_start_date
end = today

pre_date = end#get_pre_trade_date(today)
pred_ret = df.copy()
# pred_ret[~signal] = np.nan
unavailable_pool = pd.read_pickle(f'{local_config_path}restrict_list.pkl')
alpha_pool.loc[:, list(unavailable_pool.intersection(set(alpha_pool.columns)))] = False
alpha_pool = alpha_pool > 0

cash_added = {
    20220121:-2700000,
20220208:2700000,
20220211:-4000000,
20220215:4000000,
            }
instance = StartWithLimitCashVolConsiderChangablePerRatio(pred_ret, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                          per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                          deal_percent=deal_ratio, initial_cash=initial_cash, per_ratio_change=per_ratio_change,cash_added=cash_added
                                                          ,max_trigger_num=max_trigger_num)
record = instance.run_backtest()
cash_series = instance.cash_series
holding_num = instance.holding_num
last_buy_time = [instance.last_buy_time_series,instance.holding_series,holding_num]
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/930/%s_%dbp_cost_%d.xlsx' % (tag, int(10000 * cost), pre_date)
_, res_pn = helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
pd.to_pickle([res_pn, last_buy_time], f'/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/930/daily_res_pn/{pre_date}.pkl')
from dataApi.sendInfo import send_file,send_message

# send_file(['015664','015836'], out_path)
send_file(['015664'], out_path)
# send_message(['015664'],f'/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/930/daily_res_pn/{pre_date}.pkl')
cash_added[get_pre_trade_date(backtest_start_date)] = initial_cash
calc_930_compare(backtest_start_date,today,cash_added)

