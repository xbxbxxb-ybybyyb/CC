import pandas as pd
from factor_generator import FactorGenerator
from operators_wsc import *



class wsc13_overnight_future(FactorGenerator):
    def __init__(self):
        super(wsc13_overnight_future, self).__init__(required_columns=['close'],
                                                     lookback_bars=2000)

    def on_bar(self, data_dict):
        # 近月合约和次近月合约尾盘收益率之差
        future_close = data_dict['close']

        future_ret = ts_pct_change(future_close.stack().groupby('dt').nth(1), 30)
        future_ret = future_ret.iloc[future_ret.index.indexer_at_time('14:49:00')]
        future_ret.index = pd.to_datetime(future_ret.index.date)
        future_ret.index.name = 'dt'

        future_ret1 = ts_pct_change(future_close.stack().groupby('dt').nth(0), 30)
        future_ret1 = future_ret1.iloc[future_ret1.index.indexer_at_time('14:49:00')]
        future_ret1.index = pd.to_datetime(future_ret1.index.date)
        future_ret1.index.name = 'dt'

        factor = ts_rank(future_ret-future_ret1, 20).to_frame()
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor