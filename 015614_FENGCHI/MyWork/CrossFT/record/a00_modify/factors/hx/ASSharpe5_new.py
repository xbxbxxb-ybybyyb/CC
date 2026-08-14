from xquant.characteristic import CharacteristicData
from dataApi.tradeDate import trans_datetime2int
from dataApi.stockList import trans_windcode2int
from crossUtils import *
from crossConfig import *
from crossFactor import crossFactor
from crossOperators import *
import numpy as np


class ASSharpe5(crossFactor):

    def st_factor(self):
        ret5 = get_daily_1factor('close_badj', self.cal_date_range, self.code_list).pct_change(5)
        ret5 = df_match_index_col(ret5, self.code_list, self.cal_date_range)
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
    group, func = 'sw1', 'cross_mean / cross_std'
    print('-------------{}-----------{}-------------'.format(group, func))
    f = ASSharpe5(group, func, 40, 20170101, 20210531, 'hx', 'ASSharpe5', '行业内个股过去5日收益率的均值比标准差',
                article='银河证券 20160104 – 资产配置', freq='daily')
    f.save_result()