# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py
import sys, datetime

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderChangingCash import StartWithLimitCashVolConsiderChangingCash, \
    InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration_NoMaxThreshold
import pandas as pd
from dataApi.tradeDate import get_date_range, get_pre_trade_date
import configparser, os
from ExtraTools import get_path_conf
from dataApi.sendInfo import send_file
# from online_conf import code_list_path, local_config_path
path_conf = get_path_conf('/data/group/800319/strategy_local_path3_ForMix20210803_V20210907/')
local_config_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path = [path_conf[x] for x in\
                                                'local_config_path,daily_out_path,holding_info_path,code_list_path,buy_time_info_path'.split(',')]
from OnlineTool.daily_statOnline import main_compare

pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001

para = {
    'XGB_Cat_Light': [
'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_d_ic_half_d.pkl',
'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_t_ic_half_t.pkl',
'/arch1/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/Fix5minMultiAfterDeltaEraData20210909/XGBMultiFreqFix5minFixNolimit_train200_test10_ic_c_ic_half_c.pkl',
         '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
         '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample.pkl'
    ],

}

backtest_start_date = 20211012
initial_cash = 20000000
per_amt_ratio = 0.005
per_ratio_change = {
}
pct_threshold_change = {
}

cash_flow = {}
max_trigger_num = {}
tag = 'XGB_Cat_Light'
file_list = para[tag]
print(file_list)
deal_ratio = 0.1
tag = tag + '_OnlineTest'

today = 20210813#int(datetime.date.today().strftime('%Y%m%d'))

pre_date = get_pre_trade_date(today)

conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])
end_list = [x[1][1] for x in para_list]

start = list(filter(lambda x: x < backtest_start_date, end_list))[-1]
end = list(filter(lambda x: x < pre_date, end_list))[-1]
period_list = end_list[end_list.index(start):end_list.index(end) + 1]

base_dir =  '/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测线下跟踪_BeforeRay/'
for sub_dir in ['record','daily_res_pn']:
    if not os.path.exists(f'{base_dir}{sub_dir}/'):
        os.makedirs(f'{base_dir}{sub_dir}/')
signal_file = f'{base_dir}信号/signal_OutSample_{tag}_{pre_date}.pkl'

if not os.path.exists(os.path.split(signal_file)[0]):
    os.makedirs(os.path.split(signal_file)[0])

if os.path.exists(signal_file):
    signal, pred_ret = pd.read_pickle(signal_file)
else:
    signal,pred_ret = get_signal_by_val_pct_threshold_integration_NoMaxThreshold(0.05, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, backtest_start_date,
                                                               'actual_label','new',head=None, end=pre_date)

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
    pd.to_pickle([signal, pred_ret], signal_file)

tag = tag + 'OutSampleRevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f' % (deal_ratio, per_amt_ratio)
pred_ret[~signal] = np.nan

original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl')

alpha_pool = []
for date in get_date_range(get_pre_trade_date(backtest_start_date), pre_date):
    temp_pool = pd.read_pickle(f'{code_list_path}{date}.pkl')
    temp_pool = pd.DataFrame(True, index=[date], columns=temp_pool)
    alpha_pool.append(temp_pool)
alpha_pool = pd.concat(alpha_pool)
alpha_pool.columns = [int(x[:-3]) for x in alpha_pool.columns]
alpha_pool = alpha_pool.reindex(original_pool.columns, axis=1).fillna(False).shift(1).loc[backtest_start_date:]

unavailable_pool = pd.read_pickle(f'{local_config_path}restrict_list.pkl')
alpha_pool.loc[:, list(unavailable_pool.intersection(set(alpha_pool.columns)))] = False
alpha_pool = alpha_pool.fillna(False)

tag = tag.replace('RevTriggerFilterHolding', 'RevTriggerFilterHolding_AlphaTriggerPoolTop600')





instance = StartWithLimitCashVolConsiderChangingCash(pred_ret, backtest_start_date, pre_date, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                     per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                     deal_percent=deal_ratio, initial_cash=initial_cash, cash_added=cash_flow, per_ratio_change=per_ratio_change,max_trigger_num=max_trigger_num)
record = instance.run_backtest()
cash_series = instance.cash_series
holding_num = instance.holding_num
last_buy_time = {x: instance.last_buy_time[x][0] * 10000 + instance.last_buy_time[x][1] for x in instance.holding}
pd.to_pickle([record, cash_series, holding_num], f'{base_dir}record/%sOnlineTracing.pkl' % tag)
pd.to_pickle(instance.holding_series,f'{base_dir}record/holding_series_%sOnlineTracing.pkl' % tag)
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = f'{base_dir}%sVolConsiderOnlineLimit_UpBuy100_%dbp_cost_%d.xlsx' % (tag, int(10000 * cost), pre_date)

_, res_pn = helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
send_file(['015664'],out_path)
pd.to_pickle([res_pn, last_buy_time], f'{base_dir}daily_res_pn/{pre_date}.pkl')




