from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_1(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'amount_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'float_share_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, data_dict):
        # 中证800换手率
        zz800_stk_list = self.get_mdconstant('zz800_stock_list')
        close_zz800_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag][zz800_stk_list]
        amount_zz800_daily_1449 = data_dict['amount_alla_daily_' + minute_to_daily_tag][zz800_stk_list]
        float_share_zz800_daily = data_dict['float_share_alla_daily'][zz800_stk_list]
        daily_market_value = (float_share_zz800_daily * close_zz800_daily_1449).sum(axis=1)
        daily_amount = amount_zz800_daily_1449.sum(axis=1)

        factor = daily_amount / replace_zero(daily_market_value)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor