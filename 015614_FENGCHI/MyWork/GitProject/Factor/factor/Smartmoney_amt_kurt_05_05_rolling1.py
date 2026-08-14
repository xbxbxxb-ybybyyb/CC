from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import pandas as pd
from copy import deepcopy

class Smartmoney_amt_kurt_05_05_rolling1(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.limit_status_minute",
                   "FactorData.Basic_factor.low_minute","FactorData.Basic_factor.high_minute","FactorData.Basic_factor.amt_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=2
    reform_window=5
    batch_info = {'filter_thrsh': 0.5,
   'n': 1,
   'object_name': 'amt',
   'ratio_beta': 0.5,
   'stat': 'kurt'}
    rolling_days = batch_info['n']
    filter_thrsh = batch_info['filter_thrsh']
    object_name = batch_info['object_name']  # 要使用的对象名
    stat_name = batch_info['stat']  # 要计算的统计特征
    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']

        def raise_error():
            raise Exception

        # 获取dataframe列均值的函数
        def get_mean(df):
            return pd.Series(np.nanmean(df, axis=0), index=df.columns)

        # 获取dataframe列标准差的函数
        def get_std(df):
            return pd.Series(np.nanstd(df, axis=0), index=df.columns)

        # 获取dataframe列峰度的函数
        def get_kurt(df):
            return df.kurt(axis=0)

        # 获取dataframe列偏度的函数
        def get_skew(df):
            return df.skew(axis=0)

        # 获取dataframe列（均值/标准差）的函数
        def get_ms(df):
            avg = pd.Series(np.nanmean(df, axis=0), index=df.columns)
            std = pd.Series(np.nanstd(df, axis=0), index=df.columns)
            cv = pd.Series(std.values / avg.values, index=avg.index)
            std[pd.Series(cv.values < 0.00001, index=cv.index)] = np.nan
            ms = pd.Series(avg.values / std.values, index=avg.index)
            return ms

        # 获取dataframe列自相关系数的函数
        def get_scm(df):
            def get_corresponding_corr(x_df, y_df):
                x_df.dropna(how='all', inplace=True)
                y_df.dropna(how='all', inplace=True)
                common_idx = sorted(list(set(x_df.index).intersection(set(y_df.index))))
                x_df = x_df.reindex(common_idx)
                y_df = y_df.reindex(common_idx)
                common_columns = sorted(list(set(x_df.columns).intersection(set(y_df.columns))))
                x_df = x_df[common_columns]
                y_df = y_df[common_columns]

                subdf1_array = x_df.values
                subdf2_array = y_df.values
                subcorr = np.nanmean(
                    (subdf1_array - np.nanmean(subdf1_array, axis=0)) * (
                            subdf2_array - np.nanmean(subdf2_array, axis=0)),
                    axis=0) / (np.nanstd(subdf1_array, axis=0) * np.nanstd(subdf2_array, axis=0))
                subcorr = pd.Series(subcorr, index=x_df.columns)
                return subcorr

            half_length = df.shape[0] // 2;
            idx_fh = df.index[:half_length];
            idx_lh = df.index[half_length:];
            df_fh = df.loc[idx_fh, :].reset_index(drop=True);
            df_lh = df.loc[idx_lh, :].reset_index(drop=True);
            self_corr = get_corresponding_corr(df_fh, df_lh)
            scm = self_corr
            return scm

        # 获取dataframe列时序beta的函数，由于各列解释变量x一样，此处直接简化求的协方差
        def get_tb(df):
            # 由于解释变量x一样，所以用协方差替代
            def get_corresponding_cov(x_df, y_df):
                x_df.dropna(how='all', inplace=True)
                y_df.dropna(how='all', inplace=True)
                common_idx = sorted(list(set(x_df.index).intersection(set(y_df.index))))
                x_df = x_df.reindex(common_idx)
                y_df = y_df.reindex(common_idx)
                common_columns = sorted(list(set(x_df.columns).intersection(set(y_df.columns))))
                x_df = x_df[common_columns]
                y_df = y_df[common_columns]

                subdf1_array = x_df.values
                subdf2_array = y_df.values
                subcov = np.nanmean(
                    (subdf1_array - np.nanmean(subdf1_array, axis=0)) * (
                            subdf2_array - np.nanmean(subdf2_array, axis=0)),
                    axis=0)
                subcov = pd.Series(subcov, index=x_df.columns)
                return subcov

            time_idx = deepcopy(df)
            time_idx[:] = np.tile(np.array(range(time_idx.shape[0])), (time_idx.shape[1], 1)).T
            time_cov = get_corresponding_cov(df, time_idx)
            return time_cov

        # 获取dataframe列最小值的函数
        def get_min(df):
            return pd.Series(np.nanmin(df, axis=0), index=df.columns)

        # 获取dataframe列最大值的函数
        def get_max(df):
            return pd.Series(np.nanmax(df, axis=0), index=df.columns)

        # 获取dataframe每列差分的函数
        def get_dm(df):
            df_delta = df.values - df.shift(1).values
            return pd.Series(np.nanmean(df_delta, axis=0), index=df.columns)

        # 获取dataframe列排序后的自相关系数的函数
        def get_srcm(df):
            def get_corresponding_corr(x_df, y_df):
                x_df.dropna(how='all', inplace=True)
                y_df.dropna(how='all', inplace=True)
                common_idx = sorted(list(set(x_df.index).intersection(set(y_df.index))))
                x_df = x_df.reindex(common_idx)
                y_df = y_df.reindex(common_idx)
                common_columns = sorted(list(set(x_df.columns).intersection(set(y_df.columns))))
                x_df = x_df[common_columns]
                y_df = y_df[common_columns]

                subdf1_array = x_df.values
                subdf2_array = y_df.values
                subcorr = np.nanmean(
                    (subdf1_array - np.nanmean(subdf1_array, axis=0)) * (
                            subdf2_array - np.nanmean(subdf2_array, axis=0)),
                    axis=0) / (np.nanstd(subdf1_array, axis=0) * np.nanstd(subdf2_array, axis=0))
                subcorr = pd.Series(subcorr, index=x_df.columns)
                return subcorr

            df = df.rank(axis=1, pct=True)
            half_length = df.shape[0] // 2;
            idx_fh = df.index[:half_length];
            idx_lh = df.index[half_length:];
            df_fh = df.loc[idx_fh, :].reset_index(drop=True);
            df_lh = df.loc[idx_lh, :].reset_index(drop=True);
            self_corr = get_corresponding_corr(df_fh, df_lh)
            return self_corr

        # 获取dataframe列排序后的时序beta的函数，由于各列解释变量x一样，此处直接简化求的协方差
        def get_trb(df):
            def get_corresponding_cov(x_df, y_df):
                x_df.dropna(how='all', inplace=True)
                y_df.dropna(how='all', inplace=True)
                common_idx = sorted(list(set(x_df.index).intersection(set(y_df.index))))
                x_df = x_df.reindex(common_idx)
                y_df = y_df.reindex(common_idx)
                common_columns = sorted(list(set(x_df.columns).intersection(set(y_df.columns))))
                x_df = x_df[common_columns]
                y_df = y_df[common_columns]

                subdf1_array = x_df.values
                subdf2_array = y_df.values
                subcov = np.nanmean(
                    (subdf1_array - np.nanmean(subdf1_array, axis=0)) * (
                            subdf2_array - np.nanmean(subdf2_array, axis=0)),
                    axis=0)
                subcov = pd.Series(subcov, index=x_df.columns)
                return subcov

            df = df.rank(axis=1, pct=True)
            time_idx = deepcopy(df)
            time_idx[:] = np.tile(np.array(range(time_idx.shape[0])), (time_idx.shape[1], 1)).T
            time_cov = get_corresponding_cov(df, time_idx)
            return time_cov

        # 获取dataframe每列排序后差分的函数
        def get_rdm(df):
            df = df.rank(axis=1, pct=True)
            df_delta = df.values - df.shift(1).values
            return pd.Series(np.nanmean(df_delta, axis=0), index=df.columns)

        statistic_choice = {
            'mean': get_mean,
            'std': get_std,
            'skew': get_skew,
            'kurt': get_kurt,
            'ms': get_ms,
            'scm': get_scm,
            'tb': get_tb,
            'max': get_max,
            'min': get_min,
            'dm': get_dm,
            'srcm': get_srcm,
            'trb': get_trb,
            'rdm': get_rdm
        }

        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        close = min_forward_adj(close)
        high = data_filter(database.depend_data['FactorData.Basic_factor.high_minute'],limit_status,method='minute')
        high = min_forward_adj(high)
        low =data_filter(database.depend_data['FactorData.Basic_factor.low_minute'],limit_status,method='minute')
        low = min_forward_adj(low)
        volume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'],limit_status,method='minute')
        amt = data_filter(database.depend_data['FactorData.Basic_factor.amt_minute'],limit_status,method='minute')

        switchcase_rawdata = {
            "close": close,
            "volume": volume,
            "amt": amt,
            "hlratio": pd.DataFrame(high.values / low.values, index=high.index, columns=high.columns),
            "ret": pd.DataFrame(close.values / close.shift(1).values - 1, index=close.index,
                                columns=close.columns).fillna(0),
            "time_id": pd.DataFrame(np.tile(range(close.shape[0]), (close.shape[1], 1)).T, index=close.index,
                                    columns=close.columns)
        }
        min_ret = pd.DataFrame(close.values / close.shift(1).values - 1, index=close.index,
                               columns=close.columns)
        S_ratio = np.abs(min_ret) / (np.sqrt(volume))
        S_ratio_rank = S_ratio.rank(axis=0, pct=True, ascending=False, method='dense')
        Smart_money_part = S_ratio_rank[pd.DataFrame(S_ratio_rank.values < self.filter_thrsh, index=S_ratio_rank.index,
                                                     columns=S_ratio_rank.columns)].fillna(0)
        raw_data = switchcase_rawdata[self.object_name].fillna(0)
        Smart_money_raw_data = pd.DataFrame(raw_data.values * Smart_money_part.values, index=raw_data.index,
                                            columns=raw_data.columns)
        Smart_money_stat = statistic_choice.get(self.stat_name, raise_error)(Smart_money_raw_data)
        tot_stat = statistic_choice.get(self.stat_name, raise_error)(raw_data)
        subalpha = Smart_money_stat / tot_stat
        return subalpha

    def reform(self, temp_result):
        alpha = temp_result
        alpha = alpha.rolling(window=self.rolling_days).mean()
        return alpha


