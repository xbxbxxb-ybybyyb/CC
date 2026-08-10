import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *

class wsc16_overnight_cfg_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_alla_preadj', 'weight_hs300']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # abi技术指标，值越大表示市场越活跃，活动和变化频繁，反之意味着市场缺乏变化
        hs300_stk_list = self.get_mdconstant('hs300_stock_list')
        stk_close = data_dict['close_alla_preadj'][hs300_stk_list]
        stk_weight = data_dict['weight_hs300'][hs300_stk_list]
        stk_close = stk_close.between_time(futures_data_morning_begin, futures_data_afternoon_end)
        stk_weight = stk_weight.between_time(futures_data_morning_begin, futures_data_afternoon_end)

        price_diff = ts_delta(stk_close, 230)
        price_diff[price_diff >= 0] = 1
        price_diff[price_diff < 0] = -1

        factor = abs((price_diff*stk_weight).sum(axis=1))
        factor = factor.iloc[factor.index.indexer_at_time(trade_stop_time)].to_frame()
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor