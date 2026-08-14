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


    def st_factor(self):
        beta_100w = get_daily_1factor('beta_100w', self.cal_date_range, self.code_list)
        beta_100w = df_match_index_col(beta_100w, self.code_list, self.cal_date_range)
        return beta_100w


    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    f = BetaAvg()
    f.save_result()