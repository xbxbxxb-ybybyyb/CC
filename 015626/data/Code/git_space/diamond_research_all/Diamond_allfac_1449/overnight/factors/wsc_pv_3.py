from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_3(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'amount_000905.SH_daily_' + minute_to_daily_tag
        required_columns=[name1]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=120, **kwargs)

    def on_bar(self, data_dict):
        '''VOLCHG技术指标'''
        amount_000905_daily_trun = data_dict['amount_000905.SH_daily_' + minute_to_daily_tag]

        factor = amount_000905_daily_trun / ts_mean(amount_000905_daily_trun, 20) - 1        
        factor = -factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor