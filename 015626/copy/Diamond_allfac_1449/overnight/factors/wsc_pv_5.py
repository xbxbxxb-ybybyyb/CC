from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_5(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=80, **kwargs)

    def on_bar(self, data_dict):
        '''沪深300收益率截面离散度'''
        hs300_stk_list = self.get_mdconstant('hs300_stock_list')
        close_hs300_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag][hs300_stk_list]
        
        factor = ts_pct_change(close_hs300_daily_trun, 5).std(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor