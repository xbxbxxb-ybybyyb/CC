#!/usr/bin/env python
# coding: utf-8
# Author：fengchi863
# Date ：2022/3/8 16:23

import pandas as pd
import numpy as np
from SimiStock.dataApi import tradeDate, getData
from multiprocessing import Pool
from SimiStock.Version1.SimiStockGenerator.util import util
from tqdm import tqdm
from typing import List
import gc
from SimiStock.Version1.config.path_config import *


class SimiBackTest:
    def __init__(self, start_date=20180101, end_date=20211231, hedge_path=None, discount_range: tuple = (0, 1.5)):
        hedge_list = pd.read_pickle(hedge_path)
        shift_start_date = tradeDate.get_pre_trade_date(start_date, 180)
        shift_end_date = tradeDate.get_pre_trade_date(end_date, -130)
        date_list = tradeDate.get_date_range(start_date, end_date)
        shift_date_list = tradeDate.get_date_range(shift_start_date, shift_end_date)

        close_badj = getData.get_daily_1factor('close_badj', date_list=shift_date_list)
        daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=shift_date_list)
        live_days = getData.get_daily_1factor('live_days', date_list=shift_date_list)

        self.hedge_list = hedge_list
        self.date_list = date_list
        self.shift_date_list = shift_date_list
        self.live_days = live_days
        self.close_badj = close_badj
        self.daily_pctchg = daily_pctchg
        self.discount_range = discount_range

    def backtest_one_stock(self, hedge: dict, duration=120, direction='future', hedge_num=None):
        hedge_discount = hedge['discount']
        if hedge_discount <= self.discount_range[0] or hedge_discount >= self.discount_range[1]:
            return [np.nan] * 11

        stk_id = hedge['stk_id']
        trade_date = hedge['date']
        hedge_list = hedge['hedge_list']
        hedge_weight = hedge['hedge_weight']

        if hedge_num is None or hedge_num >= len(self.hedge_list):
            hedge_list = hedge_list
        else:
            hedge_list = hedge_list[:hedge_num]
            hedge_weight = hedge_weight[:hedge_num]

        if direction == 'future':
            start_date = tradeDate.get_pre_trade_date(trade_date, -1)
            end_date = tradeDate.get_pre_trade_date(trade_date, -duration)
        elif direction == 'history':
            start_date = tradeDate.get_pre_trade_date(trade_date, duration)
            end_date = tradeDate.get_pre_trade_date(trade_date, 1)
        else:
            raise Exception('direction must be given correctly')

        # 解决上市周期问题，只统计上市30天的股票
        try:
            if self.live_days.loc[start_date, stk_id] < 30:
                return [np.nan] * 13

            # 统计历史和未来120天的相关性
            history_corr_list = list()
            future_corr_list = list()
            for hedge in hedge_list:
                future_start_date = tradeDate.get_pre_trade_date(trade_date, -1)
                future_end_date = tradeDate.get_pre_trade_date(trade_date, -duration)
                history_start_date = tradeDate.get_pre_trade_date(trade_date, duration)
                history_end_date = tradeDate.get_pre_trade_date(trade_date, 1)
                h_pct = self.daily_pctchg.loc[history_start_date:history_end_date]
                f_pct = self.daily_pctchg.loc[future_start_date:future_end_date]
                tmp1 = h_pct[hedge].corr(h_pct[stk_id])
                tmp2 = f_pct[hedge].corr(f_pct[stk_id])
                history_corr_list.append(tmp1)
                future_corr_list.append(tmp2)

            stk_pctchg = self.daily_pctchg.loc[start_date:end_date][stk_id]

            hedge_pctchg = (self.daily_pctchg.loc[start_date:end_date][hedge_list] * np.array(hedge_weight))
            hedge_pctchg = hedge_pctchg.sum(axis=1)

            """统计指标"""
            corr = np.corrcoef(stk_pctchg, hedge_pctchg)[0, 1]  # 日涨跌幅的相关系数
            daily_tracking_error = (stk_pctchg - hedge_pctchg) / 100  # 每日涨跌幅误差
            tracking_error_mean = np.mean(daily_tracking_error)  # 日均跟踪误差

            # 净值曲线
            weight_sum = sum(hedge_weight)
            hedge_weight = self.weight_pct(hedge_weight)
            hedge_pctchg = self.daily_pctchg.loc[start_date:end_date][hedge_list]
            hedge_net_df = (1 + hedge_pctchg / 100).cumprod()
            hedge_net_value = (hedge_net_df * np.array(hedge_weight)).sum(axis=1)
            stk_net_value = (1 + stk_pctchg / 100).cumprod()

            """此处默认权重总和超过1.1的无效"""
            if weight_sum > 1.1:
                hedge_net_value = hedge_net_value
            else:
                hedge_net_value = hedge_net_value * weight_sum
            long_short_profit = stk_net_value - hedge_net_value
            last_profit = long_short_profit.iloc[-1]
            ann_tracking_error = (1 + last_profit) ** (duration / 242) - 1

            tracking_error_70pct = np.percentile(daily_tracking_error.map(abs), 70)

            # 最大回撤
            max_drawdown = self.maxdrawdown(1 + long_short_profit.values)
            max_profit = np.max(long_short_profit)
            max_draw_profit = max_profit if max_profit > max_drawdown else -max_drawdown

            hf_corr = pd.Series(history_corr_list).corr(pd.Series(future_corr_list))
            hf_rank_corr = pd.Series(history_corr_list).rank().corr(pd.Series(future_corr_list).rank())
            future_corr_num65 = len(list(filter(lambda x: x >= 0.65, future_corr_list)))
            future_corr_num60 = len(list(filter(lambda x: x >= 0.6, future_corr_list)))
            hedge_real_num = len(hedge_list)
        except:
            return [np.nan] * 13

        return [stk_id, trade_date, duration, direction, tracking_error_mean, ann_tracking_error,
                tracking_error_70pct, corr, max_drawdown, max_profit, max_draw_profit,
                hf_corr, hf_rank_corr, future_corr_num65, future_corr_num60, hedge_real_num]

    def backtest_stocks(self, hedge_list: List[dict], duration=120, direction='future', hedge_num=None):
        ret_list = list()
        pbar = tqdm(range(len(hedge_list)))
        for idx in pbar:
            hedge = hedge_list[idx]
            pbar.set_description('并行回测中|%s|%s' % (hedge['stk_id'], hedge['date']))
            ret = self.backtest_one_stock(hedge, duration, direction, hedge_num)
            ret_list.append(ret)
        return ret_list

    def backtest(self, hedge_num=None, duration=120, direction='future', kernal_num=10, mode='serial', save_flag=False,
                 save_path=bt_path, save_name=None, stats_flag=False, stats_save_name=None):

        if save_flag:
            if save_name is None:
                raise Exception('save_name must be given')

        if stats_flag:
            if stats_save_name is None:
                raise Exception('stats_save_name must be given')

        """可以选future或history进行测试"""
        hedge_list = self.hedge_list
        res_list = list()
        if mode is 'serial':
            pbar = tqdm(hedge_list)
            for hedge in pbar:
                pbar.set_description('串行回测中|%s|%s' % (hedge['stk_id'], hedge['date']))
                res = self.backtest_one_stock(hedge, duration, direction, hedge_num)
                res_list.append(res)

        if mode is 'multi':
            ret_dict = util.multiprocess(kernal_num, self.backtest_stocks, hedge_list, duration, direction, hedge_num)

            ret_result = dict()
            for k in ret_dict:
                ret_result[k] = ret_dict[k].get()

            for k in range(kernal_num):
                res_list.extend(ret_result[k])

        res_df = pd.DataFrame(res_list)
        res_df.columns = ['股票代码', '交易日期', '回测周期', '回测方向', '日均跟踪误差均值', '年化跟踪误差',
                          '偏离70%分位数', '相关系数', '最大回撤', '最大收益', '累计最大偏离', '历史未来相关性',
                          '历史未来秩相关性', '大于0.65个数', '大于0.6个数', '总个数']
        res_df = res_df.dropna(axis=0, how='all')
        res_df = res_df.sort_values(['交易日期', '股票代码'])
        res_df = res_df.reset_index(drop=True)

        groupby_columns = ['回测方向', '回测周期']
        summary = pd.DataFrame()
        summary['日均跟踪误差均值'] = res_df.groupby(groupby_columns).apply(lambda x: x['日均跟踪误差均值'].mean())
        summary['年化跟踪误差均值'] = res_df.groupby(groupby_columns).apply(lambda x: x['年化跟踪误差'].mean())
        summary['偏离70%分位数均值'] = res_df.groupby(groupby_columns).apply(lambda x: x['偏离70%分位数'].mean())
        summary['相关系数均值'] = res_df.groupby(groupby_columns).apply(lambda x: x['相关系数'].mean())
        summary['相关系数方差'] = res_df.groupby(groupby_columns).apply(lambda x: x['相关系数'].std())
        summary['最大回撤均值'] = res_df.groupby(groupby_columns).apply(lambda x: x['最大回撤'].mean())
        summary['最大收益均值'] = res_df.groupby(groupby_columns).apply(lambda x: x['最大收益'].mean())
        summary['累计最大偏离均值'] = res_df.groupby(groupby_columns).apply(lambda x: x['累计最大偏离'].mean())
        summary['相关系数大于0.8胜率'] = res_df.groupby(groupby_columns).apply(lambda x: (x['相关系数'] > 0.8).sum() /
                                                                             np.isfinite(x['相关系数']).sum())

        save_dict = {'明细': res_df,
                     '汇总': summary}

        if save_flag:
            util.save_dict2xls(save_dict, save_path, save_name)

        if stats_flag:
            util.stats_hedge_list(hedge_list, stats_save_name)

        del res_list
        gc.collect()

        return res_df

    @staticmethod
    def weight_pct(x):
        return [j / sum(x) for j in x]

    @staticmethod
    def maxdrawdown(arr):
        try:
            i = np.argmax((np.maximum.accumulate(arr) - arr) / np.maximum.accumulate(arr))
            j = np.argmax(arr[:i])
            return 1 - arr[i] / arr[j]
        except:
            return np.nan


if __name__ == '__main__':
    prefix = '日频close相关性_SW2_240'
    duration = 120
    direction = 'future'
    hedge_num = 1
    sbt = SimiBackTest(20180101, 20200631, hedge_path + f'{prefix}_result.pkl')
    bt_df = sbt.backtest(duration=duration, hedge_num=hedge_num, direction=direction, mode='serial', kernal_num=12,
                         save_flag=True, save_name=f'{prefix}_{duration}_{direction}_{hedge_num}_bt_result.xlsx')


