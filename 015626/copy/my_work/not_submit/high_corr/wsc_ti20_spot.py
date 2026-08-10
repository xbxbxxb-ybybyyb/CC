from factor_generator import FactorGenerator
from help_functions_wsc import replace_zero
from operators_wsc import *



class wsc_ti20_spot(FactorGenerator):
    def __init__(self):
        super(wsc_ti20_spot, self).__init__(required_columns=['close_spot', 'high_spot', 'low_spot', 'volume_spot'],
                                            lookback_bars=2000)

    def on_bar(self, data_dict):
        # mfi技术指标
        index_close = data_dict['close_spot']
        index_high = data_dict['high_spot']
        index_low = data_dict['low_spot']
        index_volume = data_dict['volume_spot']
        price1 = (index_high + index_low + index_close) / 3
        amount1 = price1 * index_volume
        amount2 = amount1.copy()
        n = 15
        price1_diff = ts_delta(price1, 1)
        amount1[price1_diff<0] = 0
        amount2[price1_diff>0] = 0
        a = ts_sum(amount1, n)
        b = ts_sum(amount2, n)
        b = replace_zero(b)
        factor_raw = 100 - 100 / (1 + a/b)
        factor_mean = ts_mean(factor_raw, 30)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor