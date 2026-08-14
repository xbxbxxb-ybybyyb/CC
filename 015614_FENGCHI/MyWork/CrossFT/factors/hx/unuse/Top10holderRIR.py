from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck

from xquant.factordata import FactorData
fd = FactorData()

class Top10holderRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=30
    author='hx'
    logic='前十大股东持股比例 个股排序与行业排序和'
    article='渤海证券-金融工程专题报告：持股类因子测试-190325'
    freq='daily'
    basic_datas = {'daily': ['share_totala']}

    def st_factor(self):

        stk_hold_list = [
        'ann_dt_gd',
        'holder_enddate',
        'holder_holdercategory',
        'holder_name',
        'holder_quantity',
        'holder_pct',
        'holder_sharecategory',
        'holder_restrictedquantity',
        'holder_aname',
        'holder_sequence',
        'holder_sharecategoryname',
        'holder_memo',
        'info_compcode',
        'holder_nat'
        ]
        df = fd.get_factor_value('Basic_factor', [trans_int2windcode(x) for x in self.code_list],
                                 [str(x) for x in get_date_range(20090331, self.cal_date_range[-1], 'R')],
                                 stk_hold_list)
        df = df.reset_index().groupby(['ann_dt_gd', 'stock'])['holder_quantity'].sum().unstack().ffill()
        df.index = df.index.map(int)
        df.columns = df.columns.map(trans_windcode2int)
        df = df.reindex(self.cal_date_range, self.code_list).ffill()
        factor = df.values[:, None] / self.database['daily']['share_totala']
        return factor

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
    val1 = cal_factor(numd={'daily': 1})
