from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *


class wsc_hf1(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf1, self).__init__(required_columns=['BuyTradeNum_500', 'BuyUniqueOrderNum_500', 'weight_500'],
                                      lookback_bars=2000)

    def on_bar(self, data):
        # 主买独立成交订单数/主买成交订单数，比值越小，说明一笔单子拆分的越细，也就是说拆分前的单子（即独立订单数）金额越大，而大单的涌入一般会出现领涨现象
        temp = data['BuyTradeNum_500'].copy()
        temp[abs(temp)<1e-8] = np.nan
        factor_raw = (data['BuyUniqueOrderNum_500'] / temp * data['weight_500']).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        factor = -ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0.5] = 0
        return factor