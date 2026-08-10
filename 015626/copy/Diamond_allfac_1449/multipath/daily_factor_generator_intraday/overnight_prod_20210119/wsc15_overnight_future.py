import pandas as pd
from factor_generator import FactorGenerator
from operators_wsc import *



class wsc15_overnight_future(FactorGenerator):
    def __init__(self):
        super(wsc15_overnight_future, self).__init__(required_columns=['close', 'high', 'low', 'open', 'recent_month_mask'],
                                                     lookback_bars=2000)

    def on_bar(self, data_dict):
        # 技术指标：尾盘45分钟的十字星
        future_close = data_dict['close']
        future_high = data_dict['high']
        future_open = data_dict['open']
        future_low = data_dict['low']
        future_mask = data_dict['recent_month_mask']

        daily_high = ts_max(future_high, 45)[future_mask].sum(axis=1)
        daily_high = daily_high.iloc[daily_high.index.indexer_at_time('14:49:00')]
        daily_high.index = pd.to_datetime(daily_high.index.date)
        daily_high.index.name = 'dt'

        daily_low = ts_min(future_low, 45)[future_mask].sum(axis=1)
        daily_low = daily_low.iloc[daily_low.index.indexer_at_time('14:49:00')]
        daily_low.index = pd.to_datetime(daily_low.index.date)
        daily_low.index.name = 'dt'

        daily_open = future_open.iloc[future_open.index.indexer_at_time('14:05:00')][future_mask].sum(axis=1)
        daily_open.index = pd.to_datetime(daily_open.index.date)
        daily_open.index.name = 'dt'

        daily_close = future_close.iloc[future_close.index.indexer_at_time('14:49:00')][future_mask].sum(axis=1)
        daily_close.index = pd.to_datetime(daily_close.index.date)
        daily_close.index.name = 'dt'

        a_daily = (daily_close-daily_open) / (daily_high-daily_low)
        factor = -ts_rank(a_daily, 20).to_frame()
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor