from factor_generator import FactorGenerator
from operators_wsc import *



class wsc12_spot(FactorGenerator):
    def __init__(self):
        super(wsc12_spot, self).__init__(required_columns=['high_spot', 'low_spot', 'close_spot'],
                                         lookback_bars=2000)

    def on_bar(self, data_dict):
        # er技术指标，用当期的high和low减去过去一段时间的close的sma，动量类指标。
        # 这个因子奇怪的是用close的ma就会反转，只有用sma才是动量而且效果好。
        index_high = data_dict['high_spot']
        index_low = data_dict['low_spot']
        index_close = data_dict['close_spot']
        N = 30
        bullpower = index_high - ts_sma(index_close, alpha=(N-1)/(N+1))
        bearpower = index_low - ts_sma(index_close, alpha=(N-1)/(N+1))
        factor_raw = bullpower + bearpower
        factor_mean = -ts_mean(factor_raw, 60)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor