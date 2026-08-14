# coding: utf-8
# Author：fengchi863
# Date ：2021/10/12 10:52

from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import *
from basic.crossOperators import *
import bottleneck as bn


class SwingPerDeal2_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 15
    author = 'fc'
    freq = '5mins'
    logic = '振幅总和除以成交笔数，个股排序+行业排序'
    article = ''
    basic_datas = {'5mins': [], '1min': ['high', 'low', 'tradenum']}

    def st_factor(self):
        tradenum = self.database['1min']['tradenum']
        high = self.database['1min']['high']
        low = self.database['1min']['low']
        ret = (high - low) / low
        swing_mean = dt_mean(ret, 5)
        trade_mean = dt_mean(tradenum, 5)
        ret = swing_mean / trade_mean
        ret = cross_resample(ret, '5mins')
        return ret

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
        indicator = self.st_factor()

        factor = bottleneck.nanrankdata(indicator, axis=-1) / np.sum(np.isfinite(indicator), axis=-1, keepdims=True)
        factor = arr_match_index(factor, self.cal_date_range, self.date_range)
        res = self.cal_groupst()
        return factor + res

    def result(self):
        return self.cal_customst()


if __name__ == '__main__':
    # f = SwingPerDeal_5m(start=20210401, end=20210501)
    # print(f.result())
    cal_factor(save_folder='factor_result_rerun5')
    #val = cal_factor()
