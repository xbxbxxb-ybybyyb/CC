from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
from basic.crossOperators import *
from basic.operators import *
import numpy as np


class ASSharpe5_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean/cross_std'
    extend_days=40
    author='hx'
    logic='行业内个股过去5日收益率的均值比标准差'
    article='银河证券20160104–资产配置'
    freq='5mins'
    basic_datas = {'5mins': ['close_badj']}

    def st_factor(self):
        ret5 = dt_pct(self.database['5mins']['close_badj'], 5)  # get_daily_1factor('close_badj', self.cal_date_range, self.code_list).pct_change(5)
        # ret5 = df_match_index_col(ret5, self.code_list, self.cal_date_range)
        return ret5

    def cal_groupst(self):
        ret5 = self.st_factor()
        self.group = sameshape(ret5, self.group_factor())
        self.func = self.group_func()
        mean = st2groupst(ret5, self.group, cross_mean)
        std = st2groupst(ret5, self.group, cross_std)
        sharpe = mean / std
        sharpe = arr_match_index(sharpe, self.cal_date_range, self.date_range)
        return sharpe

    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    val1 = cal_factor(start=20210101, end=20210630)
