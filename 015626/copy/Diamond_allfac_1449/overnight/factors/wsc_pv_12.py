from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_12(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'amount_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=120, **kwargs)

    def on_bar(self, data_dict):
        # CVI技术指标，500的效果比300,800好，但是不如全A，和全A差异很小，暂时就用500
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        close_zz500_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag][zz500_stk_list]
        amount_zz500_daily_1449 = data_dict['amount_alla_daily_' + minute_to_daily_tag][zz500_stk_list]

        stk_delta_ic = ts_delta(close_zz500_daily_1449, 1)
        up_amount_ic = amount_zz500_daily_1449[stk_delta_ic > 0].sum(axis=1)
        down_amount_ic = amount_zz500_daily_1449[stk_delta_ic < 0].sum(axis=1)
        cvi = up_amount_ic - down_amount_ic
        factor = -cvi.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor