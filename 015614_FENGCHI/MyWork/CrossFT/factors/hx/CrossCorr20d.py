from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class CrossCorr20d(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=21
    author='hx'
    logic='过去20日与全市场其它股票的平均相关系数均值'
    article=''
    freq='daily'
    basic_datas = {'daily': ['close_badj']}

    def st_factor(self):
        close = self.database['daily']['close_badj']
        ret = dt_pct(close, 1)[:, 0]
        corr = np.empty_like(ret)
        corr[:19] = np.nan
        for j in range(19, corr.shape[0]):
            corr[j] = pd.DataFrame(ret[j-19: j+1]).corr().mean().values
        return corr[:, None]

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    f = CrossCorr20d()
    #print(f.result())
    f.save_result()