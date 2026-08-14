# @Time : 2022/1/5 14:34
# @Author : Zhichen Lu
# @File : daily_prepare.py
import sys
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

import numpy as np
import pandas as pd
import bottleneck
from dataApi.tradeDate import get_pre_trade_date, get_date_range, get_recent_trade_date
import itertools
from ExtraTools import get_path_conf
from dataApi.getData import get_daily_1factor
# from online_conf import *
import os
from StrongStockModel.model.ModelResultLoadingTool import generate_long_signal,generate_short_signal
from ExtraTools import save_nonfix_in_val
from dataApi.sendInfo import send_message
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

def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


def calc_recent_count(signal, window=20):
    signal_arr = signal.values.reshape(signal.shape[0] // 7, 7, signal.shape[-1])
    idx_arr = np.empty(signal_arr.shape)
    for idx in range(7):
        idx_arr[:, idx, :] = np.ones((idx_arr.shape[0], idx_arr.shape[-1])) * idx + 1
    idx_arr[~signal_arr] = np.nan
    first_signal = np.nanmin(idx_arr, axis=1)[:, None, :]
    is_triggered_first = np.isclose(first_signal, idx_arr)
    recent_20d_s_count = bottleneck.move_sum(np.where(is_triggered_first, 1, 0), axis=0, window=window)
    recent_20d_s_count = delay(recent_20d_s_count, 2)
    recent_20d_s_count = pd.DataFrame(recent_20d_s_count.reshape(signal.shape), index=signal.index, columns=signal.columns)
    barly_recent_20d_s_count = recent_20d_s_count.sum(axis=1).unstack()
    barly_recent_20d_ratio = (barly_recent_20d_s_count.T / barly_recent_20d_s_count.sum(axis=1)).T
    return barly_recent_20d_ratio, barly_recent_20d_s_count

def get_singal(pct,tag,start,end,out_path):
    signal = generate_long_signal(pct,{8:base_model_param[tag][8]},start,get_pre_trade_date(end),f'{out_path}/{end}/')
    signal = signal[8].loc[:end].notnull()
    if signal.index[0][0]<start:
        raise Exception(f'Exist signal start date {signal.index[0][0]} is less than defined start date {start}')
    date_list = get_date_range(signal.index[0][0], get_pre_trade_date(end,-1))
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, bar_list)))
    signal = signal.reindex(index).fillna(False)
    return signal

bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]

def prepare_condition_V4(date, signal, signal_threshold, down_signal_ratio, down_condition):

    barly_r_20d_ratio, _ = calc_recent_count(signal.fillna(False), 20)
    barly_ratio = barly_r_20d_ratio.loc[date]
    barly_cum_ratio = barly_ratio.cumsum()
    condition = {}

    offline_condition = f'((((bar_first_trigger_num/bar_ratio)>({signal_threshold}*pool_num)) ' \
            f'or ((bar_cum_first_trigger_num/barly_cum_ratio)>({signal_threshold}*pool_num))) ' \
            f'or False)' \
            f'and (bar_down_trigger_signal/bar_trigger_signal)>{down_signal_ratio}'

    print('-------------V4_2_1-------------------------')
    print(offline_condition)
    print('-------------V4_2_1-------------------------')

    for bar in bar_list:
        condition[bar] = f'((((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) ' \
            f'or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num))) ' \
            f'or False)' \
            f'and (bar_down_trigger_signal/bar_trigger_signal)>{down_signal_ratio}'
        print(condition[bar])

    #         condition[bar] = f"""
    # signal_condition = ((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num))
    # down_signal_condition = (bar_down_trigger_signal/bar_trigger_signal)>{down_signal_ratio}
    # index_condition = False
    # final_flag = (signal_condition or index_condition)&down_signal_condition
    # print(final_flag)"""
    return condition, down_condition

def prepare_condition_V6_2_1_selfdefine_index(date, signal, signal_threshold, index_pct_change_ratio=0,down_condition=0
                                              ,offline_index_tag=None,online_index_tag=None):
    """
    信号数量 and (低于5日均线 or MA5<MA10)
    """
    barly_r_20d_ratio, _ = calc_recent_count(signal.fillna(False), 20)
    barly_ratio = barly_r_20d_ratio.loc[date]
    barly_cum_ratio = barly_ratio.cumsum()
    SZZZ = get_daily_1factor('close', code_list=[offline_index_tag], date_list=get_date_range(get_pre_trade_date(date,11),get_pre_trade_date(date,1)), type='bench')
    MA5 = SZZZ[-5:].mean()[offline_index_tag]
    MA10 = SZZZ[-10:].mean()[offline_index_tag]

    offline_condition =f'(((bar_first_trigger_num/bar_ratio)>({signal_threshold}*pool_num)) ' \
            f'or ((bar_cum_first_trigger_num/barly_cum_ratio)>({signal_threshold}*pool_num)))' \
            f'and (({offline_index_tag}/{offline_index_tag}_MA5 -1)<{index_pct_change_ratio} or {offline_index_tag}_MA5_to_MA10<0)'

    print('-------------V6_2_1-------------------------')
    print(offline_condition)
    print('-------------V6_2_1-------------------------')

    condition = {}
    for bar in bar_list:
        # (((bar_first_trigger_num / 0.23787878787878788) > (0.2 * pool_num)) or ((bar_cum_first_trigger_num / 0.23787878787878788) > (0.2 * pool_num))) and ((SZZS/3000-1)<0 or (100/400 - 1)<0)
        condition[bar] = f'(((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) ' \
            f'or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num)))' \
            f'and (({online_index_tag}/{MA5}-1)<{index_pct_change_ratio} or ({MA5}/{MA10} - 1)<0)'
        print(condition[bar])
    #         condition[bar] = f"""
    # signal_condition = ((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num))
    # down_signal_condition = (bar_down_trigger_signal/bar_trigger_signal)>{down_signal_ratio}
    # index_condition = False
    # final_flag = (signal_condition or index_condition)&down_signal_condition
    # print(final_flag)"""
    return condition,down_condition


def main(today):
    print(get_pre_trade_date(today, -1))

    para_list = [
        (prepare_condition_V4, (0.2, 0.5, 0), 'V4_2_1'),
        (prepare_condition_V6_2_1_selfdefine_index, (0.15, -0.008, 0, 'SZCZ', 'SZCZ'), 'V6_2_1'),
        # (prepare_condition_V6_2_1,(0.2,0,0),path_conf['condition_path'][:-1]+'V6_2_1/'),
        # (prepare_condition_V6_2_2,(0.2,0,0),path_conf['condition_path'][:-1]+'V6_2_2/'),
        # (prepare_condition_V6_2_3,(0.2,0,0),path_conf['condition_path'][:-1]+'V6_2_3/'),
        # (prepare_condition_V7,(0.2, 0.5, 0),path_conf['condition_path'][:-1]+'V7/'),
    ]
    target_date = list(filter(lambda x: x <= today, condition_change_history.keys()))
    target_date = max(target_date)
    para_list.append(condition_change_history[target_date] + ('',))
    # para_list.append()
    sig = get_singal(0.05, 'XGB_DTC_Matrix_Light_Cat', get_pre_trade_date(today, 30), today, f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/非固定时点近30日/')
    for func, para, extra_tag in para_list:
        condition = func(get_pre_trade_date(today, -1), sig, *para)
        save_nonfix_in_val(condition, f'condition{extra_tag}', today, non_fix_path)
        # pd.to_pickle(condition, f'{out_path}{today}.pkl')
    send_message(['015664'], f'Condition {today} done')
    send_message(['015664'], f'{condition[0][1000]}')

condition_change_history={
    # 20220112:(prepare_condition_V6_2_1_selfdefine_index,(0.15,-0.008,0,'SZCZ','SZCZ')),
    0:(prepare_condition_V4,(0.15,0.5,0)),

}

non_fix_path = '/data/group/800319/strategy_local_path_nonfixCondition/'
if __name__ == '__main__':

    from multiprocessing import Pool
    pool = Pool(10)
    for today in get_date_range(20220303,20220316):#[get_recent_trade_date()]:
        pool.apply_async(main,(today,))
    pool.close()
    pool.join()