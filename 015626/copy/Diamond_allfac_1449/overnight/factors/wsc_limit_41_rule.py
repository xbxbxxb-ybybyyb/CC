import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_41_rule(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天平均收益率(包含隔夜收益)
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']
        close_alla_daily_trun = close_alla_daily_trun.reindex(limit_alla_daily.index)

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1<1] = np.nan
        stk_ret = close_alla_daily_trun / preclose_alla_daily - 1


        factor = (limit_judgement1.shift(1) * stk_ret).mean(axis=1)
        factor[factor<0.008] = 0.875
        factor[factor<0.875] = 0
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor