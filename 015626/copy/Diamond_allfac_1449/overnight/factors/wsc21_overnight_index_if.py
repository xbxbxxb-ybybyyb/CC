import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc21_overnight_index_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # rsj技术指标：（上行波动率-下行波动率）/（上行波动率+下行波动率）
        index_close = data_dict['close_000300.SH']
        index_close = index_close.between_time(futures_data_morning_begin, futures_data_afternoon_end)  # 新版指数数据有14:58-15:00的数据，为了与之前的因子值保持一致，做此截断处理
        # index_close.to_excel('/data/user/017024/index_close_29210513.xlsx')

        index_ret_up = ts_pct_change(index_close, 1)
        index_ret_up[index_ret_up < 0] = 0
        index_ret_down = ts_pct_change(index_close, 1)
        index_ret_down[index_ret_down > 0] = 0
        vol_up = ts_sum(index_ret_up**2, 350)
        vol_down = ts_sum(index_ret_down**2, 350)
        rsj = (vol_up-vol_down) / replace_zero(vol_up+vol_down)

        factor = -rsj.iloc[rsj.index.indexer_at_time(trade_stop_time)].to_frame()
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor