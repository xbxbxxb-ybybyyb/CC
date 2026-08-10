import pandas as pd
from factor_generator import FactorGenerator
from operators_wsc import *



class wsc10_overnight_future(FactorGenerator):
    def __init__(self):
        super(wsc10_overnight_future, self).__init__(required_columns=['close', 'recent_month_mask'],
                                                     lookback_bars=2000)

    def on_bar(self, data_dict):
        # 近远月价差的日内变化
        future_close = data_dict['close']

        recent_month_close = future_close.stack().groupby('dt').first()  # 获取近月合约的close序列
        far_month_close = future_close.stack().groupby('dt').nth(1)  # 获取次近月合约的close序列
        price_spread = recent_month_close - far_month_close
        future_ret = (price_spread.iloc[price_spread.index.indexer_at_time('14:49:00')]-price_spread.iloc[price_spread.index.indexer_at_time('09:30:00')].values).to_frame()
        future_ret.index = pd.to_datetime(future_ret.index.date)
        future_ret.index.name = 'dt'

        factor = -ts_rank(future_ret, 20)
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor