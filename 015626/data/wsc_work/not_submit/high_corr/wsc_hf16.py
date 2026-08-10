from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
# from help_functions_wsc import replace_zero


    
class wsc_hf16(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf16, self).__init__(required_columns=['buy_superorder_count_500'],
                                       lookback_bars=3000)

    def on_bar(self, hf_data):
        # 当前时刻所有股票超大单数量之和
        factor_raw = hf_data['buy_superorder_count_500'].sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor