from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *

class wsc38_overnight_cfg(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'low_alla_daily_' + minute_to_daily_tag
        name2 = 'high_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # high/low的成分股版本变种，对0.13这个参数比较敏感，要注意下
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_low = data_dict['low_alla_daily_' + minute_to_daily_tag][zz500_stk_list]
        stk_high = data_dict['high_alla_daily_' + minute_to_daily_tag][zz500_stk_list]

        high_to_low = stk_high / stk_low -1
        factor = (high_to_low.gt(0.13)+0).sum(axis=1).to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor