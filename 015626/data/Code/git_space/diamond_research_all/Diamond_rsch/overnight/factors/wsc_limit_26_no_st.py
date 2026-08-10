import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_26_no_st(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'stopping_alla_daily', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日跌停的股票当天平均收益率(包含隔夜收益)
        st_stock_list = self.get_mdconstant('st_stock_list')
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag]
        stopping_alla_daily = data_dict['stopping_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']
        close_alla_daily_trun = close_alla_daily_trun.reindex(stopping_alla_daily.index)

        close_alla_daily_trun = close_alla_daily_trun[close_alla_daily_trun.columns.difference(st_stock_list)]
        close_alla_daily = close_alla_daily[close_alla_daily.columns.difference(st_stock_list)]
        preclose_alla_daily = preclose_alla_daily[preclose_alla_daily.columns.difference(st_stock_list)]
        stopping_alla_daily = stopping_alla_daily[stopping_alla_daily.columns.difference(st_stock_list)]

        limit_judgement1 = (close_alla_daily == stopping_alla_daily)  # 判断当天股票是否跌停
        limit_judgement1[limit_judgement1<1] = np.nan
        stk_ret = close_alla_daily_trun / preclose_alla_daily - 1


        factor = -(limit_judgement1.shift(1) * stk_ret).mean(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor