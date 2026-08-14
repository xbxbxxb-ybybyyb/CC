# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd
from dataApi.ActiveConceptApi import get_active_stock_1concept, get_daily_active_concept, get_daily_active_stock
import os


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



bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
# max_barly_trigger = 100


para = {
    'XGB_Cat_Light': [
        '/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample.pkl',
        '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
        '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',

    ],

}

def main(pct_threshold,per_amt_ratio,initial_cash,pool_num):
# pct_threshold,per_amt_ratio,pool_num = para_list[i]
# pct_threshold = 0.05
# per_amt_ratio = 0.005

    tag = 'XGB_Cat_Light'
    # file_list = ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NewBaseModel/LSTMCorrStdParaHXLoading5minFix_union_train200_test10_factor_num100_norm_window_40.pkl']
    # ['/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NewBaseModel/LSTMCorrStdParaHXLoadingFilterLimit_union_train200_test10_factor_num100_norm_window_40.pkl']
    file_list = para[tag]
    print(file_list)
    # file_list = [path + x for x in file_list]
    deal_ratio = 0.1
    tag = tag + '_OnlineTest'
    start = 20190102
    end = 20201231

    # signal,pred_ret = get_signal_by_zscore_integration(file_list,threshold=pct_threshold)
    if not os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_OutSample_%s_%.2f.pkl'%(tag,pct_threshold)):
        signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, start, 'actual_label', 'new',
                                                                       tail=54)
        pd.to_pickle([signal, pred_ret], '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_OutSample_%s_%.2f.pkl'%(tag,pct_threshold))
    else:
        signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_OutSample_%s_%.2f.pkl'%(tag,pct_threshold))
        print('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_OutSample_%s_%.2f.pkl'%(tag,pct_threshold))

    # pred_ret = pd.read_pickle('/data/group/800319/信号存储/20200111LinearCompareMV.pkl')
    tag = tag + 'OutSampleRevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f_threshold_%.2f_inital_%d'%(deal_ratio,per_amt_ratio,pct_threshold,initial_cash)
    pred_ret[~signal] = np.nan

    alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3_20210127.pkl').shift(1).loc[start:end].rank(ascending=False,axis=1)<pool_num
    # alpha_pool = pd.read_pickle('/data/group/800319/信号存储/stock_pool/stock_pool_20210426.pkl').shift(1).loc[start:end].rank(ascending=False,axis=1)<600

    # alpha_pool = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[20160101:20181231]
    original_pool = pd.read_pickle('/data/group/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[start:end]
    original_pool = original_pool.drop(alpha_pool.index,axis=0)
    alpha_pool = pd.concat([original_pool,alpha_pool]).sort_index()>0.5
    tag = tag.replace('RevTriggerFilterHolding',f'AlphaTriggerPoolV3Top{pool_num}_real{pool_num}')

    if not os.path.exists('/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/record_out_sample/record_%s.pkl'%tag):
        instance = StartWithLimitCashVolConsider(pred_ret, start,end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                 per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                 deal_percent=deal_ratio, initial_cash=initial_cash)
        record = instance.run_backtest()
        cash_series = instance.cash_series
        pd.to_pickle([record,cash_series,instance.holding_num],'/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/record_out_sample/record_%s.pkl'%tag)
        print('/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/record_out_sample/record_%s.pkl'%tag)
    else:
        print(tag,'exist')


from xquant.compute.aimr import AIMR
import itertools

para_list = list(itertools.product([0.04,0.05,0.06],[0.005,0.01,0.02],[1e8],[200,600,400]))

i = int(AIMR.getParam())
total = 9

for each in para_list[len(para_list) * i // total:len(para_list) * (i + 1) // total]:
    main(*each)