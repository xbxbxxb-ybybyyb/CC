from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
from help_functions_wsc import replace_zero


    
class wsc_hf20(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf20, self).__init__(required_columns=['SellTradeMoney_500', 'BuyTradeMoney_500'],
                                       lookback_bars=3000)

    def on_bar(self, hf_data):
        # 主买成交额/主卖成交额
        temp = hf_data['SellTradeMoney_500'].sum(axis=1)
        temp = ts_sum(temp, 30)
        temp = replace_zero(temp)
        factor_raw = ts_sum(hf_data['BuyTradeMoney_500'].sum(axis=1), 30) / temp
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor