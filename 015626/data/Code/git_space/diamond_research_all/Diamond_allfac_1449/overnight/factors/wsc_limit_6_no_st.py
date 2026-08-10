from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_6_no_st(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'low_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 每个交易日跌停后又开板的股票比例
        st_stock_list = self.get_mdconstant('st_stock_list')
        close_alla_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag]
        low_alla_daily_trun = data_dict['low_alla_daily_' + minute_to_daily_tag]
        stopping_alla_daily = data_dict['stopping_alla_daily']
        close_alla_daily_trun = close_alla_daily_trun.reindex(stopping_alla_daily.index)

        close_alla_daily_trun = close_alla_daily_trun[close_alla_daily_trun.columns.difference(st_stock_list)]
        low_alla_daily_trun = low_alla_daily_trun[low_alla_daily_trun.columns.difference(st_stock_list)]
        stopping_alla_daily = stopping_alla_daily[stopping_alla_daily.columns.difference(st_stock_list)]

        limit_judgement1 = (low_alla_daily_trun == stopping_alla_daily)  # 判断截止到1449，股票是否曾经触及跌停
        limit_judgement2 = (close_alla_daily_trun == stopping_alla_daily)  # 判断截止到1449，股票是否跌停
        
        
        factor = (limit_judgement1.sum(axis=1) - limit_judgement2.sum(axis=1)) / close_alla_daily_trun.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor