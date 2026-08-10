from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_13(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'high_000905.SH_daily_' + minute_to_daily_tag
        name2 = 'low_000905.SH_daily_' + minute_to_daily_tag
        name3 = 'volume_000905.SH_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, name3]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, data_dict):
        # EMV技术指标，在500上用500数据好，300上500和1000差不多，50上1000数据好
        high_spot_daily_1449 = data_dict['high_000905.SH_daily_' + minute_to_daily_tag]
        low_spot_daily_1449 = data_dict['low_000905.SH_daily_' + minute_to_daily_tag]
        volume_spot_daily_1449 = data_dict['volume_000905.SH_daily_' + minute_to_daily_tag]
        

        mid_pt_move = ts_delta(high_spot_daily_1449 + low_spot_daily_1449, 1) / 2
        box_ratio = volume_spot_daily_1449 / (high_spot_daily_1449 - low_spot_daily_1449)
        emv = mid_pt_move / box_ratio
        factor = -emv.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor