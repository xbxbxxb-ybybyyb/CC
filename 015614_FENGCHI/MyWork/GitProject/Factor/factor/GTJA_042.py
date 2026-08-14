from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util


class GTJA_042(BaseFactor):

        factor_type = "DAY"
        depend_data = ["FactorData.Basic_factor.high","FactorData.Basic_factor.volume",
        "FactorData.Basic_factor.adjfactor","FactorData.Basic_factor.is_valid"]

        lag = 10

        def calc_single(self,database):
            adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
            is_valid = database.depend_data['FactorData.Basic_factor.is_valid'].values
            volume = database.depend_data['FactorData.Basic_factor.volume']/adjfactor
            high = database.depend_data['FactorData.Basic_factor.high'] * adjfactor

            high_std = high.rolling(window=self.lag,min_periods=1).std()
            part1 = -high_std.rank(axis=1,pct=True).values
            high_valid = pd.DataFrame(np.where(is_valid==1,high.values,np.nan),index=high.index,columns=high.columns)
            part2 = Util.rolling_corr(high_valid,volume,self.lag).values

            alpha = part1[-1]*part2[-1]
            alpha[~np.isfinite(alpha)] = np.nan
            alpha[is_valid[-1]==0] = np.nan

            return pd.Series(alpha,index=high.columns)

