from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class DownVolRatioDiff30(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']

        ret = close.values[1:] / close.values[:-1] - 1.
        ret_an = ret[:29] 
        ret_pn = ret[-30:]
        an = np.nansum(np.where(ret_an<0.,1,np.nan)*volume.values[1:30], axis=0) / np.nansum(volume.values[1:30], axis=0)
        pn = np.nansum(np.where(ret_pn<0.,1,np.nan)*volume.values[-30:], axis=0) / np.nansum(volume.values[-30:], axis=0)
        ans = pn / an
        ans = pd.Series(ans, index=close.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans