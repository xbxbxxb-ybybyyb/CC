import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from operators_all_wsc import cross_hub_num

# ss1_zf
class fac_48_2_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'high', 'second_main_mask']

        super(fac_48_2_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc, ddd):
        
        mask = data['second_main_mask']
        unit = int((mask.index[-1] - mask.index[-2]).total_seconds() / 60)

        aaa = np.max([int(2 / unit), 1])
        bbb = np.max([int(15 / unit), 10])
        ccc = 3
        ddd = 3
        
        rtn = data['close'] - data['close'].shift(aaa)
        vol = rtn.rolling(10, min_periods=1).std()
        vol[vol < 1e-8] = np.nan
        
        ret = data['close'] - (data['high'].shift(aaa).rolling(bbb, min_periods=1).max()) - 1
        co = cross_hub_num(vol, 10) + 1
        sig = (ret / (vol) / np.sqrt(co)).rolling(ccc, min_periods = 1).mean()[mask].mean(axis = 1)
        sig = ts_rank(sig, int(2000/unit))
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
