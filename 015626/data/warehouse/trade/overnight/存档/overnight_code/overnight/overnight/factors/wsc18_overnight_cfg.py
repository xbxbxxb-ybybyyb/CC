import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc18_overnight_cfg(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_alla_preadj', 'amount_alla']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 下午开盘至尾盘的Arms技术指标，用来显示成交额是否跟随价格上涨或者价格下跌
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_close = data_dict['close_alla_preadj'][zz500_stk_list]
        stk_amount = data_dict['amount_alla'][zz500_stk_list]
        stk_close = stk_close.between_time(futures_data_morning_begin, futures_data_afternoon_end)
        stk_amount = stk_amount.between_time(futures_data_morning_begin, futures_data_afternoon_end)

        price_diff = ts_delta(stk_close, 110)
        price_diff1 = ts_delta(stk_close, 360)
        stk_amount_sum = ts_sum(stk_amount, 110)

        up_num = (price_diff >= 0).sum(axis=1)
        down_num = (price_diff < 0).sum(axis=1)
        up_amount = stk_amount_sum[price_diff1 >= 0].sum(axis=1)
        down_amount = stk_amount_sum[price_diff1 < 0].sum(axis=1)
        
        factor = (up_num / down_num) / (up_amount / down_amount)
        factor = factor.iloc[factor.index.indexer_at_time(trade_stop_time)].to_frame()
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'


        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor