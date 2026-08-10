from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_ti8_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti8_cfg, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'open_zz500', 'high_zz500', 'low_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data_dict):
        # 大阳线技术指标，当开盘价接近最低价，收盘价显著高于开盘价且接近最高价时出现该图形。指标范围: [0,1]，且指标越高未来上涨概率越大，因此若close<open，则将指标值置为0.
        stk_open = data_dict['open_zz500']
        stk_high = data_dict['high_zz500']
        stk_low = data_dict['low_zz500']
        stk_close = data_dict['close_zz500']
        stk_weight = data_dict['weight_zz500']
        x = stk_high - stk_low
        x[abs(x)<1e-8] = np.nan
        ratio1 = (stk_close-stk_open) / x
        ratio1[(stk_close-stk_open)<0] = 0
        factor_raw = (ratio1*stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 60)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor