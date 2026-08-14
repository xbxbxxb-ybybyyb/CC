from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
import numpy as np


class MoM40(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='40日动量'
    article='天风证券20170906–海外文献推荐015'
    freq='daily'
    basic_datas = {'daily': ['pct_chg']}


    def st_factor(self):
        ret = np.log(self.database['daily']['pct_chg'] / 100 + 1)
        ret = np.exp(pd.DataFrame(ret[:, 0]).rolling(40).sum().values[:, None]) - 1
        return ret


    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    val1 = cal_factor()
