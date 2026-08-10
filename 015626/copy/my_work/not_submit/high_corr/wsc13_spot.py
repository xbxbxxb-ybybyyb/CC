from factor_generator import FactorGenerator
from operators_wsc import *



class wsc13_spot(FactorGenerator):
    def __init__(self):
        super(wsc13_spot, self).__init__(required_columns=['close_spot'],
                                         lookback_bars=2000)

    def on_bar(self, data_dict):
        # ts_reg_beta：具体推导见Word
        index_close = data_dict['close_spot']
        N = 45
        factor_raw = ts_reg_beta(index_close, N)
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)
        factor[factor<=0] = 0
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor