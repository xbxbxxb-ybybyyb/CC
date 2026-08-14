# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py
import sys,datetime

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd
from dataApi.tradeDate import get_date_range,get_pre_trade_date
import configparser,os
from online_conf import code_list_path
from Script.lzc.pitches_integration import model_list,out_signal



def get_signal_by_zscore_integration(path_file_list, threshold=0.05):
    res_list = {}
    for each in path_file_list:
        temp = pd.read_pickle(each)
        res_list[each] = temp['adjusted_prediction']
    res_df = pd.DataFrame(res_list)
    pred_ret = res_df.mean(axis=1)
    pred_ret = pred_ret.reset_index()
    pred_ret = pred_ret.pivot_table(index=[pred_ret.columns[0], pred_ret.columns[1]], columns=pred_ret.columns[2], values=0)
    return pred_ret > threshold, pred_ret


pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001

para = {
    'XGB_Cat_Light': [
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],
    # 'XGB_Light': [
    #     '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
    #     '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
    #     '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
    #     '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
    #
    # ]

}



backtest_start_date = 20210223
per_amt_ratio = 0.005
tag = 'XGB_Cat_Light'
file_list = para[tag]
print(file_list)
deal_ratio = 0.1
tag = tag + '_OnlineTest'

today = int(datetime.date.today().strftime('%Y%m%d'))

for each in model_list:
    out_signal(base_path=each,end_date=get_pre_trade_date(today))
pre_date = get_pre_trade_date(today)

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])
end_list = [x[1][1] for x in para_list]


start = list(filter(lambda x : x<backtest_start_date,end_list))[-1]
end = list(filter(lambda x : x<pre_date,end_list))[-1]
period_list = end_list[end_list.index(start):end_list.index(end)+1]

split_end_day = 20210326
signal_origin,pred_ret_origin = pd.read_pickle(f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/仿真跟踪线下信号/signal_OutSample_XGB_Light_OnlineTest_{split_end_day}.pkl')
pred_ret_origin[~signal_origin] = np.nan

if False:#os.path.exists(f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/仿真跟踪线下信号/signal_OutSample_{tag}_{pre_date}.pkl'):
    signal, pred_ret = pd.read_pickle(f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/仿真跟踪线下信号/signal_OutSample_{tag}_{pre_date}.pkl')
else:
    signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, backtest_start_date, 'actual_label', 'new',
                                                               tail=len(period_list)+1)
    print(signal.shape)
    real_time_path = '/data/group/800002/realtime/alpha/market_data/'
    limit_status = pd.DataFrame()

    for date in get_date_range(backtest_start_date, pre_date):
        temp_limit_status = pd.read_pickle(f'{real_time_path}{date}/1430/stock/limit_status.pkl')
        temp_limit_status['date'] = [int(x.strftime('%Y%m%d')) for x in temp_limit_status.index]
        temp_limit_status['time'] = [int(x.strftime('%H%M')) for x in temp_limit_status.index]
        temp_limit_status = temp_limit_status.set_index(['date', 'time'])
        temp_limit_status = temp_limit_status.append(pd.DataFrame(np.nan,
                                                                  index=pd.MultiIndex.from_tuples([(date, 1430)]), columns=temp_limit_status.columns))
        temp_limit_status = temp_limit_status.shift(1).swaplevel(0, 1).loc[bar_list].swaplevel(0, 1)
        temp_limit_status.columns = [int(x[:-3]) for x in temp_limit_status.columns]
        limit_status = pd.concat([limit_status, temp_limit_status])
    limit_status = limit_status.reindex(pred_ret.columns, axis=1).reindex(pred_ret.index, axis=0)
    limit_status = limit_status.isin([1, -1])
    signal[limit_status] = False
    pd.to_pickle([signal, pred_ret], f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/仿真跟踪线下信号/signal_OutSample_{tag}_{pre_date}.pkl')

# pred_ret = pd.read_pickle('/data/group/800319/信号存储/20200111LinearCompareMV.pkl')
tag = tag + 'OutSampleRevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f' % (deal_ratio, per_amt_ratio)
pred_ret[~signal] = np.nan
pred_ret = pd.concat([pred_ret_origin,pred_ret.loc[get_pre_trade_date(split_end_day,-1):]])

original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl')

alpha_pool = []
for date in get_date_range(get_pre_trade_date(backtest_start_date),pre_date):
    temp_pool = pd.read_pickle(f'{code_list_path}{date}.pkl')
    temp_pool = pd.DataFrame(True,index=[date],columns=temp_pool)
    alpha_pool.append(temp_pool)
alpha_pool = pd.concat(alpha_pool)
alpha_pool.columns = [int(x[:-3]) for x in alpha_pool.columns]
alpha_pool = alpha_pool.reindex(original_pool.columns,axis=1).fillna(False).shift(1).loc[backtest_start_date:]

isolation_pool = pd.read_excel('/data/group/800319/strategy_local_path/restrict_list/隔离池20201010.xls')['证券代码'].astype(int)
black_name_list = pd.read_excel('/data/group/800319/strategy_local_path/restrict_list/黑名单20201010.xls')['证券代码'].astype(int)
unavailable_pool = set(isolation_pool).union(set(black_name_list))
alpha_pool.loc[:, list(unavailable_pool.intersection(set(alpha_pool.columns)))] = False
alpha_pool = alpha_pool.fillna(False)

tag = tag.replace('RevTriggerFilterHolding', 'RevTriggerFilterHolding_AlphaTriggerPoolTop600')

# res3 = get_daily_active_stock(20181228,20201031).shift(1)
# tag = tag.replace('OutSampleRevTriggerFilterHolding','OutSampleRevTriggerFilterHolding_Concept')
# if os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测线下跟踪/record/%sOnlineTracing.pkl' % tag):
instance = StartWithLimitCashVolConsider(pred_ret, backtest_start_date, pre_date, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                         per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                         deal_percent=deal_ratio, initial_cash=20000000)
record = instance.run_backtest()
cash_series = instance.cash_series
holding_num = instance.holding_num
last_buy_time = {x:instance.last_buy_time[x][0]*10000+instance.last_buy_time[x][1] for x in instance.holding}

pd.to_pickle([record, cash_series,holding_num], '/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测线下跟踪/record/%sOnlineTracing.pkl' % tag)

helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测线下跟踪/%sVolConsiderOnlineLimit_UpBuy100_%dbp_cost_%d.xlsx' % (tag, int(10000 * cost),pre_date)
_,res_pn = helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True,holding_num=holding_num)
pd.to_pickle([res_pn,last_buy_time],f'/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测线下跟踪/daily_res_pn/{pre_date}.pkl')
print(out_path)
