# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading/StockSelection', '/data/user/015664/TriggeredTrading/AWorkHandOver', '/data/user/015664/TriggeredTrading/AWorkHandOver/alphaResearch/dataUpdate', '/data/user/015664/TriggeredTrading/AWorkHandOver/Other/code', '/data/user/015664/TriggeredTrading'])
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration, get_signal_by_val_pct_threshold_integration_NoMaxThreshold
import pandas as pd
from dataApi.ActiveConceptApi import get_active_stock_1concept, get_daily_active_concept, get_daily_active_stock
import os
from dataApi.sendInfo import send_file
from Script.lzc.pitches_integration import out_signal
from StrongStockModel.NonFixWindow.generate_signal.generate_signal_by_api_Min5Test import \
    get_nonfix_signal_with_930,generate_long_signal,generate_short_signal

signal_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/NonFix信号存储RevRes/'
base_model_param = {
    f'XGB_{tag}': {x:
        [
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_{tag}_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_{tag}_train200_test10_factor_num400/',
        ] for x in range(8, 9)
    } for tag in ['d','t','c']
}
base_model_param.update({
    f'XGB_dtc': {x:
        [
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/',
            f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220216_keep5OriginFactor/Future_{x}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/',
        ] for x in range(8, 9)
    }
})

for tag in ['regW1', 'regW1barly', 'regW280', 'regW35', 'regW7']:
    model_para = {8:[f'/data/group/800442/800319/IntraExp/RevResFuture/Future_8_bar/XGB_ic_d_train200_test10_factor_num400_{tag}/XGB_ic_d_train200_test10_factor_num400_{tag}/']}
    base_model_param[f'XGB_d_{tag}'] = model_para

    model_para = {8: [f'/data/group/800442/800319/IntraExp/RevResFuture/Future_8_bar/XGB_ic_t_train200_test10_factor_num400_{tag}/XGB_ic_t_train200_test10_factor_num400_{tag}/']}
    base_model_param[f'XGB_t_{tag}'] = model_para

    model_para = {8: [f'/data/group/800442/800319/IntraExp/RevResFuture/Future_8_bar/XGB_ic_c_train200_test10_factor_num400_{tag}/XGB_ic_c_train200_test10_factor_num400_{tag}/']}
    base_model_param[f'XGB_c_{tag}'] = model_para

    model_para = {8: [
        f'/data/group/800442/800319/IntraExp/RevResFuture/Future_8_bar/XGB_ic_d_train200_test10_factor_num400_{tag}/XGB_ic_d_train200_test10_factor_num400_{tag}/',
        f'/data/group/800442/800319/IntraExp/RevResFuture/Future_8_bar/XGB_ic_t_train200_test10_factor_num400_{tag}/XGB_ic_t_train200_test10_factor_num400_{tag}/',
        f'/data/group/800442/800319/IntraExp/RevResFuture/Future_8_bar/XGB_ic_c_train200_test10_factor_num400_{tag}/XGB_ic_c_train200_test10_factor_num400_{tag}/',
    ]}
    base_model_param[f'XGB_dtc_{tag}'] = model_para


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



cost = 0.001


def calc_back_test_record(pct_threshold, per_amt_ratio, initial_cash, pool_num, deal_ratio, FIX_tag, TAG_930, alpha_pool_tag):
    print('in')

    start = 20180101
    end = 20181231

    base_dir ='/data/user/015664/AFuckingTrigger/限制买入和持仓/残差处理标签结果V2/'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    stk_min_amt = min(round(initial_cash * per_amt_ratio, -5) * 0.2, 1000000)
    print(initial_cash, stk_min_amt)

    if TAG_930 is None:
        # long_signal = generate_long_signal()
        long_signal = generate_long_signal(pct_threshold, {8: base_model_param[FIX_tag][8]}, start, end, f'{signal_path}/{FIX_tag}/long/')
        bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
        tag = FIX_tag + f' OnlyFixPoint {alpha_pool_tag}Top{pool_num}_real{pool_num}'

    else:
        bar_list = [930,1000, 1030, 1100, 1300, 1330, 1400, 1430]
        long_signal, inter_signal, final_tag = get_nonfix_signal_with_930(pct_threshold, 0, start, end, FIX_tag, TAG_930)
        # long_signal = long_signal[8]
        tag =f' Fix_{FIX_tag}_930_{TAG_930} {alpha_pool_tag}Top{pool_num}_real{pool_num}'
    tag = tag + f'start{start}_end{end}'
    file_name = '%sVolConsider_UpBuy100_%dbp_cost' % (tag, int(10000 * cost))
    out_path = f'{base_dir}/{file_name}.xlsx'

    if os.path.exists(out_path):
        return

    alpha_pool = pd.read_pickle('/data/group/800442/800319/AlphaPool/CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl').shift(1).loc[
                 start:end].rank(ascending=False, axis=1) < pool_num
    from dataApi.tradeDate import get_date_range, get_pre_trade_date
    append_pool = {}
    pool_path = '/data/user/015664/StrategyBackUp/strategy_local_path3DailyBackup/code_list/'
    date_list = get_date_range(start, end)
    date_list = sorted(list(set(date_list) - set(alpha_pool.index)))
    for date in date_list:
        if os.path.exists(f'{pool_path}{get_pre_trade_date(date)}.pkl'):
            temp_pool = pd.read_pickle(f'{pool_path}{get_pre_trade_date(date)}.pkl')
            append_pool[date] = pd.Series(True, index=[int(x[:6]) for x in temp_pool])

        else:
            print(date, 'not exist')

    append_pool = pd.DataFrame(append_pool).T.fillna(False).sort_index()
    append_pool = append_pool.reindex(date_list).fillna('pad')
    alpha_pool = pd.concat([alpha_pool, append_pool])
    original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[start:end]
    original_pool = original_pool.drop(alpha_pool.index, axis=0)
    alpha_pool = pd.concat([original_pool, alpha_pool]).reindex(original_pool.columns, axis=1).sort_index() > 0.5
    print(f'max pool num {alpha_pool.sum(axis=1).max}')

    # print('/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/record/record_%sVolConsider_UpBuy100_%dbp_cost.pkl' % (tag, int(10000 * cost)))

    instance = StartWithLimitCashVolConsider(long_signal[8], start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                             per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                             deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                             stk_min_amt=stk_min_amt)

    record = instance.run_backtest()
    cash_series = instance.cash_series
    holding_num = instance.holding_num
    order_info = instance.order_info


    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
    for each in record:
        helper.record[each] = record[each]
    # helper.evaluat_signal_by_stk(2260)
    # out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/XGB_lightGBM_CatBoostWithMax5thresholdAlphaTriggerPoolV3Top%d_real%d_deal_ratio_0.1_per_ratio_%.4f_threshold_%.2f_inital_%dVolConsider_UpBuy100_10bp_cost.xlsx'
    helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
    # send_file(['015664'], out_path)

pool_dict = {
    'old': 'daily_stock_score_v3_20210127.pkl',
    'condition_mv': 'CS_OLS_condition_mv_F400T488P1_future925t241h123d_uniform20t50.pkl',
    'rank_ex20': 'CS_OLS_condition_style_rank_ex20_F400T488P1_future925t241h123d_uniform20t50.pkl',
    'NoCondition': 'CS_OLS_no_condition_F400T488P1_future925t241h123d_uniform20t50.pkl',
    'CS_OLS': 'CS_OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl',
    'CS_XGB_OLS_condition_style_rank_ex20': 'CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl',
    'CS_XGB': 'CS_XGB_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl',
    'stock_pool_20210610': 'stock_pool_20210610.pkl',
    # 'Open_Board': get_basic_values('Open_Board_stock'),
    'OLS_XGB200_20211213': 'OLS_XGB200_20211213.pkl',
    'XGB_OLS_style_ex20': 'XGB_OLS_style_ex20.pkl',

    'OLS_XGB200_val_5': 'OLS_XGB200.pkl',
    'XGB_OLS_style_ex20_val_5': 'XGB_OLS_style_ex20.pkl',

    'OLS_XGB200': 'OLS_XGB200.pkl',
    'OLS_T3': 'OLS_T3.pkl',
    'OLS_XGB200_auction': 'OLS_XGB200_auction.pkl',
    'FixEndV2':'FixEndV2.pkl'
}

each = (0.05, 0.005, 2e8, 600)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-tag',default=str)
args = parser.parse_args()
Tag = args.tag
# calc_back_test_record(*(each + (0.1,'XGBRes_DTC_OldFrameResFactor', 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1,'XGB_DTC',None, 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1,'XGB_DTC_DiffClip',None, 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1,'XGB_DTC_Matrix_Light_Cat_XGBClipDiff',None, 'CS_XGB_OLS_condition_style_rank_ex20')))
calc_back_test_record(*(each + (0.1,Tag,None, 'CS_XGB_OLS_condition_style_rank_ex20')))
# calc_back_test_record(*(each + (0.1,'XGB_DTC','XGB_Min5_DTC707V20220330', 'CS_XGB_OLS_condition_style_rank_ex20')))

