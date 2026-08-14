# coding: utf-8
# Author：fengchi863
# Date ：2021/8/25 9:56

import talib

from basic.crossFactor import crossFactor
from basic.crossUtils import *


class ROC12d(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 30
    author = 'fc'
    factor_name = 'ROC12d'
    freq = 'daily'
    logic = '个股12天股价变动率行业内求均值'
    article = '渤海证券 20180710 – 行业轮动专题一'
    basic_datas = {'daily': ['pct_chg'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        close = self.database['daily']['pct_chg']
        close = pd.DataFrame(close[:, 0, :], index=self.cal_date_range, columns=self.code_list)
        roc = {}
        for stk in close.columns:
            try:
                roc[stk] = talib.ROC(close[stk].values, timeperiod=12)
            except:
                roc[stk] = np.array([np.nan] * len(close.index))
        ret = pd.DataFrame(roc)
        ret.index = close.index
        return ret

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    cal_factor()
