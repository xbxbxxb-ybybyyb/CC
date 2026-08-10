from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_ti13_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti13_cfg, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # CMO技术指标，用于衡量动量
        stk_close = data_dict['close_zz500']
        stk_weight = data_dict['weight_zz500']
        n = 20
        su = ts_sum(np.maximum(ts_delta(stk_close, 1), 0), n)
        sd = ts_sum(np.maximum(-ts_delta(stk_close, 1), 0), n)
        x = su + sd
        x[abs(x)<1e-8] = np.nan
        cmo = (su-sd) / x
        factor_raw = (cmo*stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 60)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor