from xquant.characteristic import CharacteristicData
from dataApi.tradeDate import trans_datetime2int
from dataApi.stockList import trans_windcode2int
from crossUtils import *
from crossConfig import *
from crossFactor import crossFactor
import numpy as np


class BetaAvg(crossFactor):

    def st_factor(self):
        beta_100w = get_daily_1factor('beta_100w', self.cal_date_range, self.code_list)
        beta_100w = df_match_index_col(beta_100w, self.code_list, self.cal_date_range)
        return beta_100w


    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    group, func = 'sw1', 'cross_mean'
    print('-------------{}-----------{}-------------'.format(group, func))
    f = BetaAvg(group, func, 40, 20170101, 20210531, 'hx', 'BetaAvg', '行业Beta',
                article='天风证券 20200403 – 风格与行业视角下的宽基指数轮动', freq='daily')
    f.save_result()