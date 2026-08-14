# coding: utf-8
# Author：fengchi863
# Date ：2022/7/2 18:56

from dataApi.tradeDate import get_today
from dataApi import stockList
from xquant.factordata import FactorData


class StockUtil:
    def __init__(self):
        self.stock_name_dict = None

    @staticmethod
    def get_stock_name_dict():
        today_date = get_today()
        fd = FactorData()
        df = fd.get_factor_value('Basic_factor', mddate=['%s' % today_date], factor_names=['short_name'])
        stock_name_dict = df['short_name'].to_dict()
        return stock_name_dict

    def get_1stock_name(self, stk_code):
        if type(stk_code) == int:
            stk_code = stockList.trans_int2windcode(stk_code)
        if not self.stock_name_dict:
            self.stock_name_dict = self.get_stock_name_dict()
        try:
            return self.stock_name_dict[stk_code]
        except:
            return stk_code

StockUtil = StockUtil()