# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsider import StartWithLimitCashVolConsider, InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_long_integration
import pandas as pd
from dataApi.ActiveConceptApi import get_active_stock_1concept, get_daily_active_concept, get_daily_active_stock
import os
from dataApi.sendInfo import send_file
from Script.lzc.pitches_integration import out_signal


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
para = {
    'XGBWithSWSHIFReSaveTWithOrigin_Cat_Light': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],
}



def calc_back_test_record(pct_threshold, per_amt_ratio, initial_cash, pool_num, deal_ratio, tag, alpha_pool_tag):
    file_list = para[tag]
    print(file_list)
    start = 20170101
    end = 20211130
    # for initial_cash in [2e8,4e8,6e8,8e8,1e9,3e9,5e9,7e9]:
    stk_min_amt = min(round(initial_cash * per_amt_ratio, -5) * 0.2, 1000000)
    print(initial_cash, stk_min_amt)
    # /data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/DoubleEnsemble/signal_XGB_DCMultiFreq_T_Light_CatWithMax5threshold_0.05.pkl
    signal_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储Sensitivity/signal_%s_%.3f.pkl' % (tag, pct_threshold)
    print(signal_file)
    if not os.path.exists(os.path.split(signal_file)[0]):
        os.makedirs(os.path.split(signal_file)[0])
    if os.path.exists(signal_file):

        print(pct_threshold, 'signal exist')
        signal, pred_ret = pd.read_pickle(signal_file)[:2]
    else:
        # signal, pred_ret = get_signal_by_val_pct_threshold_integration(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, 20160104, 'actual_label',
        #                                                                'new',
        #                                                                head=135)
        res = get_signal_by_val_pct_threshold_long_integration(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], [x.replace('.pkl', '/') for x in file_list], start,
                                                                                      'actual_label',
                                                                                      'new',
                                                                                      head=None, end=end)

        pd.to_pickle(res, signal_file)
        signal, pred_ret = res[:2]
    mdd_info = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/UpgradeThresholdCompare_to20211130//mdd_info.pkl')
    mdd_info = mdd_info[f'2021迭代后线上版本_{pct_threshold:.3f}'].unstack()[['start','end']]
    for year in mdd_info.index:
        s,e = mdd_info.loc[year].tolist()
        # break
        signal.loc[s:e,:] = False

    # pred_ret = pd.read_pickle('/data/group/800442/800319/信号存储/20200111LinearCompareMV.pkl')
    tag = tag + f'{alpha_pool_tag}Top{pool_num}_deal_ratio_%.1f_per_ratio_%.4f_threshold_%.3f_inital_%d' % (deal_ratio, per_amt_ratio, pct_threshold, int(initial_cash))
    tag = tag + f'start{start}_end{end}'
    pred_ret[~signal.fillna(False)] = np.nan
    if pool_dict[alpha_pool_tag] is None:
        alpha_pool = pd.DataFrame()
    elif isinstance(pool_dict[alpha_pool_tag], pd.DataFrame):
        alpha_pool = pool_dict[alpha_pool_tag].shift(1).loc[start:end]
    elif isinstance(pool_dict[alpha_pool_tag], str):
        alpha_pool = pd.read_pickle(f'/data/group/800442/800319/AlphaPool/{pool_dict[alpha_pool_tag]}').shift(1).loc[start:end].rank(ascending=False, axis=1) < pool_num
    else:
        raise Exception('Wrong type')
    # alpha_pool = pd.read_pickle('/data/group/800442/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[start:end]
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
    alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5


    instance = StartWithLimitCashVolConsider(pred_ret, start, end, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                             per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                             deal_percent=deal_ratio, barly_max_buy=100, initial_cash=initial_cash,
                                             stk_min_amt=stk_min_amt)

    record = instance.run_backtest()
    cash_series = instance.cash_series
    holding_num = instance.holding_num
    order_info = instance.order_info

    helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
    file_name = '%sVolConsider_UpBuy100_%dbp_cost' % (tag, int(10000 * cost))

    out_path = f'/data/user/015664/AFuckingTrigger/限制买入和持仓/UpgradeThresholdCompare_to20211130DropMDD/{file_name}.xlsx'
    if not os.path.exists(os.path.split(out_path)[0]):
        os.makedirs(os.path.split(out_path)[0])
    for each in record:
        helper.record[each] = record[each]
    # helper.evaluat_signal_by_stk(2260)
    # out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityValidation/XGB_lightGBM_CatBoostWithMax5thresholdAlphaTriggerPoolV3Top%d_real%d_deal_ratio_0.1_per_ratio_%.4f_threshold_%.2f_inital_%dVolConsider_UpBuy100_10bp_cost.xlsx'
    helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)
    send_file(['015664'], out_path)

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
import argparse
if __name__ == '__main__':


    parser = argparse.ArgumentParser()

    parser.add_argument('-th',type=float)
    args = parser.parse_args()
    print('threshold',args.th)
    print(args)
    each = (args.th, 0.005, 2e8, 600)
    calc_back_test_record(*(each + (0.1, 'XGBWithSWSHIFReSaveTWithOrigin_Cat_Light', 'CS_XGB_OLS_condition_style_rank_ex20')))



#
