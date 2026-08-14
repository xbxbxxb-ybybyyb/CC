from xquant.characteristic import CharacteristicData
from dataApi.tradeDate import trans_datetime2int
from dataApi.stockList import trans_windcode2int
from dataApi.getData import get_minute_pickle
from crossUtils import *
from crossConfig import *
from crossFactor import crossFactor
import numpy as np


class ActiveBuyRatio(crossFactor):

    def st_factor(self):
        active_buy = get_minute_pickle('buytradeamt', self.cal_date_range, self.code_list).rolling(30).sum()
        passive_buy = get_minute_pickle('selltradeamt', self.cal_date_range, self.code_list).rolling(30).sum()
        factor = active_buy / (active_buy + passive_buy)
        factor = df_match_index_col(factor, self.code_list, self.cal_date_range, freq='1min')
        return factor

    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    group, func = 'sw1', 'cross_mean'
    print('-------------{}-----------{}-------------'.format(group, func))
    f = ActiveBuyRatio(group, func, 40, 20170101, 20210531, 'hx', 'ActiveBuyRatio', '主动成交占比',
                article='长江证券 (20200810): 高频因子（七）. 分布估计下的主动成交占比', freq='1min')
    f.save_result()