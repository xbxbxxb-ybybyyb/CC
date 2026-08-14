from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np

class GTJA_064(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj", "FactorData.Basic_factor.vwap", "FactorData.Basic_factor.volume",
                   "FactorData.Basic_factor.adjfactor", "FactorData.Basic_factor.is_valid"]
    cn1 = 4
    dn = 4
    cn2 = 4
    n = 13
    dcn = 14
    mn = 60
    look_back = cn2 + n + dcn -1   
    lag = mn + look_back

    def calc_single(self, database):
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        vwap = database.depend_data['FactorData.Basic_factor.vwap'] 
        volume = database.depend_data['FactorData.Basic_factor.volume']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        vwap_adj = pd.DataFrame(vwap.values * adjfactor.values, index=vwap.index, columns=vwap.columns)
        
        rank_vwap = vwap_adj.iloc[-(self.cn1+self.dn-1):].rank(axis=1, pct=True)
        rank_volume = volume.iloc[-(self.cn1+self.dn-1):].rank(axis=1, pct=True)
        corr = self.rolling_corr(rank_volume, rank_vwap, self.cn1)
        decaylinear1 = self.decaylinear(corr.values[-self.dn:])
        rank_decay1 = pd.Series(decaylinear1, index=vwap.columns).rank(pct=True)
 
        mean_volume = volume.rolling(window=self.mn).mean()
        rolling_corr = self.rolling_corr(close_adj.rank(axis=1, pct=True).iloc[-self.look_back:], mean_volume.iloc[-self.look_back:], self.cn2)
        corr_max = rolling_corr.rolling(window=self.n).max()        
        decaylinear2 = self.decaylinear(corr_max.values[-self.dcn:])
        rank_decay2 = pd.Series(decaylinear2, index=vwap.columns).rank(pct=True)

        ans = - np.maximum(rank_decay1, rank_decay2)
        ans[is_valid.iloc[-1]==0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def array_coef(self, x, y):
        x_values = x.astype(np.float64)
        y_values = y.astype(np.float64)
        x_values[np.isinf(x_values)] = np.nan
        y_values[np.isinf(y_values)] = np.nan
        nan_index = np.isnan(x_values) | np.isnan(y_values)
        x_values[nan_index] = np.nan
        y_values[nan_index] = np.nan
        delta_x = x_values - np.nanmean(x_values, axis=0)
        delta_y = y_values - np.nanmean(y_values, axis=0)
        multi = np.nanmean(delta_x * delta_y, axis=0) / (np.nanstd(delta_x, axis=0, ddof=1) * np.nanstd(delta_y, axis=0, ddof=1))
        multi[np.isinf(multi)] = np.nan
        return multi

    def rolling_corr(self, df_x, df_y, window=None):
        """"""
        assert df_x.shape[0] == df_y.shape[0], 'dims must be same'
        corr = pd.DataFrame(np.nan, index=df_x.index, columns=df_x.columns)
        if window == None or window <= 0:
            window = df_x.shape[0]
        if window <= df_x.shape[0] and window > 1:
            for idx, index in enumerate(df_x.index):
                if idx >= window - 1:
                    corr.loc[index] = self.array_coef(df_x.iloc[idx - window + 1:idx + 1].values, df_y.iloc[idx - window + 1:idx + 1].values)
        return corr

    def decaylinear(self, arr):
        n = arr.shape[0]
        weight = np.array( [2 * i / (n * (n + 1)) for i in np.arange(1, n + 1)] )
        return np.dot(arr.T, weight)





