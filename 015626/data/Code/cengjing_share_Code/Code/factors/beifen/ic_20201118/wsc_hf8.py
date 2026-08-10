from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_hf8(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf8, self).__init__(required_columns=['Ask1AmtMean_500'],
                                      lookback_bars=2000)

    def on_bar(self, data):
        # factor logic: 见每一行后面的注释
        a = data['Ask1AmtMean_500'].std(axis=1)  # 表示当下挂单额波动率
        factor_raw = ts_rank(a, 30)  # 表示当下挂单额波动率在过去30分钟的排序
        factor_mean = ts_mean(factor_raw, 45)
        factor = -ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        factor[factor>=0] = 0
        return factor