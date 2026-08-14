from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinuteCloseDiff(BaseFactor):
    '''
    * 逻辑：主要在于尾盘1小时的close与不同分钟周期（5,10,20）的差异性，越临近收盘差异对第二天的影响更大
    * 因子参数：MinuteOpen分钟开盘价，收盘价，最高价，最低价，与分钟数据状态位
    * 作者：肖倩
    * 日期：2019.04.16
    * 函数修改日期：2020.01.08
    * 修改人：游加平       
    '''
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.sw_indcode1"]
    lag = 4
    reform_window = 21
    fmt = '%Y-%m-%d'
    weight = np.array([i/120 for i in range(0,60)])

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        industry_code = database.depend_data['FactorData.Basic_factor.sw_indcode1']

        date_list = sorted(np.unique(volume.index.strftime(self.fmt)))
        diff_list = []
        for date in date_list:
            diff_list.append(self.help_func(volume.loc[date], amt.loc[date]))
        diff_array = np.array(diff_list)
        df_close = np.nanmean(diff_array, axis=0) / np.nanstd(diff_array, axis=0, ddof=1)
        df_close = pd.Series(df_close, index=volume.columns)
        industry_code_date = industry_code.loc[date_list[-1].replace("-","")]
        industry_list = np.unique(industry_code_date.dropna().values).tolist()
        ans = pd.Series(0., index=volume.columns)
        for industry in industry_list:
            stocks = industry_code_date[industry_code_date==industry].index
            ans.loc[stocks] = df_close.loc[stocks].rank(ascending=True, pct=True).fillna(0.)
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return 1. - temp_result / temp_result.shift(self.reform_window-1)

    def help_func(self, volume, amt):
        vwap = amt.values / volume.values
        vwap = pd.DataFrame(vwap, index=volume.index, columns=volume.columns)
        minVwap5m = vwap.rolling(window=5, min_periods=1).mean()
        minVwap10m = vwap.rolling(window=10, min_periods=1).mean()
        minVwap30m = vwap.rolling(window=30, min_periods=1).mean()
        diff = vwap.values - (minVwap5m.values + minVwap10m.values + minVwap30m.values) / 3.
        volume_ratio = volume.values / np.nansum(volume.values, axis=0)
        volume_ratio[np.isinf(volume_ratio)] = np.nan
        prod = (diff*volume_ratio)[-60:]
        diff_weight = np.nansum((prod.T*self.weight).T, axis=0)
        return diff_weight.tolist()