from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time

class TurnPEStd(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.pe_ttm",
                   "FactorData.Basic_factor.amt", 
                   "FactorData.Basic_factor.free_float_shares", 
                   "FactorData.Basic_factor.close",
                   "FactorData.Basic_factor.sw_indcode1","FactorData.Basic_factor.is_valid_raw"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 15
    reform_window = 10

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        # missing is_valid_raw data
        pe_ttm = database.depend_data['FactorData.Basic_factor.pe_ttm']
        amt_by_yuan = database.depend_data['FactorData.Basic_factor.amt']
        free_float_cap = database.depend_data['FactorData.Basic_factor.free_float_shares'] * database.depend_data['FactorData.Basic_factor.close']
        industry_code_all = database.depend_data['FactorData.Basic_factor.sw_indcode1'].iloc[-1,:]
        is_valid_raw = database.depend_data['FactorData.Basic_factor.is_valid_raw']
        # print(industry_code_all)

        flag = pd.DataFrame((is_valid_raw.values == 1), index=pe_ttm.index, columns=pe_ttm.columns) 
        
        signal = pe_ttm[flag] * (amt_by_yuan[flag] / free_float_cap)
        # neutralSignal = []
        # industry_code_all.index = signal.index
        # signal[~np.isfinite(signal)] = np.nan
        # for i in industry_code_all.index:
        #     signal_at_i = signal.loc[i, :]
        #     industry_code_at_i = industry_code_all.loc[i, :]
        #     stockPool = ~signal_at_i.isna()
        #     indusDummies = pd.get_dummies(industry_code_at_i[stockPool])
        #     indusSignal = np.dot(indusDummies.T.divide(indusDummies.T.sum(axis = 1), axis = 0), signal_at_i[stockPool])
        #     signal_at_i[stockPool] = signal_at_i[stockPool] / np.dot(indusDummies, indusSignal)
        #     signal_at_i[~np.isfinite(signal_at_i)] = np.nan
        #     neutralSignal.append(signal_at_i)
        # neutralSignal = pd.concat(neutralSignal, axis = 1).T
        # neutralSignal.index = industry_code_all.index
        # signal = neutralSignal
        
        # signal = signal.subtract(signal.mean(axis = 1), axis = 0).divide(signal.std(axis = 1), axis = 0)
        # signal = -1 * signal.std(axis = 0)
        # signal.name = pe_ttm.index[-1]  
        
        # return signal
        alpha = signal.iloc[-1,:]
        industry_list = industry_code_all.fillna(0).unique().tolist()
        industry_list.remove(0)
        for i in industry_list:
            selection = pd.Series(industry_code_all.values==i, index=industry_code_all.index)
            alpha[selection] = alpha[selection].divide(alpha[selection].mean())
        
        alpha = alpha.subtract(alpha.mean()).divide(alpha.std())
        # alpha = -1 * alpha.rolling(window=n, min_periods=n).std()
        # alpha = -1 * alpha.std()

        return alpha


    def  reform(self, temp_result):
        A = temp_result.rolling(self.reform_window, min_periods=self.reform_window).std()
        A = pd.DataFrame(-1.*A.values, index=A.index, columns=A.columns,)
        return A
