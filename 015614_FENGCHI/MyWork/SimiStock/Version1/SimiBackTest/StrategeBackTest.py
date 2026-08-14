# coding: utf-8
# Author：fengchi863
# Date ：2022/4/15 15:03
from abc import abstractmethod


class StrategyBackTest:
    def __init__(self, stk_id, start_date, end_date, per_amt=5000000, available_flag=None,
                 isin_pool_flag=None):
        pass

    @abstractmethod
    def daily_update(self):
        pass

    @abstractmethod
    def bar_handler(self):
        pass

    def istradable(self):
        pass

    def isinpool(self):
        pass

    def __daily_update(self):
        pass

