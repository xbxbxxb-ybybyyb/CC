from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
import numpy as np


class DownStd(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='40日下行波动率'
    article='兴业证券20200730–海外文献推荐系列087'
    freq='daily'


    def st_factor(self):
        ret = get_daily_1factor('pct_chg', self.cal_date_range, self.code_list)
        ret = df_match_index_col(ret, self.code_list, self.cal_date_range)
        return ret

    def cal_groupst(self):
        ret = self.st_factor()
        self.group = sameshape(ret, self.group_factor())
        self.func = self.group_func()
        ret = st2groupst(ret, self.group, self.func)
        ret = pd.DataFrame(ret[:, 0])
        ret = ret.rolling(40).apply(lambda x: np.nanstd(x[x<0])).values[:, None]
        ret = arr_match_index(ret, self.cal_date_range, self.date_range)
        return ret

    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    f = DownStd()
    f.save_result()