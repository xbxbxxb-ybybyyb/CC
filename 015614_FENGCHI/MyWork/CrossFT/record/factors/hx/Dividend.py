from xquant.characteristic import CharacteristicData
from dataApi.tradeDate import trans_datetime2int
from dataApi.stockList import trans_windcode2int
from crossUtils import *
from crossConfig import *
from crossFactor import crossFactor
import numpy as np


class Dividend(crossFactor):

    def st_factor(self):
        mkt_cap_ard = get_daily_1factor('mkt_cap_ard', self.cal_date_range, self.code_list)
        dyr_12 = get_daily_1factor('dyr_12', self.cal_date_range, self.code_list)
        mkt_cap_ard = df_match_index_col(mkt_cap_ard, self.code_list, self.cal_date_range)
        dyr_12 = df_match_index_col(dyr_12, self.code_list, self.cal_date_range)
        return mkt_cap_ard, dyr_12

    def cal_groupst(self):
        mkt_cap_ard, dyr_12 = self.st_factor()
        self.group = sameshape(mkt_cap_ard, self.group_factor())
        self.func = self.group_func()
        dyr_12 = st2groupst(dyr_12 * mkt_cap_ard, self.group, self.func) / st2groupst(mkt_cap_ard, self.group, self.func)
        dyr_12 = pd.DataFrame(dyr_12[:, 0], index=self.cal_date_range, columns=self.code_list)
        dyr_12 = dyr_12.pct_change(60).values[:, None]
        dyr_12 = arr_match_index(dyr_12, self.cal_date_range, self.date_range)
        return dyr_12

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    group, func = 'sw1', 'cross_sum'
    print('-------------{}-----------{}-------------'.format(group, func))
    f = Dividend(group, func, 40, 20170101, 20210531, 'hx', 'Dividend', '股息率变动',
                  article='兴业证券 20210205 – 基本面量化视角下的红利投资研究系列之一：红利投资初探', freq='daily')
    f.save_result()
