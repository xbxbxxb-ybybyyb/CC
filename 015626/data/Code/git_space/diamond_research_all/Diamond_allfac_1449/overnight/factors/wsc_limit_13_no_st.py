from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_13_no_st(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票今天尾盘继续涨停的占昨天涨停股票的比例
        st_stock_list = self.get_mdconstant('st_stock_list')
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        close_alla_daily_trun = close_alla_daily_trun.reindex(limit_alla_daily.index)

        close_alla_daily = close_alla_daily[close_alla_daily.columns.difference(st_stock_list)]
        close_alla_daily_trun = close_alla_daily_trun[close_alla_daily_trun.columns.difference(st_stock_list)]
        limit_alla_daily = limit_alla_daily[limit_alla_daily.columns.difference(st_stock_list)]

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement2 = (close_alla_daily_trun == limit_alla_daily)  # 判断截止到1449，股票是否涨停
        limit_judgement3 = limit_judgement1.shift(1) * limit_judgement2
        
        
        factor = -limit_judgement3.sum(axis=1) / limit_judgement1.shift(1).sum(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor