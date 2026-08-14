from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class AdjLiq_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=10
    author='hx'
    logic='另类流动性因子'
    article='研究报告：海通证券-A股市场特征研究(四)：另类流动性因子-150717'
    freq='5mins'
    basic_datas = {'5mins': ['ret_close', 'turn_total']}


    def st_factor(self):
        return np.abs(self.database['5mins']['ret_close']) / 100, self.database['5mins']['turn_total']

    def cal_groupst(self):
        ret, turn = self.st_factor()
        self.group = sameshape(ret, self.group_factor())
        self.func = self.group_func()
        ret = st2groupst(ret, self.group, self.func)
        turn = st2groupst(turn, self.group, self.func)
        liq = 1 / dt_mean(ret / turn, 20)
        liq = (liq - dt_mean(liq, 244)) / dt_std(liq, 244)
        res = arr_match_index(liq, self.cal_date_range, self.date_range)
        return res

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    val1 = cal_factor(start=20210101, end=20210630)
