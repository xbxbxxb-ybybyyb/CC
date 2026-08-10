from factor_generator import FactorGenerator
from operators_wsc import *



class wsc_ti8_cfg_if(FactorGenerator):
    def __init__(self):
        super(wsc_ti8_cfg_if, self).__init__(required_columns=['high_hs300', 'low_hs300', 'close_hs300', 'open_hs300', 'weight_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data_dict):
        # 大阳线技术指标，当开盘价接近最低价，收盘价显著高于开盘价且接近最高价时出现该图形。指标范围: [0,1]，且指标越高未来上涨概率越大，因此若close<open，则将指标值置为0.
        future_high = data_dict['high_hs300']
        future_low = data_dict['low_hs300']
        future_close = data_dict['close_hs300']
        future_open = data_dict['open_hs300']
        stk_weight = data_dict['weight_hs300']
        x = future_high - future_low
        x[abs(x)<1e-8] = np.nan
        ratio1 = (future_close-future_open) / x
        ratio1[(future_close-future_open)<0] = 0
        factor_raw = (ratio1*stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 75)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor