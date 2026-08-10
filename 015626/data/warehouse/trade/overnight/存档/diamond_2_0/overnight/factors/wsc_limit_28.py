import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_28(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'preclose_alla_daily', 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天开盘平均收益率加上前一个交易日跌停的股票当天开盘平均收益率
        close_alla_daily = data_dict['close_alla_daily']
        open_alla_daily_0930 = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1 < 1] = np.nan
        limit_judgement2 = (close_alla_daily == stopping_alla_daily)  # 判断当天股票是否跌停
        limit_judgement2[limit_judgement2 < 1] = np.nan
        stk_ret = open_alla_daily_0930 / preclose_alla_daily - 1


        factor = (limit_judgement2.shift(1) * stk_ret).mean(axis=1) + (limit_judgement1.shift(1) * stk_ret).mean(axis=1)
        factor = factor.to_frame() * (-1)
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor