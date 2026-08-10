from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_11(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_000016.SH_daily_' + minute_to_daily_tag
        name2 = 'volume_000016.SH_daily_' + minute_to_daily_tag
        required_columns=[name1, name2]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=15, **kwargs)

    def on_bar(self, data_dict):
        '''ROBV技术指标'''
        '''用000905的数据表现不好，用000016的数据效果最好'''
        volume_000016_daily_trun = data_dict['volume_000016.SH_daily_' + minute_to_daily_tag]
        close_000016_daily_trun = data_dict['close_000016.SH_daily_' + minute_to_daily_tag]

        close_diff = np.sign(ts_delta(close_000016_daily_trun, 1))
        robv = volume_000016_daily_trun * close_diff
        factor = ts_sum(robv, 20)    
        factor = -factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor