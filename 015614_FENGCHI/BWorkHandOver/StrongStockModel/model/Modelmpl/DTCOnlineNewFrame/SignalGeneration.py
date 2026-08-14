# @Time : 2021/4/15 14:09
# @Author : Zhichen Lu
# @File : SignalGeneration.py

# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py
import sys,datetime
sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd
from dataApi.tradeDate import get_date_range,get_pre_trade_date
import configparser,os
from online_conf import code_list_path,local_config_path
from Script.lzc.pitches_integration import model_list,out_signal

pct_threshold = 0.05
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
for time_point in bar_list:
    file_path = f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/TrainModelByFix/XGBAllFactor_train400_test10_factornum400_eval_ic_d_fix_freq_month/{time_point}/'
    out_signal(file_path,20181231)
    file_path = f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/TrainModelByFix/XGBAllFactor_train400_test10_factornum400_eval_ic_c_fix_freq_month/{time_point}/'
    out_signal(file_path, 20181231)
para = {
time_point:[
f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/TrainModelByFix/XGBAllFactor_train400_test10_factornum400_eval_ic_d_fix_freq_month/{time_point}.pkl',
f'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/TrainModelByFix/XGBAllFactor_train400_test10_factornum400_eval_ic_c_fix_freq_month/{time_point}.pkl'
] for time_point in bar_list
}

signal_all = []
pred_ret_all = []
for time_point in bar_list:
    tag = f'XGBFixlyMonth_{time_point}_dc'
    file_list = para[time_point]
    if not os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储Fixly/signal_OutSample_%s.pkl' % tag):
        signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, [x.replace('.pkl', 'val_pred_path/') for x in file_list], file_list, 20160104, 'actual_label', 'new',
                                                                       head=73)
        pd.to_pickle([signal, pred_ret], '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储Fixly/signal_OutSample_%s.pkl' % tag)
    else:
        print('read',time_point)
        signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储Fixly/signal_OutSample_%s.pkl' % tag)
    # signal.index = [(x,time_point) for x in signal.index]
    # pred_ret.index = [(x,time_point) for x in pred_ret.index]
    signal_all.append(signal.swaplevel(0,1).loc[[time_point]].swaplevel(0,1))
    pred_ret_all.append(pred_ret.swaplevel(0,1).loc[[time_point]].swaplevel(0,1))
    del pred_ret,signal
signal_all = pd.concat(signal_all)
pred_ret_all = pd.concat(pred_ret_all)
signal_all, pred_ret_all = signal_all.sort_index(), pred_ret_all.sort_index()
pd.to_pickle([signal_all, pred_ret_all],'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储Fixly/%s.pkl'%tag)

pred_ret_all[~signal_all.fillna(False)] = np.nan

per_amt_ratio = 0.005
deal_ratio = 0.1
initial_cash = 2e8
print(pct_threshold,per_amt_ratio)

tag = 'XGBFixlyMonth_dc'

# pred_ret = pd.read_pickle('/data/group/800319/信号存储/20200111LinearCompareMV.pkl')

alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3_20210127.pkl').shift(1).loc[20160101:20181231].rank(ascending=False,axis=1)<600
original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[20160101:20181231]
original_pool = original_pool.drop(alpha_pool.index,axis=0)
alpha_pool = pd.concat([original_pool,alpha_pool]).sort_index()>0.5
tag = tag+'AlphaTriggerPoolV3Top600_real600%.1f_per_ratio_%.4f_threshold_%.2f_inital_%d'%(deal_ratio,per_amt_ratio,pct_threshold,int(initial_cash))

instance = StartWithLimitCashVolConsider(pred_ret_all, 20160101, 20181231,stock_pool=alpha_pool,target_point=bar_list,buy_cost=cost, sell_cost=cost,
                                         per_amt_ratio=per_amt_ratio,append_param={'deal_price_path':deal_price_path+'deal_price_vwap_30min_FullSample.pkl'},
                                         deal_percent=deal_ratio,barly_max_buy=100,initial_cash=initial_cash)
record = instance.run_backtest()

cash_series = instance.cash_series
holding_num = instance.holding_num
cash_series.index = cash_series.index.astype(int).astype(str)
helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost,buy_cost_ratio=cost)

out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/%sVolConsider_UpBuy100_%dbp_cost.xlsx' % (tag, int(10000 * cost))
helper.one_wave_run(record,cash_series,48,output_path=out_path ,signal_record_save=True,holding_num=holding_num)
print(out_path)