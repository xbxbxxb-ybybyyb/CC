from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc19_overnight_future(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['amount_IC.CFE', 'recent_month_mask']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 交易额的日内波动
        future_amount = data_dict['amount_IC.CFE']
        future_mask = data_dict['recent_month_mask']

        amount_std = ts_std(future_amount, 230)[future_mask].sum(axis=1)
        factor = get_single_minute_data(amount_std, trade_stop_time)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor