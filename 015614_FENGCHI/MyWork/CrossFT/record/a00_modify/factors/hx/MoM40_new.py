from xquant.characteristic import CharacteristicData
from dataApi.tradeDate import trans_datetime2int
from dataApi.stockList import trans_windcode2int
from crossUtils import *
from crossConfig import *
from crossFactor import crossFactor
import numpy as np


class MoM40(crossFactor):

    def st_factor(self):
        ret = np.log(get_daily_1factor('pct_chg', self.cal_date_range, self.code_list) / 100 + 1)
        ret = np.exp(ret.rolling(40).sum()) - 1
        ret = df_match_index_col(ret, self.code_list, self.cal_date_range)
        return ret


    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    group, func = 'sw1', 'cross_mean'
    print('-------------{}-----------{}-------------'.format(group, func))
    f = MoM40(group, func, 40, 20170101, 20210531, 'hx', 'MoM40', '40日动量',
                article='天风证券 20170906 – 海外文献推荐015', freq='daily')
    f.save_result()