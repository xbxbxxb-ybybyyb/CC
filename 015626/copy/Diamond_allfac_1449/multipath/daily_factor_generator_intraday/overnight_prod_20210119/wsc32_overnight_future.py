from factor_generator import FactorGenerator
from operators_wsc import *



class wsc32_overnight_future(FactorGenerator):
    def __init__(self):
        super(wsc32_overnight_future, self).__init__(required_columns=['daily_open', 'daily_close', 'daily_recent_month_mask'],
                                                     lookback_bars=2000)

    def on_bar(self, data_dict):
        # 用过去2个交易日的开盘价预测下一个交易日的开盘价，再减去收盘价，预测下一个交易日的隔夜收益
        future_open = data_dict['daily_open']
        future_close = data_dict['daily_close']
        future_mask = data_dict['daily_recent_month_mask']

        open_pred = ts_pred(future_open, 2)
        factor_raw = (open_pred - future_close)[future_mask].sum(axis=1)
        factor = ts_rank(factor_raw, 20)
        factor = factor.to_frame()
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor