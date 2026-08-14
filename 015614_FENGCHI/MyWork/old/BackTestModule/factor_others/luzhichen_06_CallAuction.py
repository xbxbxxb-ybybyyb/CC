from config import *
import pandas as pd
import time
import os
from multiprocessing import Pool
from dataApi.stockList import clean_stock_list
import numpy as np
from QuickFactorEvaluationBackTest import FactorBackTest
out_path = '/data/group/800319/junkData/CallAuction/'
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

def get_call_auction_data(stk_id_,start=20170101,end=20191231):
    from xquant.marketdata import MarketData
    print(stk_id_,'start')
    mdp_temp = MarketData(dfs=None)
    stk_id = str(stk_id_) + '.SH' if stk_id_ > 400000 else str(stk_id_).zfill(6) + '.SZ'
    year_list = [x for x in range(int(start / 10000), int(end / 10000) + 1)]
    data = pd.DataFrame()
    for year in year_list:
        for month in range(1, 13):
            df = mdp_temp.get_data_by_year_month("Stock", stk_id, str(year * 100 + month), ["1"], sort_by_receive_time=True)
            if len(df)==0:
                continue
            df = df.set_index(['MDDate', 'MDTime'])
            data = pd.concat([data, df])
    return data

def load_call_auction(stk_id):
    try:
        e = time.time()
        if os.path.exists(out_path+'%d.h5'%stk_id):
            return 0
        data = get_call_auction_data(stk_id)
        data.to_hdf(out_path+'%d.h5'%stk_id,str(stk_id))
        print(stk_id,'done',time.time()-e)
    except:
        print('------------------%d wrong------------------------'%stk_id)

def data_prepare():
    ZZ1800_pool = pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5', 'common_stock_list')
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    stk_list = list(filter(lambda stk_id: not os.path.exists(out_path+'%d.h5'%stk_id),ZZ1800_pool.columns.tolist()))
    pool = Pool(30)
    r = pool.map(load_call_auction,stk_list)
    pool.close()
    pool.join()

def load_local_data(stk_id):
    df = pd.read_hdf(out_path+'%d.h5'%stk_id,str(stk_id))
    return df

def calc_basic_factor(stk_id):
    temp_data = load_local_data(stk_id)
    if len(temp_data)==0:
        return pd.DataFrame()
    temp_data = temp_data.reset_index()
    temp_data['date_time'] = temp_data.MDDate.astype(str) + temp_data.MDTime.astype(str)
    temp_data['date_time'] = temp_data['date_time'].apply(lambda x: x[:-3])
    temp_data['date_time'] = pd.to_datetime(temp_data['date_time'])
    temp_data = temp_data.set_index('date_time')
    temp_data['price'] = temp_data[['Buy1Price', 'Sell1Price']].mean(axis=1)
    temp_data['pct_change'] = temp_data.price / temp_data.PreClosePx - 1
    temp_data['bar_pct_change'] = temp_data['price'].pct_change()

    phase1 = temp_data[('091500000' < temp_data.MDTime) * (temp_data.MDTime <= '092000000')][['MDDate', 'MDTime',
                                                                                              'Buy1Price', 'Sell1Price', 'price', 'pct_change', 'bar_pct_change']]  # .replace(0,np)
    phase1 = phase1[(phase1.Buy1Price != 0) * (phase1.Sell1Price != 0)]
    phase2 = temp_data['092000000' < temp_data.MDTime][['MDDate', 'MDTime',
                                                        'Buy1Price', 'Sell1Price', 'price', 'pct_change', 'bar_pct_change']]
    phase2 = phase2[(phase2.Buy1Price != 0) * (phase2.Sell1Price != 0)]
    phase1_start = phase1.resample('1B').first().dropna()
    phase1_end = phase1.resample('1B').last().dropna()
    phase2_start = phase2.resample('1B').first().dropna()
    phase2_end = phase2.resample('1B').last().dropna()
    phase1_max = phase1['pct_change'].resample('1B').max().dropna()
    phase1_min = phase1['pct_change'].resample('1B').min().dropna()
    phase2_bar_change_min = phase2['bar_pct_change'].resample('1B').min().dropna()
    #因子计算
    over_night_pct_change = phase1_start['pct_change']
    phase1_pct_change = phase1_start['price'] / phase1_end['price'] - 1
    phase2_pct_change = phase2_start['price'] / phase2_end['price'] - 1
    phase1_top = (phase1_max >= 0.1) * 1
    phase1_bottom = (phase1_min <= -0.1) * 1
    phase2_min_pct_change = (phase2_bar_change_min >= 0) * 1

    factor = pd.concat([over_night_pct_change, phase1_pct_change, phase2_pct_change, phase1_top,
                        phase1_bottom, phase2_min_pct_change], axis=1)
    factor.columns = ['over_night_pct_change', 'phase1_pct_change', 'phase2_pct_change', 'phase1_top',
                      'phase1_bottom', 'phase2_min_pct_change']
    factor.index = [int(x.strftime('%Y%m%d')) for x in factor.index]
    return factor

# os.mkdir(out_factor_path)
def load_factor_wraper(stk_id,out_factor_path = '/data/group/800319/junkData/temp_daily_by_lzc/CallAucFactor/'):
    try:
        if os.path.exists(out_factor_path+'%d.h5'%stk_id):
            return 0
        factor = calc_basic_factor(stk_id)
        factor.to_hdf(out_factor_path+'%d.h5'%stk_id,str(stk_id))
        print(stk_id, 'done')
    except:
        print('------------------%d wrong------------------------' % stk_id)
    return 1

def prepare_basic_factor():
    ZZ1800_pool = pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5', 'common_stock_list')

    stk_list = ZZ1800_pool.columns.tolist()
    # check = calc_basic_factor(stk_list[25])
    stk_list = list(filter(lambda x : not os.path.exists('/data/group/800319/junkData/temp_daily_by_lzc/CallAucFactor/%d.h5'%x),stk_list))
    # result = calc_basic_factor(stk_list[0])
    pool = Pool(20)
    r = pool.map(load_factor_wraper,stk_list)
    pool.close()
    pool.join()

def load_basic_factor(stk_id,out_factor_path = '/data/group/800319/junkData/temp_daily_by_lzc/CallAucFactor/'):
    basic_factor = pd.read_hdf(out_factor_path+'%d.h5'%stk_id,str(stk_id))
    return basic_factor

def load_all_basic_factors(stk_list):
    all_factors = dict()
    for stk in stk_list:
        all_factors[stk] = load_basic_factor(stk)
    all_factors = pd.Panel(all_factors)
    over_night_pct_change = all_factors.loc[:,:,'over_night_pct_change']
    phase1_pct_change = all_factors.loc[:, :, 'phase1_pct_change']
    phase2_pct_change = all_factors.loc[:, :, 'phase2_pct_change']
    phase1_top = all_factors.loc[:, :, 'phase1_top']
    phase1_bottom = all_factors.loc[:, :, 'phase1_bottom']
    phase2_steady_up = all_factors.loc[:, :, 'phase2_min_pct_change']
    #日频成交量
    amt_daily = get_daily_1factor('amt',code_list=stk_list)
    amt_daily_MA5 = amt_daily.rolling(5).mean()
    #分钟频成交量
    amt_minutes = get_minute_1factor('amt',20170101,20191231)
    amt_minutes = amt_minutes.reset_index()
    amt_auction = amt_minutes[amt_minutes.time==925].set_index('date').drop('time',axis=1).loc[20170101:20191231,stk_list]
    amt_aucation_ratio = 0.001*240*amt_auction/amt_daily.shift(1).loc[20170101:20191231]

    return over_night_pct_change, phase1_pct_change, phase2_pct_change,\
            phase1_top, phase1_bottom, phase2_steady_up, amt_aucation_ratio

def calc_AuctionAmt(auction_amt_threshold_down = 2,auction_amt_threshold_up = 6,open_num = 350):
    file_name = 'AucationAmtRation_down%d_up%d_open_num%d' % (auction_amt_threshold_down, auction_amt_threshold_up,open_num)
    if os.path.exists('/data/group/800319/junkData/temp_daily_by_lzc/AuctionAmt/%s.h5' % file_name):
        factor = pd.read_hdf('/data/group/800319/junkData/temp_daily_by_lzc/AuctionAmt/%s.h5' % file_name, file_name)
        return factor,file_name
    start_ = 20170101
    end_ = 20191231
    stock_pool_all = clean_stock_list(no_ST=True, stock_list='COMMON', least_live_days=120, no_pause=True, least_recover_days=5,
                                      no_limit_up=False, no_limit_down=False,
                                      address='/data/group/800319/junkData/daily')
    stock_pool_all = stock_pool_all.loc[start_:end_]
    stock_pool_all = stock_pool_all[stock_pool_all.sum().replace(0, np.nan).dropna().index]
    stk_list = stock_pool_all.columns.tolist()
    over_night_pct_change, phase1_pct_change, phase2_pct_change, \
    phase1_top, phase1_bottom, phase2_steady_up, amt_aucation_ratio = load_all_basic_factors(stk_list)
    # 因子合成


    # 成交量比按绝对阈值
    auction_amt_judge = (amt_aucation_ratio > auction_amt_threshold_down) * \
                        (amt_aucation_ratio < auction_amt_threshold_up)*1
    #成交量比按排序
    # auction_amt_rank = (amt_aucation_ratio*stock_pool_all).replace(0,np.nan).rank(axis=1,ascending=False)
    # auction_amt_judge = (auction_amt_rank<auction_amt_threshold_up)*(auction_amt_rank>auction_amt_threshold_down)
    #开盘按绝对阈值
    open_judge = (over_night_pct_change<0)*1
    # 开盘按排序
    # open_rank = (over_night_pct_change*stock_pool_all).replace(0,np.nan).rank(axis=1,ascending=True)
    # open_judge = (open_rank<open_num)*1

    buy_signal =  stock_pool_all*auction_amt_judge*phase2_steady_up#*open_judge
    print(buy_signal.sum().sum())
    daily_adj = get_daily_1factor(code_list=stock_pool_all.columns.tolist(), factor='close_badj')
    daily_open = get_daily_1factor(code_list=stock_pool_all.columns.tolist(), factor='open_badj')
    T2_profit = daily_adj.shift(-1) / daily_open - 1
    traded_profit = buy_signal * T2_profit
    for year in [2017, 2018, 2019]:
        check = traded_profit.loc[year * 10000 + 101:year * 10000 + 1231].replace(0, np.nan)
        check = check.values.reshape(check.shape[0] * check.shape[1])
        print(year, pd.Series(check).mean(), pd.Series(check).median(),pd.Series(check).dropna().shape)

    minutes_adj = get_minute_1factor('close', 201701030925, 201912311500, code_list=[1])
    minutes_adj.index = [x[0] * 10000 + x[1] for x in minutes_adj.index]
    time_list = [x % 10000 for x in minutes_adj.index[:242]]
    minute_signal_pn = pd.Panel({x: buy_signal for x in time_list})
    minute_signal_pn = minute_signal_pn.swapaxes(0, 1)
    minute_signal_pn.loc[:, 935:, :] = 0
    minute_signal = minute_signal_pn.values.reshape(minutes_adj.shape[0], buy_signal.shape[1])
    minute_signal = pd.DataFrame(minute_signal, index=minutes_adj.index, columns=buy_signal.columns)

    # os.mkdir('/data/group/800319/junkData/temp_daily_by_lzc/AuctionAmt/')
    minute_signal.to_hdf('/data/group/800319/junkData/temp_daily_by_lzc/AuctionAmt/%s.h5' % file_name, file_name)
    return minute_signal, file_name

def calc_sell_signal(up_active=0.02,down_active=0.01,up_profit=0.02,down_profit=0.01):

    start = 20170101
    end = 20191231
    file_name = 'ThresholdSell_upa%s_downa%s_upp%s_downp%s' % (up_active,down_active,up_profit,down_profit)
    if os.path.exists('%s/temp_daily_by_lzc/AuctionAmt/%s.h5' % (root_path, file_name)):
        df = pd.read_hdf('%s/temp_daily_by_lzc/AuctionAmt/%s.h5' % (root_path, file_name), file_name)
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

    active_up_judge = 0#daily_intraday_active>up_active
    active_down_judge = 0#daily_intraday_active<(-down_active)
    profit_up_judge = daily_intraday_net>(1+up_profit)
    profit_down_judge = daily_intraday_net<(1-down_profit)

    sell_signal = (active_up_judge+active_down_judge+profit_up_judge+profit_down_judge)
    sell_signal = (sell_signal>0)*-1
    sell_signal.to_hdf('%s/temp_daily_by_lzc/AuctionAmt/%s.h5' % (root_path, file_name), file_name)
    return sell_signal,file_name

if __name__=="__main__":
    # data_prepare()
    # prepare_basic_factor()
    factor_folder_name = 'AuctionAmt'
    factor_basic_path = root_path+'/temp_daily_by_lzc/'+factor_folder_name+'/'
    print(factor_basic_path)
    # os.mkdir('%s/result/'%factor_basic_path)
    factor_df1, tag = calc_AuctionAmt(open_num=-3)
    sell_signal, tag_sell = calc_sell_signal(up_active='',down_active='',up_profit=0.1,down_profit=0.001)
    print(sell_signal.sum().sum())
    factor_df1 = factor_df1 + sell_signal
    tag = tag + tag_sell
    factor_test = FactorBackTest(factor_df1)
    factor_test.evaluation(30)
    factor_test.result_output(fileroot='%s/result/'%factor_basic_path, filename='luzhichen_06_AuctionAmt')
    print(factor_test.evaluation_result)
    # if not os.path.exists('%s/result/fig_%s/'%(factor_basic_path,tag)):
    #     os.mkdir('%s/result/fig_%s/'%(factor_basic_path,tag))
    # factor_test.check_part_signal(80, '%s/result/fig_%s/'%(factor_basic_path,tag))
    print(factor_test.running_time)
    print(tag, 'done')

    # check_list = os.listdir('%s/result/' % factor_basic_path)
    # check_list = list(filter(lambda x : x.endswith('xlsx'),check_list))

    # signal_record = pd.read_excel('%s/result/' % factor_basic_path+
    #     'factorResult_AucationAmtRation_down2_up6_open_num350.xlsx',sheet_name='trading_record')
    # signal_record =signal_record.set_index('end')
    # signal_record = signal_record.resample('1y').mean()


