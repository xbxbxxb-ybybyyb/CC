from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc11_cfg_vs_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc11_cfg_vs_if, self).__init__(required_columns=['close_hs300', 'high_hs300', 'low_hs300', 'stk_volatility_hs300'],
                                              lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_hs300']

        # KDJD技术指标，先用stochastics指标衡量收盘价位于最近n分钟的最低价和最高价之间的位置，在以此为基础，计算该指标位于最近m分钟的最大值和最小值之间的位置，作为factor_init。
        stk_close = data['close_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        n = 30
        m = 150
        low_n = ts_min(stk_low, n)
        high_n = ts_max(stk_high, n)
        a = high_n - low_n
        a[abs(a)<1e-8] = np.nan
        stochastics = (stk_close- low_n) / a
        stochastics_low = ts_min(stochastics, m)
        stochastics_high = ts_max(stochastics, m)
        c = stochastics_high - stochastics_low
        c[abs(c)<1e-8] = np.nan
        stochastics_double = (stochastics - stochastics_low) / c
        factor_init = stochastics_double
        
        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 40)
        factor = ts_rank(factor_mean, 240*2)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
