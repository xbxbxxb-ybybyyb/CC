from overnight.utility import *
from overnight.naming_config import *
from overnight.factor_generator import FactorGenerator


class wsc_pv_35(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_alla']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        # 先计算中证500过去60分钟下跌分钟bar的数量，再对截面求均值，下跌的分钟bar越多因子值越大，反转因子
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_close = data_dict['close_alla'][zz500_stk_list]
        stk_close = stk_close.between_time(futures_data_morning_begin, futures_data_afternoon_end)

        price_diff = ts_delta(stk_close, 1)
        price_diff_sign = (price_diff < 0) + 0.
        factor_raw = ts_sum(price_diff_sign, 60).mean(axis=1)
        factor_raw = get_single_minute_data(factor_raw, trade_stop_time)
        factor = factor_raw.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
