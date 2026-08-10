from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_4_no_st(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        name2 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'limit_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, data_dict):
        # 每个交易日尾盘和开盘涨停的股票比例之差
        st_stock_list = self.get_mdconstant('st_stock_list')
        open_alla_daily_trun = data_dict['open_alla_daily_' + minute_to_daily_tag]
        close_alla_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        close_alla_daily_trun = close_alla_daily_trun.reindex(limit_alla_daily.index)

        open_alla_daily_trun = open_alla_daily_trun[open_alla_daily_trun.columns.difference(st_stock_list)]
        close_alla_daily_trun = close_alla_daily_trun[close_alla_daily_trun.columns.difference(st_stock_list)]
        limit_alla_daily = limit_alla_daily[limit_alla_daily.columns.difference(st_stock_list)]

        limit_judgement1 = (open_alla_daily_trun == limit_alla_daily)  # 判断股票开盘是否涨停
        limit_judgement2 = (close_alla_daily_trun == limit_alla_daily)  # 判断股票尾盘是否涨停
        
        factor = (limit_judgement1.sum(axis=1) - limit_judgement2.sum(axis=1)) / open_alla_daily_trun.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor