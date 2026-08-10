from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc14_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc14_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=3000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # vidya技术指标,vi可用来衡量股票过去一段时间的趋势，趋势越强vi值越大，此时vidya赋予当前的close更大的权重，捕捉趋势，反之同理。
        stk_close = data['close_hs300']
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        temp[abs(temp)<1e-8] = np.nan
        vi = abs(ts_delta(stk_close, n)) / temp
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 480)

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 240*12)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0] = 0
        return factor
