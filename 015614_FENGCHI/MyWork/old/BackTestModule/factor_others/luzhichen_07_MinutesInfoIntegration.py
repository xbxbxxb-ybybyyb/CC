from QuickFactorEvaluationBackTest import *
from dataApi.stockList import clean_stock_list
import gc
def load_universe(start=20170101,end=20191231):
    stock_pool_all = clean_stock_list(no_ST=True, stock_list='COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
                                      no_limit_up=False, no_limit_down=False,
                                      address='/data/group/800319/junkData/daily')
    stock_pool_all = stock_pool_all.loc[start:end]
    stk_list = stock_pool_all.sum(axis=0)
    stk_list = stk_list.replace(0,np.nan).dropna().index.tolist()
    stock_pool_all = stock_pool_all[stk_list]
    daily_stock_pool = {}
    for day in stock_pool_all.index:
        daily_stock_pool[day] = stock_pool_all.loc[day, :].replace(False, np.nan).dropna().index.tolist()
    return stock_pool_all, daily_stock_pool, stk_list

def calc_DownVolRatio_and_Skew():
    start = 20170101
    end = 20191231
    stock_pool_all, daily_stock_pool, stk_list= load_universe(start,end)
    minutes_close_adj = get_minute_1factor('close_badj', int(str(start)+'0925'), int(str(end)+'1500'), code_list=stk_list)
    minutes_close_adj.index = [x[0]*10000+x[1] for x in minutes_close_adj.index]
    time_list = [x % 10000 for x in minutes_close_adj.index[:242]]
    date_list = list(set([int(x/10000) for x in minutes_close_adj.index]))
    date_list.sort()
    minutes_close_adj_pn = pd.Panel(minutes_close_adj.values.reshape(minutes_close_adj.shape[0]//242, 242,minutes_close_adj.shape[1]),
                                    items = date_list, major_axis=time_list, minor_axis=minutes_close_adj.columns)
    minutes_pct_change = minutes_close_adj_pn.pct_change(axis=1)
    daily_skew = minutes_pct_change.skew(axis=1)
    minutes_pct_change_square = minutes_pct_change.mul(minutes_pct_change)
    minutes_square_sum = minutes_pct_change_square.sum(axis=1)
    minutes_down_judge = minutes_pct_change<0
    minutes_down_vol = minutes_down_judge.mul(minutes_pct_change_square).sum(axis=1)
    daily_down_vol_ratio = (minutes_down_vol/minutes_square_sum).T.loc[stock_pool_all.index]
    return daily_down_vol_ratio,daily_skew

def calc_TailVolRatio():
    start = 20170101
    end = 20191231
    stock_pool_all, daily_stock_pool, stk_list = load_universe(start, end)
    minutes_vol = get_minute_1factor('vol', int(str(start) + '0925'), int(str(end) + '1500'), code_list=stk_list)
    minutes_vol.index = [x[0] * 10000 + x[1] for x in minutes_vol.index]
    time_list = [x % 10000 for x in minutes_vol.index[:242]]
    date_list = list(set([int(x / 10000) for x in minutes_vol.index]))
    date_list.sort()
    minutes_vol_pn = pd.Panel(minutes_vol.values.reshape(minutes_vol.shape[0] // 242, 242, minutes_vol.shape[1]),
                                    items=date_list, major_axis=time_list, minor_axis=minutes_vol.columns)
    daily_tail_vol = minutes_vol_pn.loc[:,1430:,:].sum(axis=1)
    daily_total_vol = minutes_vol_pn.sum(axis=1)
    tail_vol_ratio = daily_tail_vol/daily_total_vol
    return tail_vol_ratio

def Avg_CashFlowOutRatio_and_BigOrder():
    start = 20170101
    end = 20191231
    stock_pool_all, daily_stock_pool, stk_list = load_universe(start, end)
    minutes_amt = get_minute_1factor('amt', int(str(start) + '0925'), int(str(end) + '1500'), code_list=stk_list)
    minutes_amt.index = [x[0] * 10000 + x[1] for x in minutes_amt.index]
    minutes_close_adj = get_minute_1factor('close_badj', int(str(start) + '0925'), int(str(end) + '1500'), code_list=stk_list)
    minutes_close_adj.index = [x[0] * 10000 + x[1] for x in minutes_close_adj.index]
    time_list = [x % 10000 for x in minutes_amt.index[:242]]
    date_list = list(set([int(x / 10000) for x in minutes_amt.index]))
    date_list.sort()
    minutes_close_adj_pn = pd.Panel(minutes_close_adj.values.reshape(minutes_close_adj.shape[0] // 242, 242, minutes_close_adj.shape[1]),
                                    items=date_list, major_axis=time_list, minor_axis=minutes_close_adj.columns)
    minutes_amt_pn = pd.Panel(minutes_amt.values.reshape(minutes_close_adj.shape[0] // 242, 242, minutes_close_adj.shape[1]),
                                    items=date_list, major_axis=time_list, minor_axis=minutes_close_adj.columns)
    minutes_pct_change = minutes_close_adj_pn.pct_change(axis=1)
    #计算流出
    flow_out = minutes_pct_change<0
    daily_flow_out_amt = minutes_amt_pn.mul(flow_out).sum(axis=1)
    daily_flow_out_bar_num = flow_out.sum(axis=1)
    avg_out = daily_flow_out_amt/daily_flow_out_bar_num
    avg_flow = minutes_amt_pn.mean(axis=1)
    out_amt_ratio = avg_out/avg_flow

    #计算大单推动涨幅
    amt_rank = pd.Panel({x:minutes_amt_pn.loc[x,:,:].rank(axis=0,ascending = False) for x in minutes_amt_pn.items})
    big_order = amt_rank<=72
    big_order_pct = big_order.mul(minutes_pct_change)
    daily_big_order_pct = (1+big_order_pct).cumprod(axis=1)
    daily_big_order_pct = daily_big_order_pct.loc[:,1500,:]
    daily_big_order_net = daily_big_order_pct.cumprod()
    return out_amt_ratio,daily_big_order_net

def calc_IntegrationFactor(ratio):
    file_name = 'MinutesInfoIntegration_%s'%ratio
    if os.path.exists(root_path + '/temp_daily_by_lzc/MinutesInfoIntegration/%s.h5'%file_name):
        df = pd.read_hdf(root_path + '/temp_daily_by_lzc/MinutesInfoIntegration/%s.h5'%file_name,file_name)
        return df,file_name
    stock_pool_all, daily_stock_pool, stk_list = load_universe()
    daily_down_vol_ratio, daily_skew = calc_DownVolRatio_and_Skew()
    tail_vol_ratio = calc_TailVolRatio()
    out_amt_ratio, daily_big_order_net = Avg_CashFlowOutRatio_and_BigOrder()

    daily_adj = get_daily_1factor(code_list=stock_pool_all.columns.tolist(), factor='close_badj')
    daily_open = get_daily_1factor(code_list=stock_pool_all.columns.tolist(), factor='open_badj')
    T2_profit = daily_adj.shift(-1) / daily_open - 1

    rank3 = (daily_down_vol_ratio.rolling(10).mean().shift(1) * stock_pool_all.replace(False, np.nan)).rank(axis=1, ascending=False)
    rank2 = (daily_skew.T.rolling(12).mean().shift(1) * stock_pool_all.replace(False, np.nan)).rank(axis=1, ascending=True)
    rank1 = (tail_vol_ratio.T.rolling(6).mean().shift(1) * stock_pool_all.replace(False, np.nan)).rank(axis=1, ascending=True)
    rank0 = (out_amt_ratio.T.rolling(15).mean().shift(1) * stock_pool_all.replace(False, np.nan)).rank(axis=1, ascending=True)
    ## rank = (daily_big_order_net.T.pct_change(1).shift(1) * stock_pool_all.replace(False, np.nan)).rank(axis=1,ascending = False)
    N = 1800*ratio
    buy_signal = (rank0 < N) * (rank2 < N) * ((rank3 < N))#*(rank1 < 400)

    print(buy_signal.sum().sum())
    traded_profit = buy_signal * T2_profit
    for year in [2017, 2018, 2019]:
        check = traded_profit.loc[year * 10000 + 101:year * 10000 + 1231].replace(0, np.nan)
        net = (1 + check.mean(axis=1)).cumprod()
        check = check.values.reshape(check.shape[0] * check.shape[1])
        print(year, pd.Series(check).mean(), pd.Series(check).median(), net.tolist()[-1], pd.Series(check).dropna().shape)
    minutes_adj = get_minute_1factor('close', 201701030925, 201912311500, code_list=[1])
    minutes_adj.index = [x[0] * 10000 + x[1] for x in minutes_adj.index]
    time_list = [x % 10000 for x in minutes_adj.index[:242]]
    minute_signal_pn = pd.Panel({x: buy_signal.loc[20170101:20191231] for x in time_list})
    minute_signal_pn = minute_signal_pn.swapaxes(0, 1)
    minute_signal_pn.loc[:, 935:, :] = 0
    minute_signal = minute_signal_pn.values.reshape(minutes_adj.shape[0], buy_signal.shape[1])
    minute_signal = pd.DataFrame(minute_signal, index=minutes_adj.index, columns=buy_signal.columns)
    minute_signal.to_hdf(root_path + '/temp_daily_by_lzc/MinutesInfoIntegration/%s.h5'%file_name,file_name)
    return minute_signal,file_name
if __name__=="__main__":

    factor_folder_name = 'MinutesInfoIntegration'
    factor_basic_path = root_path + '/temp_daily_by_lzc/' + factor_folder_name + '/'
    # os.mkdir(factor_basic_path)
    # os.mkdir(factor_basic_path+'result/')
    # factor_df1 = pd.read_hdf(factor_basic_path+factor_folder_name+'.h5',factor_folder_name)
    factor_df1,tag = calc_IntegrationFactor(0.15)
    print(tag)
    _ = gc.collect()
    factor_test = FactorBackTest(factor_df1)
    factor_test.evaluation(30)
    print(factor_test.evaluation_result)
    factor_test.result_output(fileroot='%s/result/' % factor_basic_path, filename='luzhichen_07_'+tag)

    if not os.path.exists('%s/result/fig_%s/'%(factor_basic_path,tag)):
        os.mkdir('%s/result/fig_%s/'%(factor_basic_path,tag))
    factor_test.check_part_signal(80, '%s/result/fig_%s/'%(factor_basic_path,tag))
    print(factor_test.running_time)
    print(tag, 'done')
