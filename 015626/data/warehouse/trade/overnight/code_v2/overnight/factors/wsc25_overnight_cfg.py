from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc25_overnight_cfg(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'high_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 当天涨幅到达过8%但在尾盘时回落至8%以下的股票数量，动量因子(注意ts_rank的方向)
        # 分母用open效果不好，改成前一天的close以后好很多，可能是因为把前一天隔夜的信息包含进去了
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_close = data_dict['close_alla_daily_' + minute_to_daily_tag][zz500_stk_list]
        stk_high = data_dict['high_alla_daily_' + minute_to_daily_tag][zz500_stk_list]

        stk_ret = stk_close / stk_close.shift(1) - 1
        stk_ret_max = stk_high / stk_close.shift(1) - 1
        stk_ret_up_limit = stk_ret.gt(0.08)
        stk_ret_max_limit = stk_ret_max.gt(0.08)
        
        factor = stk_ret_up_limit.sum(axis=1) - stk_ret_max_limit.sum(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor