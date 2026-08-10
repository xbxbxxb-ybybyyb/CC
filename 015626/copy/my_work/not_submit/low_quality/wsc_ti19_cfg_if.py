from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_ti19_cfg_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti9_cffg_if, self).__init__(required_columns=['close_hs300'],
                                              lookback_bars=2000)

    def on_bar(self, data_dict):
        # 由VIDYA指标改造而来
        # VIDYA指标也属于均线的一种，但是在权重中加入了ER指标
        # 当前趋势较强时，ER指标值较大，VIDYA会赋予当前价格更大的权重，使其紧随价格变动，减少其滞后性
        # 当前趋势较弱时（如震荡市），VIDYA会赋予当前价格较小的权重，增加其滞后性，使其更加平滑，避免产生更多的交易信号
        # 因子值为close-VIDYA，化简后为(1-vi)(close_t-close_(t-1))，属于动量指标
        stk_close = data_dict['close_hs300']
        n = 20
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        temp[abs(temp)<1e-8] = np.nan
        vi = abs(ts_delta(stk_close, n)) / temp
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_raw = ((stk_close - vidya)*stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 120)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor