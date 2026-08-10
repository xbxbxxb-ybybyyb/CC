from factor_generator import FactorGenerator
from help_functions_wsc import *



class wsc_ti17_spot(FactorGenerator):
    def __init__(self):
        super(wsc_ti17_spot, self).__init__(required_columns=['close_spot', 'open_spot'],
                                            lookback_bars=2000)

    def on_bar(self, data_dict):
        # imi技术指标
        index_close = data_dict['close_spot']
        index_open = data_dict['open_spot']
        n = 20
        a = index_close - index_open
        a[a<0] = 0
        b = index_open - index_close
        b[b<0] = 0
        inc = ts_sum(a, n)
        dec = ts_sum(b, n)
        factor_raw = inc / replace_zero(inc + dec)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor