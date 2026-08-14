# coding: utf-8
# Author：fengchi863
# Date ：2022/5/16 17:41

import datetime
from multiprocessing import Pool, Manager

import pandas as pd
import numpy as np
from tqdm import tqdm
import gc
from SimiStock.dataApi import getData, tradeDate
from SimiStock.dataApi.tradeDate import trade_minutes, get_trade_date_interval
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *


class StrategyEvaluation:
    def __init__(self, Cls, buy_cost_ratio=0.0005, sell_cost_ratio=0.001, price_rolling_window=10,
                 amt_per_signal=5000000, available_info=None, universe_info=None):
        self.stock_strategy = Cls
        self.record = Manager().dict()
        self.buy_cost = buy_cost_ratio
        self.sell_cost = sell_cost_ratio
        self.evaluation_result = dict()
        self.available_info = available_info
        self.universe_info = universe_info
        self.price_rolling_window = price_rolling_window
        self.amt_per_signal = amt_per_signal

    def backtest_1stock(self, stk_id, start_date, end_date, **append_para):
        para = append_para.copy()
        para['stk_id'] = stk_id
        para['start_date'] = start_date
        para['end_date'] = end_date
        if isinstance(self.available_info, pd.DataFrame):
            if stk_id in self.available_info.columns:
                para['available_flag'] = self.available_info[stk_id]
        if isinstance(self.universe_info, pd.DataFrame):
            if stk_id in self.universe_info.columns:
                para['isin_pool_flag'] = self.universe_info[stk_id]
            else:
                return True
        strat = self.stock_strategy(**para)
        record = strat.backtest()
        self.record[stk_id] = pd.DataFrame(record, columns=['date', 'time', 'flag', 'vol', 'deal_price', 'holding',
                                                            'available']).set_index(['date', 'time'])
        del record, strat
        return True

    def wrapper(self, stk_id, start, end, **append_para):
        if self.backtest_1stock(stk_id, start, end, **append_para):
            return True
        else:
            return False

    def multi_run(self, stk_list, start_date, end_date, kernel=10, **append_para):
        pbar = tqdm(total=len(stk_list))

        def update(*param):
            pbar.update()
            _stk_id = stk_list[pbar.last_print_n - 1]
            dt_now = datetime.datetime.now().strftime('%H:%M:%S')
            pbar.set_description('并行回测中|%s|%s' % (str(_stk_id), dt_now))
            if pbar.last_print_n == len(stk_list):
                pbar.close()

        pool = Pool(kernel)
        result = {}
        for stk_id in stk_list:
            # 这里这个参数真是要尝试啊，为啥加个括号呢？？
            # result[stk_id] = pool.apply_async(self.wrapper, (*(stk_id, start_date, end_date, *append_para),), callback=update) # 正确，可通过
            # result[stk_id] = pool.apply_async(self.wrapper, (stk_id, start_date, end_date, *append_para,), callback=update) # 正确，可通过代码检查，但实际字典没传进去
            # result[stk_id] = pool.apply_async(self.wrapper, (stk_id, start_date, end_date, **append_para,), callback=update)  # 错误用法
            result[stk_id] = pool.apply_async(self.wrapper,
                                              args=(stk_id, start_date, end_date,),
                                              kwds=append_para,
                                              callback=update)  # 正确，可通过
        pool.close()
        pool.join()

    def serial_run(self, stk_list, start_date, end_date, **append_para):
        pbar = tqdm(stk_list)
        for stk_id in pbar:
            dt_now = datetime.datetime.now().strftime('%H:%M:%S')
            pbar.set_description('串行回测中|%s|%s' % (str(stk_id), dt_now))
            self.backtest_1stock(stk_id, start_date, end_date, **append_para)

    def start_backtest(self, stk_list, start_date, end_date, filename=None, kernel=10, mode='multi', **append_para):
        if mode is 'multi':
            self.multi_run(stk_list, start_date, end_date, kernel, **append_para)
        elif mode == 'serial':
            self.serial_run(stk_list, start_date, end_date, **append_para)
        elif mode == 'debug':
            pass
        else:
            raise Exception('mode is not given correctly')
        self.evaluation_result['每日持仓统计'], self.evaluation_result['持仓综合统计'] = self.evaluate_daily(kernel)
        self.evaluation_result['逐笔持仓统计'], self.evaluation_result['逐笔持仓综合统计'] = self.evaluate_by_signal(kernel)
        util.save_dict2xls(self.evaluation_result, bt_path, filename)
        util.send_file(bt_path, filename)
        return self.evaluation_result

    """以下均为统计部分"""

    def evaluate_signal_by_stk(self, stk_id):
        if self.record[stk_id] is None:
            print(stk_id, '找不到该记录')
            return []
        record = self.record[stk_id].copy()
        record = record[~record['flag'].isin(['H', 'D'])].reset_index()
        record['cashflow'] = -1 * record['vol'] * record['deal_price']
        used_cash = 0
        profit = 0
        signal_res = []
        holdind_start_dt = tuple()
        buy_times, sell_times = 0, 0
        for date, bar, flag, vol, deal_price, holding, available, cashflow in list(record.values):
            if flag == 'B':
                buy_times += 1
            if flag == 'S':
                sell_times += 1
            if used_cash == 0:
                if cashflow > 0:
                    raise Exception('Wrong cash flow direction')
                used_cash = 0
                holdind_start_dt = (date, bar)
            profit += cashflow
            if cashflow < 0:  # 买入
                used_cash += -1 * cashflow
                profit -= self.buy_cost * abs(cashflow)
            if cashflow > 0:  # 卖出
                profit -= self.sell_cost * abs(cashflow)
            if holding == 0:
                holding_minutes = 240 * get_trade_date_interval(date, holdind_start_dt[0]) + (
                        240 - trade_minutes.index(holdind_start_dt[1])) + (trade_minutes.index(bar) - 1)
                signal_res.append(
                    [holdind_start_dt[0] * 10000 + holdind_start_dt[1], date * 10000 + bar, profit, used_cash,
                     holding_minutes, buy_times, sell_times, stk_id])
                used_cash = 0
                profit = 0
                buy_times, sell_times = 0, 0
        return signal_res

    def evaluate_stk_by_day(self, stk_id):

        if self.record[stk_id] is None:
            print(stk_id, '找不到该记录')
            return pd.DataFrame()
        record = self.record[stk_id].copy()
        holding_info = record[record['flag'].eq('H')]
        holding_info = holding_info.rename(columns={'vol': 'close_padj', 'deal_price': 'close'})
        holding_info = holding_info.reset_index().set_index('date')

        buy_info = record[record['flag'].eq('B')].reset_index()
        # 下一行好像不用使用，暂时注释掉
        # buy_info = pd.merge(buy_info, holding_info[['close']].reset_index(), how='left', on=['date'])

        sell_info = record[record['flag'].eq('S')].reset_index()
        # 下一行好像不用使用，暂时注释掉
        # sell_info = pd.merge(sell_info, holding_info[['close_padj']].shift(1).reset_index(), how='left', on=['date'])

        trade_info = record[record['flag'].isin(['B', 'S'])]
        trade_info['净买入'] = trade_info['vol'].values * trade_info['deal_price'].values

        mapdict = {'B': 1 + self.buy_cost, 'S': 1 - self.sell_cost}
        trade_info['flag'] = [mapdict[x] for x in trade_info['flag']]
        trade_info['扣费后净买入'] = trade_info['净买入'].values * trade_info['flag'].values
        trade_info = trade_info.reset_index()
        if len(trade_info) == 0:
            return pd.DataFrame()

        twap = getData.get_daily_1stock(stk_id, ['twap'],
                                        date_list=sorted(list(set(trade_info['date'].tolist())))).reset_index()
        trade_info = pd.merge(trade_info, twap, how='left', on=['date'])
        trade_info['择时收益'] = (trade_info['twap'].values - trade_info['deal_price'].values) * trade_info['vol'].values

        res = trade_info[['date', '净买入', '扣费后净买入', '择时收益']].groupby('date').sum()
        res = pd.concat([res, pd.DataFrame(holding_info['holding'].values * holding_info['close'].values,
                                           index=holding_info.index, columns=['收盘持仓市值'])], axis=1)
        res['买入操作次数'] = buy_info.groupby('date').size()
        res['卖出操作次数'] = sell_info.groupby('date').size()
        return res

    def evaluate_by_signal(self, kernal=10):
        eval_signal_record = list()
        stk_list = list(self.record.keys())
        pbar = tqdm(stk_list)

        def update(*param):
            pbar.update()
            _stk_id = stk_list[pbar.last_print_n - 1]
            dt_now = datetime.datetime.now().strftime('%H:%M:%S')
            pbar.set_description(
                '按信号评估中 |%s|%s' % (str(_stk_id), dt_now))
            if pbar.last_print_n == len(stk_list):
                pbar.close()

        pool_dict = {}
        pool = Pool(kernal)
        for stk in pbar:
            pool_dict[stk] = pool.apply_async(self.evaluate_signal_by_stk, (stk,), callback=update)
        pool.close()
        pool.join()

        for stk in pool_dict:
            try:
                eval_signal_record = eval_signal_record + pool_dict[stk].get()
            except:
                print(stk, 'eval Wrong')
                self.evaluate_signal_by_stk(stk)
        pool_dict.clear()
        del pool, pool_dict
        gc.collect()
        eval_signal_record = pd.DataFrame(eval_signal_record,
                                          columns=['start', 'end', 'profit', 'used_cash', 'holding_minutes',
                                                   'buy_times', 'sell_times', 'stk_id'])
        if len(eval_signal_record) == 0:
            return pd.DataFrame(), eval_signal_record
        eval_signal_record['收益率'] = eval_signal_record['profit'] / eval_signal_record['used_cash']
        eval_signal_record['平均每分钟收益率'] = eval_signal_record['收益率'] / eval_signal_record['holding_minutes']
        eval_signal_record['胜率'] = (eval_signal_record['收益率'] > 0) * 1
        eval_signal_record['end_year'] = eval_signal_record['end'] // 100000000

        # 整体统计
        eval_signal_result = eval_signal_record[['holding_minutes']].mean()
        eval_signal_record['收益率*buy_times'] = (eval_signal_record['收益率'] * eval_signal_record['buy_times'])
        eval_signal_record['平均每分钟收益率*buy_times'] = (eval_signal_record['平均每分钟收益率'] * eval_signal_record['buy_times'])
        eval_signal_record['胜*buy_times'] = eval_signal_record['胜率'] * eval_signal_record['buy_times']
        eval_signal_result['收益率'] = eval_signal_record['收益率*buy_times'].sum() / eval_signal_record['buy_times'].sum()
        eval_signal_result['平均每分钟收益率'] = eval_signal_record['平均每分钟收益率*buy_times'].sum() / eval_signal_record[
            'buy_times'].sum()
        eval_signal_result['胜率'] = eval_signal_record['胜*buy_times'].sum() / eval_signal_record['buy_times'].sum()

        win_part = eval_signal_record[eval_signal_record['收益率'] > 0][['收益率*buy_times', 'buy_times']].sum()
        lose_part = eval_signal_record[eval_signal_record['收益率'] < 0][['收益率*buy_times', 'buy_times']].sum()
        eval_signal_result['盈利交易收益均值'] = win_part['收益率*buy_times'] / win_part['buy_times']
        eval_signal_result['亏损交易收益均值'] = lose_part['收益率*buy_times'] / lose_part['buy_times']
        eval_signal_result['盈亏比(收益率)'] = -1 * eval_signal_result['盈利交易收益均值'] / eval_signal_result['亏损交易收益均值']
        del win_part, lose_part

        win_part = eval_signal_record[eval_signal_record['平均每分钟收益率'] > 0][['平均每分钟收益率*buy_times', 'buy_times']].sum()
        lose_part = eval_signal_record[eval_signal_record['平均每分钟收益率'] < 0][['平均每分钟收益率*buy_times', 'buy_times']].sum()
        eval_signal_result['盈利交易平均每分钟收益均值'] = win_part['平均每分钟收益率*buy_times'] / win_part['buy_times']
        eval_signal_result['亏损交易平均每分钟收益均值'] = lose_part['平均每分钟收益率*buy_times'] / lose_part['buy_times']
        eval_signal_result['盈亏比(平均每分钟收益率)'] = -1 * eval_signal_result['盈利交易平均每分钟收益均值'] / eval_signal_result[
            '亏损交易平均每分钟收益均值']
        del win_part, lose_part

        # 双边交易次数
        eval_signal_result['交易次数'] = eval_signal_record[['buy_times', 'sell_times']].sum().sum()

        # 分年统计
        yearly_temp_count = eval_signal_record[
            ['收益率*buy_times', '平均每分钟收益率*buy_times', '胜*buy_times', 'buy_times', 'end_year']].groupby('end_year').sum()
        yearly_eval_signal_result = (yearly_temp_count.T / yearly_temp_count['buy_times']).T.rename(
            columns={'收益率*buy_times': '收益率',
                     '平均每分钟收益率*buy_times': '平均每分钟收益率',
                     '胜*buy_times': '胜率'}).drop('buy_times', axis=1)
        del yearly_temp_count

        yearly_eval_signal_result['holding_minutes'] = \
            eval_signal_record[['holding_minutes', 'end_year']].groupby('end_year').mean()['holding_minutes']
        win_part = eval_signal_record[eval_signal_record['收益率'] > 0][
            ['收益率*buy_times', '平均每分钟收益率*buy_times', 'buy_times', 'end_year']].groupby('end_year').sum()
        lose_part = eval_signal_record[eval_signal_record['收益率'] < 0][
            ['收益率*buy_times', '平均每分钟收益率*buy_times', 'buy_times', 'end_year']].groupby('end_year').sum()
        win_part = (win_part.T / win_part['buy_times']).T.drop('buy_times', axis=1)
        lose_part = (lose_part.T / lose_part['buy_times']).T.drop('buy_times', axis=1)
        win_loss_rate = -1 * (win_part / lose_part)

        yearly_eval_signal_result = pd.concat([yearly_eval_signal_result,
                                               win_part.rename(columns={'收益率*buy_times': '盈利交易收益均值',
                                                                        '平均每分钟收益率*buy_times': '盈利交易平均每分钟收益均值'}),
                                               lose_part.rename(columns={'收益率*buy_times': '亏损交易收益均值',
                                                                         '平均每分钟收益率*buy_times': '亏损交易平均每分钟收益均值'}),
                                               win_loss_rate.rename(columns={'收益率*buy_times': '盈亏比(收益率)',
                                                                             '平均每分钟收益率*buy_times': '盈亏比(平均每分钟收益率)'})],
                                              axis=1)

        trade_times = eval_signal_record[['buy_times', 'sell_times', 'end_year']].groupby('end_year').sum()
        yearly_eval_signal_result['交易次数'] = trade_times.sum(axis=1)
        yearly_eval_signal_result = yearly_eval_signal_result.T

        yearly_eval_signal_result['全时段'] = eval_signal_result

        eval_signal_record['start'] = eval_signal_record['start'].astype(str)
        eval_signal_record['end'] = eval_signal_record['end'].astype(str)

        eval_signal_record = eval_signal_record.drop(['胜率', 'end_year'], axis=1).rename({'buy_times': '买入操作次数', 'sell_times': '卖出操作次数'})
        yearly_eval_signal_result = yearly_eval_signal_result.rename(index={'holding_minutes': '平均持仓时间'})

        return eval_signal_record, yearly_eval_signal_result

    def evaluate_daily(self, kernel=10):
        daily_result = dict()
        stk_list = list(self.record.keys())
        pbar = tqdm(total=len(stk_list))

        def update(*param):
            pbar.update()
            _stk_id = stk_list[pbar.last_print_n - 1]
            dt_now = datetime.datetime.now().strftime('%H:%M:%S')
            pbar.set_description('按日评估中 |%s|%s' % (str(_stk_id), dt_now))
            if pbar.last_print_n == len(stk_list):
                pbar.close()

        self.pool_dict = Manager().dict()
        pool = Pool(kernel)
        for i in range(len(stk_list)):
            stk_id = stk_list[i]
            daily_result[stk_id] = pool.apply_async(self.evaluate_stk_by_day, (stk_id,), callback=update)
        pool.close()
        pool.join()

        if len(daily_result) == 0:
            return pd.DataFrame(), pd.DataFrame()

        for k in daily_result:
            try:
                daily_result[k] = daily_result[k].get()
            except:
                daily_result[k] = self.evaluate_stk_by_day(k)
        res_pn = pd.Panel(daily_result)

        if 0 in res_pn.shape:
            return pd.DataFrame(), pd.DataFrame()
        daily_info = res_pn.sum(axis='items')

        daily_info['买入股票数'] = res_pn.loc[:, :, '买入操作次数'].replace(0, np.nan).count(axis=1)
        daily_info['卖出股票数'] = res_pn.loc[:, :, '卖出操作次数'].replace(0, np.nan).count(axis=1)

        daily_info['占用资金'] = daily_info['收盘持仓市值'].shift(1).fillna(0) + np.fmax(daily_info['净买入'], 0)
        daily_info['当日收益'] = daily_info['收盘持仓市值'].diff() - daily_info['扣费后净买入']
        if len(daily_info) > 0:
            daily_info.at[daily_info.index[0], '当日收益'] = daily_info['收盘持仓市值'].tolist()[0] - daily_info['扣费后净买入'].tolist()[0]
        daily_info['当日收益率'] = daily_info['当日收益'] / daily_info['占用资金']
        daily_info['择时收益率'] = daily_info['择时收益'] / daily_info['占用资金']
        # 这一行为了调换列的顺序
        daily_info = pd.concat([daily_info.drop(['择时收益', '择时收益率'], axis=1), daily_info[['择时收益', '择时收益率']]], axis=1)
        daily_info['累积收益'] = daily_info['当日收益'].cumsum()
        daily_info['累积收益率'] = daily_info['当日收益率'].cumsum()

        daily_info['benchmark'] = getData.get_daily_1factor('close', date_list=daily_info.index.tolist(), code_list=['ZZ500'], type='bench')['ZZ500']
        daily_info['benchmark_pct_change'] = daily_info['benchmark'].pct_change()
        daily_info['基准收益比'] = daily_info['当日收益率'] / daily_info['benchmark_pct_change']

        daily_info['year'] = daily_info.index // 10000
        daily_info = daily_info[~np.isnan(daily_info['累积收益率'])]

        yearly_stat = dict()
        for year in sorted(list(set(daily_info['year']))) + ['全时段']:
            if year == '全时段':
                temp_info = daily_info
            else:
                temp_info = daily_info[daily_info['year'] == year]
            temp_stat = pd.Series()
            temp_stat['相对基准收益收益比(涨)'] = temp_info[temp_info['benchmark_pct_change'] > 0]['基准收益比'].mean()
            temp_stat['相对基准收益收益比(跌)'] = temp_info[temp_info['benchmark_pct_change'] < 0]['基准收益比'].mean()
            temp_stat['相对基准收益盈亏比'] = -1 * temp_info[temp_info['benchmark_pct_change'] > 0]['基准收益比'].mean() / temp_info[temp_info['benchmark_pct_change'] < 0]['基准收益比'].mean()
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

        date_list = tradeDate.get_date_range(daily_info.index[0], daily_info.index[-1])
        daily_info = daily_info.reindex(date_list)
        daily_info[['收盘持仓市值', '累积收益', '累积收益率']] = daily_info[['收盘持仓市值', '累积收益', '累积收益率']].fillna(method='pad')
        daily_info['占用资金'] = daily_info['收盘持仓市值'].shift(1).fillna(0) + np.fmax(daily_info['净买入'].fillna(0), 0)
        daily_info = daily_info.fillna(0)
        daily_info.index = daily_info.index.astype(str)
        daily_info = daily_info.drop(['benchmark', 'benchmark_pct_change', '基准收益比', 'year'], axis=1)
        return daily_info, yearly_stat