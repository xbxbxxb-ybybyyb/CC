from factor_generator import FactorGenerator
from operators_wsc import *



class wsc_ti9_if(FactorGenerator):
    def __init__(self):
        super(wsc_ti9_if, self).__init__(required_columns=['close_spot_if', 'open_spot_if', 'low_spot_if'],
                                         lookback_bars=2000)

    def on_bar(self, data_dict):
        # 蜡烛图：实体（带方向）/下影线
        index_open = data_dict['open_spot_if']
        index_low = data_dict['low_spot_if']
        index_close = data_dict['close_spot_if']
        x = index_close - index_open
        y = index_open.copy()
        y[x<0] = index_close
        z = y - index_low
        z[abs(z)<1e-8] = np.nan
        u = x/z
        factor_raw = u
        factor_mean = ts_mean(factor_raw, 45)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor