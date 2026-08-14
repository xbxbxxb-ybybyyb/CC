from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
import numpy as np
from basic.operators import *

class ActiveBuyRatio(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days = 1
    author='hx'
    logic='主动成交占比'
    article='长江证券20200810:高频因子（七）分布估计下的主动成交占比'
    freq='1min'

    basic_datas = {'1min': ['buytradeamt', 'selltradeamt']}

    def st_factor(self):
        active_buy = dt_mean(self.database['1min']['buytradeamt'], 30)  # get_minute_pickle('buytradeamt', self.cal_date_range, self.code_list).rolling(30).sum()
        passive_buy = dt_mean(self.database['1min']['selltradeamt'], 30)  # get_minute_pickle('selltradeamt', self.cal_date_range, self.code_list).rolling(30).sum()
        factor = active_buy / (active_buy + passive_buy)
        #factor = df_match_index_col(factor, self.code_list, self.cal_date_range, freq='1min')
        return factor

    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    val1 = cal_factor(numd={'1min': 20})
    val2 = cal_factor(numd={'1min': 15})
    gap = abs(val1 - val2)
    print(np.sum(np.where(np.isfinite(gap), gap, 0)))
