from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

class NorthTop3RIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=40
    author='hx'
    logic='北向资金流入排名+北向资金行业Top3股票平均流入排名'
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
        north = northward / mkt_cap_ard
        return north

    def cal_groupst(self):
        factor = self.st_factor()
        stgroup = sameshape(factor, self.group_factor())
        groups = np.unique(stgroup[np.isfinite(stgroup)])
        shape = factor.shape
        rank = np.full(factor.shape, np.nan)
        for g in groups:
            val = stgroup == g
            rank = np.where(val, bottleneck.nanrankdata(np.where(val, -factor, np.nan), axis=len(shape) - 1), rank)
        factor[rank > 3] = np.nan

        group = sameshape(factor, self.group_factor())
        groups = np.unique(group[np.isfinite(group)])
        res = np.full(factor.shape[:-1] + (len(groups),), np.nan)
        for j, g in enumerate(groups):
            res[..., j] = self.group_func()(np.where(group == g, factor, np.nan), axis=-1)
        res = bottleneck.nanrankdata(res, axis=-1) / np.sum(np.isfinite(res), axis=-1, keepdims=True)
        res2 = np.full(factor.shape, np.nan)
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
        return self.cal_groupst()


if __name__ == '__main__':
    val1= cal_factor('data/user/016385/test/crossft/factors/hx', 'NorthTop3RIR.py',{'daily':1},notrun=False)