from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc13_cfg_vr_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc13_cfg_vr_if, self).__init__(required_columns=['close_hs300', 'open_hs300', 'stk_volatility_hs300', 'high_hs300', 'low_hs300'],
                                              lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_hs300']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1

        # 东方金工20200421，通过股价在回滚区间内的位置衡量股票日内买卖压力
        stk_close = data['close_hs300']
        stk_high = data['high_hs300']
        stk_low = data['low_hs300']
        stk_open = data['open_hs300']
        stk_price = (stk_high + stk_low + stk_open + stk_close) / 4
        n = 45
        rpp = ts_sum(stk_price, n)
        high_n = ts_max(stk_high, n)
        low_n = ts_min(stk_low, n)
        temp = high_n - low_n
        temp[abs(temp)<1e-8] = np.nan
        arpp = (rpp - low_n) / temp
        factor_init = arpp

        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 2)
        factor = ts_rank(factor_mean, 240*2)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
