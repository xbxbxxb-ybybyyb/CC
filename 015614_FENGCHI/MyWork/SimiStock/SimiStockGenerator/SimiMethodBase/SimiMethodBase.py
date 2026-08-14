# coding: utf-8
# Author：fengchi863
# Date ：2022/3/7 17:42

"""
没有调仓对冲参数的版本暂时废弃
"""

from dataApi import getData
from abc import abstractmethod
from typing import List
import pandas as pd
import numpy as np
from SimiStock.config.path_config import *
from tqdm import tqdm
from SimiStock.dataApi import getData, tradeDate
from SimiStock.SimiStockGenerator.util import util


class SimiMethodBase:
    def __init__(self, start_date=20180101, end_date=20210631, concept='SW1', discount=95):
        block_data = pd.read_pickle(data_path + f'block_data_{discount}.pkl')
        rong_df = pd.read_pickle(data_path + '2rong.pkl')
        clean_stock = pd.read_pickle(data_path + 'clean_stock.pkl')
        shift_start_date = tradeDate.get_pre_trade_date(start_date, 260)
        shift_end_date = tradeDate.get_pre_trade_date(end_date, 0)
        date_list = tradeDate.get_date_range(start_date, end_date)
        shift_date_list = tradeDate.get_date_range(shift_start_date, shift_end_date)

        self.date_list = date_list
        self.shift_date_list = shift_date_list

        self.block_data = block_data.query(f'{start_date} <= 交易日期 <= {end_date}')
        self.rong_df = rong_df
        concept_df = self.get_concept_df(concept=concept)
        self.concept_df = concept_df
        self.clean_stock = clean_stock

    def get_concept_df(self, concept='SW1'):
        if concept in ['SW1', 'SW2', 'SW3', 'CITICS1', 'CITICS2', 'CITICS3']:
            # df = getData.get_daily_1factor(concept, date_list=self.date_list)
            """测试2021年以后申万一级行业"""
            df = getData.get_daily_1factor('SW20211', date_list=self.date_list)
            df = df.bfill()
            return df
        elif concept is 'allMarket':
            df = getData.get_daily_1factor('SW1', date_list=self.date_list)
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
        stk_list, stk_weight, stk_value = self.simi_strategy(stk_id, trade_date, self.get_concept_list(stk_id, trade_date))
        discount = self.block_data.query(f'股票代码 == {stk_id} & 交易日期 == {trade_date}')['折价比例'].values[0]
        return {'stk_id': int(stk_id),
                'date': int(trade_date),
                'discount': discount,
                'hedge_list': stk_list,
                'hedge_weight': stk_weight,
                'hedge_value': stk_value}

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
    def simi_strategy(self, stk_id: int, trade_date: int, concept_list: List[int]):
        """
        寻找相似度高的个股的抽象函数
        :param stk_id: 大宗交易的股票代码
        :param trade_date: 大宗交易的日期
        :param concept_list: 个股所处板块或概念内的其他个股
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
            ret_dict = util.multiprocess(kernal_num, self.get_simi_stocks, stk_date_list)

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
    smb = SimiMethodBase(concept='SW1', start_date=20210101, end_date=20210930)
    # check = smb.get_simi_stock(1, 20200103)
    check = smb.get_hedge_list()
