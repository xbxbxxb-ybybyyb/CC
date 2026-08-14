# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/015614/BWorkHandOver')
sys.path.append('/data/user/015614/BWorkHandOver/ensemblemonitor-strategy-python')
sys.path.append('/data/user/015614/BWorkHandOver/StrongStockModel')

from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.\
    StartWithLimitCashVolConsiderNonFixSignal8BarExtraContition8WindowSignal \
    import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
import pandas as pd
from dataApi.sendInfo import send_file
from dataApi.tradeDate import get_date_range,get_pre_trade_date,get_recent_trade_date
from StrongStockModel.model.ModelResultLoadingTool import generate_long_signal,generate_short_signal
from ExtraTools import get_nonfix_in_val
from NonFixWindow.daily_statOnlineNonFix import main_compare


# long_param = {i: f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/NonFixSim/long_nonfix_window_8barOriginFactor//signal_long_XGB_DTC_Matrix_Future_{i}_Bar_pct_0.05.pkl' for i in range(1,9)}
# short_param = {i:f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/NonFixSim/short_8barOriginFactor/signal_short_XGB_DTC_Matrix_Future_{i}_Bar_pct_0.pkl' for i in range(1,8)}

base_model_param = {

'XGB_DTC_Matrix_Light_Cat':{
    x: [
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/SWMeanFuture_{x}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
        f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_all_sample_ic_all_t/',
        f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/catboost_all_sample_ic_all_t/',
    ] for x in range(1, 9)
},

'XGB_DTC_Matrix':{
    x: [
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220406Integration/SWMeanFuture_{x}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220406Integration/SWMeanFuture_{x}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220406Integration/SWMeanFuture_{x}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220406Integration/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220406Integration/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220406Integration/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
        # f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/lightgbm_all_sample_ic_all_t/',
        # f'/data/group/800442/800319/wyl/model_record/nonfix/future_{x}_bar/catboost_all_sample_ic_all_t/',
    ] for x in range(1, 9)
}
}

def calc_back_test_record(start,end,long_threshold, short_threshold, per_amt_ratio, initial_cash, deal_ratio, tag, alpha_pool_tag, base_dir):
    import os
    down_definition = 0
    base_dir = f'{base_dir}/'
    for sub_dir in ['record', 'daily_res_pn','信号']:
        if not os.path.exists(f'{base_dir}{sub_dir}/'):
            os.makedirs(f'{base_dir}{sub_dir}/')
    condition_series = {
        get_pre_trade_date(start): f'((((bar_first_trigger_num/bar_ratio)>(0.15*pool_num)) or '
        f'((bar_cum_first_trigger_num/barly_cum_ratio)>(0.15*pool_num))) or False)and (bar_down_trigger_signal/bar_trigger_signal)>0.5',
        2022042:'(((bar_first_trigger_num/bar_ratio)>(0.15*pool_num)) or ((bar_cum_first_trigger_num/barly_cum_ratio)>(0.15*pool_num)))and ((SZCZ/SZCZ_MA5 -1)<-0.008 or SZCZ_MA5_to_MA10<0)',

    }
    stk_min_amt = min(round(initial_cash * per_amt_ratio, -5) * 0.2, 1000000)
    alpha_pool = {}
    date_list = get_date_range(start,end)
    for date in date_list:
        # temp_pool = pd.read_pickle(f'/data/user/015664/StrategyBackUp/strategy_local_path3DailyBackup/code_list/{get_pre_trade_date(date)}.pkl')
        temp_pool = get_nonfix_in_val('code_list',date,strats_path)
        restrict_list = get_nonfix_in_val('restrict_list',date,strats_path)
        print(date,len(set(temp_pool).intersection(restrict_list)))
        temp_pool = sorted(list(set(temp_pool) - restrict_list))
        alpha_pool[date] = pd.Series(True,index=[int(x[:6]) for x in temp_pool])

    alpha_pool = pd.DataFrame(alpha_pool).T
    original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl')
    alpha_pool = alpha_pool.reindex(original_pool.columns,axis=1).fillna(False)

    short_signal = generate_short_signal(short_threshold,base_model_param[tag],min(start,get_pre_trade_date(end,30)),end,out_path=f'{base_dir}信号/{end}/short/')
    long_signal = generate_long_signal(long_threshold,base_model_param[tag],min(start,get_pre_trade_date(end,30)),end,out_path=f'{base_dir}信号/{end}/long/')

    file_name = f'{tag}_{end}_VolConsider_UpBuy100_{int(10000 * cost)}bp_cost'
    import os
    print('record not exist')
    instance = StartWithLimitCashVolConsider(long_signal, short_signal, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                             per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                             deal_percent=deal_ratio, barly_max_buy=2, initial_cash=initial_cash,
                                             stk_min_amt=stk_min_amt, condition_series=condition_series, down_swing_threshold=down_definition,max_trigger_num=max_trigger_num,
                                             cash_added=cash_added)

    record = instance.run_backtest()
    cash_series = instance.cash_series
    holding_num = instance.holding_num
    order_info = instance.order_info
    holding_info = instance.barly_holding_info


    pd.to_pickle([record,cash_series,holding_num,order_info,holding_info,instance.barly_condition_indicator],f'{base_dir}/record/record_{file_name}.pkl')

    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)

    out_path = f'{base_dir}/{file_name}.xlsx'
    for each in record:
        helper.record[each] = record[each]
    helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
    send_file(['015664'], out_path)

cash_added = {
20220526:48000000
}

max_trigger_num = {20220425:0,20220526:100}
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
if __name__ == '__main__':
    import time
    # time.time(60*10)
    # each = ( 0.005, 2e8, 600)
    # calc_back_test_record(*(each + (0.1, 'XGB_NonFixWindow_8Bar', 'CS_XGB_OLS_condition_style_rank_ex20')))
    import datetime
    Tag = 'XGB_DTC_Matrix_Light_Cat'
    # Tag = 'XGB_DTC_Matrix'
    import time
    # time.sleep(60*30)
    b_dir = '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘跟踪NonFix8ModelConditionFrom20220422/'
    strats_path = '/data/group/800319/strategy_local_path3/'
    backtest_start_date = 20220422
    pre_date = get_pre_trade_date(int(datetime.date.today().strftime('%Y%m%d')))
    calc_back_test_record(start=backtest_start_date,end=pre_date,long_threshold=0.05, short_threshold=0, per_amt_ratio=0.005, initial_cash=2000000,
                          deal_ratio=0.1, tag=Tag, base_dir=b_dir,
                          alpha_pool_tag=None)
    main_compare(tag=Tag, start_backtest_date=backtest_start_date, base_dir=b_dir,
                 strategy_base_path=strats_path, extra_tag='实盘跟踪',
                 send_diff=True,basic_indicator_file=True)

