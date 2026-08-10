from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_18(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'low_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日跌停的股票今天一度触发跌停的比例
        close_alla_daily = data_dict['close_alla_daily']
        low_alla_daily_trun = data_dict['low_alla_daily_' + minute_to_daily_tag]
        stopping_alla_daily = data_dict['stopping_alla_daily']

        limit_judgement1 = (close_alla_daily == stopping_alla_daily)  # 判断当天股票是否跌停
        limit_judgement2 = (low_alla_daily_trun == stopping_alla_daily)  # 判断当天股票是否一度触发跌停
        limit_judgement3 = limit_judgement1.shift(1) * limit_judgement2  # 前一交易日跌停的股票今天开盘是否继续跌停
        
        
        factor = limit_judgement3.sum(axis=1) / close_alla_daily.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor