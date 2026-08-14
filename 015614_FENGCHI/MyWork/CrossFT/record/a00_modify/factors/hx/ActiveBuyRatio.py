from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
import numpy as np


class ActiveBuyRatio(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='主动成交占比'
    article='长江证券20200810:高频因子（七）分布估计下的主动成交占比'
    freq='1min'


    def st_factor(self):
        active_buy = get_minute_pickle('buytradeamt', self.cal_date_range, self.code_list).rolling(30).sum()
        passive_buy = get_minute_pickle('selltradeamt', self.cal_date_range, self.code_list).rolling(30).sum()
        factor = active_buy / (active_buy + passive_buy)
        factor = df_match_index_col(factor, self.code_list, self.cal_date_range, freq='1min')
        return factor

    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    f = ActiveBuyRatio()
    f.save_result()