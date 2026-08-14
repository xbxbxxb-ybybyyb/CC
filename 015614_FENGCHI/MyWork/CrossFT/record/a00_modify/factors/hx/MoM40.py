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


    def st_factor(self):
        ret = np.log(get_daily_1factor('pct_chg', self.cal_date_range, self.code_list) / 100 + 1)
        ret = np.exp(ret.rolling(40).sum()) - 1
        ret = df_match_index_col(ret, self.code_list, self.cal_date_range)
        return ret


    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    f = MoM40()
    f.save_result()