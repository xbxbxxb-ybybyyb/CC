from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_16_no_st(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=120, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日跌停的股票今天开盘继续跌停的数量占昨天跌停股票的比例
        st_stock_list = self.get_mdconstant('st_stock_list')
        close_alla_daily = data_dict['close_alla_daily']
        open_alla_daily_trun = data_dict['open_alla_daily_' + minute_to_daily_tag]
        stopping_alla_daily = data_dict['stopping_alla_daily']

        open_alla_daily_trun = open_alla_daily_trun[open_alla_daily_trun.columns.difference(st_stock_list)]
        close_alla_daily = close_alla_daily[close_alla_daily.columns.difference(st_stock_list)]
        stopping_alla_daily = stopping_alla_daily[stopping_alla_daily.columns.difference(st_stock_list)]

        limit_judgement1 = (close_alla_daily == stopping_alla_daily)  # 判断当天股票是否跌停
        limit_judgement2 = (open_alla_daily_trun == stopping_alla_daily)  # 判断开盘时股票是否跌停
        limit_judgement3 = limit_judgement1.shift(1) * limit_judgement2  # 前一交易日跌停的股票今天开盘是否继续跌停
        
        
        factor = -limit_judgement3.sum(axis=1) / limit_judgement1.shift(1).sum(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor