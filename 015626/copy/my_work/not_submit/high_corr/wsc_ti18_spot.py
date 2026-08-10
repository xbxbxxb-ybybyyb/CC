from factor_generator import FactorGenerator
from help_functions_wsc import *



class wsc_ti18_spot(FactorGenerator):
    def __init__(self):
        super(wsc_ti18_spot, self).__init__(required_columns=['close_spot', 'high_spot', 'low_spot', 'amount_spot'],
                                            lookback_bars=2000)

    def on_bar(self, data_dict):
        # kvo技术指标
        index_close = data_dict['close_spot']
        index_high = data_dict['high_spot']
        index_low = data_dict['low_spot']
        index_amout = data_dict['amount_spot']
        price1 = index_close + index_low + index_high
        price1 = (ts_delta(price1, 1) > 0) + 0
        price1[price1<1] = -1
        price2 = index_high - index_low
        amount_power = index_amount * abs(2 * price2 / ts_sum(price2, 15) - 1) * price1 
        factor_raw = amount_power
        factor_mean = ts_mean(factor_raw, 60)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor