from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class StkIndCumRetExcessNum(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=6
    author='hx'
    logic='个股开盘净值超过行业开盘净值的累计数'
    article=''
    freq='5mins'
    basic_datas = {'5mins': ['ret_close']}

    def st_factor(self):
        ret = self.database['5mins']['ret_close']
        ret = ts_cumsum(ret)
        return ret

    def cal_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        res = st2groupst(indicator, group, self.group_func())
        return res

    def cal_customst(self):
        factor = self.st_factor()
        res = self.cal_groupst()
        factor = dt_mean((factor > res).astype(res.dtype), 240)
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        return factor

    def result(self):
        return self.cal_customst()

if __name__=='__main__':
    val1 = cal_factor()


