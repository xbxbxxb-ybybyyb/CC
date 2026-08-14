from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
import numpy as np


class Northward(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=40
    author='hx'
    logic='北上资金净买入变动'
    article='长江证券20210408–基于北上资金的行业配置（III）'
    freq='daily'


    def st_factor(self):
        ct_data = CharacteristicData()
        northward = ct_data.get_shhknorthward(str(self.cal_start), str(self.end)).pivot(
            'TRADINGDAY', 'TRADINGCODE', 'NETVALUE')
        northward.index = northward.index.map(trans_datetime2int)
        northward.columns = northward.columns.map(trans_windcode2int)
        northward = northward.replace(['', None], np.nan)
        northward = northward.applymap(float)
        northward = df_match_index_col(northward, self.code_list, self.cal_date_range)

        mkt_cap_ard = get_daily_1factor('mkt_cap_ard', self.cal_date_range, self.code_list)
        mkt_cap_ard = df_match_index_col(mkt_cap_ard, self.code_list, self.cal_date_range)
        return northward, mkt_cap_ard

    def cal_groupst(self):
        northward, mkt_cap_ard = self.st_factor()
        self.group = sameshape(northward, self.group_factor())
        self.func = self.group_func()
        northward = st2groupst(northward, self.group, self.func)
        mkt_cap_ard = st2groupst(mkt_cap_ard, self.group, self.func)
        res = arr_match_index(northward / mkt_cap_ard, self.cal_date_range, self.date_range)
        return res

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    val2 = cal_factor(numd={'daily': 15})