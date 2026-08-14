import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MedianDownVarRatio(BaseFactor):
    # 因子名称：MedianDownVarRatio
    # 计算公式：过去40天下跌时的分钟收益率的平方和的平均值 / 过去40天分钟收益率的平方和的平均值，中心化后取绝对值再取相反数
    # 因子逻辑：下跌时和上涨时的日内波动越相近，该因子值越大，这样的股票噪音交易者和投机行为比例较少
    depend_data = ['FactorData.Basic_factor.close_minute']
    reform_window = 40
    sqr_sum = []
    down = []

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        stk_code = close.columns
        r = close.values[1:] / close.values[:-1] - 1
        sqr_sum = np.nansum(r ** 2, axis=0)
        down = np.nansum(r, axis=0) < 0
        self.sqr_sum.append(sqr_sum)
        self.sqr_sum = self.sqr_sum[-self.reform_window:]
        self.down.append(down)
        self.down = self.down[-self.reform_window:]
        if (len(self.sqr_sum) == self.reform_window) & (len(self.down) == self.reform_window):
            sqr_sum = np.array(self.sqr_sum)
            down = np.array(self.down)
            res = np.nanmean(np.where(down, sqr_sum, np.nan), axis=0) / np.nanmean(sqr_sum, axis=0)
            res = pd.Series(-np.abs(res - np.nanmean(res)), index=stk_code)
            return res
        else:
            return pd.Series(np.nan, index=stk_code)

