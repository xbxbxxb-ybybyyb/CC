from overnight.utility import *
from overnight.naming_config import *
from overnight.factor_generator import FactorGenerator


class wsc_pv_33_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_alla']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        # 沪深300上涨股票与下跌股票过去30分钟的平均收益率之比，比值越小因子值越大，反转因子
        hs300_stk_list = self.get_mdconstant('hs300_stock_list')
        stk_close = data_dict['close_alla'][hs300_stk_list]
        stk_close = stk_close.between_time(futures_data_morning_begin, futures_data_afternoon_end)

        stk_ret = ts_pct_change(stk_close, 30)
        stk_ret = get_single_minute_data(stk_ret, trade_stop_time)
        stk_ret_up = stk_ret[stk_ret>0].mean(axis=1)
        stk_ret_down = stk_ret[stk_ret<0].mean(axis=1)
        factor_raw = stk_ret_up / abs(stk_ret_down)  # 加绝对值是因为stk_ret_down<0
        factor = -factor_raw.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
