import pandas as pd
from dataApi.getData import *
import numpy as np
from config import *
from QuickFactorEvaluationBackTest import *
from dataApi.stockList import clean_stock_list
stock_pool_all = clean_stock_list(no_ST=True, stock_list='COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
                                      no_limit_up=False, no_limit_down=False,
                                      address='/data/group/800319/junkData/daily')
def get_ActiveReverse(DD_threshold,top_threshold,reverse_back_threshold):

    start = 20170101
    end = 20191231

    file_name = 'ActiveReverse_DD%s_top%s_rev%s' % (str(DD_threshold), str(top_threshold), str(reverse_back_threshold))
    if os.path.exists('%s/temp_daily_by_lzc/ActiveReserse/%s.h5' % (root_path, file_name)):
        df = pd.read_hdf('%s/temp_daily_by_lzc/ActiveReserse/%s.h5' % (root_path, file_name), file_name)
        return df

    ####
    stock_pool_all = clean_stock_list(no_ST=True, stock_list='COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
                                      no_limit_up=False, no_limit_down=False,
                                      address='/data/group/800319/junkData/daily')
    daily_stock_pool = {}
    for day in stock_pool_all:
        daily_stock_pool[day] = stock_pool_all[day]
    stk_list = stock_pool_all.columns.tolist()
    ####
    daily_adj = get_daily_1factor(code_list=stk_list, factor='close_badj')
    daily = get_daily_1factor(code_list=stk_list, factor='close_badj')
    minutes_adj = get_minute_1factor(start_datetime=start * 10000 + 925, end_datetime=end * 10000 + 1500, \
                                     code_list=stk_list, factor='close_badj')
    minutes_adj.index = [x[0] * 10000 + x[1] for x in minutes_adj.index]
    daily_adj = daily_adj.loc[start:end]
    minutes_adj = minutes_adj.loc[start * 10000 + 925:end * 10000 + 1500]
    ####
    benchmark_net = get_minute_1factor(start_datetime=start * 10000 + 925, end_datetime=end * 10000 + 1500, code_list=['ZZ500'], factor='close', type='bench')
    benchmark_net.index = [x[0] * 10000 + x[1] for x in benchmark_net.index]
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
    # 上次最大回撤至今涨了多少
    reverse_back = (daily_intraday_active_pn.values - daily_intraday_active_cummax.values) / daily_intraday_active_MDD.values + 1
    reverse_back = pd.Panel(reverse_back, items=daily_intraday_active_pn.items, major_axis=daily_intraday_active_pn.major_axis,
                            minor_axis=daily_intraday_active_pn.minor_axis)
    reverse_back = reverse_back.cummax(axis=1)
    # 反弹不超过某阈值

    reverse_back_judge = (reverse_back < reverse_back_threshold) * 1
    buy_signal = DD_judge.values * top_judge.values * MDD_judge.values * reverse_back_judge.values
    buy_signal = buy_signal.reshape(minutes_adj.shape[0], minutes_adj.shape[1])
    buy_signal = pd.DataFrame(buy_signal, index=minutes_adj.index, columns=minutes_adj.columns)

    file_name = 'ActiveReverse_DD%s_top%s_rev%s' % (str(DD_threshold), str(top_threshold), str(reverse_back_threshold))
    buy_signal.to_hdf('%s/temp_daily_by_lzc/ActiveReserse/%s.h5' % (root_path, file_name), file_name)
    return buy_signal

def calc_Factor(n):
    start = 20170101
    end = 20191231
    # if os.path.exists('%s/temp_daily_by_lzc/CorrT/CorrT%d.h5' % (root_path,n)):
    #     signal_df = pd.read_hdf('%s/temp_daily_by_lzc/CorrT/CorrT%d.h5' % (root_path, n), 'CorrT%d' % n)
    #     return signal_df
    ####
    stock_pool_all = clean_stock_list(no_ST=True, stock_list='COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
                                      no_limit_up=False, no_limit_down=False,
                                      address='/data/group/800319/junkData/daily')
    daily_stock_pool = {}
    for day in stock_pool_all:
        daily_stock_pool[day] = stock_pool_all[day]
    stk_list = stock_pool_all.columns.tolist()
    ####
    daily_adj = get_daily_1factor(code_list=stk_list, factor='close_badj')
    minutes_adj = get_minute_1factor(start_datetime=start * 10000 + 925, end_datetime=end * 10000 + 1500, \
                                     code_list=stk_list, factor='close_badj')
    minutes_adj.index = [x[0] * 10000 + x[1] for x in minutes_adj.index]
    daily_adj = daily_adj.loc[start:end]
    minutes_adj = minutes_adj.loc[start * 10000 + 925:end * 10000 + 1500]
    ####
    benchmark_net = get_minute_1factor(start_datetime=start * 10000 + 925, end_datetime=end * 10000 + 1500, code_list=['ZZ500'], factor='close', type='bench')
    benchmark_net.index = [x[0] * 10000 + x[1] for x in benchmark_net.index]
    benchmark_daily = get_daily_1factor(code_list=['ZZ500'], factor='close', type='bench')

    daily_free_float_share = []
    for day in daily_adj.index:
        temp_df = get_daily_1day(code_list=daily_adj.columns.tolist(), date=day, factor_list=['free_float_shares'])
        daily_free_float_share.append(temp_df.rename(columns={'free_float_shares': day}).T)
    daily_free_float_share = pd.concat(daily_free_float_share)
    daily_amt = get_daily_1factor(code_list=stk_list, factor='amt')
    daily_amt = daily_amt.loc[daily_adj.index]
    daily_turnover = daily_amt / daily_free_float_share


    factor = daily_adj.rolling(n).corr(daily_turnover)
    factor = (factor * stock_pool_all).replace(0, np.nan)
    factor_signal = (factor.rank(axis=1, ascending=True) < 150) * 1
    factor_signal = factor_signal.shift(1)

    time_list = [x % 10000 for x in minutes_adj.index[:242]]

    signal_pn = pd.Panel(1, items=daily_adj.index, major_axis=time_list, minor_axis=factor_signal.columns)
    signal_pn = signal_pn.multiply(factor_signal.T, axis=1)
    signal_pn.loc[:, :1000, :] = 0
    signal_df = pd.DataFrame(signal_pn.values.reshape(minutes_adj.shape[0], minutes_adj.shape[1]),
                             index=minutes_adj.index, columns=factor_signal.columns)
    # os.mkdir('%s/temp_daily_by_lzc/CorrT/' % root_path)
    signal_df.to_hdf('%s/temp_daily_by_lzc/CorrT/CorrT%d.h5' % (root_path,n), 'CorrT%d'%n)

    return signal_df
if __name__=="__main__":
    n = 30
    factor_df = calc_Factor(n)
    tag = 'CorrT%d'%n + '_rev'
    # factor_df1 = pd.read_hdf('%s/temp_daily_by_lzc/CorrT/CorrT.h5' % root_path, 'CorrT')
    print(factor_df.shape)
    ##############
    DD_threshold, top_threshold, reverse_back_threshold = (0.6,0.04,10000000)
    factor_df_intraday = get_ActiveReverse(DD_threshold, top_threshold, reverse_back_threshold)
    file_name = 'ActiveReverse_DD%s_top%s_rev%s' % (str(DD_threshold), str(top_threshold), str(reverse_back_threshold))
    tag = tag+file_name
    print(tag)
    ################
    factor_df1 = factor_df*factor_df_intraday

    factor_test = FactorBackTest(factor_df1)
    factor_test.evaluation(30)
    factor_test.result_output(fileroot='%s/temp_daily_by_lzc/CorrT/' % root_path, filename=tag)
    print(factor_test.evaluation_result)
    e = time.time()
    if not os.path.exists('%s/temp_daily_by_lzc/CorrT/fig_%s/' % (root_path,tag)):
        os.mkdir('%s/temp_daily_by_lzc/CorrT/fig_%s/' % (root_path,tag))
    factor_test.check_part_signal(80, '%s/temp_daily_by_lzc/CorrT/fig_%s/' % (root_path,tag), 15)
    print('fig time', time.time() - e)
    print(factor_test.running_time)



