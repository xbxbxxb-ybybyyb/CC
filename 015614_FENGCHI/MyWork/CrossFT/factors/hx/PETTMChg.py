from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
import numpy as np


class PETTMChg(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=244
    author='hx'
    logic='市盈率TTM分位数'
    article='长江证券20210404–估值三问：当前在哪里，能往哪儿去，在投资中起什么作用？'
    freq='daily'
    basic_datas = {'daily': ['mkt_cap_ard', 'pe_ttm']}


    def st_factor(self):
        mkt_cap_ard = self.database['daily']['mkt_cap_ard']
        pe = self.database['daily']['pe_ttm']
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
    val1 = cal_factor()
