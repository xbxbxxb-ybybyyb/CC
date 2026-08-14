import time
from config import *
from multiprocessing import Pool
import datetime
import copy
from xquant.strategy.backtest.Performance import *
import pandas as pd
from scipy import stats
import random
import gc
# from numba import jit


def get_signals_evaluation(signals_records,N):
    """
    信号评估
    :param signals_records: 每行一次交易统计
    :return:
    """
    evaluation = signals_records.mean().loc[['profit', 'active', 'holding_minutes']]
    evaluation = evaluation.rename(index= \
                                       {'profit': 'mean_profit', 'active': 'mean_active', 'holding_minutes': 'mean_holding_minutes'})
    evaluation['profit_win_rate'] = (signals_records['profit'] > 0).mean()
    evaluation['mean_earning'] = ((signals_records['profit'] > 0) * signals_records['profit']).replace(0, np.nan).dropna().mean()
    evaluation['mean_loss'] = ((signals_records['profit'] <= 0) * signals_records['profit']).replace(0, np.nan).dropna().mean()
    evaluation['earning_loss_ratio'] = evaluation['mean_earning'] / abs(evaluation['mean_loss'])
    evaluation['active_win_rate'] = (signals_records['active'] > 0).mean()
    evaluation['mean_active_earning'] = ((signals_records['active'] > 0) * signals_records['active']).replace(0, np.nan).dropna().mean()
    evaluation['mean_active_loss'] = ((signals_records['active'] < 0) * signals_records['active']).replace(0, np.nan).dropna().mean()
    evaluation['active_earning_loss_ratio'] = evaluation['mean_active_earning'] / abs(evaluation['mean_active_loss'])
    evaluation['close_position_at_T+%d_end'%N] = (signals_records['end'].apply(lambda x : x%10000)==1456).sum()/float(len(signals_records))
    signal_exit = signals_records[signals_records['strict_exit']==1]
    evaluation['mean_active_exit'] = signal_exit['active'].mean()
    evaluation['active_exit_win_rate'] = (signal_exit['active']>0).mean()
    signal_whole = signals_records[signals_records['strict_exit']==0]
    evaluation['mean_active_signal'] = signal_whole['active'].mean()
    evaluation['active_signal_win_rate'] = (signal_whole['active'] > 0).mean()
    return evaluation

def get_signals_evaluation_daily(signals_records_):
    """
    信号日频评估
    :param signals_records: 每行一次交易统计
    :return:
    """
    signals_records = copy.deepcopy(signals_records_)
    signals_records.start = signals_records.start.astype(str)
    signals_records.start = pd.to_datetime(signals_records.start)
    signals_records.end = signals_records.end.astype(str)
    signals_records.end = pd.to_datetime(signals_records.end)
    count_start = signals_records.set_index('start').resample('B').size()
    count_end = signals_records.set_index('end').resample('B').size()
    profit_day = signals_records.set_index('end').profit.resample('B').mean()
    win_rate_profit_day = (signals_records.set_index('end').profit > 0).resample('B').mean()
    active_day = signals_records.set_index('end').active.resample('B').mean()
    win_rate_active_day = (signals_records.set_index('end').active > 0).resample('B').mean()
    holding_minutes_day = signals_records.set_index('end').holding_minutes.astype(float).resample('B').mean()
    result_day = pd.concat([count_start, count_end], axis=1)
    result_day.columns = ['numBuy', 'numSell']
    result_day .index.name = None
    result_day['mean_profit'] = profit_day
    result_day['mean_active'] = active_day
    result_day['profit_win_rate'] = win_rate_profit_day
    result_day['active_win_rate'] = win_rate_active_day
    result_day['holdingMinutes'] = holding_minutes_day
    result_day.index = result_day.index.to_period('D')
    return result_day

def get_net_value_evaluation(net_value, benchmark_net):
    Pf = Performance()
    annual_return = Pf.Annualized_Returns(net_value, start_date=net_value.index[0], end_date=net_value.index[-1])
    benchmark_return = Pf.Benchmark_Returns(benchmark_net, start_date=benchmark_net.index[0], end_date=benchmark_net.index[-1])
    annual_active = annual_return[0][0] - benchmark_return[0][0]
    volatility = Pf.Volatility(net_value, start_date=net_value.index[0], end_date=net_value.index[-1])
    # sharpe = Pf.Sharpe_Ratio(net_value, end_date=net_value.index[-1], rf=0.02, start_date=net_value.index[0])
    sharpe = (annual_return[0][0]-0.02)/(volatility[0]**0.5)
    MDD = (1 - net_value[net_value.columns[0]] / net_value[net_value.columns[0]].cummax()).max()
    net_evaluation = pd.DataFrame([annual_return[0][0], annual_active, volatility[0], sharpe, MDD], \
                                  index=['Annual Return', 'Annual Active', 'Volatility', 'Sharpe', 'MDD'])
    return net_evaluation

def factor_cross_evaluation(factor,close,windows=242,profit = None):
    """
    截面IC统计
    :param factor:因子 DataFrame(columns=[股票代码int],index=[时间戳 int 分钟级])
    :param close: 收盘价(目前暂时用不复权，后期待韩旭更新复权数据后更改)  DataFrame(columns=[股票代码int],index=[时间戳 int 分钟级])
    :param windows: 未来收益率窗口
    :param profit: 未来收益 DataFrame(columns=[股票代码int],index=[时间戳 int 分钟级])
    :return: IC序列、pvalue、t值、IC均值、IC标准差、均值/标准差
    """
    stk_list = factor.columns.tolist()
    bar_list = factor.index.tolist()
    date_list = list(set(map(lambda x : int(x/10000),bar_list)))
    if type(profit)==type(None):
        profit = close.pct_change(windows).shift(-windows)
        profit = profit.loc[:,stk_list]
    corr = pd.Series(bar_list,index = bar_list)
    corr = corr.apply(lambda idx : profit.loc[idx,:].corr(factor.loc[idx,:]))
    t_stat = stats.ttest_1samp(corr.dropna(),0)
    return corr,t_stat.pvalue,t_stat.statistic,corr.mean(),corr.std(),corr.mean()/corr.std()

def factor_vertical_corr(factor,close,windows=242, profit = None):
    """
    计算因子时序相关性
    :param factor:因子 DataFrame(columns=[股票代码int],index=[时间戳 int 分钟级])
    :param close: 收盘价(目前暂时用不复权，后期待韩旭更新复权数据后更改)  DataFrame(columns=[股票代码int],index=[时间戳 int 分钟级])
    :param windows: 未来收益率窗口
    :param profit: 未来收益 DataFrame(columns=[股票代码int],index=[时间戳 int 分钟级])
    :return: 每个股票的时序相关性、均值、标准差
    """
    stk_list = factor.columns.tolist()
    bar_list = factor.index.tolist()
    date_list = list(set(map(lambda x : int(x/10000),bar_list)))
    if type(profit)==type(None):
        profit = close.pct_change(windows).shift(-windows)
        profit = profit.loc[:,stk_list]
    corr = pd.Series(stk_list,index=stk_list)
    corr = corr.apply(lambda x :profit[x].corr(factor[x]))
    return corr,corr.mean(),corr.std()

def factor_values_evaluation(factor_,windows=242):
    """
    整个因子评估
    :param factor_:因子
    :param windows: 未来收益率窗口
    :return: 时序、截面相关性评估结果
    """
    stk_list = factor_.columns.tolist()
    h5 = pd.HDFStore('/data/group/800319/junkData/minuteByFactor/close.h5')
    close = h5['/close']
    h5.close()
    close = close.reset_index()
    close['datetime'] = (close['date'].astype(str) + close['time'].astype(str)).astype(int)
    close = close.set_index('datetime').drop(['date','time'],axis=1)
    profit = close.pct_change(windows).shift(-windows)
    profit = profit.loc[:,stk_list]
    stk_list = list(set(stk_list).intersection(set(factor_.columns)))
    bar_list = list(set(factor_.index).intersection(profit.index))
    factor = factor_.loc[bar_list,stk_list]
    profit = profit.loc[bar_list,stk_list]
    IC,IC_p,IC_t,IC_mean,IC_std,_ = factor_cross_evaluation(factor,None,windows,profit)
    series_corr,series_corr_mean,series_corr_std = factor_vertical_corr(factor,None,windows,profit)
    result = pd.DataFrame({'IC_mean':IC_mean,'IC_std':IC_std,'IC_t':IC_t,\
                           'series_corr_mean':series_corr_mean,'series_corr_std':series_corr_std},index=[0])
    return result

class FactorBackTest:
    def __init__(self, factor, start_date:int=20170101, end_date: int=20191231,daily_stock_pool:dict =common_stock_list_pool,
                 hedge_index ='ZZ500', order_holding=2, max_holding_day=1):
        """

        :param factor: 因子信号
        :param start_date:
        :param end_date:
        :param daily_stock_pool:每日股票池 dict {日期:股票列表}
        :param hedge_index: 基准代码
        :param order_holding: 下单挂单持续时间
        :param max_holding_day: int 持有T+max_holding_day日强制平仓
        """
        self.__start_date = start_date
        self.__end_date = end_date
        self.__trading_days = s.tradingday(self.__start_date, self.__end_date, \
                                           frequency='DAY', dayType=None, dateType='TRADINGDAYS')
        self.__trading_days = list(map(int, self.__trading_days))
        self.__daily_stock_pool = {}
        self.__daily_available_pool = {}
        e = time.time()
        self.stk_list = set()
        self.max_holding_day = max_holding_day
        self.order_holding_minutes = order_holding
        for day in self.__trading_days:
            if day in daily_stock_pool:
                temp_list = daily_stock_pool[day]
                self.stk_list = self.stk_list.union(set(temp_list))
                self.__daily_stock_pool[day] = temp_list
                available_stk = s.stock_filter(temp_list, str(day), 'SSO')  # 开盘涨跌停、停牌、STSP剔除
                if len(available_stk) == 0:
                    available_stk = []
                else:
                    available_stk = available_stk['stock'].apply(lambda x: int(x[:-3])).tolist()
                self.__daily_available_pool[day] = available_stk
        print(len(self.stk_list))
        self.stk_list = list(self.stk_list.intersection(set(factor.columns)))
        print('stock pool process',time.time()-e)

        # self.stk_list = set([])
        # for date in self.__daily_stock_pool:
        #     self.stk_list = self.stk_list.union(set(self.__daily_stock_pool[date]))
        # self.stk_list = list(self.stk_list)

        self.__hedge_index = hedge_index
        self.__order_list = []
        self.__lag = 20
        self.__cost = 0.0012
        self.result = {}
        self.evaluation_result = None
        self.evaluation_result_daily = pd.DataFrame()
        self.position = {}
        # self.factors = factor.loc[start_date*10000+924:end_date*10000+1501]
        e = time.time()
        while True:
            random_id = str(random.randrange(100000)).zfill(6)
            self.fac_path_path = '%s/temp_factor_junk/temp_factor_%s.h5' %(root_path,random_id)
            if not os.path.exists(self.fac_path_path):
                factor.loc[start_date*10000+924:end_date*10000+1501,self.stk_list].to_hdf(self.fac_path_path, 'factor')
                print(factor.loc[start_date*10000+924:end_date*10000+1501,self.stk_list].shape)
                break
        print('factor_loading',time.time()-e)
        self.__order_holding = order_holding
        self.__prepare_daily_data(self.stk_list)
        self.running_time = {}
        e = time.time()
        self.total, self.sell, self.buy = self.get_ratio(factor)
        self.running_time['Ratio Calculation'] = time.time() - e

    def __prepare_daily_data(self,stk_list):
        """
        初始化股票权息信息、复权因子等
        :return:
        """
        # self.stock_adj_close = get_mkt_data(self.stk_list,self.__trading_days,'close_badj')
        # self.stock_non_adj_close = get_mkt_data(self.stk_list,self.__trading_days,'close')
        self.dividend_info = getEXRightDividend(self.__start_date, self.__end_date, self.stk_list)
        h5 = pd.HDFStore('%s/daily/adjfactor.h5' % root_path, 'r')
        adjfactor = h5['/adjfactor'].loc[:, stk_list]
        h5.close()
        adjfactor = adjfactor.fillna(1)
        self.adjfactor = adjfactor
        self.benchmark_net = load_minutes_data(self.__hedge_index, self.__trading_days, 'index')
        self.benchmark_net = self.benchmark_net[['close']].rename(columns={'close': self.__hedge_index}).fillna(method='pad')

        benchmark_net = self.benchmark_net.rename(index={x: datetime.datetime.strptime(str(x), '%Y%m%d%H%M%S') for x in self.benchmark_net.index})
        benchmark_net = benchmark_net.resample('1B').last().dropna()
        benchmark_net = benchmark_net.rename(index={x: int(x.strftime('%Y%m%d')) for x in benchmark_net.index})
        self.benchmark_daily = benchmark_net
        # e = time.time()
        # pool = Pool(10)
        # result = pool.map(self.get_ratio,self.__trading_days)
        # pool.close()
        # pool.join()
        # print(time.time()-e)
        # self.total_count, self.sell_count, self.buy_count = pd.DataFrame(result).sum(axis=0).tolist()

    def get_ratio(self,factors):
        date_list = [x for x in self.__daily_stock_pool.keys()]
        date_list.sort()
        start = date_list[0]
        temp_stk_list = self.__daily_stock_pool[start]
        total = sell = buy = 0
        for day in date_list[1:]:
            if set(temp_stk_list)==set(self.__daily_stock_pool[day]):
                continue
            stk_list = list(set(temp_stk_list).intersection(set(self.stk_list)))
            temp_factor = factors[stk_list].loc[start*10000:day*10000+1500].values
            total += temp_factor.shape[0]*temp_factor.shape[1] - np.isnan(temp_factor).sum().sum()
            sell += np.equal(temp_factor,-1).sum().sum()
            buy += np.equal(temp_factor,1).sum().sum()
            start = day
            temp_stk_list = self.__daily_stock_pool[start]
        return total, sell, buy

    def get_ratio_one_day(self,day):
        temp_stk_list = set(self.__daily_stock_pool[day]).intersection(set(self.factors.columns))
        temp_factor = self.factors[temp_stk_list].loc[day*10000:day*10000+1500]
        total_count = temp_factor.notnull().sum().sum()
        sell_count = temp_factor.eq(-1).sum().sum()
        buy_count = temp_factor.eq(1).sum().sum()
        print(day,'done')
        return [total_count,sell_count,buy_count]

    def get_next_bar_minutes(self, minutes_data, order_holding):
        """
        获取用于计算每个bar上能成交量的信息的行情数据
        :param minutes_data: 原始分钟行情
        :param order_holding:挂单持续的分钟数
        :return:DataFrame,每个时间index对应的是接下来n分钟的合成K线
        """
        if order_holding == 1:
            return minutes_data.shift(-1)
        else:
            next_bar = copy.deepcopy(minutes_data)
            next_bar['high'] = next_bar['high'].rolling(2).max()
            next_bar['low'] = next_bar['low'].rolling(2).min()
            next_bar['open'] = next_bar['open'].shift(1)
            next_bar['vol'] = next_bar['vol'].rolling(2).sum()
            next_bar['amt'] = next_bar['amt'].rolling(2).sum()
            next_bar = next_bar.shift(-2)
            return next_bar

    def get_deal_info(self, price, num, flag: str, temp_mkt: pd.DataFrame, date_time):
        """
        粗糙版模拟撮合
        :param price: 报价(前一bar收盘)
        :param num: 手数
        :param flag: 'B' 'S'
        :param temp_mkt: 当天分钟行情数据shift(-1)后的 DataFrame
        :param date_time: 报单时间
        :return: 成交额、成交量
        """
        if flag == 'B':
            deal_ratio = (price - temp_mkt.loc[date_time, 'low']) / (temp_mkt.loc[date_time, 'high'] - temp_mkt.loc[date_time, 'low'] + 0.01)
        elif flag == 'S':
            deal_ratio = (temp_mkt.loc[date_time, 'high'] - price) / (temp_mkt.loc[date_time, 'high'] - temp_mkt.loc[date_time, 'low'] + 0.01)
        else:
            raise Exception('Wrong Trading Flag %s' % flag)

        if deal_ratio < 0:
            deal_ratio = 0
        elif deal_ratio > 1:
            deal_ratio = 1
        tradable_vol = int(deal_ratio * temp_mkt.loc[date_time, 'vol'] * 0.5)
        tradable_vol = int(tradable_vol / 100) * 100
        deal_vol = min(num, tradable_vol)
        deal_vol = deal_vol

        return price * deal_vol, deal_vol

    def calculate(self, kernel_num):
        """
        并行计算单只股票回测并将结果保存至self.position中
        :param kernel_num: 并行数
        :return:
        """
        e = time.time()
        stk_list = self.stk_list
        print('multiprocessing',len(stk_list))
        with Pool(kernel_num) as pool:
            # pos_list = pool.map(self.single_stock_wraper, [(stk_id, self.factors[stk_id]) for stk_id in stk_list])
            pos_list = pool.map(self.single_stock_wraper, [stk_id for stk_id in stk_list])
            # temp_pos = self.single_stock_back_test(stk_id, self.factors[stk_id])
            pool.close()
            print('done1')
            pool.join()
            print('done2s')
        record_list = []
        for i in range(len(pos_list)):
            try:
                self.position[stk_list[i]],temp_record = pos_list[i]#.get()[0]
                record_list.append(temp_record)
            except:
                print(stk_list[i], 'wrong')
                self.position[stk_list[i]] = self.single_stock_wraper((stk_list[i],))
        self.trading_record = pd.concat(record_list)
        self.trading_record['strict_exit'] = self.trading_record['end'].apply(lambda x : x%10000==1456)*1
        self.running_time['BackTest Calculation'] = time.time() - e

    def calculate_one_by_one(self):
        """
        并行计算单只股票回测并将结果保存至self.position中
        :param kernel_num: 并行数
        :return:
        """
        for stk_id in self.factors.columns:
            self.position[stk_id] = self.single_stock_back_test(stk_id, self.factors[stk_id])

    # 获取每次信号的盈利、超额
    def single_stock_wraper(self, stk_id):
        try:
            result = self.single_stock_back_test(stk_id,max_holding_day=self.max_holding_day)
            n = gc.collect()
            return result
        except:
            print('--------------------------------------------------------')
            print(stk_id, 'wrong')
            print('--------------------------------------------------------')
            return self.single_stock_back_test(stk_id,max_holding_day=self.max_holding_day)

    def single_stock_back_test(self, stk_id, trade_port=0.95, startup_cash=1000000, max_holding_day=1):
        """
        单只股票回测
        :param stk_id:
        :param factor_signal_origin:因子信号pd.Series()
        :param trade_port:每次下单金额占总可用金额的比例
        :param startup_cash:初始资金量
        :return:
        """
        print(stk_id, 'start')
        factor_signal_origin = pd.read_hdf(self.fac_path_path,'factor')
        factor_signal_origin = factor_signal_origin[stk_id]
        _ = gc.collect()
        e_whole = time.time()
        factor_signal = factor_signal_origin[pd.Series(factor_signal_origin.index, \
                                                       index=factor_signal_origin.index).apply(lambda x: 930 <= x % 10000 <= 1455)]
        factor_signal = factor_signal.replace(0, np.nan).dropna()
        stock_minutes_data = load_minutes_data(stk_id, self.__trading_days)
        dividend_info = self.dividend_info[self.dividend_info['code'].eq(stk_id)].set_index('date')
        pos_list = []
        date_time = None
        pre_minute = None
        holding = tradable_holding = frozen_holding = 0
        cash = startup_cash
        # pbar = tqdm(self.__trading_days)
        holding_day = 0
        for date in self.__trading_days:
            if holding>0:
                holding_day += 1
            if stk_id in self.__daily_stock_pool[date]:
                trade_flag = True
            elif holding == 0:
                # 如果股票当日不再股票池，且没有持仓，不交易
                continue
            else:
                # 如果股票当日不在股票池，有无持仓，当日清仓
                trade_flag = False
            # pbar.set_description('stock %s in %s'%(str(stk_id),str(date)))
            tradable_holding = holding
            frozen_holding = 0
            temp_minutes = stock_minutes_data.loc[date * 10000:(date * 10000 + 1501)]
            temp_signal = factor_signal.loc[date * 10000:(date * 10000 + 1501)]
            if date_time == None and len(temp_signal) == 0:
                continue
            if len(temp_minutes) == 0:
                continue
            else:
                temp_minutes = temp_minutes.fillna(method='pad')
            next_bar_minutes = self.get_next_bar_minutes(temp_minutes, self.__order_holding)
            # 每日开盘处理权息
            if date in dividend_info.index:
                cash += (holding * dividend_info.loc[date, 'payoutRatio'] * 0.9 - holding * dividend_info.loc[date, 'receiveRatio'])
                holding += holding * dividend_info.loc[date, 'shareRatio']
                tradable_holding = holding
            if date_time == None:
                # 第一个交易日的第一个bar
                pos_list.append([temp_signal.index[0], cash, holding, tradable_holding, frozen_holding])
            elif len(temp_signal) > 0:
                # 非第一个交易日、且当日有信号
                pos_list.append([temp_signal.index[0], cash, holding, tradable_holding, frozen_holding])
                assert (date_time == pre_minute)
            else:
                # 非第一个个交易日、当日无信号
                pass
            if holding > 0 and trade_flag == False:
                temp_signal = pd.Series([])

            for date_time in temp_signal.index:
                if pre_minute == None:
                    # 策略开始的第一天的第一分钟
                    pass
                elif date_time != temp_signal.index[0]:
                    # 其他天的第一分钟已在该日初始化时处理过
                    # position.loc[date_time, ['holding', 'cash', 'frozen_holding', 'tradable_holding']] = \
                    #     holding, cash, frozen_holding, tradable_holding
                    pos_list.append([date_time, cash, holding, tradable_holding, frozen_holding])
                pre_minute = date_time
                cash_change = 0
                position_change = 0
                cost = 0
                if tradable_holding > 0 and factor_signal[date_time] == -1:
                    cash_change, position_change = \
                        self.get_deal_info(temp_minutes.loc[date_time, 'close'], \
                                           tradable_holding, 'S', next_bar_minutes, date_time)
                    position_change = min(position_change, tradable_holding)
                    cost = abs(cash_change) * self.__cost
                    position_change = position_change * factor_signal[date_time]
                    cash_change = -1 * cash_change * factor_signal[date_time]
                    pos_list[-1].extend([position_change, cash_change, cost, 1, 1 if position_change != 0 else 0])
                if factor_signal[date_time] == 1 and holding == 0:
                    trade_num = cash * trade_port / temp_minutes.loc[date_time, 'close']
                    trade_num = max(int(trade_num / 100) * 100, 100)
                    cash_change, position_change = \
                        self.get_deal_info(temp_minutes.loc[date_time, 'close'], \
                                           trade_num, 'B', next_bar_minutes, date_time)
                    position_change = position_change * factor_signal[date_time]
                    cash_change = -1 * cash_change * factor_signal[date_time]
                    pos_list[-1].extend([position_change, cash_change, cost, 1, 1 if position_change != 0 else 0])
                    holding_day = 0
                holding += position_change
                frozen_holding += max(0, position_change)
                tradable_holding += min(0, position_change)
                cash += (cash_change - cost)
            # 每日集合竞价前一个bar
            # position.loc[int(date_time / 10000) * 10000 + 1500, \
            #              ['holding', 'cash', 'frozen_holding', 'tradable_holding']] = holding, cash, frozen_holding, tradable_holding
            ########################################

            date_time = date * 10000 + 1456

            pos_list.append([date_time, cash, holding, tradable_holding, frozen_holding])
            # 每日尾盘用集合竞价清理可卖的头寸
            if tradable_holding > 0 and holding_day>=max_holding_day:
                factor_signal_origin[date_time] = -2
                position_change = -1 * tradable_holding
                cash_change = -1 * position_change * temp_minutes.loc[int(date_time / 10000) * 10000 + 1500, 'close']
                cost = self.__cost * abs(cash_change)
                pos_list[-1].extend([position_change, cash_change, cost, 0, 0])
                holding += position_change
                frozen_holding += max(0, position_change)
                tradable_holding += min(0, position_change)
                cash += (cash_change - cost)
                holding_day = 0
            else:
                pos_list[-1].extend([np.nan, np.nan, np.nan, 0, 0])
            # 尾盘集合竞价最后一个bar
            date_time = date * 10000 + 1500
            pos_list.append([date_time, cash, holding, tradable_holding, frozen_holding, np.nan, np.nan, np.nan])
            pre_minute = date_time
            ###################################
        # 每日填充无信号的bar上的仓位记录
        ######################################
        pos_list_df = pd.DataFrame(pos_list, columns=['datetime', 'cash', 'holding', 'tradable_holding', 'frozen_holding', \
                                                      'traded_vol', 'traded_amt', 'cost', 'executed signal', 'sucessed signal']).set_index('datetime')
        new_position = pd.DataFrame(index=stock_minutes_data.index, \
                                    columns=['holding', 'cash', 'frozen_holding', 'tradable_holding', \
                                             'traded_vol', 'traded_amt', 'cost', 'executed signal', 'sucessed signal'])
        new_position.loc[pos_list_df.index, ['holding', 'cash', 'frozen_holding', 'tradable_holding', \
                                             'traded_vol', 'traded_amt', 'cost', 'executed signal', 'sucessed signal']] = \
            pos_list_df.loc[:, ['holding', 'cash', 'frozen_holding', 'tradable_holding', \
                                'traded_vol', 'traded_amt', 'cost', 'executed signal', 'sucessed signal']]

        new_position.loc[:, ['holding', 'cash', 'frozen_holding', 'tradable_holding']] = \
            new_position.loc[:, ['holding', 'cash', 'frozen_holding', 'tradable_holding']].fillna(method='backfill')

        new_position['holding_values'] = new_position['holding'] * stock_minutes_data.loc[new_position.index, 'close']

        new_position['account_values'] = new_position['holding_values'] + new_position['cash']
        new_position['close'] = stock_minutes_data.loc[new_position.index, 'close']
        new_position['signal'] = factor_signal_origin
        record = self.get_signals_stat_of_one_stock(stk_id, new_position)
        print(stk_id, 'done', time.time() - e_whole)

        return new_position, record

    def get_universe_signals_records(self):
        """
        获取所有股票回测的每笔交易记录
        :param kernel_num:并行数
        :return:DataFrame() 每只股票记录每次交易的开始结束时间、用了几次平仓、持仓时间、超额收益、收益
        """
        # pool = Pool(kernel_num)
        e = time.time()
        signal_dict = {}
        for stk in self.position:
            # print(stk)
            # signal_dict[stk] = self.get_signals_stat(stk)
            # signal_dict[stk] = pool.map_async(self.get_signals_stat_of_one_stock,(stk,))
            signal_dict[stk] = self.get_signals_stat_of_one_stock(stk)
        # pool.close()
        # pool.join()
        signal_df = pd.DataFrame()
        for stk in signal_dict:
            # signal_df = pd.concat([signal_df,signal_dict[stk].get()[0]])
            signal_df = pd.concat([signal_df, signal_dict[stk]])
        self.trading_record = signal_df
        self.running_time['Signal Processing'] = time.time() - e
        return self.trading_record
        # 600251

    def get_signals_stat_of_one_stock(self, stk_id,pos):
        """
        获取某只股票的历史交易记录
        :param stk_id_:
        :return: DataFrame() 记录每次交易的开始结束时间、用了几次平仓、持仓时间、超额收益、收益
        """
        e_check = time.time()
        pos['holding_shift'] = pos['holding'].shift(-1)
        trade_record = pos.loc[pos['traded_vol'].replace(0, np.nan).dropna().index].copy()
        trade_record['signal_holding'] = trade_record['traded_vol'].cumsum()
        # print('data prepare:', time.time() - e_check)
        record_list = []
        record = []
        for date_time in trade_record.index:
            if record == []:
                record.append(date_time)
            if trade_record.loc[date_time, 'holding_shift'] == 0 and len(record) == 1:
                record.append(date_time)
                record_list.append(record)
                record = []
        # print('pitches prepare1:', time.time() - e_check)
        pitches_list = list(map(lambda x: self.get_one_signal_stat(trade_record.loc[x[0]:x[-1]]), \
                                record_list))
        # print('pitches prepare2:', time.time() - e_check)
        for i in range(len(pitches_list)):
            record_list[i] = record_list[i] + pitches_list[i]

        record_df = pd.DataFrame(record_list, columns=['start', 'end', 'profit', 'active', 'selling_times'])
        # print('data generation:', time.time() - e_check)
        record_df['holding_minutes'] = pd.Series(record_df.index, index=record_df.index).apply(lambda x: len(pos.loc[record_df.loc[x, 'start']:record_df.loc[x, 'end']]))
        record_df['stk_id'] = stk_id
        # print(stk_id, 'done', time.time() - e_check)
        return record_df

    def get_one_signal_stat(self, pitch):
        profit = (pitch['account_values'].tolist()[-1] - pitch['account_values'].tolist()[0] - pitch['cost'].tolist()[-1]) / (-pitch['traded_amt'].tolist()[0])

        """
        获取Benchmark部分待补全
        已补全
        """
        benchmark_profit = self.benchmark_net.loc[pitch.index[-1], self.__hedge_index] / self.benchmark_net.loc[pitch.index[0], self.__hedge_index] - 1
        return [profit, profit - benchmark_profit, len(pitch) - 1]

    # 获取所有股票组合的历史净值整合
    def calc_portfolio(self):
        e = time.time()
        account_cross_section = [self.position[x][['account_values']].rename(columns= \
                                                                                                         {'account_values': x}) for x in self.position.keys()]
        account_cross_section = pd.concat(account_cross_section, axis=1)
        account_cross_section = account_cross_section.rename(index= \
                                                                 {x: datetime.datetime.strptime(str(x), '%Y%m%d%H%M%S') for x in account_cross_section.index})
        account_cross_section_daily = account_cross_section.resample('1B').last()
        account_cross_section_daily = account_cross_section_daily.rename(index= \
                                                                             {x: int(x.strftime('%Y%m%d')) for x in account_cross_section_daily.index})
        account_cross_section_daily = account_cross_section_daily[pd.Series(account_cross_section_daily.index, \
                                                                            index=account_cross_section_daily.index).isin(self.__trading_days)]
        account_cross_section_daily = account_cross_section_daily
        self.pct_change = account_cross_section_daily.pct_change().replace(0, np.nan)
        profit_series = self.pct_change.mean(axis=1)
        net_series = (1 + profit_series).cumprod()
        self.net_value = net_series.fillna(method='pad').fillna(1)
        benchmarket = self.benchmark_daily.loc[self.net_value.index,self.benchmark_daily.columns[0]]
        benchmarket = benchmarket/benchmarket.tolist()[0]
        self.active_net = self.net_value - benchmarket
        self.running_time['Portfolio Calculation'] = time.time() - e
        return self.net_value

    def failed_signal_count(self, stk_id):
        # pos = self.position[stk_id]
        # tradable_signal = pos[(pos['signal'].isin([1,-1]))*(pos['traded_vol'].notnull())]
        # dealed_signal = tradable_signal[tradable_signal['traded_vol']!=0]
        return self.position[stk_id][['executed signal', 'sucessed signal']].sum().tolist()  # tradable_signal.shape[0],dealed_signal.shape[0]

    def get_failed_signal_info(self, max_kernel_num):
        e = time.time()
        result_df = pd.DataFrame(index=self.position.keys())
        result_df['executed signal'] = result_df.index
        result_df['executed signal'] = result_df['executed signal'].apply(lambda x: self.position[x]['executed signal'].sum())
        result_df['sucessed signal'] = result_df.index
        result_df['sucessed signal'] = result_df['sucessed signal'].apply(lambda x: self.position[x]['sucessed signal'].sum())
        self.failed_signal_info = result_df  # .sum()
        self.running_time['Failed Signal Calculation'] = time.time() - e
        return self.failed_signal_info

    def get_failed_signal_info_old(self, max_kernel_num):
        kernel_num = min(max_kernel_num, self.factors.shape[1])
        pool = Pool(kernel_num)
        result = {}
        for stk in self.position:
            result[stk] = pool.map_async(self.failed_signal_count, (stk,))
        pool.close()
        pool.join()
        failed_signal_info = []
        for stk in result:
            failed_signal_info.append([stk] + list(result[stk].get()[0]))
        failed_signal_info = pd.DataFrame(failed_signal_info, columns=['stk_id', 'sent_signal', 'dealed_signal'])
        self.failed_signal_info = failed_signal_info.set_index('stk_id')
        return self.failed_signal_info

    def evaluation(self, max_kernel_num):
        """
        回测并计算所有评估结果
        :param max_kernel_num:
        :return:
        """
        kernel_num = min(len(self.stk_list), max_kernel_num)
        e = time.time()
        if len(self.position) == 0:
            print('runing calculation')
            self.calculate(kernel_num)
            # self.calculate_one_by_one()
            print('calculation done', time.time() - e)
        else:
            pass
        # self.get_universe_signals_records()
        # print('finish record process', time.time() - e)
        self.calc_portfolio()
        print('finish calculate portfolio', time.time() - e)
        failed_signal_info = self.get_failed_signal_info(max_kernel_num)
        print('finish signal info stat', time.time() - e)
        # 组合净值部分评估
        net_value_evaluation = get_net_value_evaluation(pd.DataFrame(self.net_value), self.benchmark_daily)

        # 信号评估部分
        signal_evalution = get_signals_evaluation(self.trading_record,self.max_holding_day)
        self.evaluation_result = pd.concat([signal_evalution, net_value_evaluation]).T
        self.evaluation_result['signal_count_daily'] = len(self.trading_record)/float(len(self.__trading_days))
        failed_signal_info = failed_signal_info.sum()
        self.evaluation_result['failed_signal_ratio'] = 1 - failed_signal_info['sucessed signal'] / failed_signal_info['executed signal']
        # total, sell, buy = self.get_ratio()
        self.evaluation_result['Buy Signal Raio'] = self.buy/float(self.total)
        self.evaluation_result['Sell Signal Raio'] = self.sell / float(self.total)
        self.evaluation_result['list_minutes'] = self.order_holding_minutes
        self.evaluation_result['exit_days'] = self.max_holding_day
        self.evaluation_result_daily = get_signals_evaluation_daily(self.trading_record)
        net_value_cross_section = [self.position[x][['account_values']].rename(columns={'account_values': x}) for x in self.position]
        self.net_value_cross_section = pd.concat(net_value_cross_section, axis=1)#
        self.net_value_cross_section.index = [datetime.datetime.strptime(str(x),'%Y%m%d%H%M') for x in self.net_value_cross_section.index]
        self.net_value_cross_section = self.net_value_cross_section.resample('1B').last().fillna(method='pad')
        self.running_time['Toatl Evaluation'] = time.time() - e
        try:
            os.remove(self.fac_path_path)
        except:
            pass

        print('finish evaluation', time.time() - e)

    def check_part_signal(self,N,out_path,max_kernel=0):
        trading_record = copy.deepcopy(self.trading_record.sort_values('end'))
        trading_record.index = [x for x in range(len(trading_record))]
        trading_record['start'] = trading_record['start'].apply(lambda x : int(str(x).replace('-','').replace(':','').replace(' ','')[:12]))
        trading_record['end'] = trading_record['end'].apply(lambda x : int(str(x).replace('-','').replace(':','').replace(' ','')[:12]))
        trading_record = trading_record[:N]
        stk_list = set(trading_record['stk_id'])
        # pool = Pool(max_kernel)
        # para_list = []
        for stk in stk_list:
            temp_record_list = trading_record[trading_record['stk_id']==stk]
            stk_start, stk_end = trading_record['start'].tolist()[0],trading_record['end'].tolist()[-1]
            stk_start = int(stk_start/10000)*10000 + 925
            stk_end = int(stk_end/10000)*10000+1500
            temp_mkt_data = get_minute_1stock(stk, stk_start, stk_end, ['open','close','high','low'])
            temp_mkt_data.index = [int(x[0]*10000+x[1]) for x in temp_mkt_data.index]
            for idx in temp_record_list.index:
                start, end, stk_id = temp_record_list.loc[idx, ['start', 'end', 'stk_id']]
                temp_record = self.position[stk_id].loc[start:end]
                signal_list = temp_record[['executed signal', 'signal']]#.dropna()
                signal_list = signal_list[signal_list['signal']!=0]
                start_open = int(start/10000)*10000 + 925
                end_close = int(end/10000)*10000+1500
                temp_bench = self.benchmark_net.loc[start_open:end_close]/self.benchmark_net.loc[start_open,self.benchmark_net.columns[0]]
                mkt_piece = pd.concat([temp_mkt_data.loc[start_open:end_close]/temp_mkt_data.loc[start_open,'close'],temp_bench],axis=1)
                # pd.to_pickle([stk,out_path,signal_list,mkt_piece],'%s/temp_daily_by_lzc/plot_sample.pkl'%root_path)
                out_fig((stk,out_path,signal_list,mkt_piece))
                print('fig',stk,start,end,'done')
                # para_list.append((stk,out_path,signal_list,mkt_piece))
        # pool.map(out_fig,para_list)
        # pool.close()
        # pool.join()
        pass

    def result_output(self,filename = None,fileroot = None):
        """
        将所有结果输出值excel所有评估结果
        filename ： 用于保存结果的.xlsx文件名,如goldCross20
        fileroot ；文件的输出目录 , 如‘/data/user/006693/’
        """
        filename = 'factorResult_' + filename + '.xlsx'
        fileroot = fileroot + filename
        with pd.ExcelWriter(fileroot) as writer:
            self.evaluation_result.T.reindex(['mean_profit',
                                            'mean_active',
                                            'profit_win_rate',
                                            'active_win_rate',
                                            'mean_earning',
                                            'mean_loss',
                                            'earning_loss_ratio',
                                            'mean_active_earning',
                                            'mean_active_loss',
                                            'active_earning_loss_ratio',
                                            'mean_active_signal',
                                            'mean_active_exit',
                                            'active_signal_win_rate',
                                            'active_exit_win_rate',
                                            'close_position_at_T+%d_end'%self.max_holding_day,
                                            'Annual Return',
                                            'Annual Active',
                                            'Volatility',
                                            'Sharpe',
                                            'MDD',
                                            'signal_count_daily',
                                            'failed_signal_ratio',
                                            'Buy Signal Raio',
                                            'Sell Signal Raio',
                                            'mean_holding_minutes',
                                            'list_minutes',
                                            'exit_days'],axis=0).to_excel(writer, 'result')
            self.evaluation_result_daily.to_excel(writer, 'resultDaily')
            net = pd.concat([self.net_value,self.active_net],axis=1)
            net.columns = ['单边净值','超额收益']
            net.index = [datetime.datetime.strptime(str(x),'%Y%m%d') for x in net.index]
            net.to_excel(writer, 'net_value')
            trading_record = copy.deepcopy(self.trading_record)
            trading_record.start = pd.to_datetime(trading_record.start.astype(str))
            trading_record.end = pd.to_datetime(trading_record.end.astype(str))
            trading_record.to_excel(writer, 'trading_record')
            self.net_value_cross_section.to_excel(writer, 'net_values_each_stock')



def test():
    factor_df = pd.read_hdf('/data/user/015664/日内回测/factor_relative_ma.h5', 'factor_relative_ma')
    factor_df1 = factor_df.T[300:800].T
    print(factor_df1.shape)
    factor_test = FactorBackTest(factor_df1,daily_stock_pool=common_stock_list_pool)
    factor_test.evaluation(40)
    factor_test.result_output(fileroot=root_path, filename='Relative_Factor')
    print(factor_test.evaluation_result)
    print(factor_test.running_time)


if __name__ == "__main__":
    test()










