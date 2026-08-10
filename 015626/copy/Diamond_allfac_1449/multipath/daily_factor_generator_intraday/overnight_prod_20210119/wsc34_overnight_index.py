from factor_generator import FactorGenerator
from operators_wsc import *


class wsc34_overnight_index(FactorGenerator):
    def __init__(self):
        super(wsc34_overnight_index, self).__init__(required_columns=['daily_close_spot', 'daily_high_spot', 'daily_low_spot'],
                                                    lookback_bars=2000)

    def on_bar(self, data_dict):
        # er技术指标，同样是反转因子
        index_close = data_dict['daily_close_spot']
        index_high = data_dict['daily_high_spot']
        index_low = data_dict['daily_low_spot']
                
        n = 60
        bullpower = index_high - ts_sma_span(index_close, n)
        bearpower = index_low - ts_sma_span(index_close, n)
        factor_raw = bullpower + bearpower
        factor = -ts_rank(factor_raw, 20)
        factor = factor.to_frame()
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor