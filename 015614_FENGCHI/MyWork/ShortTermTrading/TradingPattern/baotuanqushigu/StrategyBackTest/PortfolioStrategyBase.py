# @Time : 2020/10/25 10:04
# @Author : Zhichen Lu
# @File : PortfolioStrategyBase.py
import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import os
from abc import abstractmethod

import numpy as np
import pandas as pd
from StrongStockModel.conf.path_config import root_path, deal_price_path
from StrongStockModel.dataApi.getData import get_date_range, get_daily_1stock, get_minute_1factor, get_daily_1factor
from StrongStockModel.dataApi.stockList import clean_stock_list
from StrongStockModel.dataApi.tradeDate import trade_minutes, get_trade_date_interval
from tqdm import tqdm
from multiprocessing import Pool, Manager
import gc
import time, datetime

class PortfolioStrategyBase:

    def __init__(self, start=20140101, end=20181231, stock_pool=None, target_point=None, buy_cost=0.001, sell_cost=0.001, per_amt=500000, append_param={}):
        self.date_list = get_date_range(start, end)
        start, end = self.date_list[0], self.date_list[-1]
        if stock_pool is None:
            stock_pool = pd.read_pickle(root_path + 'stock_pool_without_limit_up_down.pkl')
            if start >= stock_pool.index[0] and end <= stock_pool.index[-1]:
                self.stock_pool = stock_pool.loc[start:end]
            else:
                self.stock_pool = self.__load_stock_pool(start, end)
        else:
            self.stock_pool = stock_pool

        if set(self.date_list) != set(self.stock_pool.index):
            self.stock_pool = self.stock_pool.reindex(self.date_list)

        if target_point is None:
            self.trading_point = trade_minutes[1:-1]
        elif target_point == '5min':
            self.trading_point = [trade_minutes[1:][i * 5] for i in range(48)]
        elif target_point == '30min':
            self.trading_point = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
        else:
            self.trading_point = target_point

        self.stk_list = self.stock_pool.columns.tolist()
        self.daily_info = {x: get_daily_1factor(x, date_list=self.date_list, code_list=self.stk_list) for x in
                           ['close', 'close_badj']}  # get_daily_1stock(stk, ['close', 'close_badj'], self.date_list)
        self.daily_info['close_padj'] = self.daily_info['close'].shift(-1) * self.daily_info['close_badj'] / self.daily_info['close_badj'].shift(-1)
        self.daily_info['adj_ratio'] = self.daily_info['close'] / self.daily_info['close_padj']
        self.pre_dail_info = {x: self.daily_info[x].shift(1) for x in self.daily_info}

        close = get_minute_1factor('close', start_datetime=self.date_list[0] * 10000 + 925, end_datetime=self.date_list[-1] * 10000 + 1500,
                                   code_list=self.stock_pool.columns.tolist())
        if os.path.exists(deal_price_path + 'deal_price%d_%d.pkl' % (start, end)) and 'deal_price_path' not in append_param:
            deal_price = pd.read_pickle(deal_price_path + 'deal_price%d_%d.pkl' % (start, end))
            # deal_price = deal_price.swaplevel(0, 1).loc[self.trading_point].swaplevel(0, 1)
        elif 'deal_price_path' in append_param:
            print('load from', append_param['deal_price_path'])
            deal_price = pd.read_pickle(append_param['deal_price_path']).loc[start:end]
        else:
            deal_price = close.rolling(10).mean().shift(-10)
            deal_price.to_pickle(deal_price_path + 'deal_price%d_%d.pkl' % (start, end))
        deal_price = deal_price.swaplevel(0, 1).loc[self.trading_point].swaplevel(0, 1)
        close = close.swaplevel(0, 1).loc[self.trading_point].swaplevel(0, 1)
        self.per_amt = per_amt
        self.step = len(self.trading_point)
        self.close = close
        self.deal_price = deal_price
        self.data_flow = {'close': None, 'deal_price': None}
        self.buy_cost = buy_cost
        self.sell_cost = sell_cost
        self.pre_date_idx, self.pre_date = None, None
        self.date, self.date_idx = None, None
        self.__re_initial(self.stock_pool.columns.tolist())

    @abstractmethod
    def trade(self, stk):
        return self.bar_dealprice[stk]

    @abstractmethod
    def bar_handler(self):
        pass

    def __load_stock_pool(self, start, end):
        stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                      no_pause=True, least_recover_days=1,
                                      no_pause_limit=0.5, no_pause_stats_days=120,
                                      no_limit_up=False, no_limit_down=False,
                                      other_limit=None, start_date=start, end_date=end)
        h5_path = "/data/group/wdb_h5/WIND/universe_complete/universe_complete.h5"
        limit_info = {}
        limit_info['OPENUPLIMIT'] = pd.read_hdf(h5_path, 'OPENUPLIMIT')
        limit_info['OPENDOWNLIMIT'] = pd.read_hdf(h5_path, 'OPENDOWNLIMIT')
        for k in limit_info:
            limit_info[k] = limit_info[k].reset_index()
            limit_info[k]['dt'] = limit_info[k]['dt'].apply(lambda x: int(x.strftime('%Y%m%d')))
            limit_info[k]['Ticker'] = limit_info[k]['Ticker'].apply(lambda x: int(x[:-3]))
            limit_info[k] = limit_info[k].pivot_table(index='dt', columns='Ticker', values=k).reindex(stock_pool.index, axis=0).reindex(stock_pool.columns, axis=1).fillna(0) > 0

        stock_pool = stock_pool & limit_info['OPENUPLIMIT'] & limit_info['OPENDOWNLIMIT']
        return stock_pool

    def __re_initial(self, stk_list=None):
        self.holding = {}
        self.available = {}
        self.evaluation_result = {}
        self.record = Manager().dict()

    def isinpool(self, stk):
        bool_val = self.stock_pool[self.date_idx:self.date_idx + 1][stk].tolist()[0]
        return bool_val

    def buy(self, stk, vol=None, amt=None):
        if not self.isinpool(stk):
            """
            不在股票池内时不可买
            """
            return 0, np.nan
        if stk in self.holding:
            holding = self.holding[stk]
        else:
            holding = 0

        if stk in self.available:
            available = self.available[stk]
        else:
            available = 0
        deal_price = self.trade(stk)  # self.bar_dealprice[stk]
        if deal_price == 0 or np.isnan(deal_price):
            return 0, np.nan
        if vol is None and amt is None:
            vol = round(self.per_amt / deal_price, -2)
        elif vol is None:
            vol = round(amt / deal_price, -2)
        elif amt is None:
            pass
        else:
            raise Exception('One of amt and vol must be not None')
        if np.isnan(vol) or vol == 0:
            return 0, deal_price
        holding += vol
        self.holding[stk], self.available[stk] = holding, available
        if stk not in self.record:
            self.record[stk] = [[self.datetime[0], self.datetime[1], 'B', vol, deal_price, holding, available]]
        else:
            record = self.record[stk]
            record.append([self.datetime[0], self.datetime[1], 'B', vol, deal_price, holding, available])
            self.record[stk] = record
        return vol, deal_price

    def sell(self, stk, vol=None):
        available = self.available[stk]
        holding = self.holding[stk]
        if vol is None:
            vol = available
        else:
            vol = min(vol, available)
        if vol == 0 or np.isnan(vol):
            return 0, np.nan
        deal_price = self.trade(stk)
        if deal_price == 0 or np.isnan(deal_price):
            return 0, np.nan
        holding -= vol
        available -= vol
        if holding > 0:
            self.holding[stk] = holding
        else:
            del self.holding[stk]
        if available > 0:
            self.available[stk] = available
        else:
            del self.available[stk]
        if stk not in self.record:
            raise Exception('Sell without record')
        else:
            record = self.record[stk]
            record.append([self.datetime[0], self.datetime[1], 'S', -vol, deal_price, holding, available])
            self.record[stk] = record
        return vol, deal_price

    @abstractmethod
    def daily_update(self, idx, date):
        self.pre_date_idx, self.pre_date = self.date_idx, self.date
        self.date_idx, self.date = idx, date
        self.data_flow['close'] = self.close[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        self.data_flow['deal_price'] = self.deal_price[self.date_idx * self.step:(self.date_idx + 1) * self.step]

        if self.pre_date is None:
            return
        pre_close_padj, pre_close, pre_adj_ratio = self.pre_dail_info['close_padj'][self.date_idx:self.date_idx + 1].T[date], \
                                                   self.pre_dail_info['close'][self.date_idx:self.date_idx + 1].T[date], \
                                                   self.pre_dail_info['adj_ratio'][self.date_idx:self.date_idx + 1].T[date]
        for stk in self.holding:
            holding = self.holding[stk]
            stk_close_padj, stk_close, stk_adj_ratio = pre_close_padj[stk], pre_close[stk], pre_adj_ratio[stk]
            available = self.available[stk] if stk in self.available else 0
            if holding > 0:
                record = self.record[stk]
                record.append([self.pre_date, 1500, 'H', stk_close_padj, stk_close, holding, available])
                if abs(1 - stk_adj_ratio) > 0.0001:
                    holding = holding * stk_adj_ratio
                    self.holding[stk] = holding
                record.append([self.date, 925, 'D', np.nan, np.nan, holding, holding])
                self.record[stk] = record
                self.available[stk] = holding

    def transfer(self, each):
        self.record[each] = pd.DataFrame(self.record[each], columns=['date', 'time', 'flag', 'vol', 'deal_price', 'holding', 'available']).set_index(['date', 'time'])

    def run_backtest(self, kernel=10):
        self.__re_initial()
        for date_idx, date in enumerate(tqdm(self.date_list)):
            self.daily_update(date_idx, date)
            for time_idx, time_point in enumerate(self.trading_point):
                try:
                    self.bar_dealprice = self.data_flow['deal_price'][time_idx:time_idx + 1].T[(date, time_point)]
                except:
                    print(1)
                self.datetime = (date, time_point, date_idx, time_idx)
                self.bar_point = date_idx * self.step + time_idx
                self.bar_handler()
                # print(self.datetime)
            print(date, len(self.holding))
        record = list(self.record.keys())
        # pool = Pool(kernel)
        # pool.map(self.transfer,record)
        # pool.close()
        # pool.join()
        for each in record:
            self.record[each] = pd.DataFrame(self.record[each], columns=['date', 'time', 'flag', 'vol', 'deal_price', 'holding', 'available']).set_index(['date', 'time'])
        gc.collect()
        return self.record._getvalue()


class EvaluationHelper:

    def __init__(self, buy_cost_ratio=0.001, sell_cost_ratio=0.001):
        """
        :param Cls:股票回测类的类名
        :param buy_cost_ratio: 买入费率
        :param sell_cost_ratio: 卖出费率
        :param price_rolling_window: 计算成交价格时间窗口
        :param amt_per_signal: 每次买入金额
        :param available_info: 每只股票某天是否可交易(False为无论是否有持仓都不能买卖)  pd.DataFrame(index=datelist,columns=[stk_id])
        :param universe_info: pd.DataFrame(index=datelist,columns=[stk_id])
                            每只股票每天是否处于股票池中(True为可买可卖,False为可卖不可买，False且无持仓不进入日内循环和 bar_handler)
        """
        self.record = Manager().dict()
        self.buy_cost = buy_cost_ratio
        self.sell_cost = sell_cost_ratio
        self.evaluation_result = {}

    def evaluat_signal_by_stk(self, stk):
        if self.record[stk] is None:
            print(stk, 'None')
            return []
        record = self.record[stk].copy()
        record = record[~record['flag'].isin(['H', 'D'])].reset_index()
        record['cashflow'] = -1 * record['vol'] * record['deal_price']
        cash_occupy = 0
        profit = 0
        signal_res = []
        buy_times, sell_times = 0, 0
        for date, bar, flag, vol, deal_price, holding, available, cashflow in list(record.values):
            if flag == 'B':
                buy_times += 1
            if flag == 'S':
                sell_times += 1
            if cash_occupy == 0:
                if cashflow > 0:
                    raise Exception('Wrong cash flow direction')
                cash_occupy = 0
                start = (date, bar)
            profit += cashflow
            if cashflow < 0:
                cash_occupy += -1 * cashflow
                profit -= self.buy_cost * abs(cashflow)
            if cashflow > 0:
                profit -= self.sell_cost * abs(cashflow)
            if holding == 0:
                holding_minutes = 240 * get_trade_date_interval(date, start[0]) + (240 - trade_minutes.index(start[1])) + (trade_minutes.index(bar) - 1)
                signal_res.append([start[0] * 10000 + start[1], date * 10000 + bar, profit, cash_occupy, holding_minutes, buy_times, sell_times, stk])
                cash_occupy = 0
                profit = 0
                buy_times, sell_times = 0, 0
        return signal_res
        # signal_res_df = pd.DataFrame(signal_res, columns=['start', 'end', 'profit', 'cash_occupy', 'holding_minutes', 'buy_times', 'sell_times'])
        # if signal_res_df.shape[0]>0:
        #     signal_res_df['stk_id'] = stk
        # del record
        # gc.collect()
        # return signal_res_df

    def evaluate_stk_by_day(self, stk):

        if self.record[stk] is None:
            print(stk, 'None')
            return pd.DataFrame()
        record = self.record[stk].copy()
        holding_info = record[record['flag'].eq('H')]
        holding_info = holding_info.rename(columns={'vol': 'close_padj', 'deal_price': 'close'})

        holding_info = holding_info.reset_index().set_index('date')

        buy_info = record[record['flag'].eq('B')].reset_index()
        buy_info = pd.merge(buy_info, holding_info[['close']].reset_index(), how='left', on=['date'])

        sell_info = record[record['flag'].eq('S')].reset_index()
        sell_info = pd.merge(sell_info, holding_info[['close_padj']].shift(1).reset_index(), how='left', on=['date'])

        trade_info = record[record['flag'].isin(['B', 'S'])]
        trade_info['净买入'] = trade_info['vol'].values * trade_info['deal_price'].values
        #####修改替换函数
        mapdict = {'B': 1 + self.buy_cost, 'S': 1 - self.sell_cost}
        trade_info['flag'] = [mapdict[x] for x in trade_info['flag']]
        #####
        #trade_info['扣费后净买入'] = trade_info['vol'].values * trade_info['deal_price'].values * (trade_info['flag'].replace('B',1 - self.buy_cost).replace('S',1-self.sell_cost)).values
        trade_info['扣费后净买入'] = trade_info['vol'].values * trade_info['deal_price'].values * trade_info['flag'].values
        trade_info = trade_info.reset_index()
        if len(trade_info) == 0:
            return pd.DataFrame()
        twap = get_daily_1stock(stk, ['twap'], date_list=sorted(list(set(trade_info['date'].tolist())))).reset_index()
        trade_info = pd.merge(trade_info, twap, how='left', on=['date'])
        trade_info['择时收益'] = (trade_info['twap'].values - trade_info['deal_price'].values) * trade_info['vol'].values

        res = trade_info[['date', '净买入', '扣费后净买入', '择时收益']].groupby('date').sum()
        res = pd.concat([res, pd.DataFrame(holding_info['holding'].values * holding_info['close'].values, index=holding_info.index, columns=['收盘持仓市值'])], axis=1)
        res['买入操作次数'] = buy_info.groupby('date').size()
        res['卖出操作次数'] = sell_info.groupby('date').size()
        return res

    def evaluate_daily(self, kernel=10):
        # record = self.record._getvalue()
        daily_result = {}
        e = time.time()
        stk_list = list(self.record.keys())
        pbar = tqdm(total=len(stk_list))

        def update(*param):
            pbar.update()
            pbar.set_description('按日评估中 |%s|%s' % (str(stk_list[pbar.last_print_n - 1]), datetime.datetime.now().strftime('%H:%M:%S')))
            if pbar.last_print_n == len(stk_list):
                pbar.close()

        self.pool_dict = Manager().dict()
        pool = Pool(kernel)
        for i in range(len(stk_list)):
            stk = stk_list[i]
            daily_result[stk] = pool.apply_async(self.evaluate_stk_by_day, (stk,), callback=update)
        pool.close()
        pool.join()
        print('评估结束', time.time() - e)
        if len(daily_result) == 0:
            return pd.DataFrame(), pd.DataFrame()
        for k in daily_result:
            try:
                daily_result[k] = daily_result[k].get()
            except:
                print(k, 'wrong')
                daily_result[k] = self.evaluate_stk_by_day(k)
        res_pn = pd.Panel(daily_result)
        # pd.to_pickle(res_pn, '/data/group/800319/Faamonitor/factors/daily_record_pn_factor400_5pct_beta.pkl')
        # res_pn = pd.read_pickle('/data/group/800319/Faamonitor/factors/daily_record_pn_for_update.pkl')
        if 0 in res_pn.shape:
            return pd.DataFrame(), pd.DataFrame()
        daily_info = res_pn.sum(axis='items')
        # daily_count = res_pn.count(axis='items')
        # check = res_pn.loc[:,20170307,:].sort_values('close',axis=1)
        ####取出买入操作次数，卖出操作次数矩阵
        daily_info['买入股票数'] = res_pn.loc[:, :, '买入操作次数'].replace(0, np.nan).count(axis=1)
        daily_info['卖出股票数'] = res_pn.loc[:, :, '卖出操作次数'].replace(0, np.nan).count(axis=1)
        # check = res_pn.loc[:, :, '卖出操作次数'].replace(0, np.nan).loc[20160205]   recor_797 = self.record[797]
        daily_info['占用资金'] = daily_info['收盘持仓市值'].shift(1).fillna(0) + np.fmax(daily_info['净买入'], 0)
        daily_info['当日收益'] = daily_info['收盘持仓市值'].diff() - daily_info['扣费后净买入']
        if len(daily_info) > 0:
            daily_info.at[daily_info.index[0], '当日收益'] = daily_info['收盘持仓市值'].tolist()[0] - daily_info['扣费后净买入'].tolist()[0]
        daily_info['当日收益率'] = daily_info['当日收益'] / daily_info['占用资金']
        daily_info['择时收益率'] = daily_info['择时收益'] / daily_info['占用资金']
        daily_info = pd.concat([daily_info.drop(['择时收益', '择时收益率'], axis=1), daily_info[['择时收益', '择时收益率']]], axis=1)
        daily_info['累积收益'] = daily_info['当日收益'].cumsum()
        daily_info['累积收益率'] = daily_info['当日收益率'].cumsum()

        daily_info['benchmark'] = get_daily_1factor('close', date_list=daily_info.index.tolist(), code_list=['ZZ500'], type='bench')['ZZ500']
        daily_info['benchmark_pct_change'] = daily_info['benchmark'].pct_change()
        daily_info['基准收益比'] = daily_info['当日收益率'] / daily_info['benchmark_pct_change']

        daily_info['year'] = [x // 10000 for x in daily_info.index.tolist()]
        daily_info = daily_info[daily_info['累积收益率'].fillna(0) != 0]
        yearly_stat = {}
        for year in sorted(list(set(daily_info['year']))) + ['全时段']:
            if year == '全时段':
                temp_info = daily_info
            else:
                temp_info = daily_info[daily_info['year'] == year]
            temp_stat = pd.Series()
            temp_stat['相对基准收益收益比(涨)'] = temp_info[temp_info['benchmark_pct_change'] > 0]['基准收益比'].mean()
            temp_stat['相对基准收益收益比(跌)'] = temp_info[temp_info['benchmark_pct_change'] < 0]['基准收益比'].mean()
            temp_stat['相对基准收益盈亏比'] = temp_info[temp_info['benchmark_pct_change'] > 0]['基准收益比'].mean() / temp_info[temp_info['benchmark_pct_change'] < 0]['基准收益比'].mean()
            temp_stat['根据大盘涨跌计算盈亏比'] = -1 * temp_info[temp_info['benchmark_pct_change'] > 0]['当日收益率'].mean() / temp_info[temp_info['benchmark_pct_change'] < 0]['当日收益率'].mean()
            temp_stat['根据大盘涨跌计算账面盈亏比'] = -1 * temp_info[temp_info['benchmark_pct_change'] > 0]['当日收益'].mean() / temp_info[temp_info['benchmark_pct_change'] < 0]['当日收益'].mean()
            temp_stat['收益率盈亏比'] = -1 * temp_info[temp_info['当日收益率'] > 0]['当日收益率'].mean() / temp_info[temp_info['当日收益率'] < 0]['当日收益率'].mean()
            temp_stat['日胜率'] = (temp_info['当日收益率'] > 0).sum() / ((temp_info['当日收益率'] > 0).sum() + (temp_info['当日收益率'] < 0).sum())
            temp_stat['账面收益盈亏比'] = -1 * temp_info[temp_info['当日收益'] > 0]['当日收益'].mean() / temp_info[temp_info['当日收益'] < 0]['当日收益'].mean()
            temp_stat['收益率均值'], temp_stat['收益率波动'] = temp_info['当日收益率'].mean(), temp_info['当日收益率'].std()
            temp_stat['累计收益率最大回撤'] = (temp_info['累积收益率'].cummax() - temp_info['累积收益率']).max()
            temp_stat['累计账面最大亏损'] = (temp_info['累积收益'].cummax() - temp_info['累积收益']).max()
            yearly_stat[year] = temp_stat
        yearly_stat = pd.DataFrame(yearly_stat)

        date_list = get_date_range(daily_info.index[0], daily_info.index[-1])
        daily_info = daily_info.reindex(date_list)
        daily_info[['收盘持仓市值', '累积收益', '累积收益率']] = daily_info[['收盘持仓市值', '累积收益', '累积收益率']].fillna(method='pad')
        daily_info['占用资金'] = daily_info['收盘持仓市值'].shift(1).fillna(0) + np.fmax(daily_info['净买入'].fillna(0), 0)
        daily_info = daily_info.fillna(0)
        daily_info.index = daily_info.index.astype(str)
        daily_info = daily_info.drop(['benchmark', 'benchmark_pct_change', '基准收益比', 'year'], axis=1)
        return daily_info, yearly_stat

    def evaluate_by_signal(self, kernel=10):
        eval_signal_record = []
        # record = self.record._getvalue()
        key_list = list(self.record.keys())
        pbar = tqdm(total=len(key_list))

        def update(*param):
            pbar.update()
            pbar.set_description('按信号评估中 |%s|%s' % (str(key_list[pbar.last_print_n - 1]), datetime.datetime.now().strftime('%H:%M:%S')))
            if pbar.last_print_n == len(key_list):
                pbar.close()

        pool_dict = {}
        pool = Pool(kernel)
        for stk in key_list:
            pool_dict[stk] = pool.apply_async(self.evaluat_signal_by_stk, (stk,), callback=update)
        pool.close()
        pool.join()
        for stk in pool_dict:
            try:
                eval_signal_record = eval_signal_record + pool_dict[stk].get()
            except:
                print(stk, 'eval Wrong')
                self.evaluat_signal_by_stk(stk)
        pool_dict.clear()
        del pool, pool_dict
        gc.collect()
        eval_signal_record = pd.DataFrame(eval_signal_record, columns=['start', 'end', 'profit', 'cash_occupy', 'holding_minutes', 'buy_times', 'sell_times', 'stk_id'])
        if len(eval_signal_record) == 0:
            return pd.DataFrame(), eval_signal_record
        eval_signal_record['收益率'] = eval_signal_record['profit'] / eval_signal_record['cash_occupy']
        eval_signal_record['平均每分钟收益率'] = eval_signal_record['收益率'] / eval_signal_record['holding_minutes']
        eval_signal_record['胜率'] = (eval_signal_record['收益率'] > 0) * 1
        eval_signal_record['end_year'] = eval_signal_record['end'] // 100000000

        # 整体统计
        eval_signal_result = eval_signal_record[['holding_minutes']].mean()  # eval_signal_record[['holding_minutes', '收益率', '平均每分钟收益率', '胜率']].mean()
        eval_signal_record['收益率*buy_times'] = (eval_signal_record['收益率'] * eval_signal_record['buy_times'])
        eval_signal_record['平均每分钟收益率*buy_times'] = (eval_signal_record['平均每分钟收益率'] * eval_signal_record['buy_times'])
        eval_signal_record['胜*buy_times'] = eval_signal_record['胜率'] * eval_signal_record['buy_times']
        eval_signal_result['收益率'] = eval_signal_record['收益率*buy_times'].sum() / eval_signal_record['buy_times'].sum()
        eval_signal_result['平均每分钟收益率'] = eval_signal_record['平均每分钟收益率*buy_times'].sum() / eval_signal_record['buy_times'].sum()
        eval_signal_result['胜率'] = eval_signal_record['胜*buy_times'].sum() / eval_signal_record['buy_times'].sum()
        win_part = eval_signal_record[eval_signal_record['收益率'] > 0][['收益率*buy_times', 'buy_times']].sum()
        lose_part = eval_signal_record[eval_signal_record['收益率'] < 0][['收益率*buy_times', 'buy_times']].sum()
        eval_signal_result['盈利交易收益均值'] = win_part['收益率*buy_times'] / win_part['buy_times']
        eval_signal_result['亏损交易收益均值'] = lose_part['收益率*buy_times'] / lose_part['buy_times']  # eval_signal_record[eval_signal_record['收益率'] < 0]['收益率'].mean()
        eval_signal_result['盈亏比(收益率)'] = -1 * eval_signal_result['盈利交易收益均值'] / eval_signal_result['亏损交易收益均值']
        del win_part, lose_part
        win_part = eval_signal_record[eval_signal_record['平均每分钟收益率'] > 0][['平均每分钟收益率*buy_times', 'buy_times']].sum()
        lose_part = eval_signal_record[eval_signal_record['平均每分钟收益率'] < 0][['平均每分钟收益率*buy_times', 'buy_times']].sum()
        eval_signal_result['盈利交易平均每分钟收益均值'] = win_part['平均每分钟收益率*buy_times'] / win_part['buy_times']  # eval_signal_record[eval_signal_record['收益率'] > 0]['平均每分钟收益率'].mean()
        eval_signal_result['亏损交易平均每分钟收益均值'] = lose_part['平均每分钟收益率*buy_times'] / lose_part['buy_times']  # eval_signal_record[eval_signal_record['收益率'] < 0]['平均每分钟收益率'].mean()
        del win_part, lose_part
        eval_signal_result['盈亏比(平均每分钟收益率)'] = -1 * eval_signal_result['盈利交易平均每分钟收益均值'] / eval_signal_result['亏损交易平均每分钟收益均值']
        eval_signal_result['交易次数'] = eval_signal_record[['buy_times', 'sell_times']].sum().sum()
        # 分年统计
        # yearly_eval_signal_result = eval_signal_record[['holding_minutes', 'end_year']].groupby('end_year').mean()
        yearly_temp_count = eval_signal_record[['收益率*buy_times', '平均每分钟收益率*buy_times', '胜*buy_times', 'buy_times', 'end_year']].groupby('end_year').sum()
        yearly_eval_signal_result = (yearly_temp_count.T / yearly_temp_count['buy_times']).T.rename(columns={'收益率*buy_times': '收益率',
                                                                                                             '平均每分钟收益率*buy_times': '平均每分钟收益率',
                                                                                                             '胜*buy_times': '胜率'}).drop('buy_times', axis=1)
        del yearly_temp_count
        yearly_eval_signal_result['holding_minutes'] = eval_signal_record[['holding_minutes', 'end_year']].groupby('end_year').mean()['holding_minutes']

        win_part = eval_signal_record[eval_signal_record['收益率'] > 0][['收益率*buy_times', '平均每分钟收益率*buy_times', 'buy_times', 'end_year']].groupby('end_year').sum()
        lose_part = eval_signal_record[eval_signal_record['收益率'] < 0][['收益率*buy_times', '平均每分钟收益率*buy_times', 'buy_times', 'end_year']].groupby('end_year').sum()
        win_part = (win_part.T / win_part['buy_times']).T.drop('buy_times', axis=1)
        lose_part = (lose_part.T / lose_part['buy_times']).T.drop('buy_times', axis=1)
        win_loss_rate = -1 * (win_part / lose_part)
        yearly_eval_signal_result = pd.concat([yearly_eval_signal_result,
                                               win_part.rename(columns={'收益率*buy_times': '盈利交易收益均值', '平均每分钟收益率*buy_times': '盈利交易平均每分钟收益均值'}),
                                               lose_part.rename(columns={'收益率*buy_times': '亏损交易收益均值', '平均每分钟收益率*buy_times': '亏损交易平均每分钟收益均值'}),
                                               win_loss_rate.rename(columns={'收益率*buy_times': '盈亏比(收益率)', '平均每分钟收益率*buy_times': '盈亏比(平均每分钟收益率)'})], axis=1)
        trade_times = eval_signal_record[['buy_times', 'sell_times', 'end_year']].groupby('end_year').sum()
        yearly_eval_signal_result['交易次数'] = trade_times.sum(axis=1)
        yearly_eval_signal_result = yearly_eval_signal_result.T
        yearly_eval_signal_result['全时段'] = eval_signal_result
        eval_signal_record['start'] = eval_signal_record['start'].astype(str)
        eval_signal_record['end'] = eval_signal_record['end'].astype(str)
        print('new stat')
        return eval_signal_record.drop(['胜率', 'end_year'], axis=1).rename({'buy_times': '买入操作次数', 'sell_times': '卖出操作次数'}), yearly_eval_signal_result.rename(
            index={'holding_minutes': '平均持仓时间'})

    def one_wave_run(self, record, kernel=10, output_path=None, signal_record_save=False):
        """
        一次运行回测和评估并输出
        :param stk_list: 股票列表 [int,int,...]
        :param start:int
        :param end:int
        :param kernel: 并行数 int
        :param output_path:输出文件路径
        :param mode: 模式 'multi'/'serial'  （并行/串行）
        :param append_para: 附加参数 {} 参数会被传入到股票策略类的初始化函数中
        :return:
        """
        del self.record
        gc.collect()
        self.record = Manager().dict()
        for k in record:
            self.record[k] = record[k]
        self.evaluation_result['每日持仓统计'], self.evaluation_result['持仓综合统计'] = self.evaluate_daily(kernel)
        self.evaluation_result['逐笔持仓统计'], self.evaluation_result['逐笔持仓综合统计'] = self.evaluate_by_signal(kernel)
        if not output_path is None:
            with pd.ExcelWriter(output_path) as writer:
                for each in self.evaluation_result:
                    if each == '逐笔持仓统计' and not signal_record_save:
                        continue
                    self.evaluation_result[each].to_excel(writer, each)
        return self.evaluation_result


