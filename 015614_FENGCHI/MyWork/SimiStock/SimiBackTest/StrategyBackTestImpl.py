# coding: utf-8
# Author：fengchi863
# Date ：2022/5/16 17:24

import pandas as pd
import time
import os
from SimiStock.SimiBackTest.StrategeBackTestBase import StrategyBackTestBase
from SimiStock.SimiBackTest.StrategyEvaluation import StrategyEvaluation
from SimiStock.config.path_config import *
from ShortTermTrading.conf.path_conf import junk_path
import numpy as np


class StockStrategyImpl(StrategyBackTestBase):
    def __init__(self, stk_id, start_date, end_date, price_rolling_window=5, amt_per_signal=10000000,
                 available_flag=None, isin_pool_flag=None):
        super().__init__(stk_id, start_date, end_date, price_rolling_window, amt_per_signal, available_flag, isin_pool_flag)

        hedge_list = pd.read_pickle(hedge_path + '整体_相似度版本对冲池.pkl')
        # columns = ['stk_id', 'trade_date', 'datetime', 'father_date', 'weight', 'prediction']
        signal_df = pd.DataFrame()
        for _hedge in hedge_list[:1]:
            stk_id = _hedge['stk_id']
            trade_date = _hedge['date']
            signal_df = signal_df.append([[stk_id, trade_date, 145700, np.nan, np.nan, '多开']])
            _hedge_list = _hedge['hedge_list']
            if len(_hedge_list[0]['hedge_list']) > 3:
                for idx, tmp_hedge in enumerate(_hedge_list[:3]):
                    start_ = tmp_hedge['start_date']
                    end_ = tmp_hedge['end_date']
                    signal_df = signal_df.append([[tmp_hedge['hedge_list'][idx], start_, 145700,
                                                   f'{stk_id}_{trade_date}', tmp_hedge['hedge_value'][idx], '空开']])
                    signal_df = signal_df.append([[tmp_hedge['hedge_list'][idx], end_, 145700, f'{stk_id}_{trade_date}',
                                                   tmp_hedge['hedge_value'][idx], '空平']])
            signal_df = signal_df.append([[stk_id, trade_date, 145700, np.nan, np.nan, '多平']])
        signal_df.columns = ['stk_id', 'trade_date', 'datetime', 'father_date', 'weight', 'prediction']
        self.signal_df = signal_df

    def daily_update(self):
        pass

    def bar_handler(self):
        signal = self.signal_df.query(f'stk_id == {self.stk_id} & trade_date == {self.trade_date}')['prediction']
        if signal is '多开':
            self.buy_action(vol=100, direction='Long')
        if signal is '多平' and self.position['available'] == 0:
            self.sell_action(vol=100, direction='Long')
        if signal is '空开':
            self.buy_action(vol=100, direction='Short')
        if signal is '空平' and self.position['available'] == 0:
            self.sell_action(vol=100, direction='Short')


if __name__ == '__main__':
    hedge_list = pd.read_pickle(hedge_path + '整体_相似度版本对冲池.pkl')
    # columns = ['stk_id', 'trade_date', 'datetime', 'father_date', 'weight', 'prediction']
    # signal_df = pd.DataFrame()
    # for _hedge in hedge_list[:1]:
    #     stk_id = _hedge['stk_id']
    #     trade_date = _hedge['date']
    #     signal_df = signal_df.append([[stk_id, trade_date, 145700, np.nan, np.nan, '多开']])
    #     _hedge_list = _hedge['hedge_list']
    #     if len(_hedge_list[0]['hedge_list']) > 3:
    #         for idx, tmp_hedge in enumerate(_hedge_list[:3]):
    #             start_ = tmp_hedge['start_date']
    #             end_ = tmp_hedge['end_date']
    #             signal_df = signal_df.append([[tmp_hedge['hedge_list'][idx], start_, 145700, f'{stk_id}_{trade_date}', tmp_hedge['hedge_value'][idx], '空开']])
    #             signal_df = signal_df.append([[tmp_hedge['hedge_list'][idx], end_, 145700, f'{stk_id}_{trade_date}', tmp_hedge['hedge_value'][idx], '空平']])
    #     signal_df = signal_df.append([[stk_id, trade_date, 145700, np.nan, np.nan, '多平']])
    # signal_df.columns = ['stk_id', 'trade_date', 'datetime', 'father_date', 'weight', 'prediction']

    start_date = 20210101
    end_date = 20211231
    universe_stk_list = list(set(signal_df['stk_id'].tolist()))

    strats = StrategyEvaluation(StockStrategyImpl, universe_info=universe_stk_list)
    e = time.time()
    strats.serial_run(universe_stk_list, start_date, end_date)
    print('strategy time:', time.time()-e)