from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_ti9_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti9_cfg, self).__init__(required_columns=['close_zz500', 'open_zz500', 'low_zz500', 'weight_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data_dict):
        # 蜡烛图：实体（带方向）/下影线
        stk_open = data_dict['open_zz500']
        stk_low = data_dict['low_zz500']
        stk_close = data_dict['close_zz500']
        stk_weight = data_dict['weight_zz500']
        x = stk_close - stk_open
        y = stk_open.copy()
        y[x<0] = stk_close
        z = y - stk_low
        z[abs(z)<1e-8] = np.nan
        u = x/z
        factor_raw = (u * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 60)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor