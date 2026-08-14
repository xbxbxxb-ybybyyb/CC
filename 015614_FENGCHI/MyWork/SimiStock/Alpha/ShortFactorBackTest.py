# coding: utf-8
# Author：fengchi863
# Date ：2022/6/7 10:23

"""
用于回测负向因子
"""
import os

import numpy as np
import pandas as pd

from SimiStock.config.path_config import *
from SimiStock.dataApi import getData, stockList, tradeDate


class ShortFactorBackTest:
    def __init__(self, start_date=20170101, end_date=20211231, factor_name=None, price_type='twap'):
        self.factor_name = factor_name
        date_list = tradeDate.get_date_range(start_date, end_date)
        shift_date_list = tradeDate.get_date_range(start_date, tradeDate.get_pre_trade_date(end_date, -120))
        clean_stock = stockList.clean_stock_list()
        twap = getData.get_daily_1factor('twap', date_list=shift_date_list, code_list=list(clean_stock.columns))  # 这个价格是否是均价
        adjfactor = getData.get_daily_1factor('adjfactor', date_list=shift_date_list, code_list=list(clean_stock.columns))

        self.twap = twap * adjfactor
        self.clean_stock = clean_stock
        self.stock_list = list(clean_stock.columns)

        if os.path.exists(factor_path + factor_name + '.pkl'):
            factor_value = pd.read_pickle(factor_path + factor_name + '.pkl')
            factor_value = factor_value.loc[start_date:end_date, :]
        else:
            factor_value = pd.DataFrame(np.random.rand(len(tradeDate.get_date_range(start_date, end_date)), len(self.stock_list)),
                                        index=tradeDate.get_date_range(start_date, end_date),
                                        columns=self.stock_list)
        self.factor_value = factor_value

        self.start_date = start_date
        self.end_date = end_date
        self.price_type = price_type
        self.date_list = date_list
        self.shift_date_list = shift_date_list
        self.label = self.load_label(start_date, end_date)
        self.data_buffer = dict()

        # 保存待检测因子中性化后的因子值
        self.neutralized_factor_value = None

    def load_label(self, start_date, end_date):
        if self.price_type is 'twap':
            label = self.twap.shift(-1) / self.twap - 1
            label = label.loc[start_date:end_date]
            return label
        else:
            return None

    def get_ic_value(self, factor_value):
        ic = factor_value.corrwith(self.label, axis=0)
        return ic

    def get_ls_rank_ic(self, factor_value):
        quantile50 = factor_value.quantile(0.5, axis=1)
        long_index = factor_value.sub(quantile50, axis=0) > 0
        short_index = factor_value.sub(quantile50, axis=0) <= 0
        long_rank_ic = factor_value[long_index].rank().corrwith(self.label[long_index].rank(), axis=1)
        short_rank_ic = factor_value[short_index].rank().corrwith(self.label[short_index].rank(), axis=1)
        return long_rank_ic, short_rank_ic

    @staticmethod
    def fillna_with_industry_mean(raw_factor_df, ind_df):
        factor_df_na_filled = raw_factor_df.copy()
        factor_df_na_filled[:] = 0
        for i in np.unique(ind_df.stack().dropna().values).tolist():
            i_industry_df = pd.DataFrame(ind_df.values == i, index=ind_df.index, columns=ind_df.columns)
            factor_ind_i = raw_factor_df * i_industry_df / i_industry_df
            factor_ind_i_median = factor_ind_i.mean(axis=1)
            factor_ind_i_median_reshaped = factor_ind_i_median[:, None]
            factor_ind_i_median_matrix = pd.DataFrame(np.tile(factor_ind_i_median_reshaped, [1, ind_df.shape[1]]),
                                                      index=ind_df.index, columns=ind_df.columns)
            factor_ind_i = factor_ind_i_median_matrix
            factor_ind_i = factor_ind_i * i_industry_df / i_industry_df
            factor_ind_i[pd.DataFrame(i_industry_df.values == False, index=i_industry_df.index,
                                      columns=i_industry_df.columns)] = 0
            factor_df_na_filled = factor_df_na_filled + factor_ind_i
        factor_df_na_filled[pd.DataFrame(np.isnan(ind_df.values), index=ind_df.index, columns=ind_df.columns)] = np.nan
        return factor_df_na_filled

    @staticmethod
    def outlier_filter(value_df, scale=5):
        value_df_raw = value_df.copy()
        diversion_series = value_df.apply(lambda x: len(np.unique(x.dropna())), axis=1) / value_df.count(axis=1)

        factor_max = value_df.max(axis=1)
        value_df = value_df.reindex(factor_max.index)
        factor_median = value_df.median(axis=1)
        factor_deviation_from_median = value_df.sub(factor_median, axis=0)
        factor_deviation_from_median[
            pd.DataFrame(factor_deviation_from_median.values == 0, index=factor_deviation_from_median.index,
                         columns=factor_deviation_from_median.columns)] = np.nan
        factor_mad = factor_deviation_from_median.abs().median(axis=1)

        lower_limit = factor_median - scale * factor_mad
        upper_limit = factor_median + scale * factor_mad
        lower_limit = lower_limit.fillna(method='ffill')
        upper_limit = upper_limit.fillna(method='ffill')

        lower_limit_plus1 = factor_median - (scale + 1) * factor_mad
        upper_limit_plus1 = factor_median + (scale + 1) * factor_mad
        lower_limit_plus1 = lower_limit_plus1.fillna(method='ffill')
        upper_limit_plus1 = upper_limit_plus1.fillna(method='ffill')

        lower_limit_plus2 = factor_median - (scale + 2) * factor_mad
        upper_limit_plus2 = factor_median + (scale + 2) * factor_mad
        lower_limit_plus2 = lower_limit_plus2.fillna(method='ffill')
        upper_limit_plus2 = upper_limit_plus2.fillna(method='ffill')

        extreme_count = (value_df.sub(upper_limit, axis=0) > 0) | (value_df.sub(lower_limit, axis=0) < 0)
        extreme_count = extreme_count.sum(axis=1)
        nan_count = value_df.count(axis=1)
        extreme_rate = extreme_count / nan_count

        value_df[((diversion_series > 0.1) & (diversion_series <= 1)) == False] = value_df_raw[
            ((diversion_series > 0.1) & (diversion_series <= 1)) == False]
        value_df[(((diversion_series > 0.1) & (diversion_series <= 1)) == True) & (extreme_rate <= 0.1)] = \
            value_df.clip_lower(lower_limit, axis='index').clip_upper(upper_limit, axis='index')[
                (((diversion_series > 0.1) & (diversion_series <= 1)) == True) & (extreme_rate <= 0.1)]
        value_df[(((diversion_series > 0.1) & (diversion_series <= 1)) == True) & (extreme_rate > 0.1) & (
                extreme_rate <= 0.2)] = \
            value_df.clip_lower(lower_limit_plus1, axis='index').clip_upper(upper_limit_plus1, axis='index')[
                (((diversion_series > 0.1) & (diversion_series <= 1)) == True) & (extreme_rate > 0.1) & (
                        extreme_rate <= 0.2)]
        value_df[(((diversion_series > 0.1) & (diversion_series <= 1)) == True) & (extreme_rate > 0.2)] = \
            value_df.clip_lower(lower_limit_plus2, axis='index').clip_upper(upper_limit_plus2, axis='index')[
                (((diversion_series > 0.1) & (diversion_series <= 1)) == True) & (extreme_rate > 0.2)]
        return value_df

    @staticmethod
    def z_score_standardizer(value_df):
        factor_mean = value_df.mean(axis=1)
        factor_std = value_df.std(axis=1)
        value_df = value_df.sub(factor_mean, axis=0)
        value_df = value_df.div(factor_std, axis=0)
        return value_df

    @staticmethod
    def factor_neutralizer(factor_df, mkt_cap_ard_df, industry_df):
        # 初版为了方便，只写了size和industry中性；后续应该开发一个能支持更多因子正交化的函数
        residual_list = []
        residual_date_list = []
        for j, i_date in enumerate(list(factor_df.index)):
            if j % 50 == 0:
                print("factor neutralizing, {} / {} days".format(j, list(factor_df.index).__len__()))
            y = factor_df.loc[i_date]
            x = pd.get_dummies(industry_df.loc[i_date])  # 将1*N的行业信息变为N*31的虚拟变量矩阵（dataframe）
            x = x.join(mkt_cap_ard_df.loc[i_date], on=None, how='left')  # 加入市值信息
            y = y.dropna()  # 去na、使矩阵non-singular，后续才能做回归
            x = x.dropna()
            index_intersect = list(set(y.index).intersection(x.index))  # 要取x和y都有值的
            y = y.reindex(index_intersect)
            x = x.reindex(index_intersect)
            ind_checker = x.sum()  # 再次检查是否有行业缺失，如有的话删除这个dummy variable，以保证矩阵non-singular
            for i in range(ind_checker.__len__()):
                if ind_checker.iloc[i] == 0:
                    x = x.drop(ind_checker.index[i], axis=1)
            if index_intersect.__len__() > 0:
                b = np.linalg.inv(x.T.dot(x)).dot(x.T).dot(y)  # OLS 求回归系数，这里要用到求逆，有点慢
                residual = y - x.dot(b)  # 求残差
                residual_list.append(residual)  # 将残差保存下来
                residual_date_list.append(i_date)

        # 将残差list一次性转变为DataFrame
        neutralized_factor_df = pd.DataFrame(residual_list, index=residual_date_list)
        neutralized_factor_df = neutralized_factor_df.reindex(factor_df.index)
        neutralized_factor_df = neutralized_factor_df.sort_index(axis=1)
        return neutralized_factor_df

    def get_neu_factor_value(self):
        industry_df_sw = self.data_buffer['industry_df_sw']
        mkt_cap_ard_df = self.data_buffer['mkt_cap_ard_df']
        is_valid_df = self.data_buffer['is_valid_df']
        temp_factor = self.load_factor(self.stock_list, self.date_list[0], self.date_list[-1])

        temp_factor_stack = temp_factor.stack(dropna=False)
        industry_df_sw_stack = industry_df_sw.stack(dropna=False)
        mkt_cap_ard_df_stack = mkt_cap_ard_df.stack(dropna=False)
        is_valid_stack = is_valid_df.stack(dropna=False)

        temp_factor_stack_filtered = temp_factor_stack[is_valid_stack == 1]
        industry_df_sw_stack_filtered = industry_df_sw_stack[is_valid_stack == 1]
        mkt_cap_ard_df_stack_filtered = mkt_cap_ard_df_stack[is_valid_stack == 1]

        temp_factor = temp_factor_stack_filtered.unstack()
        industry_df_sw = industry_df_sw_stack_filtered.unstack()
        mkt_cap_ard_df = mkt_cap_ard_df_stack_filtered.unstack()

        temp_factor = self.fillna_with_industry_mean(temp_factor, industry_df_sw)
        temp_factor = self.outlier_filter(temp_factor)
        temp_factor = self.z_score_standardizer(temp_factor)

        mkt_cap_ard_df = self.outlier_filter(mkt_cap_ard_df)
        mkt_cap_ard_df = self.z_score_standardizer(mkt_cap_ard_df)

        temp_factor = self.factor_neutralizer(temp_factor, mkt_cap_ard_df, industry_df_sw)

        temp_factor = self.outlier_filter(temp_factor)
        temp_factor = self.z_score_standardizer(temp_factor)
        temp_factor = temp_factor.reindex(columns=self.stock_list).fillna(0)
        return temp_factor

    def prepare_data_buffer(self):
        ind = getData.get_daily_1factor('SW1', date_list=self.date_list, code_list=self.stock_list)
        mkt_cap_ard = getData.get_daily_1factor('a_mkt_cap', date_list=self.date_list, code_list=self.stock_list)
        mkt_cap_ard = np.log(mkt_cap_ard)
        is_valid = self.clean_stock.loc[self.date_list, self.stock_list]
        is_valid = is_valid.astype('float64')
        self.data_buffer.update({
            'industry_df_sw': ind,
            'mkt_cap_ard_df': mkt_cap_ard,
            'is_valid_df': is_valid
        })

    def load_factor(self, stock_list, start_date, end_date):
        result = self.factor_value
        result = result.loc[start_date:end_date]
        result2 = result.reindex(columns=stock_list)
        result2 = result2.astype('float64')
        return result2

    def get_group_ret(self, factor_value, group_num=10):
        universe_df = self.data_buffer['is_valid_df']
        group_ret = pd.DataFrame(index=self.date_list, columns=list(np.array(range(group_num))))
        for idx in range(len(self.date_list) - 1):
            start = self.date_list[idx]
            univ = universe_df.loc[start][universe_df.loc[start] == 1].index.tolist()
            factor_select_stock = list(factor_value.loc[start, univ].dropna().sort_values().index)
            N = len(factor_select_stock)
            for i in range(group_num):
                group_stock = factor_select_stock[int(N / group_num * i): int(N / group_num * (i + 1))]
                group_ret.loc[start, i] = self.label.loc[start, group_stock].mean()
        return group_ret.shift(1).fillna(0)

    def launch_test(self):
        self.prepare_data_buffer()
        self.neutralized_factor_value = self.get_neu_factor_value()
        daily_group_ret = self.get_group_ret(self.factor_value)
        daily_long_rank_ic, daily_short_rank_ic = self.get_ls_rank_ic(self.factor_value)
        daily_ic = self.get_ic_value(self.factor_value)
        daily_long_neu_rank_ic, daily_short_neu_rank_ic = self.get_ls_rank_ic(self.neutralized_factor_value)
        daily_neu_ic = self.get_ic_value(self.neutralized_factor_value)
        print('ic_mean: ', daily_ic.mean())
        print('long_rank_ic: ', daily_long_rank_ic.mean(), '\nshort_rank_ic: ', daily_short_rank_ic.mean())
        print('neu_ic_mean：', daily_neu_ic.mean())
        print('long_neu_rank_ic: ', daily_long_neu_rank_ic.mean(),
              '\nshort_neu_rank_ic: ', daily_short_neu_rank_ic.mean())
        print('group_ret: ', daily_group_ret.mean(axis=0))


if __name__ == '__main__':
    sfbt = ShortFactorBackTest(start_date=20210701, end_date=20211231, factor_name='test_factor', price_type='twap')
    sfbt.launch_test()
