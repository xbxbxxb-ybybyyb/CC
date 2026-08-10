
from overnight.utility import *
from overnight.naming_config import *
from overnight.factor_generator import FactorGenerator


class wsc_pv_38_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # dbcd技术指标，对沪深300指数，先计算当下分钟价格和过去n分钟价格均值的pct_chg，再对该值求ts_delta
        # 总之就是当下价格和过去一段时间价格之比，比值越大因子值越小，反转因子
        close_spot_if = data_dict['close_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        
        n = 5
        m = 16
        bias = close_spot_if / ts_mean(close_spot_if, n) - 1
        bias_diff = ts_delta(bias, m)
        factor_raw = get_single_minute_data(bias_diff, trade_stop_time)
        factor_mean = ts_mean(factor_raw, 5)
        factor = -factor_mean.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor


