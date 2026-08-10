from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc28_overnight_cfg(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'low_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 当天涨幅一度小于7%，但尾盘还是大于7%的股票数量，反转因子(注意ts_rank的方向)
        # 分母用open效果不好，改成前一天的close以后好很多，可能是因为把前一天隔夜的信息包含进去了
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_close = data_dict['close_alla_daily_' + minute_to_daily_tag][zz500_stk_list]
        stk_low = data_dict['low_alla_daily_' + minute_to_daily_tag][zz500_stk_list]

        stk_ret = stk_close / stk_close.shift(1) - 1
        stk_ret_min = stk_low / stk_close.shift(1) - 1
        stk_ret_up_limit = stk_ret.gt(0.07)
        stk_ret_min_limit = stk_ret_min.gt(0.07)
        
        factor = stk_ret_min_limit.sum(axis=1) - stk_ret_up_limit.sum(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor