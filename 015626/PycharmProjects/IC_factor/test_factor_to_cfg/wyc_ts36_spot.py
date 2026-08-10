from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts36_spot(FactorGenerator):
    def __init__(self):

        required_columns=['high_spot','low_spot','volume','amount']
        lookback_bars=2000
        super(wyc_ts36_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        factor = ts_rank_bk(delta((df['high_spot'] + df['low_spot'] + df['amount']/df['volume']), 60), 60)

        factor = ts_rank_bk(factor, 242 * 2)
        factor = ts_mean(factor, 200)

        return factor