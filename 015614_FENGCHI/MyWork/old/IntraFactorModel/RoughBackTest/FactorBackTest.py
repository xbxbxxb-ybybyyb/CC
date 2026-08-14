# coding: utf-8
# Author：fengchi863
# Date ：2020/5/13 13:38

from dataApi.getData import get_minute_1factor
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_recent_trade_date, get_pre_trade_date, get_date_range
from dataApi.usefulTools import *


def shift_back(arr, n):
    arr_shift = arr.copy()
    arr_shift[:-n] = arr_shift[n:]
    arr_shift[-n:] = np.nan
    return arr_shift


class FactorBackTest():
    def __init__(self, start_date=20170103, end_date=20191231, pool='COMMON'):
        if type(pool) == str:
            if pool not in ['COMMON', 'ZZ500', 'ZZ1000', 'ZZ800', 'HS300', 'ALL']:
                raise Exception('Wrong pool type')
            pool = clean_stock_list(pool, no_limit_down=True, no_limit_up=True)
        elif type(pool) == pd.DataFrame:
            pass
        else:
            raise Exception('Wrong pool type')
        stock_pool = pool.loc[start_date:end_date]
        date_list = get_date_range(start_date, end_date)
        stock_pool = stock_pool.reindex(date_list)
        close = get_minute_1factor('close', start_datetime=start_date, end_datetime=end_date, code_list=stock_pool.columns.tolist())
        # open = get_minute_1factor('open', start_datetime=start_date, end_datetime=end_date, code_list=stock_pool.columns.tolist())
        # open = frame2arr(open)
        index, columns = close.index.tolist(), close.columns.tolist()
        close = frame2arr(close)
        self.start_date = start_date
        self.end_date = end_date
        self.close = close
        self.index = index
        self.columns = columns
        self.date_list = date_list
        self.pool = stock_pool

    def get_signal(self, factor, threshold=0.2, N=2):
        print(threshold, N)
        label = np.zeros(factor.shape)
        for i in range(N, int(factor.shape[1] / 20)):
            base_period = factor[:, (i - N) * 20:i * 20, :].reshape(242 * N * 20, factor.shape[-1])
            label_period = factor[:, i * 20:(i + 1) * 20, :]  # .copy()
            down_threshold, up_threshold = np.nanquantile(base_period, threshold, axis=0), np.nanquantile(base_period, 1 - threshold, axis=0)
            label[:, i * 20:(i + 1) * 20, :] = (label_period < down_threshold) * -1 + (label_period > up_threshold) * 1
        label[np.isnan(factor)] = np.nan
        return label

    def get_signal(self, factor, threshold=0.2, N=2):
        label = np.zeros(factor.shape)
        for i in range(N, int(factor.shape[1] / 20) + 1):
            base_period = factor[:, (i - N) * 20:i * 20, :].reshape(242 * N * 20, factor.shape[-1])
            label_period = factor[:, i * 20:(i + 1) * 20, :].copy()
            down_threshold, up_threshold = np.nanquantile(base_period, threshold, axis=0), np.nanquantile(base_period, 1 - threshold, axis=0)
            label[:, i * 20:(i + 1) * 20, :] = (label_period < down_threshold) * -1 + (label_period > up_threshold) * 1
        label[np.isnan(factor)] = np.nan
        return label

    def run_backtest(self, factor_: pd.DataFrame, n=5, threshold=0.2, N=2):
        factor = frame2arr(factor_.reindex(self.index, axis=0).reindex(self.columns, axis=1))
        pool_arr = self.pool.values
        pool_arr = np.array([pool_arr for i in range(242)])
        factor[~pool_arr] = np.nan
        signal = self.get_signal(factor, threshold, N)
        # 未来n分钟收益
        future_profit = shift_back(self.close, n) / self.close - 1
        future_profit[(future_profit == np.inf) | (future_profit == -np.inf)] = np.nan
        future_profit[~pool_arr] = np.nan
        # 计算时序相关性
        corr_df = self.ts_corr(factor, future_profit)
        # 日内信号的收益
        signal_profit = future_profit * signal
        signal_profit[~((signal == 1) | (signal == -1))] = np.nan
        daily_intraday_cumprofit = np.nansum(signal_profit, axis=0)
        daily_profit = pd.DataFrame(daily_intraday_cumprofit, index=self.date_list, columns=self.columns)
        daily_win_count = pd.DataFrame(np.nansum((signal_profit > 0) * 1., axis=0),
                                       index=self.date_list, columns=self.columns)
        daily_lose_count = pd.DataFrame(np.nansum((signal_profit < 0) * 1., axis=0),
                                        index=self.date_list, columns=self.columns)
        daily_signal_count = pd.DataFrame(np.nansum(((signal == 1) | (signal == -1)), axis=0) * 1.,
                                          index=self.date_list, columns=self.columns)
        daily_effective_signal_count = daily_win_count + daily_lose_count
        daily_lose_count[daily_signal_count == 0] = np.nan
        daily_effective_signal_count[daily_signal_count == 0] = np.nan
        daily_profit[daily_signal_count == 0] = np.nan
        daily_win_count[daily_signal_count == 0] = np.nan
        daily_signal_count[daily_signal_count == 0] = np.nan
        # 累计单利求和、累计单利分年求和、日收益均值、日收益按年均值、胜率
        # 在每个交易日上求所有股票的均值，再求时序上市场的均值
        # result = pd.DataFrame(index = [x for x in range(int(self.start_date/10000),int(self.end_date/10000)+1)]+['all'])
        daily_profit[~self.pool] = np.nan
        info = pd.DataFrame({'日均收益': daily_profit.mean(axis=1)})  # .cumsum()
        info['year'] = [int(x / 10000) for x in info.index]
        result = info.groupby('year').mean()
        result.loc['all', :] = info.mean()
        for year in result.index[:-1]:
            result.loc[year, '累计单利'] = info[info['year'] == year]['日均收益'].cumsum().tolist()[-1]
        result.loc['all', '累计单利'] = info['日均收益'].cumsum().tolist()[-1]

        # 盈亏比 时序ic
        ic_mean_series = corr_df.mean(axis=1)
        for year in result.index[:-1]:
            start, end = get_pre_trade_date(get_recent_trade_date(year * 10000 + 101), -1), get_recent_trade_date((year + 1) * 10000 + 101)
            temp_signal_profit = signal_profit[:, self.date_list.index(start):self.date_list.index(end) + 1, :]
            temp_signal_profit = temp_signal_profit.reshape(temp_signal_profit.shape[0] * temp_signal_profit.shape[1], temp_signal_profit.shape[2])
            profit_loss_ratio = np.nanmean(np.where(temp_signal_profit > 0, temp_signal_profit, np.nan), axis=0) / np.nanmean(
                np.where(temp_signal_profit < 0, temp_signal_profit, np.nan), axis=0)
            result.loc[year, '盈亏比'] = np.nanmean(profit_loss_ratio)
            result.loc[year, '时序IC'] = ic_mean_series.loc[start:end].mean()
        temp_signal_profit = signal_profit.reshape(signal_profit.shape[0] * signal_profit.shape[1], signal_profit.shape[2])
        profit_loss_ratio = np.nanmean(np.where(temp_signal_profit > 0, temp_signal_profit, np.nan), axis=0) / np.nanmean(
            np.where(temp_signal_profit < 0, temp_signal_profit, np.nan), axis=0)
        result.loc['all', '盈亏比'] = np.nanmean(profit_loss_ratio)
        result.loc['all', '时序IC'] = ic_mean_series.mean()
        result_series = info.drop('year', axis=1)
        result_series['时序ic均值'] = ic_mean_series
        result_series['单次信号收益均值'] = (daily_profit / daily_signal_count).mean(axis=1)
        # 信号数、胜率
        daily_signal_count.index = pd.to_datetime(daily_signal_count.index.astype(str))
        daily_win_count.index = pd.to_datetime(daily_win_count.index.astype(str))
        daily_effective_signal_count.index = pd.to_datetime(daily_effective_signal_count.index.astype(str))
        # 信号数
        monthly_avg_daily_signal_count = daily_signal_count.resample('1m').mean()
        monthly_avg_daily_signal_count.index = [int(x.strftime('%Y%m')) for x in monthly_avg_daily_signal_count.index]
        yearly_avg_signal_count = daily_signal_count.resample('1Y').mean()
        yearly_avg_signal_count.index = [int(x.strftime('%Y')) for x in yearly_avg_signal_count.index]
        yearly_avg_signal_count.loc['all', :] = daily_signal_count.mean()
        # 预测准确信号数
        monthly_win_rate = daily_win_count.resample('1m').sum() / daily_effective_signal_count.resample('1m').sum()
        yearly_win_rate = daily_win_count.resample('1Y').sum() / daily_effective_signal_count.resample('1Y').sum()
        monthly_win_rate.index = [int(x.strftime('%Y%m')) for x in monthly_win_rate.index]
        yearly_win_rate.index = [int(x.strftime('%Y')) for x in yearly_win_rate.index]
        all_win_rate = daily_win_count.sum() / daily_effective_signal_count.sum()
        yearly_win_rate.loc['all', :] = all_win_rate
        win_rate = pd.concat([yearly_win_rate, monthly_win_rate])

        result['日均信号次数'] = yearly_avg_signal_count.mean(axis=1)
        result['胜率'] = yearly_win_rate.mean(axis=1)
        return {'评估结果': result, '按日期评估均值': result_series, '日均信号次数': pd.concat([yearly_avg_signal_count, monthly_avg_daily_signal_count]),
                '胜率': win_rate}

    def ts_corr(self, factor, future_profit):
        i = 0
        while np.nansum(factor[i, :, :]) == 0:
            i += 1
            if i >= 242:
                break
        j = 0
        while np.nansum(factor[-j, :, :]) == 0 or np.nansum(future_profit[-j, :, :]) == 0:
            j += 1
            if j >= 242:
                break

        if i >= 242 or j >= 242 or (242 - i - j) < 30:
            return pd.DataFrame(np.nan, index=self.date_list, columns=self.columns)
        corr = ts_corr(factor[i:242 - j], future_profit[i:242 - j], 240 - i - j + 2)
        corr_df = pd.DataFrame(corr[-1], index=self.date_list, columns=self.columns)
        return corr_df

    def calc_out_result(self, factor, file_name, n, path='/data/group/800319/junkData/IntraFactorModel/FactorEvaluation/'):
        evaluation_result = self.run_backtest(factor, n=n)
        with pd.ExcelWriter(path + '%s.xlsx' % file_name) as writer:
            for sheet in evaluation_result:
                evaluation_result[sheet].to_excel(writer, sheet_name=sheet)
