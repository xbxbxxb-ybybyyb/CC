from factor_generator import FactorGenerator
from operators_wsc import *


class wsc35_overnight_index(FactorGenerator):
    def __init__(self):
        super(wsc35_overnight_index, self).__init__(required_columns=['daily_close_spot'],
                                                    lookback_bars=2000)

    def on_bar(self, data_dict):
        # pos技术指标，反转因子
        index_close = data_dict['daily_close_spot']
                
        n = 75
        price1 = ts_delta(index_close, n) / ts_delay(index_close, n)
        pos1 = (price1 - ts_min(price1, n)) / (ts_max(price1, n) - ts_min(price1, n))
        factor_raw = pos1
        factor = -ts_rank(factor_raw, 20)
        factor = factor.to_frame()
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor