from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc3_cfg_cr_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc3_cfg_cr_if, self).__init__(required_columns=['close_hs300', 'open_hs300', 'high_hs300', 'low_hs300', 'stk_index_corr_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_hs300']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # 用(close-open)/(high-low)衡量一分钟内的股价波动
        stk_close = data['close_hs300']
        stk_open = data['open_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']        
        a = stk_high - stk_low
        a[abs(a)<1e-8] = np.nan
        b = stk_close - stk_open
        b[b<0] = np.nan
        factor_init = ts_sum(b/a, 60)
        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)
        factor[factor<=-0.5] = 0
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
