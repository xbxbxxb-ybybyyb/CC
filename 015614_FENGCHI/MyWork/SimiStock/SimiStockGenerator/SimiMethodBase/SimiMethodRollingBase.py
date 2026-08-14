# coding: utf-8
# Author：fengchi863
# Date ：2022/3/7 17:42

from dataApi import getData
from abc import abstractmethod
from typing import List
import pandas as pd
import numpy as np
import sys
import traceback
from SimiStock.config.path_config import *
from tqdm import tqdm
from SimiStock.dataApi import getData, tradeDate
from SimiStock.SimiStockGenerator.util import util


class SimiMethodRollingBase:
    def __init__(self, start_date=20180101, end_date=20210631, concept='SW1', discount=95,
                 history_future_len=(120, 5), pre_calc_days_num=2):
        if type(discount) is int:
            block_data = pd.read_pickle(data_path + f'block_data_{discount}.pkl')
        elif discount == 'raw':
            block_data = pd.read_pickle(data_path + f'raw_block_data.pkl')
        rong_df = pd.read_pickle(data_path + '2rong.pkl')
        clean_stock = pd.read_pickle(data_path + 'clean_stock.pkl')
        shift_start_date = tradeDate.get_pre_trade_date(start_date, 260)
        shift_end_date = tradeDate.get_pre_trade_date(end_date, -(120 - history_future_len[1]))
        date_list = tradeDate.get_date_range(start_date, end_date)
        shift_date_list = tradeDate.get_date_range(shift_start_date, shift_end_date)

        self.date_list = date_list
        self.shift_date_list = shift_date_list
        self.start_date = start_date
        self.end_date = end_date

        self.block_data = block_data.query(f'{start_date} <= 交易日期 <= {end_date}')
        self.rong_df = rong_df
        concept_df = self.get_concept_df(concept=concept)
        self.concept_df = concept_df
        self.clean_stock = clean_stock

        """param"""
        self.history_period = history_future_len[0]
        self.future_period = history_future_len[1]
        self.pre_calc_days_num = pre_calc_days_num

    def get_concept_df(self, concept='SW1'):
        if concept in ['SW1', 'SW2', 'SW3', 'CITICS1', 'CITICS2', 'CITICS3', 'SW20211']:
            df = getData.get_daily_1factor(concept, date_list=self.shift_date_list)
            if concept is 'SW20211':
                df = df.bfill()
            return df
        elif concept is 'allMarket':
            df = getData.get_daily_1factor('SW1', date_list=self.shift_date_list)
            df[~np.isnan(df)] = 1
            return df
        else:
            raise Exception('concept is not given correctly')

    def get_concept_list(self, stk_id, trade_date):
        row = self.concept_df.loc[trade_date]
        ind_code = row[stk_id]
        stk_list = row[row == ind_code].index.tolist()
        rong_row = self.rong_df.loc[trade_date]
        rong_list = rong_row[rong_row == 1].index.tolist()
        stk_list = list(set(stk_list).intersection(set(rong_list)))
        clean_row = self.clean_stock.loc[trade_date]
        clean_list = clean_row[clean_row == 1].index.tolist()
        stk_list = list(set(stk_list).intersection(set(clean_list)))
        if stk_id in stk_list:
            stk_list.remove(stk_id)
        return stk_list

    def get_simi_stock(self, stk_id, trade_date):
        date_tuple_list = self.get_rolling_date(trade_date)
        hedge_list = self.simi_strategy(stk_id, date_tuple_list)
        discount = self.block_data.query(f'股票代码 == {stk_id} & 交易日期 == {trade_date}')['折价比例'].values[0]
        return {'stk_id': int(stk_id),
                'date': int(trade_date),
                'discount': discount,
                'hedge_list': hedge_list,
                'param': {'history_future_len': (self.history_period, self.future_period)}}

    def get_rolling_date(self, trade_date, direction='future'):
        date_tuple_list = list()
        if direction is 'future':
            stop_date = tradeDate.get_pre_trade_date(trade_date, -120)   # 这个120是必须的，大宗持有120天
            start_date = trade_date
            calc_date = tradeDate.get_pre_trade_date(start_date, self.pre_calc_days_num)
            end_date = tradeDate.get_pre_trade_date(start_date, -self.future_period)
            train_start_date = tradeDate.get_pre_trade_date(calc_date, self.history_period)
            train_end_date = tradeDate.get_pre_trade_date(calc_date, 1)
            date_tuple_list.append((calc_date, start_date, end_date, train_start_date, train_end_date))
            while end_date < stop_date:
                start_date = end_date
                calc_date = tradeDate.get_pre_trade_date(start_date, self.pre_calc_days_num)
                end_date = tradeDate.get_pre_trade_date(start_date, -self.future_period)
                if end_date >= stop_date:
                    end_date = stop_date
                train_start_date = tradeDate.get_pre_trade_date(calc_date, self.history_period)
                train_end_date = tradeDate.get_pre_trade_date(calc_date, 1)
                date_tuple_list.append((calc_date, start_date, end_date, train_start_date, train_end_date))
        return date_tuple_list

    def get_simi_stocks(self, stk_date_list: List[tuple]):
        ret_list = list()
        pbar = tqdm(range(len(stk_date_list)))
        for idx in pbar:
            stk_id, trade_date = stk_date_list[idx]
            pbar.set_description('并行生成中|%s|%s' % (int(stk_id), int(trade_date)))
            hedge = self.get_simi_stock(stk_id, trade_date)
            ret_list.append(hedge)
        return ret_list

    @abstractmethod
    def simi_strategy(self, stk_id: int, date_tuple_list: List[tuple]):
        """
        寻找相似度高的个股的抽象函数
        :param stk_id: 大宗交易的股票代码
        :param date_tuple_list: 日期序列
        :return: 返回经过排序后的相似度个股列表以及每个股票所配权重
        """
        pass

    def get_hedge_list(self, kernal_num=10, mode='serial'):
        ret_list = []
        if mode is 'serial':
            pbar = tqdm(range(len(self.block_data)))
            for idx in pbar:
                row = self.block_data.iloc[idx]
                stk_id = row['股票代码']
                trade_date = row['交易日期']
                pbar.set_description('串行生成中|%s|%s' % (int(stk_id), int(trade_date)))
                ret_list.append(self.get_simi_stock(stk_id, trade_date))

        if mode is 'multi':
            stk_date_list = list(zip(self.block_data['股票代码'].tolist(), self.block_data['交易日期'].tolist()))
            try:
                ret_dict = util.multiprocess(kernal_num, self.get_simi_stocks, stk_date_list)
            except:
                error_type, error_value, error_trace = sys.exc_info()
                error = [error_type, error_value, error_trace]
                util.save_list2pkl(error, hedge_path + 'error_log.pkl')

            ret_result = dict()
            for k in ret_dict:
                try:
                    ret_result[k] = ret_dict[k].get()
                except Exception as e:
                    print('多进程内部出错')
                    print(e)

            for k in ret_result:
                ret_list.extend(ret_result[k])

        # 剔除没有找到对冲标的的历史样本
        _ret_list = ret_list.copy()
        for hedge in _ret_list:
            if not hedge['hedge_list']:
                ret_list.remove(hedge)

        return ret_list


if __name__ == '__main__':
    smb = SimiMethodRollingBase(concept='SW1')
    # check = smb.get_simi_stock(1, 20200103)
    check = smb.get_hedge_list()
    # check = smb.get_rolling_date(20201015)
