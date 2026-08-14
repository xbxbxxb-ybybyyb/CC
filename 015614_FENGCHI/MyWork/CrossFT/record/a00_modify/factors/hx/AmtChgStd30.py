from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
import numpy as np


class AmtChgStd30(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=40
    author='hx'
    logic='行业成交额变化率30日的标准差'
    article='银河证券20160425–量化选股'
    freq='daily'


    def st_factor(self):
        amt = get_daily_1factor('amt', self.cal_date_range, self.code_list)
        amt = df_match_index_col(amt, self.code_list, self.cal_date_range)
        return amt

    def cal_customst(self):
        self.factor = self.st_factor()
        self.stgroup = sameshape(self.factor, self.group_factor())
        calfunc = self.group_func()
        amt = st2groupst(self.factor, self.stgroup, calfunc)
        amt = pd.DataFrame(amt[:, 0]).pct_change().rolling(30).std().values[:, None]
        amt = arr_match_index(amt, self.cal_date_range, self.date_range)
        print(amt.shape)
        return amt

    def result(self):
        return self.cal_customst()

if __name__ == '__main__':
    f = AmtChgStd30()
    f.save_result()