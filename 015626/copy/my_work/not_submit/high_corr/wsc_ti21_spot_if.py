from factor_generator import FactorGenerator
# from help_functions_wsc import replace_zero
from operators_wsc import *



class wsc_ti21_spot(FactorGenerator):
    def __init__(self):
        super(wsc_ti21_spot, self).__init__(required_columns=['close_spot_if'],
                                            lookback_bars=2000)

    def on_bar(self, data_dict):
        # macd技术指标
        index_close = data_dict['close_spot_if']
        a1 = 2 / (12 + 1)
        a2 = 2 /(26 + 1)
        price1 = ts_truncated_ema(index_close, 60, a1)
        price2 = ts_truncated_ema(index_close, 60, a2)
        factor_raw = price1 - price2
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor