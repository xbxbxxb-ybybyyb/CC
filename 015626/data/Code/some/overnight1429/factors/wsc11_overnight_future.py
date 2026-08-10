import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc11_overnight_future(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_IC.CFE', 'volume_IC.CFE', 'position_IC.CFE', 'recent_month_mask']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 长江金工：经持仓量调整的价量相关性
        future_close = data_dict['close_IC.CFE']
        future_position = data_dict['position_IC.CFE']
        future_volume = data_dict['volume_IC.CFE']
        future_mask = data_dict['recent_month_mask']

        position_1 = future_position[future_mask].sum(axis=1).between_time(futures_data_morning_begin, trade_stop_time)
        volume_1 = future_volume[future_mask].sum(axis=1).between_time(futures_data_morning_begin, trade_stop_time)
        close_1 = future_close[future_mask].sum(axis=1).between_time(futures_data_morning_begin, trade_stop_time)

        volume_weight = volume_1.groupby(volume_1.index.date).apply(lambda x: x / x.sum())
        position_daily = position_1.groupby(position_1.index.date).last() - position_1.groupby(position_1.index.date).first()
        position_T_1 = volume_weight.groupby(volume_weight.index.date).apply(lambda x: x * position_daily[x.index.date[0]])
        position_T_0 = position_T_1 - position_1.groupby(position_1.index.date).apply(lambda x: x.diff())

        position_modify = (position_T_0 + position_T_1).groupby(position_T_0.index.date).apply(lambda x: x.cumsum()\
                                                                + position_1[(x.index.date[0]).strftime("%Y%m%d")].iloc[0])

        factor = pd.concat([close_1, position_modify], axis=1)
        factor = factor.groupby(factor.index.date).apply(lambda x: (x.diff().iloc[:,0]).corr(x.diff().iloc[:,1]))
        factor.index = pd.to_datetime(factor.index)
        factor.index.name = 'dt'
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor