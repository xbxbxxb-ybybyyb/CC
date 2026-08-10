from factor_generator import FactorGenerator
from operators_wsc import *


class wsc31_overnight_index(FactorGenerator):
    def __init__(self):
        super(wsc31_overnight_index, self).__init__(required_columns=['daily_open_spot', 'daily_close_spot'],
                                                    lookback_bars=2000)

    def on_bar(self, data_dict):
        # 用过去5个交易日的开盘价预测下一个交易日的开盘价，再减去收盘价，预测下一个交易日的隔夜收益
        index_open = data_dict['daily_open_spot']
        index_close = data_dict['daily_close_spot']
                
        open_pred = ts_pred(index_open, 5)
        factor_raw = (open_pred - index_close)
        factor = ts_rank(factor_raw, 20)
        factor = factor.to_frame()
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor