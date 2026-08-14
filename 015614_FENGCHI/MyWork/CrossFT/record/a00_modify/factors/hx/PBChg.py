from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
import numpy as np


class PBChg(crossFactor):
    cross_group='sw1'
    cross_func='cross_sum'
    extend_days=40
    author='hx'
    logic='市净率分位数'
    article='长江证券20210404–估值三问：当前在哪里，能往哪儿去，在投资中起什么作用？'
    freq='daily'


    def st_factor(self):
        mkt_cap_ard = get_daily_1factor('mkt_cap_ard', self.cal_date_range, self.code_list)
        pb = get_daily_1factor('s_val_pb_new', self.cal_date_range, self.code_list)
        mkt_cap_ard = df_match_index_col(mkt_cap_ard, self.code_list, self.cal_date_range)
        pb = df_match_index_col(pb, self.code_list, self.cal_date_range)
        return mkt_cap_ard, pb

    def cal_groupst(self):
        mkt_cap_ard, pb = self.st_factor()
        self.group = sameshape(mkt_cap_ard, self.group_factor())
        self.func = self.group_func()
        pb = st2groupst(pb * mkt_cap_ard, self.group, self.func) / st2groupst(mkt_cap_ard, self.group, self.func)
        pb = pd.DataFrame(pb[:, 0], index=self.cal_date_range, columns=self.code_list)
        pb = pb.rolling(244).apply(lambda x: ((x <= x[-1]).sum() / x.shape[0])).values[:, None]
        pb = arr_match_index(pb, self.cal_date_range, self.date_range)
        return pb

    def result(self):
        return self.cal_groupst()

if __name__ == '__main__':
    f = PBChg()
    f.save_result()