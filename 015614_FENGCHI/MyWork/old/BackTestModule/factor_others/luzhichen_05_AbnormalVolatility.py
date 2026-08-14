import pandas as pd
import numpy as np
import os
from dataApi.getData import *
from config import *
from QuickFactorEvaluationBackTest import FactorBackTest
import time
import copy
from dataApi.stockList import clean_stock_list

def load_basic_data(start,end,index_id):
    daily_stock_pool = get_stock_pool(index_id)
    pool = pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5', index_id)
    stk_list = pool.columns.tolist()
    daily_adj = get_daily_1factor(code_list=stk_list, factor='close_badj')
    daily = get_daily_1factor(code_list=stk_list, factor='close')
    minutes_adj = get_minute_1factor(start_datetime=start * 10000 + 925, end_datetime=end * 10000 + 1500,
                                     code_list=stk_list, factor='close_badj')
    minutes_adj.index = [x[0] * 10000 + x[1] for x in minutes_adj.index]
    daily_adj = daily_adj.loc[start:end]
    minutes_adj = minutes_adj.loc[start * 10000 + 925:end * 10000 + 1500]
    benchmark_net = get_minute_1factor(start_datetime=start * 10000 + 925, end_datetime=end * 10000 + 1500, code_list=['ZZ500'], factor='close', type='bench')
    benchmark_net.index = [x[0] * 10000 + x[1] for x in benchmark_net.index]
    return daily,daily_adj,minutes_adj,benchmark_net,pool,daily_stock_pool

def calc_AbnormalVol_up(threshold,stk_num):
    # threshold = 0.04
    # stk_num = 250
    start_ = 20170101
    end_ = 20191231
    stock_pool_all = clean_stock_list(no_ST=True, stock_list='COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
                                      no_limit_up=False, no_limit_down=False,
                                      address='/data/group/800319/junkData/daily')
    daily_close, daily_adj, minutes_adj, benchmark_net, pool, daily_stock_pool = \
        load_basic_data(start_, end_, 'common_stock_list')
    benchmark_daily = pd.read_excel('/data/user/015664/日内回测/万德全A.xlsx')
    benchmark_daily = benchmark_daily[2:].T.set_index(2).T  # .set_index('Date')
    benchmark_daily['Date'] = benchmark_daily['Date'].apply(lambda x: int(x.strftime('%Y%m%d')))
    benchmark_daily = benchmark_daily.set_index('Date')
    high = get_daily_1factor(code_list=pool.columns.tolist(), factor='high')
    high = high.loc[start_:end_]
    benchmark_daily['daily_pct_change'] = benchmark_daily['close'].pct_change()
    benchmark_daily['intraday_pct_change'] = benchmark_daily['close'] / benchmark_daily['open'] - 1
    benchmark_daily = benchmark_daily.loc[start_:end_]
    daily_close = daily_close.loc[start_:end_]
    # 定义进一个月涨幅
    pct_change_month = daily_adj.pct_change(20) * stock_pool_all.loc[pool.index,pool.columns].replace(False,np.nan)#pool.replace(False,np.nan)
    pct_change_month = pct_change_month.loc[start_:end_]
    pct_change_rank_up = pct_change_month.rank(axis=1, ascending=False)
    pct_change_judge_up = (pct_change_rank_up < stk_num)  # *(pct_change_rank_up>20)
    ##定义上涨时期的异动
    up_values = high / daily_close - 1
    up_stock = (up_values > threshold) * 1
    mkt_up_judge = benchmark_daily['daily_pct_change'].apply(lambda x: (x > 0) * 1)
    up_judge = up_stock.mul(mkt_up_judge, axis=0) * pct_change_judge_up
    buy_signal = up_judge.shift(1)
    buy_signal = buy_signal * pool.loc[buy_signal.index]
    time_list = [x % 10000 for x in minutes_adj.index[:242]]
    minute_signal_pn = pd.Panel({x: buy_signal for x in time_list})
    minute_signal_pn = minute_signal_pn.swapaxes(0, 1)
    minute_signal_pn.loc[:, 938:, :] = 0
    minute_signal = minute_signal_pn.values.reshape(minutes_adj.shape[0], minutes_adj.shape[1])
    minute_signal = pd.DataFrame(minute_signal, index=minutes_adj.index, columns=minutes_adj.columns)
    tag = 'AbnormalVolatility_up_buy%s_stk_num%d' % (str(threshold),stk_num)
    minute_signal.to_hdf('%s/temp_daily_by_lzc/AbnormalVolatility/%s.h5' % (root_path, tag), tag)

    daily_open = get_daily_1factor(code_list=pool.columns.tolist(), factor='open_badj')
    T2_profit = daily_adj.shift(-1) / daily_open - 1
    traded_profit = buy_signal * T2_profit
    for year in [2017, 2018, 2019]:
        check = traded_profit.loc[year * 10000 + 101:year * 10000 + 1231].replace(0, np.nan)
        check = check.values.reshape(check.shape[0] * check.shape[1])
        print(year, pd.Series(check).mean())
    return minute_signal,tag

def calc_AbnormalVol_down(threshold):
    start_ = 20170101
    end_ = 20191231
    daily_close, daily_adj, minutes_adj, benchmark_net, pool, daily_stock_pool = \
        load_basic_data(start_, end_, 'common_stock_list')
    benchmark_daily = pd.read_excel('/data/user/015664/日内回测/万德全A.xlsx')
    benchmark_daily = benchmark_daily[2:].T.set_index(2).T  # .set_index('Date')
    benchmark_daily['Date'] = benchmark_daily['Date'].apply(lambda x: int(x.strftime('%Y%m%d')))
    benchmark_daily = benchmark_daily.set_index('Date')
    low = get_daily_1factor(code_list=pool.columns.tolist(), factor='low')
    low = low.loc[start_:end_]
    benchmark_daily['daily_pct_change'] = benchmark_daily['close'].pct_change()
    benchmark_daily['intraday_pct_change'] = benchmark_daily['close'] / benchmark_daily['open'] - 1
    benchmark_daily = benchmark_daily.loc[start_:end_]
    daily_close = daily_close.loc[start_:end_]
    #定义进一个月涨幅
    pct_change_month = daily_adj.pct_change(20)*pool
    pct_change_month = pct_change_month.loc[start_:end_]
    pct_change_rank_down = pct_change_month.rank(axis=1, ascending=True)
    pct_change_judge_down = (pct_change_rank_down < 200)*(pct_change_rank_down >50)
    ##定义下跌时期的异动
    down_values = daily_close / low - 1
    down_stock = (down_values > threshold) * 1
    mkt_down_judge = benchmark_daily['daily_pct_change'].apply(lambda x: (x < 0) * 1)
    down_judge = down_stock.mul(mkt_down_judge, axis=0)*pct_change_judge_down
    buy_signal =  down_judge.shift(1)
    buy_signal = buy_signal*pool.loc[buy_signal.index]
    time_list = [x % 10000 for x in minutes_adj.index[:242]]
    minute_signal_pn = pd.Panel({x: buy_signal for x in time_list})
    minute_signal_pn = minute_signal_pn.swapaxes(0, 1)
    minute_signal_pn.loc[:, 938:, :] = 0
    minute_signal = minute_signal_pn.values.reshape(minutes_adj.shape[0], minutes_adj.shape[1])
    minute_signal = pd.DataFrame(minute_signal, index=minutes_adj.index, columns=minutes_adj.columns)
    tag = 'AbnormalVolatility_down_buy%s' % (str(threshold))
    minute_signal.to_hdf('%s/temp_daily_by_lzc/AbnormalVolatility/%s.h5' % (root_path, tag), tag)
    return minute_signal,tag

def sell_signal(DD_threshold,top_threshold):

    start = 20170101
    end = 20191231

    # DD_threshold, top_threshold = 0.3,0.05

    file_name = 'ActiveReverseSell_DD%s_top%s' % (str(DD_threshold), str(top_threshold))
    if os.path.exists('%s/temp_daily_by_lzc/AbnormalVolatility/%s.h5' % (root_path, file_name)):
        df = pd.read_hdf('%s/temp_daily_by_lzc/AbnormalVolatility/%s.h5' % (root_path, file_name), file_name)
        return df, file_name
    daily, daily_adj, minutes_adj, benchmark_net, pool, daily_stock_pool = \
        load_basic_data(start, end, 'common_stock_list')
    stk_list = pool.columns.tolist()
    # 计算每个个股每天的日内net_value
    daily_3d = minutes_adj.values.reshape(daily_adj.shape[0], 242, daily_adj.shape[1])
    daily_intraday_net = daily_3d.swapaxes(0, 1) / daily_3d[:, 0, :]
    daily_intraday_net = pd.DataFrame(daily_intraday_net.swapaxes(0, 1).reshape(minutes_adj.shape[0], minutes_adj.shape[1]),
                                      index=minutes_adj.index, columns=minutes_adj.columns)
    # 计算基准每天的日内Net Value
    benchmark_daily_intraday = benchmark_net.values.reshape(int(benchmark_net.shape[0] / 242), 242)
    benchmark_daily_intraday = (benchmark_daily_intraday.swapaxes(0, 1) / benchmark_daily_intraday[:, 0]).swapaxes(0, 1)
    benchmark_daily_intraday = pd.DataFrame(benchmark_daily_intraday.reshape(benchmark_net.shape[0], 1),
                                            index=benchmark_net.index, columns=benchmark_net.columns)
    # 每只个股每天日内超额
    time_list = [x % 10000 for x in daily_intraday_net.index[:242]]
    daily_intraday_active = daily_intraday_net.values - benchmark_daily_intraday.loc[daily_intraday_net.index].values
    daily_intraday_active = pd.DataFrame(daily_intraday_active, index=daily_intraday_net.index, columns=daily_intraday_net.columns)

    daily_intraday_active_pn = pd.Panel(daily_intraday_active.values.reshape(daily_intraday_active.shape[0] // 242, 242, daily_intraday_active.shape[1]),
                                        items=daily_adj.index, major_axis=time_list, minor_axis=daily_intraday_active.columns)
    daily_intraday_active_cummax = daily_intraday_active_pn.cummax(axis=1)
    daily_intraday_active_DD = pd.Panel(daily_intraday_active_cummax.values - daily_intraday_active_pn.values,
                                        items=daily_intraday_active_pn.items, major_axis=daily_intraday_active_pn.major_axis,
                                        minor_axis=daily_intraday_active_pn.minor_axis)
    daily_intraday_active_MDD = daily_intraday_active_DD.cummax(axis=1)
    # 当前处于超额收益最大回撤点
    MDD_judge = (daily_intraday_active_MDD == daily_intraday_active_DD) * 1
    # 先前超额收益高点非开盘时候
    top_judge = (daily_intraday_active_cummax > top_threshold) * 1
    # 回撤超过阈值
    DD_judge = (daily_intraday_active_MDD > DD_threshold * daily_intraday_active_cummax) * 1
    # 反弹不超过某阈值
    sell_signal = DD_judge.mul(top_judge).mul(MDD_judge)
    # sell_signal.loc[:, :1300, :] = 0
    # # 1400后超额收益处于高点，则止盈
    # active_top_judge = (daily_intraday_active_cummax==daily_intraday_active_pn)*1
    # active_top_judge.loc[:, :1400, :] = 0
    # # 1400后绝对收益处于最高点，则止盈
    # daily_intraday_net = daily_3d.swapaxes(0, 1) / daily_3d[:, 0, :]
    # daily_intraday_net = pd.Panel(daily_intraday_net.swapaxes(0, 1),
    #                               items=daily_intraday_active_pn.items, major_axis=daily_intraday_active_pn.major_axis,
    #                               minor_axis=daily_intraday_active_pn.minor_axis)
    # daily_intraday_net_cummax = daily_intraday_net.cummax(axis=1)
    # prodit_top_judge = (daily_intraday_net_cummax==daily_intraday_net)*1
    # prodit_top_judge.loc[:, :1400, :] = 0
    # sell_signal = sell_signal.add(prodit_top_judge).add(active_top_judge)
    sell_signal = (sell_signal>0)*-1
    sell_signal = sell_signal.values.reshape(minutes_adj.shape[0], minutes_adj.shape[1])
    sell_signal = pd.DataFrame(sell_signal, index=minutes_adj.index, columns=minutes_adj.columns)
    file_name = 'ActiveReverseSell_DD%s_top%s' % (str(DD_threshold), str(top_threshold))
    sell_signal.to_hdf('%s/temp_daily_by_lzc/AbnormalVolatility/%s.h5' % (root_path, file_name), file_name)
    return sell_signal,file_name


if __name__=="__main__":
    print('_extra_filter123')
    threshold_ = 0.04
    factor_df1,tag = calc_AbnormalVol_up(threshold_,250)
    # factor_sell,tag_sell = sell_signal(DD_threshold=0.31,top_threshold=0.05)
    # tag = tag+tag_sell
    # factor_df1 = factor_buy + factor_sell
    # tag = 'AbnormalVolatility_buy%s' % str(threshold_)+'_only_up'
    # factor_df1 = pd.read_hdf('%s/temp_daily_by_lzc/AbnormalVolatility/AbnormalVolatility_buy%s.h5' % (root_path, tag), tag)
    tag = tag+'_extra_filter'
    factor_df1 = factor_df1#.T[:100].T
    factor_test = FactorBackTest(factor_df1,daily_stock_pool=common_stock_list_pool)
    factor_test.evaluation(10)
    factor_test.result_output(fileroot='/data/group/800319/junkData/temp_daily_by_lzc/AbnormalVolatility/result/', filename=tag)
    print(factor_test.evaluation_result)
    if not os.path.exists('/data/group/800319/junkData/temp_daily_by_lzc/AbnormalVolatility/result/fig_%s/' % tag):
        os.mkdir('/data/group/800319/junkData/temp_daily_by_lzc/AbnormalVolatility/result/fig_%s/' % tag)
    factor_test.check_part_signal(80, '/data/group/800319/junkData/temp_daily_by_lzc/AbnormalVolatility/result/fig_%s/' % tag)
    print(factor_test.running_time)
    print(tag, 'done')