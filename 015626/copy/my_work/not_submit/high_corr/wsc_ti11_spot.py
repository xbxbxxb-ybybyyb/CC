from factor_generator import FactorGenerator
from help_functions_wsc import *



class wsc_ti11_spot(FactorGenerator):
    def __init__(self):
        super(wsc_ti11_spot, self).__init__(required_columns=['high_spot', 'amount_spot', 'close_spot', 'open_spot'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # Chaikin money flow技术指标，逻辑类似adl技术指标，参考ti2
        index_high = data_dict['high_spot']
        index_amount = data_dict['amount_spot']
        index_close = data_dict['close_spot']
        index_open = data_dict['open_spot']
        x = index_high - index_low
        x[abs(x)<1e-8] = np.nan
        y = (index_close*2-index_low-index_high) / x
        factor_raw = ts_sum(y, 30) * index_amount / ts_sum(index_amount, 30)
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor