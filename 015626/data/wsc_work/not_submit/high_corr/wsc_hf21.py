from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
from help_functions_wsc import replace_zero


    
class wsc_hf21(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf21, self).__init__(required_columns=['buy_smallorder_count_500', 'buy_smallorder_money_500'],
                                       lookback_bars=3000)

    def on_bar(self, hf_data):
        # 平均每笔小单交易的成交额，类似还有中单大单和超大单，不再一一写了
        factor_raw = (hf_data['buy_smallorder_money_500'] / replace_zero(hf_data['buy_smallorder_count_500']) * weight_500).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor