from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
from help_functions_wsc import replace_zero


    
class wsc_hf18(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf18, self).__init__(required_columns=['Bid1AmtMean_500', 'Buy1NumOrdersMean_500', 'weight_500'],
                                       lookback_bars=3000)

    def on_bar(self, hf_data):
        # 买一挂单金额除以买一挂单数量，表征平均一单的挂单金额，还是大小单逻辑
        weight_500 = hf_data['weight_500']
        temp = hf_data['Buy1NumOrdersMean_500'].copy()
        temp = replace_zero(temp)
        factor_raw = (hf_data['Bid1AmtMean_500'] / temp * weight_500).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor