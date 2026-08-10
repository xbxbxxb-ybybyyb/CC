from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
# from help_functions_wsc import replace_zero


    
class wsc_hf15(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf15, self).__init__(required_columns=['PxVolCorr_500', 'weight_500'],
                                       lookback_bars=3000)

    def on_bar(self, hf_data):
        # 股价价量相关性
        weight_500 = hf_data['weight_500']
        factor_raw = (hf_data['PxVolCorr_500']*weight_500).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1800)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor