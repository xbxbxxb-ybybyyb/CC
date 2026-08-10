from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *
from joblib import Parallel, delayed



def ts_reg_beta1(df1, d):
    output = pd.Series(np.nan, index=df1.index, name=df1.name)
    temp_y = df1.values
    temp_y = rolling_window(temp_y, d)
    temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
    y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
    x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
    flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
    flag = np.where(flag <= d - int(d / 2), 1, np.nan)
    output.iloc[d - 1:] = (y / x) * flag
    return output

# 成分股因子截面切割多进程
def multi_processin_joblib(df, func, n_jobs=12, **kwargs):
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T


class wsc12_cfg_search_ws_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc12_cfg_search_ws_if, self).__init__(required_columns=['close_hs300', 'weight_hs300'],
                                                     lookback_bars=3000)

    def on_bar(self, data):
        # mask
        stk_weight = data['weight_hs300']

        # 算子搜索
        stk_close = data['close_hs300']
        factor_init = multi_processin_joblib(stk_close, ts_reg_beta1, 16, d=40)
        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        factor = ts_rank(factor_mean, 240*5)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
