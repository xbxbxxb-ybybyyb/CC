from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_10_no_st(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'low_alla_daily_' + minute_to_daily_tag
        name2 = 'high_alla_daily_' + minute_to_daily_tag
        name3 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, name3, 'stopping_alla_daily', 'limit_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=120, **kwargs)

    def on_bar(self, data_dict):
        # as follows
        st_stock_list = self.get_mdconstant('st_stock_list')
        low_alla_daily_trun = data_dict['low_alla_daily_' + minute_to_daily_tag]
        high_alla_daily_trun = data_dict['high_alla_daily_' + minute_to_daily_tag]
        close_alla_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag]
        stopping_alla_daily = data_dict['stopping_alla_daily']
        limit_alla_daily = data_dict['limit_alla_daily']
        close_alla_daily_trun = close_alla_daily_trun.reindex(limit_alla_daily.index)

        high_alla_daily_trun = high_alla_daily_trun[high_alla_daily_trun.columns.difference(st_stock_list)]
        low_alla_daily_trun = low_alla_daily_trun[low_alla_daily_trun.columns.difference(st_stock_list)]
        close_alla_daily_trun = close_alla_daily_trun[close_alla_daily_trun.columns.difference(st_stock_list)]
        limit_alla_daily = limit_alla_daily[limit_alla_daily.columns.difference(st_stock_list)]
        stopping_alla_daily = stopping_alla_daily[stopping_alla_daily.columns.difference(st_stock_list)]

        limit_judgement1 = (low_alla_daily_trun == stopping_alla_daily)  # 判断截止到1449，股票是否曾经触及跌停
        limit_judgement2 = (high_alla_daily_trun == limit_alla_daily)  # 判断截止到1449，股票是否曾经触及涨停
        limit_judgement3 = (close_alla_daily_trun == limit_alla_daily)  # 判断股票尾盘是否涨停
        limit_judgement4 = (close_alla_daily_trun == stopping_alla_daily)  # 判断股票尾盘是否涨停
        
        
        factor = (limit_judgement1.sum(axis=1) - limit_judgement2.sum(axis=1) + limit_judgement3.sum(axis=1) - limit_judgement4.sum(axis=1)) / low_alla_daily_trun.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor