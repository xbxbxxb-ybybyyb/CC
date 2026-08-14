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
from online_conf import code_list_path, local_config_path
from Script.lzc.pitches_integration import out_signal
from dataApi.getData import trans_windcode2int
from OnlineTool.daily_statOnline import main_compare


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
        '/data/user/015664/AFuckingTrigger/OnlineModel/XGB_d.pkl',
        '/data/user/015664/AFuckingTrigger/OnlineModel/XGB_t.pkl',
        '/data/user/015664/AFuckingTrigger/OnlineModel/XGB_c.pkl',
 '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
 '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample.pkl'
    ],
    'XGBMonthlyV4WithSWMeanFixFixMIX_Cat_Light_Val': [
        '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample.pkl',
        '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400.pkl',
        f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400.pkl',

        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400.pkl',
        '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400.pkl',
    ],

}

backtest_start_date = 20210406
per_amt_ratio = 0.005

per_ratio_change = {
    20210525: 0.02,
    20210617:0.01,
    20210624:0.005,
    20210727:0.006,
    20210729:0.00167,
    20210730:0.005,
    20210803:0.003125,
    20210804:0.005,20211214:0.001,20211215:0.005
}
pct_threshold_change = {
    20210525: 0.04,20210527:0.05,
}

cash_flow = {20210413:28000000,
             20210420:-20000000,
            20210506:20000000,
            20210513:50000000,
             20210525:120000000,
             20210527:-170000000,
            20210603:50000000,
            20210604:70000000,
             20210616:-10000000,
             20210706:60000000,
            20210727:-50000000,
             20210730:-100000000-7925804.88,
             20210802:30000000,
             20210804:-30000000,
             20210817:-30859736.86,
            20210825:20000000,
             20210827:30000000,
            20210928:-36846732.2,
            20210930:36846732.2,
            20211015:-44401839.49,
            20211105:30000000,
            20211111:50000000,
            20211126:-80000000,
             20211209:30000000,
             20211216:50000000,
             # 20211215:-4100000,
             20211217:-81000000
             }
max_trigger_num = {20210729:28,20210730:100,20210803:28,20211214:28}
tag_dict = {20210406:'XGB_Cat_Light',20211206:'XGBMonthlyV4WithSWMeanFixFixMIX_Cat_Light_Val'}
# file_list = para[tag]
# print(file_list)
deal_ratio = 0.1
strategy_tag = 'XGB_Cat_Light_SWMatrix'
final_tag = strategy_tag + '_OnlineTest'

today = int(datetime.date.today().strftime('%Y%m%d'))

pre_date = get_pre_trade_date(today)

conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])
end_list = [x[1][1] for x in para_list]

start = list(filter(lambda x: x < backtest_start_date, end_list))[-1]
end = list(filter(lambda x: x < pre_date, end_list))[-1]
period_list = end_list[end_list.index(start):end_list.index(end) + 1]

pre_start_date = None
signal_all,pred_ret_all = [],[]
change_point_list = sorted(list(tag_dict.keys()))
for date_point in change_point_list:
    tag = tag_dict[date_point]
    if date_point==change_point_list[-1]:
        end_date = pre_date
    else:
        end_date = get_pre_trade_date(change_point_list[change_point_list.index(date_point)+1])

    signal_file = f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/实盘跟踪线下信号/signal_OutSample_{tag}_OnlineTest_{end_date}.pkl'
    if os.path.exists(signal_file):
        signal, pred_ret = pd.read_pickle(signal_file)
    else:
        file_list = para[tag]
        for x in file_list[::-1]:
            temp = pd.read_pickle(x)
            if temp.index[-1][0]>=end_date:
                continue
            each = x.replace('.pkl','/')
            out_signal(base_path=each, end_date=get_pre_trade_date(today))
            import shutil
            # shutil.copy(each[:-1]+'_val_pred/20210518.pkl',each[:-1]+'_val_pred/20210527.pkl')

        all_signal, all_pred_ret = [], []
        pre_per_date = date_point
        for per_date in sorted(list(pct_threshold_change.keys())) + [end_date]:
            if per_date<date_point:
                continue
            if per_date == end_date:
                signal, pred_ret = get_signal_by_val_pct_threshold_integration_NoMaxThreshold(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, backtest_start_date,
                                                                               'actual_label', 'new',
                                                                               tail=len(period_list) + 2)
            else:
                signal, pred_ret = get_signal_by_val_pct_threshold_integration_NoMaxThreshold(pct_threshold, [x.replace('.pkl', '_val_pred/') for x in file_list], file_list, backtest_start_date,
                                                                               'actual_label', 'new',
                                                                               tail=len(period_list) + 1)
            signal, pred_ret = signal.loc[pre_per_date:per_date], pred_ret.loc[pre_per_date:per_date]
            all_signal.append(signal)
            all_pred_ret.append(pred_ret)
            pre_per_date = get_pre_trade_date(per_date, -1)
        signal, pred_ret = pd.concat(all_signal).fillna(False),pd.concat(all_pred_ret).fillna(False)
        print(signal.shape)
        real_time_path = '/data/group/800002/realtime/alpha/market_data/'
        limit_status = pd.DataFrame()

        for date in get_date_range(backtest_start_date, end_date):
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
    signal_all.append(signal)
    pred_ret_all.append(pred_ret)
signal,pred_ret = pd.concat(signal_all).fillna(False),pd.concat(pred_ret_all)
print('out')
pd.to_pickle([signal, pred_ret], f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/实盘跟踪线下信号/signal_OutSample_{strategy_tag}_OnlineTest_{pre_date}.pkl')
# pred_ret = pd.read_pickle('/data/group/800442/800319/信号存储/20200111LinearCompareMV.pkl')
# pred_ret = pd.read_pickle('/data/group/800442/800319/信号存储/20200111LinearCompareMV.pkl')

final_tag = final_tag + 'OutSampleRevTriggerFilterHolding_deal_ratio_%.1f_per_ratio_%.4f' % (deal_ratio, per_amt_ratio)
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

final_tag = final_tag.replace('RevTriggerFilterHolding', 'RevTriggerFilterHolding_AlphaTriggerPoolTop600')


instance = StartWithLimitCashVolConsiderChangingCash(pred_ret, backtest_start_date, pre_date, stock_pool=alpha_pool, target_point=bar_list, buy_cost=cost, sell_cost=cost,
                                                     per_amt_ratio=per_amt_ratio, append_param={'deal_price_path': deal_price_path + 'deal_price_vwap_30min_FullSample.pkl'},
                                                     deal_percent=deal_ratio, initial_cash=2000000, cash_added=cash_flow, per_ratio_change=per_ratio_change,max_trigger_num=max_trigger_num)
record = instance.run_backtest()
cash_series = instance.cash_series
holding_num = instance.holding_num
last_buy_time = {x: instance.last_buy_time[x][0] * 10000 + instance.last_buy_time[x][1] for x in instance.holding}
pd.to_pickle([record, cash_series, holding_num], '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/record/%sOnlineTracing.pkl' % final_tag)

helper = InitailCashBasedEvaluationHelper(sell_cost_ratio=cost, buy_cost_ratio=cost)
cash_series.index = cash_series.index.astype(int).astype(str)
out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/%sVolConsiderOnlineLimit_UpBuy100_%dbp_cost_%d.xlsx' % (final_tag, int(10000 * cost), pre_date)
_, res_pn = helper.one_wave_run(record, cash_series, 48, output_path=out_path, signal_record_save=True, holding_num=holding_num)

pd.to_pickle([res_pn, last_buy_time], f'/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/daily_res_pn/{pre_date}.pkl')
print(out_path)
cash_flow[get_pre_trade_date(backtest_start_date)] = 2000000
main_compare(today,tag=strategy_tag,cash_flow=cash_flow)
