import pandas as pd
from factor_generator import FactorGenerator
from operators_wsc import *



class wsc4_overnight_future(FactorGenerator):
    def __init__(self):
        super(wsc4_overnight_future, self).__init__(required_columns=['close', 'recent_month_mask', 'close_spot'],
                                                    lookback_bars=2000)

    def on_bar(self, data_dict):
        # 尾盘基差
        future_close = data_dict['close']
        index_close = data_dict['close_spot']
        future_mask = data_dict['recent_month_mask']

        index_close_1449 = index_close.iloc[index_close.index.indexer_at_time('14:49:00')]
        index_close_1449.index = pd.to_datetime(index_close_1449.index.date)
        index_close_1449.index.name = 'dt'

        close_1449 = future_close[future_mask].sum(axis=1)
        close_1449 = close_1449.iloc[close_1449.index.indexer_at_time('14:49:00')]
        close_1449.index = pd.to_datetime(close_1449.index.date)
        close_1449.index.name = 'dt'

        factor_raw = index_close_1449 / close_1449
        factor = ts_rank(factor_raw, 45)
        factor = factor.to_frame()
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor