# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderNonFixSignal8Bar import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
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
}
}

def calc_back_test_record(long_threshold, short_threshold, per_amt_ratio, initial_cash, deal_ratio, tag, alpha_pool_tag, base_dir):
    start = 20220323
    import datetime
    end = get_pre_trade_date(int(datetime.date.today().strftime('%Y%m%d')))
    import os
    pre_date = end
    base_dir = f'{base_dir}/'
    for sub_dir in ['record', 'daily_res_pn','信号']:
        if not os.path.exists(f'{base_dir}{sub_dir}/'):
            os.makedirs(f'{base_dir}{sub_dir}/')

    stk_min_amt = min(round(initial_cash * per_amt_ratio, -5) * 0.2, 1000000)
    alpha_pool = {}
    date_list = get_date_range(start,end)
    for date in date_list:
        # temp_pool = pd.read_pickle(f'/data/user/015664/StrategyBackUp/strategy_local_path3DailyBackup/code_list/{get_pre_trade_date(date)}.pkl')
        temp_pool = get_nonfix_in_val('code_list',date)
        restrict_list = get_nonfix_in_val('restrict_list',date)
        print(date,len(set(temp_pool).intersection(restrict_list)))
        temp_pool = sorted(list(set(temp_pool) - restrict_list))
        alpha_pool[date] = pd.Series(True,index=[int(x[:6]) for x in temp_pool])

    alpha_pool = pd.DataFrame(alpha_pool).T
    original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl')
    alpha_pool = alpha_pool.reindex(original_pool.columns,axis=1).fillna(False)

    short_signal = generate_short_signal(short_threshold,base_model_param[tag],start,end,out_path=f'{base_dir}信号/{end}/short/')
    long_signal = generate_long_signal(long_threshold,base_model_param[tag],start,end,out_path=f'{base_dir}信号/{end}/long/')

    file_name = f'{tag}_{end}_VolConsider_UpBuy100_{int(10000 * cost)}bp_cost'
    import os
    print('record not exist')
    instance = StartWithLimitCashVolConsider(long_signal, short_signal, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                             per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                             deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                             stk_min_amt=stk_min_amt)

    record = instance.run_backtest()
    cash_series = instance.cash_series
    holding_num = instance.holding_num
    order_info = instance.order_info
    holding_info = instance.barly_holding_info


    pd.to_pickle([record,cash_series,holding_num,order_info,holding_info],f'{base_dir}/record/record_{file_name}.pkl')

    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)

    out_path = f'{base_dir}/{file_name}.xlsx'
    for each in record:
        helper.record[each] = record[each]
    helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
    send_file(['015664'], out_path)

bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
cost = 0.001
if __name__ == '__main__':

    # each = ( 0.005, 2e8, 600)
    # calc_back_test_record(*(each + (0.1, 'XGB_NonFixWindow_8Bar', 'CS_XGB_OLS_condition_style_rank_ex20')))

    Tag = 'XGB_DTC_Matrix_Light_Cat'
    b_dir = '/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测NonFix8ModelDropProbFactor20220323/'
    strats_path = '/data/group/800319/strategy_local_path_nonfix/'
    calc_back_test_record(long_threshold=0.05, short_threshold=0, per_amt_ratio=0.005, initial_cash=50000000,
                          deal_ratio=0.1, tag=Tag, base_dir=b_dir,
                          alpha_pool_tag=None)
    main_compare(None, tag=Tag, start_backtest_date=20220323, base_dir=b_dir,
                 strategy_base_path=strats_path, extra_tag='仿真跟踪', send_diff=True)

