# coding: utf-8
# Author：fengchi863
# Date ：2021/5/28 9:28

from xquant.factordata import FactorData
from FaaMonitor.Util.DtUtil import DtUtil
from FaaMonitor.dataApi import stockList

class MyUtil:
    def __init__(self):
        stock_name_dict = self.get_stock_name_dict()

        self.stock_name_dict = stock_name_dict

    def get_tip_str(self, stk: list or int):
        if type(stk) == int:
            wincode = stockList.trans_int2windcode(stk)
            ret = wincode + ',' + self.stock_name_dict[wincode]
            return ret
        elif type(stk) == str:
            ret = stk + ',' + self.stock_name_dict[stk]
            return ret
        elif type(stk) == list:
            ret = list()
            for s in stk:
                wincode = stockList.trans_int2windcode(s)
                ret.append(wincode + ',' + self.stock_name_dict[wincode])
            ret = '；'.join(ret)
            return ret

    @staticmethod
    def get_stock_name_dict():
        today_date = DtUtil.get_today_date()
        fd = FactorData()
        df = fd.get_factor_value('Basic_factor', mddate=['%s' % today_date], factor_names=['short_name'])
        stock_name_dict = df['short_name'].to_dict()
        return stock_name_dict

    def get_1stock_name(self, stk_code):
        if type(stk_code) == int:
            stk_code = stockList.trans_int2windcode(stk_code)
        try:
            return self.stock_name_dict[stk_code]
        except:
            return stk_code

MyUtil = MyUtil()
