from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np


class PaymentRIR(crossFactor):
    cross_group='sw1'
    cross_func='cross_mean'
    extend_days=1
    author='hx'
    logic='应付职工薪酬增速 行业排序与个股排序和'
    article='研究报告：海通证券-选股因子系列研究（九）：上市公司薪酬那点事-141210 '
    freq='daily'

    def st_factor(self):
        pay = get_ttm_quarter('empl_ben_payable')
        pay = get_qoq(pay)
        pay = fill_quarter2daily_by_issue_date(pay)
        pay = pay.reindex(self.cal_date_range, self.code_list).values[:, None]
        return pay

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
        return self.cal_groupst()


if __name__ == '__main__':
    self = PaymentRIR()
    self.save_result()