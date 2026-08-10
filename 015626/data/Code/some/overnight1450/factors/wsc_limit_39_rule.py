from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_39_rule(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'low_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        '''盘中一度达到跌停的股票比例'''
        '''中枢不稳定'''
        low_alla_daily_trun = data_dict['low_alla_daily_' + minute_to_daily_tag]
        stopping_alla_daily = data_dict['stopping_alla_daily']

        limit_judgement1 = (low_alla_daily_trun == stopping_alla_daily)  # 判断股票是否一度达到跌停
        
        factor = limit_judgement1.sum(axis=1) / stopping_alla_daily.count(axis=1)
        factor[factor<0.02] = 0
        factor[factor>0] = 0.875
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor