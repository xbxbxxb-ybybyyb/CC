from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class BigSmallAmtMomDiff(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='过去20日大小成交量动量差'
    article=''
    freq='daily'
    basic_datas = {'daily': ['close_badj', 'amt']}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        amt = self.database['daily']['amt']
        ret = dt_pct(close, 1)
        amt_md = dt_median(amt, 20)
        mom = dt_mean(pn_condition2(amt - amt_md, ret), 20)
        return mom

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = BigSmallAmtMomDiff()
    #print(f.result())
    f.save_result()