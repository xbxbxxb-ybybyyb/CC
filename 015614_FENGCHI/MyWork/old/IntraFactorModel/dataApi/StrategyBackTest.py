"""
Time : 2018/4/6 13:33
Author : Zhichen Lu
File : StrategyBackTest.py
"""
import time

from tqdm import tqdm

from dataApi.getData import *
from dataApi.getData import get_minute_1factor, get_daily_1factor
from dataApi.indName import sw_level1, citics_level1
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_recent_trade_date, get_pre_trade_date, get_date_range
from dataApi.usefulTools import *


def shift_back(arr, n):
    arr_shift = arr.copy()
    arr_shift[:-n] = arr_shift[n:]
    arr_shift[-n:] = np.nan
    return arr_shift


def get_top_part_index(bar_factor, filtered_stk, num, type):
    """
    返回因子值最大或最小的num个股票的loc
    :param bar_factor: 某个分钟截面上的因子值
    :param filtered_stk: 过滤后的股票
    :param num: 目标股票数量
    :param type: 'max':选银因子值最大的num个股票 'min':选最小的
    :return:
    """
    if type == 'max':
        func = np.nanargmax
    elif type == 'min':
        func = np.nanargmin
    else:
        raise Exception('Wrong sorting type')
    if num <= 0:
        return np.array([])
    factor_for_filter = bar_factor.copy()
    factor_for_filter[~(filtered_stk > 0)] = np.nan
    factor_for_filter = bottleneck.nanrankdata(factor_for_filter)
    filtered_stk = []
    for i in range(num):
        if (1 - np.isnan(factor_for_filter)).sum() == 0:
            break
        filtered_stk.append(func(factor_for_filter))
        factor_for_filter[filtered_stk[-1]] = np.nan
    return np.array(filtered_stk)


class StrategyBackTest():

    def __init__(self, start_date=20170103, end_date=20191231, pool='COMMON', benchmark='ZZ500', industry='SW',
                 holding_minutes=2, fee=0.0012):
        """
        类初始化
        :param start_date: 起始日期
        :param end_date: 截至日期
        :param pool: 股票池可选['COMMON','ZZ500','ZZ1000','ZZ800','HS300','ALL'],或自定义DataFrame(index=date_list,columns=股票列表) 值=True or False
        :param benchmark: 基准，目前暂时只包含'ZZ500'
        :param industry: 股票的行业划分，可选['SW','CITIC'],也支持自定义行业并输入DataFrame(index=date_list,columns=股票列表) 值=当日该股票的行业名称
        :param holding_minutes: 股票发出买卖信号后挂单时间
        :param fee: 交易费用
        """
        start_date = get_pre_trade_date(get_recent_trade_date(start_date - 1), -1)
        end_date = get_recent_trade_date(end_date)
        if type(pool) == str:
            if pool not in ['COMMON', 'ZZ500', 'ZZ1000', 'ZZ800', 'HS300', 'ALL']:
                raise Exception('Wrong pool type')
            pool = clean_stock_list(pool, no_limit_down=True, no_limit_up=True)
        elif type(pool) == pd.DataFrame:
            pass
        else:
            raise Exception('Wrong pool type')
        stock_pool = pool.loc[start_date:end_date]
        date_list = get_date_range(start_date, end_date)
        stock_pool = stock_pool.reindex(date_list)
        close = get_minute_1factor('close', start_datetime=start_date, end_datetime=end_date,
                                   code_list=stock_pool.columns.tolist())
        index, columns = close.index.tolist(), close.columns.tolist()
        close = frame2arr(close)
        tradable_buy_vol, tradable_sell_vol = self.__get_tradabale_vol(index, columns, holding_minutes)
        tradable_buy_vol = frame2arr(tradable_buy_vol)
        tradable_sell_vol = frame2arr(tradable_sell_vol)
        stk_benchmark_weight = \
        pd.read_hdf('/data/group/800319/junkData/daily/ZZ500_exdiv_weight.h5', 'ZZ500_exdiv_weight').loc[
            date_list, stock_pool.columns]
        if type(industry) == str:
            if industry not in ['SW', 'CITIC']:
                raise Exception('Wrong industry type')
            stk_ind_map = pd.read_hdf('/data/group/800319/junkData/daily/%s1.h5' % industry, industry + '1').loc[
                date_list, stock_pool.columns]
            if industry == 'SW':
                for ind in sw_level1:
                    stk_ind_map = stk_ind_map.replace(ind, sw_level1[ind])
            elif industry == 'CITIC':
                for ind in citics_level1:
                    stk_ind_map = stk_ind_map.replace(ind, citics_level1[ind])
        elif type(industry) == pd.DataFrame:
            stk_ind_map = industry
        else:
            raise Exception('Wrong industry type')
        stk_ind_weight_pn = pd.Panel({'ind_weight': stk_benchmark_weight, 'stk_ind_map': stk_ind_map})
        ind_weight = pd.DataFrame()
        for x in stk_ind_weight_pn.major_axis:
            ind_weight = ind_weight.append(
                pd.DataFrame(stk_ind_weight_pn.loc[:, x, :].groupby('stk_ind_map').sum()).rename(
                    columns={'ind_weight': x}).T)
        ind_weight = ind_weight.sort_index(axis=0)  # .sort_index(axis=1)
        self.close = close
        self.start_date = start_date
        self.end_date = end_date
        self.date_list = date_list
        self.stk_list = columns
        self.datetime_list = index
        self.ind_list = ind_weight.columns.tolist()
        self.ret = close / close[0] - 1
        self.ind_weight = ind_weight.reindex(date_list, axis=0).reindex(self.ind_list,
                                                                        axis=1).values  # index=datelist  columns=ind_list values=该行业的权重
        self.stk_ind = stk_ind_map.reindex(date_list, axis=0).reindex(self.stk_list, axis=1).values  # 股票当天所处行业
        self.stk_benchmark_weight = stk_benchmark_weight.reindex(date_list, axis=0).reindex(self.stk_list,
                                                                                            axis=1).values  # 股票在指数中的权重
        self.tradable_buy_vol = tradable_buy_vol
        self.tradable_sell_vol = tradable_sell_vol
        self.adj_factor = get_daily_1factor('adjfactor', date_list=date_list).reindex(columns, axis=1).fillna(1)
        self.close_daily = get_daily_1factor('close', date_list=self.date_list, code_list=self.stk_list)
        self.benchmark_daily_close = get_daily_1factor('close', date_list=self.date_list, code_list=[benchmark],
                                                       type='bench')
        self.benchmark_minutes_close = frame2arr(
            get_minute_1factor('close', start_datetime=start_date, end_datetime=end_date, code_list=[benchmark],
                               type='bench'))
        self.benchmark_minutes_close = self.benchmark_minutes_close[:, :, 0]
        self.stock_pool = stock_pool
        self.fee = fee
        self.__refresh()

    def __refresh(self):
        self.holding = {}
        self.holding_record = {}
        self.trade_pieces = []
        self.buy_record = {}
        self.sell_record = {}
        self.result = {}

    def __get_tradabale_vol(self, bar_list, stk_list, holding_minutes):
        """
        计算并获取每只股票每分钟挂单可交易数量数据
        :param bar_list: 时间戳列表
        :param stk_list: 股票列表
        :param holding_minutes: 挂单时间
        :return: 可买数量,可卖数量
        """
        file_name = '/data/group/800319/junkData/tradable_vol/tradable_vol_%d.pkl' % holding_minutes
        if os.path.exists(file_name):
            tradable_buy_vol, tradable_sell_vol = pd.read_pickle(file_name)
            return tradable_buy_vol.loc[bar_list, stk_list], tradable_sell_vol.loc[bar_list, stk_list]
        high = get_minute_1factor('high', start_datetime=20170103, end_datetime=20191231)
        index, columns = high.index.tolist(), high.columns.tolist()
        high = frame2arr(high)
        low = frame2arr(get_minute_1factor('low', start_datetime=20170103, end_datetime=20191231))
        vol = frame2arr(get_minute_1factor('vol', start_datetime=20170103, end_datetime=20191231))
        close = frame2arr(get_minute_1factor('close', start_datetime=20170103, end_datetime=20191231))
        # 计算可成交量
        tradable_vol = shift_back(ts_sum(vol, holding_minutes), holding_minutes)
        future_high = shift_back(ts_max(high, holding_minutes), holding_minutes)
        future_low = shift_back(ts_min(low, holding_minutes), holding_minutes)
        tradable_buy_vol = np.fmax(0.5 * tradable_vol * (close - future_low) / (future_high - future_low), 0)
        tradable_sell_vol = np.fmax(0.5 * tradable_vol * (future_high - close) / (future_high - future_low), 0)
        tradable_buy_vol = arr2frame(tradable_buy_vol, index=index, columns=columns)
        tradable_sell_vol = arr2frame(tradable_sell_vol, index=index, columns=columns)
        pd.to_pickle([tradable_buy_vol, tradable_sell_vol], file_name)
        return tradable_buy_vol.loc[bar_list[0]:bar_list[-1], stk_list], tradable_sell_vol.loc[bar_list[0]:bar_list[-1],
                                                                         stk_list]

    def __clear_holding(self, date, bar, filtered_stk, bar_sold_vol, close_piece):
        """
        卖出后清理持仓并返回卖完的股票的持有记录
        :param bar: 时间戳(date,time)
        :param bar_sold_vol: 当前bar上卖出的股票的volume
        :param close_piece: 股价
        :return: trading_pices list, item=[stk_id,[time1,time2,...],[vol1,vol2,...,-sold_vol1,-sold_vol2,...],[price1,price2,...,sold_price1,sold_price2,...]]
        """
        trading_pieces = []
        for idx, stk in enumerate(filtered_stk):
            if bar_sold_vol[idx] > self.holding[stk][1]:
                raise Exception("Sold volume is bigger than actual holding!!!!!!!!")
            self.holding[stk][1] -= bar_sold_vol[idx]
            self.holding[stk][2].append((date, self.datetime_list[bar][1]))
            self.holding[stk][3].append(-1 * bar_sold_vol[idx])
            self.holding[stk][4].append(close_piece[idx])
            self.holding[stk][5].append(self.benchmark_minutes_close[bar, self.date_list.index(date)])
            if self.holding[stk][1] == 0:
                piece = self.holding.pop(stk)
                trading_pieces.append(piece)
        self.trade_pieces += trading_pieces
        return trading_pieces

    def __update_holding(self, date, bar, filtered_stk, bar_bought, close_slice):
        """
        每次买入后更新持仓
        :param date:
        :param bar:
        :param filtered_stk:
        :param bar_bought:
        :param close_slice:
        :return:
        """
        for idx, stk in enumerate(filtered_stk):
            if stk not in self.holding:
                self.holding[stk] = [self.stk_list[stk], bar_bought[idx], [(date, self.datetime_list[bar][1])],
                                     [bar_bought[idx]], [close_slice[bar, stk]],
                                     [self.benchmark_minutes_close[bar, self.date_list.index(date)]]]

            else:
                self.holding[stk][1] += bar_bought[idx]
                self.holding[stk][2].append((date, self.datetime_list[bar][1]))
                self.holding[stk][3].append(bar_bought[idx])
                self.holding[stk][4].append(close_slice[bar, stk])
                self.holding[stk][5].append(self.benchmark_minutes_close[bar, self.date_list.index(date)])

    def __sending_order(self, bar, filtered_stk, target_vol, flag, tradable_vol=None):
        """
        获取可买入数量
        :param bar:
        :param filtered_stk:
        :param target_vol:
        :param flag:
        :param tradable_vol:
        :return:
        """
        if len(filtered_stk) == 0:
            return np.array([])
        if tradable_vol is None:
            if flag == 'B':
                tradable_vol = self.tradable_buy_vol
            elif flag == 'S':
                tradable_vol = self.tradable_sell_vol
            else:
                raise Exception('Wrong Flag')
        else:
            pass
        vol = tradable_vol[bar, filtered_stk]
        vol = (target_vol < vol) * target_vol + (target_vol > vol) * vol
        return np.vectorize(lambda x: int(x / 100) * 100 if not np.isnan(x) else 0)(vol)

    def backtest(self, factor_, daily_selected_pool=None, target_holding_num=200, amtMax=100000, turnover=0.5,
                 trade_percentile=0.05, bar_order_stk_num=3,
                 max_holding_days=5, least_force_sell_order_num=1):
        """
        回测函数
        :param daily_selected_pool: 日内因子 array shape = (242,天数,股票数) axis=1上的日期顺序与 self.date_list日期顺序一致， axis=2上股票顺序与 self.stk_list上的股票顺序一致
        :param daily_selected_pool: 日间股票池，用于标注每日所选出的用于下一交易日的股票池，
                可输入类型为 np.array 或 pd.DataFrame
                输入类型为np.array时其shape必须为(len(self.date_list),len(self.stk_list))
                默认为None时会选择初始化时的pool中的全部股票作为交易的股票池
        :param target_holding_num: 目标持仓股票数
        :param amtMax: 最大下单量
        :param turnover: 目标换手率
        :param trade_percentile: 阈值分位数
        :param bar_order_stk_num: 每分钟下单股票数
        :param max_holding_days: 最大持仓天数
        :param least_force_sell_order_num: 强平时每分钟最少挂单的股票数
        :return: self.holding_record, self.buy_record,self.sell_record
        """
        if daily_selected_pool == None:
            interdayPool = self.stock_pool.values
        elif type(daily_selected_pool) == np.array:
            interdayPool = daily_selected_pool.copy()
        elif type(daily_selected_pool) == pd.DataFrame:
            interdayPool = daily_selected_pool.reindex(self.date_list, axis=0).reindex(self.stk_list, axis=1).fillna(
                False).replace(1, True).replace(0, False).values
        self.__refresh()
        factor = factor_.loc[(self.start_date, 925):(self.end_date, 1500), self.stk_list]
        factor = frame2arr(factor)
        sell_record = {}
        buy_record = {}
        holding_record = {}
        # date_list = self.date_list
        # ind_weight = self.ind_weight
        holding_df = None
        bar = tqdm(self.date_list)
        for idx, date in enumerate(bar):
            bar.set_description(f"回测运行中 {date}")
            if idx == 0:
                continue
            temp_ind_wieght = self.ind_weight[idx - 1]
            # 筛选出每日用于交易的池子的因子值
            temp_factor = factor[:, idx, :] * interdayPool[idx - 1]
            temp_factor[:, ~(interdayPool[idx - 1] > 0)] = np.nan
            stk_ind = np.array(
                list(map(lambda x: self.ind_list.index(x) if x in self.ind_list else np.nan, self.stk_ind[idx])))
            available_stk = interdayPool[idx - 1]
            if holding_df is None:
                # 首个交易日行业中性分配买入金额
                target_buy = np.round(target_holding_num * temp_ind_wieght, 0)
                target_sell = None
                force_sell = []
            else:
                # 非首个交易日，行业中性后按换手率卖出、行业中性后按换手率买入
                target_buy = np.round(target_holding_num * temp_ind_wieght * turnover, 0)
                holding_ind = np.array([x[-1] for x in holding_df])
                target_sell = np.round(
                    np.array([np.nansum(holding_ind == x) for x in range(len(target_buy))]) * turnover)
                # 强平池 [股票loc]
                holding_days = [(x[0], len(get_date_range(x[2][0], date)) - 1) for x in holding_df]
                force_sell = list(filter(lambda x: x[1] >= max_holding_days, holding_days))
                force_sell = list(map(lambda x: x[0], force_sell))
                # 可买股票=当日选出用于交易的股票池 - 前一交易日收盘时已持有的股票
                unavailable_stk = np.array([False for i in range(len(self.stk_list))])
                unavailable_stk[[int(x[0]) for x in holding_df]] = True
                available_stk = (available_stk * (~unavailable_stk)) > 0
                # TBD
            temp_buy_record, temp_sell_record = self.__intraday_trading(idx, date, temp_factor, available_stk,
                                                                        target_sell, target_buy,
                                                                        amtMax, stk_ind, force_sell, trade_percentile,
                                                                        bar_order_stk_num, least_force_sell_order_num)

            buy_record[date] = temp_buy_record
            sell_record[date] = temp_sell_record
            # 持仓记录 [股票的loc,持仓vol,买入时间,行业loc]
            holding_df = [[x, self.holding[x][1], self.holding[x][2][0], stk_ind[x]] for x in self.holding]
            holding_record[date] = holding_df
        self.buy_record = buy_record
        self.sell_record = sell_record
        self.holding_record = holding_record
        return self.holding_record, self.buy_record, self.sell_record

    def __intraday_trading(self, idx, day, intraday_factor, available_stk, target_sell_ind, target_buy_ind, amtMax,
                           stk_ind, exit_list=[],
                           percentile=0.05, trade_num=3, force_order_num=1, buy_limit=(-0.07, 0.05),
                           sell_limit=(-0.05, 0.07)):
        """
        每日日内交易函数
        :param idx: 日期在self.date_list中的索引 如果self.date_list=[20170103,20170104],日期为20170104，则idx=1
        :param day: 日期 例20170103
        :param intraday_factor: 分钟行情因子，np.array() shape=(242,len(self.stk_list)) 股票顺序与 self.stk_list 中的id顺序一致
        :param available_stk: 可买的股票 np.array() shape=(回测日期内1800股票池的股票个数) 可买的股票值为True 不可买的值为False
        :param target_sell_ind: 行业目标卖出股票数 array shape=(行业数) 行业顺序与 self.ind_list中的行业顺序一致
        :param target_buy_ind: 行业目标买入股票数 array shape=(行业数) 行业顺序与 self.ind_list中的行业顺序一致
        :param amtMax: 最大买入金额
        :param stk_ind: 股票的行业名称 array shape=(len(self.stk_list)) 值为行业代码
        :param exit_list: 待强平的股票 list 值为股票在矩阵中的索引编号
        :param percentile: 筛选分位数
        :param trade_num: 每次下单数量
        :param force_order_num: 每次最小强平数量
        :param buy_limit: 买入股票的日内收益范围限制 (down,up)
        :param sell_limit: 卖出股票的日内收益范围限制
        :return: sell_record=[[stk_id,stk_loc,trade_time,vol,sell_price],...]
                    buy_record = [[stk_id,stk_loc,trade_time,vol,sell_price],...]
        """
        sell_record, buy_record = [], []
        # 股票所在行业的待买入股票数量
        target_buy_stk = np.vectorize(lambda x: target_buy_ind[int(x)] if not np.isnan(x) else 0)(stk_ind)
        if not target_sell_ind is None:
            target_sell_stk = np.vectorize(lambda x: target_sell_ind[int(x)] if not np.isnan(x) else 0)(stk_ind)
        close = self.close[:, idx, :]
        tradable_buy_vol = self.tradable_buy_vol[:, idx, :]
        tradable_sell_vol = self.tradable_sell_vol[:, idx, :]
        if not target_sell_ind is None:
            tradable_sell_vol = self.tradable_sell_vol[:, idx, :]
        # factor_rank = bottleneck.nanrankdata(intraday_factor, axis=1)
        ret = self.ret[:, idx, :]
        # 股票当日买入金额
        bought_amt = np.zeros(intraday_factor.shape[1])
        sold_amt = np.zeros(intraday_factor.shape[1])
        # 股票当日目标买入金额
        target_amt_buy = np.zeros(intraday_factor.shape[1])
        target_amt_buy[:] = np.nan
        sell_buy_diff = 0
        sold_num = None
        bought_num = None
        buy_sell_ratio = target_buy_ind.sum() / target_sell_ind.sum() if not target_sell_ind is None else 1
        for bar in range(31, 242):
            # 计算前一分钟卖出股票数量与买入股票数量的差
            if not bought_num is None and not sold_num is None:
                sell_buy_diff = sold_num - bought_num
            # 卖出 bar=31
            bar_factor = intraday_factor[bar]
            if not target_sell_ind is None:
                # 筛选出因子排名靠后、收益在一定区间、当日未卖过且行业待卖出股票大于0或当日已卖过未卖完的股票、当日没买过
                holding_position = np.zeros(len(self.stk_list))
                holding_position[[x for x in self.holding]] = np.array([self.holding[x][1] for x in self.holding])
                bought_today = np.zeros(len(self.stk_list))
                bought_today[[x[0] for x in buy_record]] = 1
                filtered_stk = (bar_factor < np.nanquantile(bar_factor, percentile)) * \
                               (holding_position > 0) * \
                               (sell_limit[0] < ret[bar]) * (ret[bar] < sell_limit[1]) * \
                               ((target_sell_stk > 0) + (target_sell_stk == 0) * (sold_amt > 0)) * \
                               (1 - bought_today)
                filtered_stk = get_top_part_index(bar_factor, filtered_stk, trade_num - sell_buy_diff, 'min')
                # 如果有需要强平的股票
                if len(exit_list) > 0:
                    exit_stk = np.array([False for x in range(len(self.stk_list))])
                    exit_stk[exit_list] = True
                    exit_stk[list(filtered_stk)] = False
                    force_sell_stk = get_top_part_index(bar_factor, exit_stk,
                                                        max(int((trade_num - sell_buy_diff) / 2), force_order_num),
                                                        type='min')
                    filtered_stk = np.array(list(set(filtered_stk).union(set(force_sell_stk))))
                # 下单量 = 当前持仓量
                order_vol = np.array([self.holding[x][1] for x in filtered_stk])
                bar_sold_vol = self.__sending_order(bar, filtered_stk, order_vol, 'S', tradable_sell_vol)
                filtered_stk = filtered_stk[bar_sold_vol > 0]
                bar_sold_vol = bar_sold_vol[bar_sold_vol > 0]
                sold_num = len(filtered_stk)
                # 如果当前bar有卖出，更新相关数据
                if sold_num > 0:
                    # 如果股票是第一次卖，则行业待卖出股票减一
                    for stk in filtered_stk:
                        if sold_amt[stk] == 0:
                            target_sell_ind[int(stk_ind[stk])] -= 1
                    # 更新已卖出数据
                    sold_amt[filtered_stk] += bar_sold_vol * close[bar, filtered_stk]
                    target_sell_stk = np.vectorize(lambda x: target_sell_ind[int(x)] if not np.isnan(x) else 0)(stk_ind)
                    self.__clear_holding(day, bar, filtered_stk, bar_sold_vol, close[bar, filtered_stk])
                    for i, stk_loc in enumerate(filtered_stk):
                        sell_record.append(
                            [stk_loc, self.stk_list[stk_loc], (day, self.datetime_list[bar][1]), bar_sold_vol[i],
                             close[bar, stk_loc]])
                    exit_list = list(filter(lambda x: x in self.holding, exit_list))
                # 如果前一个bar买入比卖出多太多，该bar不买入
                if len(buy_record) > (len(sell_record) - len(filtered_stk)) * buy_sell_ratio:
                    continue
            ############买入
            # 筛选出:1)在可买股票池、2)因子排名靠前、3)收益在一定区间、4)当日未买过或当日买过但是没买够目标金额、
            # 5)股票所处行业待买入量不为0的股票、6)股票所处行业待买入量不为0的股票或为0但已卖过的某些股票没卖够
            # filtered_stk = (bar_factor > (bar_factor.count() * (1 - percentile))) * \
            #                ret.loc[bar].apply(lambda x: buy_limit[0] < x < buy_limit[1]) * \
            #                ((target_amt_buy > bought_amt) + target_amt_buy.isnull()) * \
            #                (stk_target['buy_target'] > 0 + (stk_target['buy_target'] == 0) * (target_amt_buy > 0) * (target_amt_buy > bought_amt))

            filtered_stk = available_stk * \
                           (bar_factor > np.nanquantile(bar_factor, 1 - percentile)) * \
                           (buy_limit[0] < ret[bar]) * (ret[bar] < buy_limit[1]) * \
                           ((target_amt_buy > bought_amt) + np.isnan(target_amt_buy)) * \
                           (target_buy_stk > 0 + (target_buy_stk == 0) * (target_amt_buy > 0) * (
                                       target_amt_buy > bought_amt))
            filtered_stk = get_top_part_index(bar_factor, filtered_stk, trade_num + sell_buy_diff, 'max')
            if len(filtered_stk) == 0:
                bought_num = 0
                continue
            # 如该分钟前某只股票已买过，则该分钟下单量=(该股票的目标买入金额-目前已经买入的金额)/当前价格
            # 如该分钟当日第一次对某只股票下单，则下单量=最大买入金额
            order_amt = (target_amt_buy - bought_amt)[filtered_stk]
            order_amt = np.vectorize(lambda x: amtMax if np.isnan(x) else x)(order_amt)
            order_vol = np.vectorize(lambda x: round(x, -2))(order_amt / close[bar, filtered_stk])
            bar_bought_vol = self.__sending_order(bar, filtered_stk, order_vol, 'B', tradable_buy_vol)
            filtered_stk = filtered_stk[bar_bought_vol > 0]
            bar_bought_vol = bar_bought_vol[bar_bought_vol > 0]
            if len(filtered_stk) == 0:
                bought_num = 0
                continue
            # 将新买入的股票的目标买入金额设为最大买入金额
            # 下单后未能买入，且之前没有持仓的，不设目标买入金额
            target_amt_buy[filtered_stk] = amtMax
            # 如果所买入股票是第一次买入，则对应行业待买入股票数量减1
            for stk in filtered_stk:
                if stk not in self.holding:
                    target_buy_ind[int(stk_ind[stk])] -= 1
            # 当日股票买入金额更新
            bought_amt[filtered_stk] += bar_bought_vol * close[bar, filtered_stk]
            # target_buy_stk = stk_ind.apply(lambda x: target_buy_ind[x] if x in target_buy_ind else np.nan)
            target_buy_stk = np.vectorize(lambda x: target_buy_ind[int(x)] if not np.isnan(x) else 0)(stk_ind)
            self.__update_holding(day, bar, filtered_stk, bar_bought_vol, close)
            for i, stk_loc in enumerate(filtered_stk):
                buy_record.append(
                    [stk_loc, self.stk_list[stk_loc], (day, self.datetime_list[bar][1]), bar_bought_vol[i],
                     close[bar, stk_loc]])
            bought_num = len(bar_bought_vol)
        return buy_record, sell_record

    def get_holding_df_by_date(self, date):
        """
        获取某天的收盘时的持仓信息
        :param date:
        :return:
        """
        if date not in self.holding_record:
            raise Exception('Target date does not contain any holding information!')
        holding = pd.DataFrame(self.holding_record[date], columns=['stk_loc', 'vol', 'datetime', 'ind_loc'])
        holding['stk_id'] = holding['stk_loc'].apply(lambda x: self.stk_list[int(x)])
        holding['industry'] = holding['ind_loc'].apply(lambda x: self.ind_list[int(x)])
        holding = holding.set_index('stk_id')
        holding['val'] = holding['vol'] * self.close_daily.loc[date, holding.index]
        return holding

    #############################统计部分
    def calc_portfolio_evaluation(self):
        """
        收益评估
        :return:
        """
        evaluation_result = pd.DataFrame()
        bar = tqdm(self.date_list[2:])
        bar.set_description('收益评估中')
        for date in bar:
            pre_trading_day = get_pre_trade_date(date, 1)
            # 今日持仓信息
            buy_record = pd.DataFrame(self.buy_record[date], columns=['stk_loc', 'stk_id', 'datetime', 'vol', 'price'])
            sell_record = pd.DataFrame(self.sell_record[date],
                                       columns=['stk_loc', 'stk_id', 'datetime', 'vol', 'price'])
            #  [股票的loc,持仓vol,买入时间,行业loc]
            holding = self.get_holding_df_by_date(date)
            buy_record['val'] = buy_record['vol'] * buy_record['price']
            sell_record['val'] = sell_record['vol'] * sell_record['price'] * (1 - self.fee)
            # 昨日持仓信息
            pre_holding = self.get_holding_df_by_date(pre_trading_day)
            # self.holding_record[pre_trading_day].copy()  # .reset_index()
            # 昨日持仓收盘价按今日前复权
            pre_holding['close_fadj'] = self.close_daily.loc[pre_trading_day, pre_holding.index] * \
                                        self.adj_factor.loc[pre_trading_day, pre_holding.index] / self.adj_factor.loc[
                                            date, pre_holding.index]
            pre_holding['close_T+1'] = self.close_daily.loc[date, pre_holding.index]
            # 昨日收盘持仓按今日往前复权后价格计算市值
            pre_holding['T_fadj_val'] = pre_holding['close_fadj'] * pre_holding['vol']
            # 昨日收盘持仓假设持仓至今日收盘的价值
            pre_holding['T+1_val'] = pre_holding['close_T+1'] * pre_holding['vol']
            profit_info = pd.Series()
            profit_info['买入股票数'] = buy_record.shape[0]
            profit_info['买入股票金额'] = buy_record['val'].sum()
            profit_info['卖出股票数'] = sell_record.shape[0]
            profit_info['卖出股票金额'] = sell_record['val'].sum()
            profit_info['当日收盘持股数量'] = holding.shape[0]
            profit_info['当日收盘持仓市值'] = holding['val'].sum()
            profit_info['日收益'] = profit_info['当日收盘持仓市值'] + profit_info['卖出股票金额'] - profit_info['买入股票金额'] - pre_holding[
                'T_fadj_val'].sum()
            profit_info['日收益率'] = profit_info['日收益'] * 2 / (pre_holding['T_fadj_val'].sum() + profit_info['当日收盘持仓市值'])
            profit_info['持有收益率'] = pre_holding['T+1_val'].sum() / pre_holding['T_fadj_val'].sum() - 1
            evaluation_result[date] = profit_info
        # 首个交易日信息统计
        date = self.date_list[1]
        buy_record = pd.DataFrame(self.buy_record[date], columns=['stk_loc', 'stk_id', 'datetime', 'vol', 'price'])
        holding = self.get_holding_df_by_date(date)
        buy_record['val'] = buy_record['vol'] * buy_record['price']
        profit_info = pd.Series()
        profit_info['买入股票数'] = buy_record.shape[0]
        profit_info['买入股票金额'] = buy_record['val'].sum()
        profit_info['买入股票数'] = buy_record.shape[0]
        profit_info['买入股票金额'] = buy_record['val'].sum()
        profit_info['当日收盘持仓市值'] = holding['val'].sum()
        evaluation_result[date] = profit_info
        # alpha计算
        evaluation_result = evaluation_result.T.reindex(self.date_list[1:])
        evaluation_result['指数收益率'] = self.benchmark_daily_close[self.benchmark_daily_close.columns[0]].pct_change()
        evaluation_result['每日alpha'] = evaluation_result['日收益率'] - evaluation_result['指数收益率']
        evaluation_result['每日持有alpha'] = evaluation_result['持有收益率'] - evaluation_result['指数收益率']
        evaluation_result['每日交易alpha'] = evaluation_result['每日alpha'] - evaluation_result['每日持有alpha']
        evaluation_result['累计收益率'] = evaluation_result['日收益率'].cumsum()
        evaluation_result['累计超额收益率'] = evaluation_result['每日alpha'].cumsum()
        self.result['总体信息'] = evaluation_result
        return self.result['总体信息']

    def calc_signal_evaluation(self):
        """
        单次信号评估
        计算单次信号的平均收益、超额收益、收益胜率、超额收益胜率
        计算不同持仓周期下的平均收益、超额收益、收益胜率、超额收益胜率
        :return:
        """
        evaluation_result = []
        bar = tqdm(self.trade_pieces)
        bar.set_description("逐笔持仓统计中")
        for signal_info in bar:
            temp_result = self.evaluate_one_signal(signal_info)
            evaluation_result.append(temp_result)
        # evaluation_result = list(map(self.evaluate_one_signal,self.trade_pieces))
        evaluation_result = pd.DataFrame(evaluation_result,
                                         columns=['股票代码', '起始bar', '结束bar', '持有天数', '现货收益', '基准收益', 'alpha', '买次数',
                                                  '卖次数', '总次数'])
        self.siganl_evaluation = evaluation_result
        signal_avg_evaluation = pd.DataFrame()
        signal_avg_evaluation['均值'] = evaluation_result.mean()
        signal_avg_evaluation['胜率'] = evaluation_result[['现货收益', 'alpha']].apply(lambda x: x > 0).astype(float).mean()
        periodly_evaluation = evaluation_result.groupby('持有天数').mean().drop('股票代码', axis=1)
        periodly_evaluation.columns = [x + '均值' for x in periodly_evaluation.columns]
        periodly_evaluation['该持仓天数的数量'] = evaluation_result.groupby('持有天数').size()
        self.result['每笔持仓统计'] = evaluation_result
        self.result['收益胜率'] = signal_avg_evaluation
        self.result['分持仓日统计'] = periodly_evaluation
        return self.result['收益胜率'], self.result['分持仓日统计']

    def evaluate_one_signal(self, signal_info):
        stk = signal_info[0]
        vol, price, bench = [np.array(x) for x in signal_info[3:]]
        bar_list = signal_info[2]
        adj_factor = self.adj_factor.loc[[x[0] for x in bar_list], stk].values
        price_adj = price * adj_factor / adj_factor[0]
        amt = vol * price_adj
        amt[vol < 0] = amt[vol < 0] * (1 - self.fee)
        profit = -1 * np.nansum(amt) / np.nansum(amt[amt > 0])
        # 相应指数仓位计算
        vol_bench = np.array([np.nan for i in range(amt.shape[0])])
        vol_bench[vol > 0] = amt[vol > 0] / bench[vol > 0]
        vol_total_bench = np.nansum(vol_bench)
        vol_bench[vol < 0] = -1 * vol_total_bench * amt[vol < 0] / np.nansum(amt[vol < 0])
        amt_bench = vol_bench * bench
        bench_profit = -1 * np.nansum(amt_bench) / np.nansum(amt_bench[amt_bench > 0])
        holding_days = len(get_date_range(bar_list[0][0], bar_list[-1][0])) - 1
        # [股票代码,起始bar,结束bar,持有天数,现货收益,基准收益,alpha,买次数,卖次数,总次数]
        return [signal_info[0], bar_list[0], bar_list[-1], holding_days, profit, bench_profit, profit - bench_profit,
                np.nansum(vol > 0), np.nansum(vol < 0), len(vol)]

    def calc_daily_industry_weight(self):
        """
        计算每日行业权重
        :return:
        """
        daily_industry_weight = pd.DataFrame()
        holding_date = [x for x in self.holding_record]
        holding_date.sort()
        bar = tqdm(holding_date)
        bar.set_description('每日行业权重统计中')
        for date in bar:
            holding_df = self.get_holding_df_by_date(date)
            holding_df_ind = holding_df.groupby('industry').sum()[['val']]
            holding_df_ind = holding_df_ind / holding_df_ind.sum()
            daily_industry_weight = daily_industry_weight.append(holding_df_ind.rename(columns={'val': date}).T)
        self.result['行业权重'] = daily_industry_weight.reindex(self.ind_list, axis=1)
        return self.result['行业权重']

    def evaluate(self, factor, daily_selected_pool=None, target_holding_num=200, amtMax=100000, turnover=0.5,
                 trade_percentile=0.05, bar_order_stk_num=3,
                 max_holding_days=5, least_force_sell_order_num=1):
        """
        回测并计算结果
        :return:
        """
        self.__refresh()
        print('开始回测...')
        self.backtest(factor, daily_selected_pool, target_holding_num, amtMax, turnover, trade_percentile,
                      bar_order_stk_num, max_holding_days, least_force_sell_order_num)
        print('总体信息评估中...')
        self.calc_portfolio_evaluation()
        print('单笔持仓信息评估中...')
        self.calc_signal_evaluation()
        print('行业权重统计中...')
        self.calc_daily_industry_weight()
        return self.result

    def output_result(self, output_path, file_name):
        print('正在输出回测结果...')
        if not file_name.endswith('.xlsx'):
            file_name = file_name + '.xlsx'
        with pd.ExcelWriter(output_path + file_name) as writer:
            for sheet in self.result:
                self.result[sheet].to_excel(writer, sheet_name=sheet)

    def evaluation_and_report(self, factor, output_path, file_name, daily_selected_pool=None, target_holding_num=200,
                              amtMax=100000, turnover=0.5, trade_percentile=0.05, bar_order_stk_num=3,
                              max_holding_days=5, least_force_sell_order_num=1):
        result = self.evaluate(factor, daily_selected_pool, target_holding_num, amtMax, turnover, trade_percentile,
                               bar_order_stk_num, max_holding_days, least_force_sell_order_num)
        self.output_result(output_path, file_name)


def main():
    factor = pd.read_hdf(
        '/data/group/800319/storeFactor/alpha14 .h5',
        'alpha14 ')
    # 初始化，约125s
    e = time.time()
    strat = StrategyBackTest()
    print('initialization', time.time() - e)
    # 回测并输出,约750s
    strat.evaluation_and_report(factor,
                                output_path='/data/group/800319/junkData/temp_daily_by_lzc/Alpha101_v0/',
                                file_name='alpha14_evaluation')
    print('calculation', time.time() - e)


if __name__ == "__main__":
    main()
