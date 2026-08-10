from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc40_overnight_cfg_alla(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'low_alla_daily_' + minute_to_daily_tag
        name3 = 'high_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, name3]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 当天振幅超过8%的股票数量减去盘中最大跌幅在8%以上的股票数量
        # 分母用open效果不好，改成前一天的close以后好很多，可能是因为把前一天隔夜的信息包含进去了
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_close = data_dict['close_alla_daily_' + minute_to_daily_tag]
        stk_low = data_dict['low_alla_daily_' + minute_to_daily_tag]
        stk_high = data_dict['high_alla_daily_' + minute_to_daily_tag]

        stk_ret = stk_low / stk_close.shift(1) - 1
        stk_ret_max = stk_high / stk_low - 1
        stk_ret_up_limit = stk_ret.lt(-0.08)
        stk_ret_max_limit = stk_ret_max.gt(0.08)
        
        factor_raw = stk_ret_up_limit.sum(axis=1) - stk_ret_max_limit.sum(axis=1)
        factor = factor_raw.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor