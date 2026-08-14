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
from online_conf import *
import os

path_conf = get_path_conf('/data/group/800319/strategy_local_path3/', create=True)
local_config_path, holding_info_path, hyper_param_path, code_list_path, model_config_path, buy_time_info_path, \
vol_info_path, init_conf_path, daily_out_path, ratio_path, matrix_conf = \
    [path_conf[x] for x in
     ['local_config_path', 'holding_info_path', 'hyper_param_path', 'code_list_path', 'model_config_path', 'buy_time_info_path',
      'vol_info_path', 'init_conf_path', 'daily_out_path', 'ratio_path', 'matrix_conf']]


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


def prepare_condition_V4(date, signal_file, signal_threshold, down_signal_ratio, down_condition):
    bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    signal, _ = pd.read_pickle(signal_file)
    signal = signal.loc[:date]
    date_list = get_date_range(signal.index[0][0], date)
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, bar_list)))
    signal = signal.reindex(index).fillna(False)
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


def prepare_condition_V6_2_1(date, signal_file, signal_threshold, index_pct_change_ratio=0,down_condition=0,index_tag='SZZ'):
    """
    信号数量 and (低于5日均线 or MA5<MA10)
    """
    bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    signal, _ = pd.read_pickle(signal_file)
    signal = signal.loc[:date]
    date_list = get_date_range(signal.index[0][0], date)
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, bar_list)))
    signal = signal.reindex(index).fillna(False)
    barly_r_20d_ratio, _ = calc_recent_count(signal.fillna(False), 20)
    barly_ratio = barly_r_20d_ratio.loc[date]
    barly_cum_ratio = barly_ratio.cumsum()
    SZZZ = get_daily_1factor('close', code_list=['SZZZ'], date_list=get_date_range(get_pre_trade_date(date,11),get_pre_trade_date(date,1)), type='bench')
    MA5 = SZZZ[-5:].mean()['SZZZ']
    MA10 = SZZZ[-10:].mean()['SZZZ']
    condition = {}
    for bar in bar_list:
        # (((bar_first_trigger_num / 0.23787878787878788) > (0.2 * pool_num)) or ((bar_cum_first_trigger_num / 0.23787878787878788) > (0.2 * pool_num))) and ((SZZS/3000-1)<0 or (100/400 - 1)<0)
        condition[bar] = f'(((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) ' \
            f'or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num)))' \
            f'and ((SZZS/{MA5}-1)<{index_pct_change_ratio} or ({MA5}/{MA10} - 1)<0)'
        print(condition[bar])
    #         condition[bar] = f"""
    # signal_condition = ((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num))
    # down_signal_condition = (bar_down_trigger_signal/bar_trigger_signal)>{down_signal_ratio}
    # index_condition = False
    # final_flag = (signal_condition or index_condition)&down_signal_condition
    # print(final_flag)"""
    return condition,down_condition

def prepare_condition_V6_2_1_selfdefine_index(date, signal_file, signal_threshold, index_pct_change_ratio=0,down_condition=0
                                              ,offline_index_tag=None,online_index_tag=None):
    """
    信号数量 and (低于5日均线 or MA5<MA10)
    """
    bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    signal, _ = pd.read_pickle(signal_file)
    signal = signal.loc[:date]
    date_list = get_date_range(signal.index[0][0], date)
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, bar_list)))
    signal = signal.reindex(index).fillna(False)
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


def prepare_condition_V6_2_2(date, signal_file, signal_threshold, index_pct_change_ratio=0, down_condition=0):
    """
    信号数量 and 低于5日均线
    """
    bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    signal, _ = pd.read_pickle(signal_file)
    signal = signal.loc[:date]
    date_list = get_date_range(signal.index[0][0], date)
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, bar_list)))
    signal = signal.reindex(index).fillna(False)
    barly_r_20d_ratio, _ = calc_recent_count(signal.fillna(False), 20)
    barly_ratio = barly_r_20d_ratio.loc[date]
    barly_cum_ratio = barly_ratio.cumsum()
    SZZZ = get_daily_1factor('close', code_list=['SZZZ'], date_list=get_date_range(get_pre_trade_date(date,11),get_pre_trade_date(date,1)), type='bench')
    MA5 = SZZZ[-5:].mean()['SZZZ']
    MA10 = SZZZ[-10:].mean()['SZZZ']
    condition = {}
    for bar in bar_list:
        # (((bar_first_trigger_num / 0.23787878787878788) > (0.2 * pool_num)) or ((bar_cum_first_trigger_num / 0.23787878787878788) > (0.2 * pool_num))) and ((SZZS/3000-1)<0 or (100/400 - 1)<0)
        condition[bar] = f'(((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) ' \
            f'or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num)))' \
            f'and (SZZS/{MA5}-1)<{index_pct_change_ratio}'
        print(condition[bar])
    #         condition[bar] = f"""
    # signal_condition = ((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num))
    # down_signal_condition = (bar_down_trigger_signal/bar_trigger_signal)>{down_signal_ratio}
    # index_condition = False
    # final_flag = (signal_condition or index_condition)&down_signal_condition
    # print(final_flag)"""
    return condition, down_condition

def prepare_condition_V6_2_3(date, signal_file, signal_threshold, index_pct_change_ratio=0, down_condition=0):
    """
    信号数量 and MA5<MA10
    """
    bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    signal, _ = pd.read_pickle(signal_file)
    signal = signal.loc[:date]
    date_list = get_date_range(signal.index[0][0], date)
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, bar_list)))
    signal = signal.reindex(index).fillna(False)
    barly_r_20d_ratio, _ = calc_recent_count(signal.fillna(False), 20)
    barly_ratio = barly_r_20d_ratio.loc[date]
    barly_cum_ratio = barly_ratio.cumsum()
    SZZZ = get_daily_1factor('close', code_list=['SZZZ'], date_list=get_date_range(get_pre_trade_date(date,11),get_pre_trade_date(date,1)), type='bench')
    MA5 = SZZZ[-5:].mean()['SZZZ']
    MA10 = SZZZ[-10:].mean()['SZZZ']
    condition = {}
    for bar in bar_list:
        # (((bar_first_trigger_num / 0.23787878787878788) > (0.2 * pool_num)) or ((bar_cum_first_trigger_num / 0.23787878787878788) > (0.2 * pool_num))) and ((SZZS/3000-1)<0 or (100/400 - 1)<0)
        condition[bar] = f'(((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) ' \
            f'or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num)))' \
            f'and ({MA5}/{MA10} - 1)<0'
        print(condition[bar])
    #         condition[bar] = f"""
    # signal_condition = ((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num))
    # down_signal_condition = (bar_down_trigger_signal/bar_trigger_signal)>{down_signal_ratio}
    # index_condition = False
    # final_flag = (signal_condition or index_condition)&down_signal_condition
    # print(final_flag)"""
    return condition, down_condition

def prepare_condition_V7(date, signal_file, signal_threshold, down_signal_ratio, down_condition):
    bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    signal, _ = pd.read_pickle(signal_file)
    signal = signal.loc[:date]
    date_list = get_date_range(signal.index[0][0], date)
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list, bar_list)))
    signal = signal.reindex(index).fillna(False)
    barly_r_20d_ratio, _ = calc_recent_count(signal.fillna(False), 20)
    barly_ratio = barly_r_20d_ratio.loc[date]
    barly_cum_ratio = barly_ratio.cumsum()
    SZZZ = get_daily_1factor('close', code_list=['SZZZ'], date_list=get_date_range(get_pre_trade_date(date, 11), get_pre_trade_date(date, 1)), type='bench')
    MA5 = SZZZ[-5:].mean()['SZZZ']
    MA10 = SZZZ[-10:].mean()['SZZZ']
    condition = {}
    for bar in bar_list:
        condition[bar] = f'(((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) ' \
            f'or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num)))' \
            f'and ((bar_down_trigger_signal/bar_trigger_signal)>{down_signal_ratio} or ({MA5}/{MA10} - 1)<0)'
        print(condition[bar])

    #         condition[bar] = f"""
    # signal_condition = ((bar_first_trigger_num/{barly_ratio[bar]})>({signal_threshold}*pool_num)) or ((bar_cum_first_trigger_num/{barly_cum_ratio[bar]})>({signal_threshold}*pool_num))
    # down_signal_condition = (bar_down_trigger_signal/bar_trigger_signal)>{down_signal_ratio}
    # index_condition = False
    # final_flag = (signal_condition or index_condition)&down_signal_condition
    # print(final_flag)"""
    return condition, down_condition

condition_change_history={
    20220112:(prepare_condition_V6_2_1_selfdefine_index,(0.15,-0.008,0,'SZCZ','SZCZ')),
    20220221:(prepare_condition_V4,(0.15,0.5,0)),
    20220309:(prepare_condition_V6_2_1_selfdefine_index,(0.15,-0.008,0,'SZCZ','SZCZ')),
    20220322:(prepare_condition_V4,(0.15,0.5,0)),
}


if __name__ == '__main__':

    # today = get_recent_trade_date()
    # signal_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_new_out_sample_2021_XGBWithSWSHIFReSaveTWithOrigin_Cat_LightWithoutMax5_0.05.pkl'
    # signal_threshold, down_signal_ratio, down_condition = 0.2, 0.5, 0
    # date_list = get_date_range(20210910, 20210928) + [20220106,20220107]
    from dataApi.sendInfo import send_message

    for today in [get_recent_trade_date()]:
        signal_file = f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/实盘跟踪线下信号/signal_OutSample_XGB_Cat_Light_SWMatrix_OnlineTest_{get_pre_trade_date(today)}.pkl'
        print(get_pre_trade_date(today, -1))

        para_list = [
            (prepare_condition_V4,(0.2,0.5,0),path_conf['condition_path'][:-1]+'V4_2_1/'),
            (prepare_condition_V6_2_1_selfdefine_index, (0.15, -0.008, 0, 'SZCZ', 'SZCZ'), path_conf['condition_path'][:-1]+'V6_2_1/'),
            # (prepare_condition_V6_2_1,(0.2,0,0),path_conf['condition_path'][:-1]+'V6_2_1/'),
            # (prepare_condition_V6_2_2,(0.2,0,0),path_conf['condition_path'][:-1]+'V6_2_2/'),
            # (prepare_condition_V6_2_3,(0.2,0,0),path_conf['condition_path'][:-1]+'V6_2_3/'),
            # (prepare_condition_V7,(0.2, 0.5, 0),path_conf['condition_path'][:-1]+'V7/'),
                     ]
        target_date = list(filter(lambda x :x<=today,condition_change_history.keys()))
        target_date = max(target_date)
        para_list.append(condition_change_history[target_date]+(path_conf['condition_path'],))
        # para_list.append()
        for func,para,out_path in para_list:
            condition = func(get_pre_trade_date(today, -1), signal_file,*para)
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            pd.to_pickle(condition, f'{out_path}{today}.pkl')
        send_message(['015664'],f'Condition {today} done')
        send_message(['015664'],f'{condition[0][1000]}')
    # signal1,pred_ret1 = pd.read_pickle(f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/实盘跟踪线下信号/signal_OutSample_XGB_Cat_Light_SWMatrix_OnlineTest_20220107.pkl')
    # signal2,pred_ret2 = pd.read_pickle(f'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/实盘跟踪线下信号/signal_OutSample_XGB_Cat_Light_SWMatrix_OnlineTest_20220106.pkl')
    #
    # check = pred_ret1.loc[:20220106] - pred_ret2.loc[:20220106]
