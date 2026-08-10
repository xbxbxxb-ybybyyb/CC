from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_hf9(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf9, self).__init__(required_columns=['Bid1AmtMean_500', 'Ask1AmtMean_500', 'close_500', 'weight_500'],
                                      lookback_bars=2000)

    def on_bar(self, hf_data):
        # factor logic：过去20分钟的收益率和买一挂单额＞卖一挂单额是两个动量指标，将它们叠加
        close_500 = hf_data['close_500']
        weight_500 = hf_data['weight_500']
        stk_ret = ts_pct_change(close_500, 20)
        stk_ret = stk_ret.replace([-np.inf, np.inf], np.nan)
        flag1 = hf_data['Bid1AmtMean_500'] >= hf_data['Ask1AmtMean_500']
        flag2 = stk_ret >= 0
        factor_raw = (ts_sum(flag1*flag2, 10)*weight_500).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 9)
        factor = ts_rank(factor_mean, 500)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor