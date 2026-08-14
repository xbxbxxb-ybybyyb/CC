from xquant.characteristic import CharacteristicData
from dataApi.tradeDate import trans_datetime2int
from dataApi.stockList import trans_windcode2int
from crossUtils import *
from crossConfig import *
from crossFactor import crossFactor
import numpy as np


class PETTMChg(crossFactor):

    def st_factor(self):
        mkt_cap_ard = get_daily_1factor('mkt_cap_ard', self.cal_date_range, self.code_list)
        pe = get_daily_1factor('pe_ttm', self.cal_date_range, self.code_list)
        mkt_cap_ard = df_match_index_col(mkt_cap_ard, self.code_list, self.cal_date_range)
        pe = df_match_index_col(pe, self.code_list, self.cal_date_range)
        return mkt_cap_ard, pe

    def cal_groupst(self):
        mkt_cap_ard, pe = self.st_factor()
        self.group = sameshape(mkt_cap_ard, self.group_factor())
        self.func = self.group_func()
        pe = st2groupst(pe * mkt_cap_ard, self.group, self.func) / st2groupst(mkt_cap_ard, self.group, self.func)
        pe = pd.DataFrame(pe[:, 0], index=self.cal_date_range, columns=self.code_list)
        pe = pe.rolling(244).apply(lambda x: ((x <= x[-1]).sum() / x.shape[0])).values[:, None]
        pe = arr_match_index(pe, self.cal_date_range, self.date_range)
        return pe

    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    group, func = 'sw1', 'cross_sum'
    print('-------------{}-----------{}-------------'.format(group, func))
    f = PETTMChg(group, func, 40, 20170101, 20210531, 'hx', 'PETTMChg', '市盈率TTM分位数',
                article='长江证券 20210404 – 估值三问：当前在哪里，能往哪儿去，在投资中起什么作用？', freq='daily')
    f.save_result()