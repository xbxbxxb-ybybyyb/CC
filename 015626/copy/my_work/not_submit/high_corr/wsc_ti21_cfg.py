from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import multi_processing_joblib
from operators_wsc import *



class wsc_ti21_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti21_cfg, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # macd技术指标
        stk_close = data_dict['close_zz500']
        stk_weight = data_dict['weight_zz500']
        a1 = 2 / (12 + 1)
        a2 = 2 /(26 + 1)
        price1 = multi_processing_joblib(df=stk_close, func=ts_truncated_ema, n_jobs=-1, d=60, alpha=a1)
        price2 = multi_processing_joblib(df=stk_close, func=ts_truncated_ema, n_jobs=-1, d=60, alpha=a2)
        factor_raw = ((price1 - price2)*stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor