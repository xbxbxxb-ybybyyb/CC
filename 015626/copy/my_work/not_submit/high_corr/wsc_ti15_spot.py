from factor_generator import FactorGenerator
from help_functions_wsc import *



class wsc_ti15_spot(FactorGenerator):
    def __init__(self):
        super(wsc_ti15_spot, self).__init__(required_columns=['close_spot'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # dpo技术指标， 将长周期从价格中剔除出去，只反映价格的短期趋势
        index_close = data_dict['close_spot']
        n = 20
        dpo = index_close - ts_delay(ts_mean(index_close, n), int(n/2)+1)
        factor_raw = dpo
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor