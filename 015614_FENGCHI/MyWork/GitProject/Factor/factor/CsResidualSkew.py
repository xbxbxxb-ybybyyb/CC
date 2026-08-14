import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class CsResidualSkew(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.sw_indcode1',
                   'FactorData.Basic_factor.mkt_cap_ard', 'FactorData.Basic_factor.s_val_pb_new']
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close_min = database.depend_data['FactorData.Basic_factor.close_minute']
        ind = database.depend_data['FactorData.Basic_factor.sw_indcode1']
        cap = database.depend_data['FactorData.Basic_factor.mkt_cap_ard']
        pb = database.depend_data['FactorData.Basic_factor.s_val_pb_new']
        stk_code = close_min.columns
        y = close_min.resample('5min').last().dropna(how='all', axis=0).pct_change().values[1:].T
        ind = pd.get_dummies(ind.iloc[-1]).reindex(index=stk_code).values
        size = np.log(cap.values[-1])
        size = (size - np.nanmean(size)) / np.nanstd(size)
        value = 1 / pb.values[-1]
        value = (value - np.nanmean(value)) / np.nanstd(value)
        x = np.nan * np.ones((len(y), ind.shape[1] + 2))
        x[:, :ind.shape[1]] = ind
        x[:, -2] = size
        x[:, -1] = value
        w = (1 / (cap.values[-1] ** 0.5))
        yx = np.hstack((y, x))
        w = w[~np.isnan(yx).any(axis=1)]
        yx = yx[~np.isnan(yx).any(axis=1)]
        y_temp = yx[:, :y.shape[1]]
        x_temp = yx[:, y.shape[1]:]
        col = (x_temp != 0).any(axis=0)
        x_temp = x_temp[:, col]
        w = w * np.eye(len(w))
        b = np.linalg.inv(x_temp.T.dot(w).dot(x_temp)
                          ).dot(x_temp.T).dot(w).dot(y_temp)
        e = y - x[:, col].dot(b)
        res = -pd.DataFrame(e.T, columns=stk_code).skew()
        return res

    def reform(self, temp_result):
        a = np.arange(1, 21)
        a = a / a.sum()
        alpha = temp_result.rolling(20).apply(lambda x: (x * a).sum())
        return alpha
