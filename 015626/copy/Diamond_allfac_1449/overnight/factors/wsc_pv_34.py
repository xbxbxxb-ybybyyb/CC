from overnight.utility import *
from overnight.naming_config import *
from overnight.factor_generator import FactorGenerator


class wsc_pv_34(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_alla']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 先计算中证500的5分钟收益率在过去120分钟的排名，再对整个截面取均值，均值越大因子值越小，反转因子
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_close = data_dict['close_alla'][zz500_stk_list]
        stk_close = stk_close.between_time(futures_data_morning_begin, futures_data_afternoon_end)

        stk_ret = ts_pct_change(stk_close, 5)
        ret_rank = ts_rank(stk_ret, 120)
        ret_rank = get_single_minute_data(ret_rank, trade_stop_time)
        factor_raw = ret_rank.mean(axis=1)
        factor = -factor_raw.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
