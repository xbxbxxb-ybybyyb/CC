from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_ti2_spot(FutureFactor):
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'amount']}
    normalize_size = 950
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-60:]
        spot_high = data['high_000905.SH'].values[-60:]
        spot_low = data['low_000905.SH'].values[-60:]
        spot_amount = data['amount_000905.SH'].values[-60:]
        x = replace_zero(spot_high - spot_low)
        amount_adj = (2 * spot_close - spot_high - spot_low) / x * spot_amount
        factor_raw = ts_sum(amount_adj, 60)
        return factor_raw[-1]
