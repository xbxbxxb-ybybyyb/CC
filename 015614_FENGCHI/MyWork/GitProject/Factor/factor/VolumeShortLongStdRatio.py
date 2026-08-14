from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np

class VolumeShortLongStdRatio(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume"]
    lag = 199
    short = 10

    def calc_single(self, database):
        volume = database.depend_data['FactorData.Basic_factor.volume']

        volume_std_short = np.nanstd(volume.values[-self.short:], axis=0, ddof=1)
        volume_std_short = np.where(volume_std_short!=0., volume_std_short, np.nan)
        volume_std_long = np.nanstd(volume.values, axis=0, ddof=1)
        ans = np.log(volume_std_long / volume_std_short)

        ans = pd.Series(ans, index=volume.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans