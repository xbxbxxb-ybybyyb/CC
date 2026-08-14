from xquant.characteristic import CharacteristicData
from dataApi.tradeDate import trans_datetime2int
from dataApi.stockList import trans_windcode2int
from crossUtils import *
from crossConfig import *
from crossFactor import crossFactor
import numpy as np


class DownStd(crossFactor):

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
    group, func = 'sw1', 'cross_mean'
    print('-------------{}-----------{}-------------'.format(group, func))
    f = DownStd(group, func, 40, 20170101, 20210531, 'hx', 'DownStd', '40日下行波动率',
                article='兴业证券 20200730 – 海外文献推荐系列087', freq='daily')
    f.save_result()