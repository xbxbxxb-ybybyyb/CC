from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc5_cfg_vs_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc5_cfg_vs_if, self).__init__(required_columns=['close_hs300', 'stk_volatility_hs300'],
                                             lookback_bars=3000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_hs300']
        
        # 计算长短两条均线包围的面积
        stk_close = data['close_hs300']
        ma_long = ts_mean(stk_close, 95)
        ma_short = ts_mean(stk_close, 15)
        ma_diff = ma_short - ma_long
        factor_init = ma_diff
        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        factor = ts_rank(factor_mean, 240*15)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
