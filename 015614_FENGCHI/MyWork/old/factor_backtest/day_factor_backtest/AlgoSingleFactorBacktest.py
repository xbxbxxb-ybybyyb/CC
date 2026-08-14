# __author__ = "Jiaping You"
# __copyright__ = "Copyright (C) 2019 HTSC"
# __version__ = "1.0"

import os
import sys
import datetime
import pandas as pd
import numpy as np

from day_factor_backtest.backtest.factor_test import SingleFactorTest
from day_factor_backtest.backtest.utility import *
from day_factor_backtest.backtest.report_generator import generate_pdf
from day_factor_backtest.utility.normalization import Normalization2
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from day_factor_backtest.backtest.corr_check import get_excess_return

daily_store_path = '/data/group/800080/factor_test/daily/'


class AlgoSingleFactorBacktest(SingleFactorTest):
    """
    Algorithm group single daily factor backtest wrapper
    """

    def load_factor(self, factor_data, name='test_factor'):
        """"""
        ### input factor data transformation: normalization, winsorization and neutralization
        pprint('Factor data preprocessing')
        factor_data = self.data_transform(factor_data)

        self.factor_data = factor_data.copy()

        self.name = name
        data_dict = self.base_data.copy()

        pprint('Filter factor by universe')
        data_dict['factor_data'] = factor_data.reindex(columns=data_dict['stock_filter_' + str(self.universe)].columns)
        # replace inf, -inf by nan
        data_dict['factor_data'][~np.isfinite(data_dict['factor_data'])] = np.nan

        pprint('Align factor with base data')
        data_dict = align_data_inner(data_dict)
        data_dict['factor_data'][data_dict['stock_filter_' + str(self.universe)] == False] = np.nan
        data_dict['factor_data'] = data_dict['factor_data'].dropna(how='all', axis=1)
        data_dict = align_data_inner(data_dict)
        self._data = data_dict

    def data_convert(self, factor_data):
        """
        convert factor data from dataframe to multi-index format
        """

        if isinstance(factor_data, pd.DataFrame):
            factor_data = factor_data.stack(dropna=False)
        elif isinstance(factor_data, pd.core.series.Series):
            pass
        else:
            raise AssertionError('factor data format error')

        return factor_data

    def update_Neu_factor(self, factor, NormSize, INDUSTRY_MARK_DF, dates_need_update):

        if factor.index[-1] != NormSize.index[-1]:
            assert False
        if factor.index[0] != NormSize.index[0]:
            assert False

        Factor_neu_df = []
        for cur_date in dates_need_update:
            factor_cur_day = factor.loc[cur_date]
            factor_cur_day.name = 'factor'
            NormSize_cur_day = NormSize.loc[cur_date]
            industry_mark_df_cur_day = INDUSTRY_MARK_DF.xs(cur_date, level=1).transpose()

            prepared_neu = pd.concat([factor_cur_day, NormSize_cur_day, industry_mark_df_cur_day], axis=1).dropna()
            reg = LinearRegression(fit_intercept=False, n_jobs=1)
            X = prepared_neu.drop(['factor'], axis=1).values
            y = prepared_neu.transpose().loc[['factor']].values.T
            reg.fit(X, y)
            residual = y - reg.predict(X)
            factor_series = pd.Series(np.nan, index=factor_cur_day.index, name=cur_date)
            factor_series.loc[prepared_neu.index] = residual.T[0]
            Factor_neu_df.append(factor_series)

        Factor_neu_df = pd.concat(Factor_neu_df, axis=1).transpose()
        return Factor_neu_df

    def get_neu_factor(self, factor_df):
        """
        Args:
           factor_df: factor dataframe
        Returns:
            industry and size neutral factor
        """
        start_date = factor_df.index[0].strftime('%Y%m%d')
        end_date = factor_df.index[-1].strftime('%Y%m%d')
        industry_code_all = pd.read_pickle(daily_store_path + 'industry_code_all.pkl')[start_date:end_date]
        industry_list = industry_code_all.stack().unique()
        industry_list = industry_list[industry_list != 0]

        INDUSTRY_MARK = {}
        for industry in industry_list:
            tmp = pd.DataFrame(0., index=industry_code_all.index, columns=industry_code_all.columns)
            tmp[industry_code_all == industry] = 1
            INDUSTRY_MARK[(industry)] = tmp
        INDUSTRY_MARK_DF = pd.concat(INDUSTRY_MARK)

        size = pd.read_pickle(daily_store_path + 'mkt_cap_ard.pkl').shift(1)[start_date:end_date]
        size = np.log(size)

        NormSize = Normalization2(size, axis=0)
        NormSize = NormSize.norm_dataframe()

        if industry_code_all.index[-1] != NormSize.index[-1]:
            assert False
        if industry_code_all.index[0] != NormSize.index[0]:
            assert False
        try:
            dates_need_update = factor_df.index.tolist()
            factor_neu_update = self.update_Neu_factor(factor_df, NormSize, INDUSTRY_MARK_DF, dates_need_update)
            factor_neu_all = factor_neu_update
            factor_neu_all = factor_neu_all.sort_index()
            return factor_neu_all
        except:
            raise AssertionError("factor data has some problem in neutralization, please check your data.")

    def data_transform(self, factor_data):
        """
        Step 1: normalization and winsorization
        Step 2: size and industry neutralization
        """

        NormFactor = Normalization2(factor_data, axis=0)
        NormFactor = NormFactor.norm_dataframe()

        neutralized_data = self.get_neu_factor(NormFactor)

        return neutralized_data

    def compute_top_excess_return(self, group=5):
        """"""
        weight = np.arange(group, 0, -1)
        weight = weight / np.sum(weight)

        if self.neutralized_data is not None:
            factor_data = self.neutralized_data
        elif self.standardized_data is not None:
            factor_data = self.standardized_data
        else:
            factor_data = self.data['factor_data']

        factor_top = factor_data[factor_data.rank(pct=True, ascending=False, axis=1) < (1. / group)]  #### top 20% stock

        _ = segment_test(factor_top, self.data[self.price_use], self.holding_period,
                         self.data[self.bmk_use], group,
                         handle_return_outlier=self.robust_segment, transaction_cost=self.transaction_cost)

        select_cols = ['Q' + str(i) for i in np.arange(1, group + 1)]

        if self.transaction_cost is None:
            seg_return = _
            seg_return_top = seg_return
        else:
            seg_return, seg_return_after_cost = _[0], _[1]
            seg_return_top = seg_return_after_cost

        er_col, top_q, bottom_q = find_er_ls_col(seg_return_top)
        if int(top_q[1:]) > int(bottom_q[1:]):
            weight = weight[::-1]
        top_return = seg_return_top[select_cols].multiply(weight, axis=1).sum(axis=1)
        top_excess_return = top_return - seg_return_top[er_col[0:2]] + seg_return_top[er_col]

        return top_excess_return

    def sample_random(self, excess, random_state=0, bootstrap_steps=9):
        ## sample containing two parts
        # part 1: 10% of the sample
        sample_90, sample_10 = train_test_split(excess, test_size=1. / (bootstrap_steps + 1), random_state=random_state)
        # part 2:bootstrap sampling of the rest 90%
        excess_sample = sample_10.tolist()
        for i in range(bootstrap_steps):
            sample_new = sample_90.sample(n=len(sample_10), replace=True, random_state=random_state).tolist()
            excess_sample += sample_new
            random_state += 10
        return pd.Series(excess_sample).mean()

    def compute_sampling_ret_stat(self, excess_return, in_sample=True, random_state=0, bootstrap_steps=9,
                                  experiment_steps=10):
        """
        random sampling of excess return

        """
        assert bootstrap_steps >= 1, "bootstrap_steps must be >= 1"
        sample_bin_ret_mean = []
        for i in range(experiment_steps):
            sample_bin_ret_mean.append(
                self.sample_random(excess_return, random_state=random_state, bootstrap_steps=bootstrap_steps) * 1e4)
            random_state += 1
        sample_bin_ret_mean = pd.Series(sample_bin_ret_mean, index=np.arange(1, experiment_steps + 1))

        bins_ret_diff2ret = (sample_bin_ret_mean.nlargest(
            int(experiment_steps / 2)).mean() - sample_bin_ret_mean.nsmallest(
            int(experiment_steps / 2)).mean()) / sample_bin_ret_mean.mean()
        std2ret = sample_bin_ret_mean.std() / sample_bin_ret_mean.mean()

        sample_bins_ret_stat = pd.DataFrame([bins_ret_diff2ret, std2ret])
        sample_bins_ret_stat.index = ['bins_ret_diff2ret', 'std2ret']
        sample_bins_ret_stat.columns = ['sample_bins_ret_stat']

        sample_bin_ret_mean = sample_bin_ret_mean.to_frame()
        sample_bin_ret_mean.columns = ['sample_bin_ret_mean']

        bin_ret_diff = pd.DataFrame(index=excess_return.index[::5],
                                    columns=[str(i) for i in np.arange(1, experiment_steps + 1)] + ['bins_ret_diff2ret',
                                                                                                    'sample_std2ret'])
        if bin_ret_diff.shape[0] <= 50:
            print('warning, date num less than 250')
            sample_bins_ret_diff2ret = np.nan
            sample_std2ret = np.nan

        for sdate, edate in zip(bin_ret_diff.index, bin_ret_diff.index[50:]):
            ret_list = []
            for iexp in np.arange(1, experiment_steps + 1):
                _ = self.sample_random(excess_return[sdate:edate], random_state=iexp) * 1e4
                ret_list.append(_)
                bin_ret_diff.loc[edate, str(iexp)] = _
            ret_list = pd.Series(ret_list, index=np.arange(1, experiment_steps + 1))
            ret_mean = ret_list.mean()
            bin_ret_diff.loc[edate, 'bins_ret_diff2ret'] = (ret_list.nlargest(
                int(experiment_steps / 2)).mean() - ret_list.nsmallest(int(experiment_steps / 2)).mean()) / ret_mean
            bin_ret_diff.loc[edate, 'sample_std2ret'] = ret_list.std() / ret_mean

        sample_bins_ret_diff2ret = bin_ret_diff['bins_ret_diff2ret'].dropna()
        sample_std2ret = bin_ret_diff['sample_std2ret'].dropna()

        return sample_bin_ret_mean, sample_bins_ret_stat, sample_bins_ret_diff2ret, sample_std2ret

    def compute_calmar_ratio_half_year(self, excess_return):
        year_list = np.unique(excess_return.index.year.tolist())
        half_year_list = []
        for year in year_list:
            half_year_list.append(str(year) + '0630')
            half_year_list.append(str(year) + '1231')

        calmar_ratio = {}
        for idx, half in enumerate(half_year_list):
            if idx == 0:
                sub_part_ret = excess_return[:half]
            else:
                sub_part_ret = excess_return[half_year_list[idx - 1]:half]
            if len(sub_part_ret):
                nav = (1. + sub_part_ret).cumprod()
                calmar = sub_part_ret.mean() / np.abs(max_drawdown(nav))
                calmar_ratio[half] = calmar
        if len(calmar_ratio):
            calmar_ratio = pd.Series(calmar_ratio).to_frame()
            calmar_ratio.columns = ['calmar_ratio']
            return calmar_ratio
        else:
            return np.nan

    @staticmethod
    def get_new_factor_corr(new_factor_name, new_factor_df):
        day_factor_dir = "/data/group/800080/factor_test/excess_return/vwap"
        factor_file_list = os.listdir(day_factor_dir)
        factor_name_list, factor_df_list = [], []
        for factor_file in factor_file_list:
            factor_name = factor_file.split('.')[0]
            factor_file = "{0}/{1}".format(day_factor_dir, factor_file)
            factor_df = pd.read_pickle(factor_file)
            factor_name_list.append(factor_name)
            factor_df_list.append(factor_df)
        factor_name_list = [new_factor_name] + factor_name_list
        factor_df_list = [new_factor_df] + factor_df_list
        df = pd.concat(factor_df_list, join='inner', axis=1)
        df.columns = factor_name_list
        corr_df = df.corr()
        new_factor_corr = corr_df[new_factor_name].sort_values(ascending=False).tail(-1)
        if new_factor_corr.empty:
            return 'No Strong Correlated Factor'
        else:
            max_factor_name = new_factor_corr.head(1).index[0]
            max_factor_corr = new_factor_corr.head(1).values[0]
            if max_factor_corr > 0.7:
                return 'Max Correlated Factor: {0}, {1}'.format(max_factor_name, round(max_factor_corr, 3))
            else:
                return 'No Strong Correlated Factor'

    def algo_shoot(self):
        """
        new metrics added by algo group
        """
        pprint('compute new metrics ......')

        excess_return = self.compute_top_excess_return()

        sample_stat = self.compute_sampling_ret_stat(excess_return)
        self.output_dict['sample_bin_ret_mean'] = sample_stat[0]
        self.output_dict['sample_bins_ret_stat'] = sample_stat[1]
        self.output_dict['sample_bins_ret_diff2ret'] = sample_stat[2]
        self.output_dict['sample_std2ret'] = sample_stat[3]

        self.output_dict['Calmar_half_year'] = self.compute_calmar_ratio_half_year(excess_return)

    def generate_report(self, factor_data):
        excel_saver(self.output_dict, self.excel_name)
        save_pickle(self.output_dict, self.pickle_name)

        pprint('Generating pdf report')
        # calculate correlation with existing factors
        factor_data.index = map(lambda x: x.strftime('%Y%m%d'), factor_data.index)
        factor_excess_data = get_excess_return(factor_data, '20160101', '20181231')
        corr_information = self.get_new_factor_corr('newfactor', factor_excess_data)

        generate_pdf(self.pickle_name, corr_information)
        pprint('* Finished - %s *' % (self.name))

    def run_backtest(self, factor_data, name='test_factor', result_folder='test_factor'):
        """"""
        self.load_factor(factor_data=factor_data, name=name)
        self.shoot(result_folder=result_folder)

        #### new metrics
        self.algo_shoot()
        self.generate_report(factor_data)


if __name__ == '__main__':
    start_date = 20160101
    end_date = 20180701
    factor_data = pd.read_pickle('/data/group/800020/AlphaDataCenter/Factor/daily/ZaoYinTrader.pkl')
    result_folder = '/data/user/015629/'

    instance = AlgoSingleFactorBacktest(start_date, end_date, universe='alpha_universe', holding_period=1,
                                        benchmark='alpha_universe',
                                        transaction_cost=0.001, segment_number=10, seg_by_industry=False,
                                        interest_type='',
                                        ret_price='vwap', ret_shift=True, easy_test=False, ic_type='original')

    instance.run_backtest(factor_data, name='ZaoYinTrader', result_folder=result_folder)
