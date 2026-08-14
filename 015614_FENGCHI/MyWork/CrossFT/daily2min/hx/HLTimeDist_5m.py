from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class HLTimeDist_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=60
    author='hx'
    logic='现价相对过去3个月内最高、最低价的收益率距离现在的天数与行业指数收益率距离现在的天数之和'
    article='渤海证券-金融工程专题报告：动量类新因子以及结合基本面的动量反转测试-191213 '
    freq='5mins'
    basic_datas = {'5mins': ['high_badj', 'low_badj', 'close_badj', 'ret_close']}


    def st_factor(self):
        high = self.database['5mins']['high_badj']
        low = self.database['5mins']['low_badj']
        factor = dt_argmax(high, 60) - dt_argmin(low, 60)
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def cal_groupst(self):
        pct_chg = self.database['5mins']['ret_close']
        self.stgroup = sameshape(pct_chg, self.group_factor())
        calfunc = self.group_func()
        pct_chg = st2groupst(pct_chg, self.stgroup, calfunc)
        val = np.lib.stride_tricks.as_strided(pct_chg[:, 0], shape=(
        pct_chg.shape[0] - 59, 60, pct_chg.shape[2]), strides=(
        pct_chg.strides[0], pct_chg.strides[0], pct_chg.strides[2])).copy()
        val = np.expm1(np.nancumsum(np.log1p(val), axis=1))
        factor = (np.nanargmin(val, axis=1) - np.nanargmax(val, axis=1)) / 60
        factor = np.pad(factor, ((59,0),(0,0)), mode='constant', constant_values=np.nan)[:, None]
        return arr_match_index(factor, self.cal_date_range, self.date_range)

    def cal_customst(self):
        return self.st_factor() + self.cal_groupst()

    def result(self):
        return self.cal_customst()

if __name__=='__main__':
    val1 = cal_factor()
