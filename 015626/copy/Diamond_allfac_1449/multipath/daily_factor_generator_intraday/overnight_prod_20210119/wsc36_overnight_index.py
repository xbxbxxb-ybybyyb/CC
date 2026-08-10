from factor_generator import FactorGenerator
from operators_wsc import *


class wsc36_overnight_index(FactorGenerator):
    def __init__(self):
        super(wsc36_overnight_index, self).__init__(required_columns=['daily_open_spot', 'daily_high_spot', 'daily_low_spot'],
                                                    lookback_bars=2000)

    def on_bar(self, data_dict):
        # adtm技术指标，反转因子
        index_open = data_dict['daily_open_spot']
        index_high = data_dict['daily_high_spot']
        index_low = data_dict['daily_low_spot']
                
        n = 75
        dtm = max2(index_high-index_open, ts_delta(index_open, 1))
        dtm[ts_delta(index_open, 1)<=0] = 0
        dbm = max2(index_open-index_low, -ts_delta(index_open, 1))
        dbm[ts_delta(index_open, 1)>=0] = 0
        stm = ts_sum(dtm, n)
        sbm = ts_sum(dbm, n)
        adtm = (stm-sbm) / max2(stm, sbm)
        factor_raw = adtm
        factor = -ts_rank(factor_raw, 20)
        factor = factor.to_frame()
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor