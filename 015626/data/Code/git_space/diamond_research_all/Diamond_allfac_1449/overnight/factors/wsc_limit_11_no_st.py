from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_11_no_st(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票今天开盘继续涨停比例
        st_stock_list = self.get_mdconstant('st_stock_list')
        close_alla_daily = data_dict['close_alla_daily']
        open_alla_daily_trun = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']

        open_alla_daily_trun = open_alla_daily_trun[open_alla_daily_trun.columns.difference(st_stock_list)]
        close_alla_daily = close_alla_daily[close_alla_daily.columns.difference(st_stock_list)]
        limit_alla_daily = limit_alla_daily[limit_alla_daily.columns.difference(st_stock_list)]

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement2 = (open_alla_daily_trun == limit_alla_daily)  # 判断开盘时股票是否涨停
        limit_judgement3 = limit_judgement1.shift(1) * limit_judgement2
        
        
        factor = -limit_judgement3.sum(axis=1) / close_alla_daily.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor