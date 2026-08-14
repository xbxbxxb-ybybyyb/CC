from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class DMIRIR_5m(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=41
    author='hx'
    logic='DMI动向指标的个股排序与行业排序之和'
    article='广发证券-多因子Alpha系列报告之（四十二）：海量技术指标掘金Alpha因子-210730'
    freq='5mins'
    basic_datas = {'5mins': ['close_badj', 'high_badj', 'low_badj']}

    def st_factor(self):
        close = self.database['5mins']['close_badj']
        high = self.database['5mins']['high_badj']
        low = self.database['5mins']['low_badj']
        TRI = dt_mean(max2(max2(high - low, abss(high - dt_delay(close, 1))), abss(low - dt_delay(close, 1))), 20)
        HD = high - dt_delay(high, 1)
        LD = dt_delay(low, 1) - low
        DMP = dt_mean(np.where((HD > 0) & (HD > LD), HD, 0), 20)
        DDM = dt_mean(np.where((LD > 0) & (LD > HD), LD, 0), 20)
        PDI = div2(DMP , TRI)
        MDI = div2(DDM , TRI)
        ADX = dt_mean(abss(MDI - PDI) / (MDI + PDI), 10)
        ADXR = (ADX + dt_delay(ADX, 10)) / 2
        return ADXR

    def cal_groupst(self):
        indicator = self.st_factor()
        group = sameshape(indicator, self.group_factor())
        groups = np.unique(group[np.isfinite(group)])
        res = np.full(indicator.shape[:-1] + (len(groups),), np.nan)
        for j, g in enumerate(groups):
            res[..., j] = self.group_func()(np.where(group == g, indicator, np.nan), axis=-1)
        res = bottleneck.nanrankdata(res, axis=-1) / np.sum(np.isfinite(res), axis=-1, keepdims=True)
        res2 = np.full(indicator.shape, np.nan)
        for j, g in enumerate(groups):
            res2 = np.where(group == g, res[..., [j]], res2)
        return arr_match_index(res2, self.cal_date_range, self.date_range)

    def cal_customst(self):
        factor = self.st_factor()
        factor = bottleneck.nanrankdata(factor, axis=-1) / np.sum(np.isfinite(factor), axis=-1, keepdims=True)
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        res = self.cal_groupst()
        return factor + res

    def result(self):
        return self.cal_customst()
if __name__=='__main__':
    val1 = cal_factor(start=20210101, end=20210630)

