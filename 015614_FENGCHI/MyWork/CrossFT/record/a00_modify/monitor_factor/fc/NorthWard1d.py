# coding: utf-8
# Author：fengchi863
# Date ：2021/8/18 11:08

from xquant.characteristic import CharacteristicData

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class NorthWard1d(crossFactor):
    cross_group=None
    cross_func=None
    extend_days=0
    author='fc'
    freq='daily'
    logic='单日北向资金流入情况'
    article='市场监控结论'

    def st_factor(self):
        ct_data = CharacteristicData()
        northward = ct_data.get_shhknorthward(str(self.cal_start), str(self.end))
        northward = northward.pivot('TRADINGDAY', 'TRADINGCODE', 'NETVALUE')
        northward = northward.replace(['', None], np.nan)
        northward.index = northward.index.map(trans_datetime2int)
        northward = northward.reindex(index=self.date_range)
        tmp = northward.applymap(float)
        northward_1d = tmp.sum(axis=1) / 1e8
        ret = index2st(northward_1d.values.reshape(-1, 1), len(self.code_list))
        # a = pd.DataFrame(np.repeat([northward_1d.values], len(self.code_list), axis=0).T, index=northward_1d.index,
        #                  columns=self.code_list)
        # factor = df_match_index_col(a, self.code_list, self.cal_date_range)
        return arr_match_index(ret, self.cal_date_range, self.date_range)

    def result(self):
        return self.st_factor()


if __name__ == '__main__':
    f = NorthWard1d()
    f.save_result()