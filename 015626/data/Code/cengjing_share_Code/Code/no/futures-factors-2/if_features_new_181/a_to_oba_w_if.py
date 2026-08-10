from future_factor import FutureFactor
import pandas as pd
import numpy as np
import bottleneck as bk
from help_functions_wsc import replace_zero


class a_to_oba_w_if(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 0
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'SellTradeMoney', 'buy_lo_amount', 'weight']
    normalize_size = 0
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '(-0.75,1]'
    handle_preadj = False

    def calculate(self, data):
        amount = data['BuyTradeMoney'].values[-1] + data['SellTradeMoney'].values[-1]
        buy_lo_amount = data['buy_lo_amount'].values[-1]
        weight = data['weight'].values[-1]

        temp_1 = amount / replace_zero(buy_lo_amount)
        temp_1[temp_1 > 3000] = 0
        factor = np.nansum(temp_1 * weight)
        return factor
