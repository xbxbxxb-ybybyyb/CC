from factor_generator import FactorGenerator
from operators_wsc import *



class wsc_ti2_spot(FactorGenerator):
    def __init__(self):
        super(wsc_ti2_spot, self).__init__(required_columns=['high_spot', 'low_spot', 'close_spot', 'amount_spot'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # adl技术指标, 用分钟内价格变化对amount进行调整，调整系数: [-1, 1]，close越接近high调整系数越大，越接近low越低
        # 原指标还要对amount_adj累加，在现有框架下，为了保证每个时间点因子值可比，用ts_sum代替累加
        # 个人理解是amount是个动量指标，(2 * index_close - index_high - index_low) / (index_high - index_low)也是个动量指标，相当于两个动量指标共同作用得到的结果
        index_high = data_dict['high_spot']
        index_low = data_dict['low_spot']
        index_close = data_dict['close_spot']
        index_amount = data_dict['amount_spot']
        x = index_high - index_low
        x[abs(x)<1e-8] = np.nan
        amount_adj = (2 * index_close - index_high - index_low) / x * index_amount
        amount_adj = ts_sum(amount_adj, 60)
        factor = ts_rank(amount_adj, 950)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor