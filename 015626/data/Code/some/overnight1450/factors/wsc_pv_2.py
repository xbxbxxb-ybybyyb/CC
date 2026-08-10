from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_2(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 中证500过去120天成分股新高的数量
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        close_zz500_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag][zz500_stk_list]
        factor = (close_zz500_daily_1449 >= ts_max(close_zz500_daily_1449, 120)).sum(axis=1)

        factor = factor.to_frame() * (-1)
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor