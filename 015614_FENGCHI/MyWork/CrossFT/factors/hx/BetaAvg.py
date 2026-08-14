from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
import numpy as np


class BetaAvg(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='行业Beta'
    article='天风证券20200403–风格与行业视角下的宽基指数轮动'
    freq='daily'
    basic_datas = {'daily': ['beta_100w']}


    def st_factor(self):
        beta_100w = self.database['daily']['beta_100w']
        return beta_100w


    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    val1 = cal_factor()
