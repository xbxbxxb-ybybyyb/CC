import gc
import pandas as pd
import numpy as np
from dataApi.stockList import clean_stock_list
from dataApi.dividend import getEXRightDividend
from dataApi.getData import get_minute_1factor
from dataApi.tradeDate import get_recent_trade_date, get_pre_trade_date, get_date_range

class FactorBackTest(object):


    def __init__(self, start_date=20170103, end_date=20191231, stocks='COMMON'):

        start_date = get_pre_trade_date(get_recent_trade_date(start_date - 1), -1)
        end_date = get_recent_trade_date(end_date)

        if stocks in ('COMMON', 'ALL', 'HS300', 'ZZ500', 'ZZ1000'):
            stock_list = clean_stock_list(stocks).loc[start_date: end_date]
        elif isinstance(stocks, pd.DataFrame):
            stock_list = stocks.reindex(get_date_range(start_date, end_date))
        else:
            raise ValueError("Type of stocks wrong.")

        columns = stock_list.columns.to_list()
        dividend = getEXRightDividend()
        share_ratio = dividend.pivot('date', 'code', 'shareRatio').reindex_like(stock_list).fillna(0)
        receive_ratio = dividend.pivot('date', 'code', 'receiveRatio').reindex_like(stock_list).fillna(0)
        payout_ratio = dividend.pivot('date', 'code', 'payoutRatio').reindex_like(stock_list).fillna(0)

        bench = get_minute_1factor('close', start_date, end_date, code_list=['ZZ500'], type='bench').ffill().iloc[:, 0]
        high = get_minute_1factor('high', start_date, end_date).reindex(columns=stock_list.columns)
        index = [x * 10000 + y for x, y in high.index]
        low = get_minute_1factor('low', start_date, end_date).reindex(columns=stock_list.columns)
        close = get_minute_1factor('close', start_date, end_date).reindex(columns=stock_list.columns)
        vol = get_minute_1factor('vol', start_date, end_date).reindex(columns=stock_list.columns)

        stock_list = stock_list.values
        share_ratio = share_ratio.values
        receive_ratio = receive_ratio.values
        payout_ratio = payout_ratio.values
        bench = bench.values.reshape(bench.shape[0] // 242, 242).swapaxes(0, 1)
        high = high.values.reshape(high.shape[0] // 242, 242, high.shape[1]).swapaxes(0, 1)
        low = low.values.reshape(low.shape[0] // 242, 242, low.shape[1]).swapaxes(0, 1)
        close = close.values.reshape(close.shape[0] // 242, 242, close.shape[1]).swapaxes(0, 1)
        vol = vol.values.reshape(vol.shape[0] // 242, 242, vol.shape[1]).swapaxes(0, 1)

        buy = (close[1:-6] - np.fmin(low[2:-5], low[3:-4])) / (
                np.fmax(high[2:-5], high[3:-4]) - np.fmin(low[2:-5], low[3:-4]) + 0.01)
        np.clip(buy, 0., 1., out=buy)
        np.multiply(buy, (vol[2:-5] + vol[3:-4]) * 0.5, out=buy)

        sell = (np.fmax(high[2:-5], high[3:-4]) - close[1:-6]) / (
                np.fmax(high[2:-5], high[3:-4]) - np.fmin(low[2:-5], low[3:-4]) + 0.01)
        np.clip(sell, 0., 1., out=sell)
        np.multiply(sell, (vol[2:-5] + vol[3:-4]) * 0.5, out=sell)

        self.__start_date = start_date
        self.__end_date = end_date
        self.__columns = columns
        self.__index = index
        self.__stock_list = stock_list
        self.__share_ratio = share_ratio
        self.__receive_ratio = receive_ratio
        self.__payout_ratio = payout_ratio
        self.__bench = bench
        self.__close = close
        self.__buy = buy
        self.__sell = sell

        del high, low, close, vol, buy, sell
        gc.collect()

    def evaluate(self, factor, money=1e6, buy_fee_ratio=0., sell_fee_ratio=0.0012):

        factor = factor.reindex(index=self.__index, columns=self.__columns).fillna(0)
        factor = factor.values.reshape(factor.shape[0] // 242, 242, factor.shape[1]).swapaxes(0, 1).astype(
            int) * self.__stock_list
        factor = factor[1:-6]

        max_amt_buy = (self.__buy * (factor > 0.5) * self.__close[1:-6]).cumsum(axis=0)
        max_amt_buy[max_amt_buy > money] = money
        max_amt_buy[1:] = max_amt_buy[1:] - max_amt_buy[:-1]

        buy_amt = max_amt_buy.sum(axis=0)
        buy_amt[buy_amt < 0.5] = np.nan
        buy_fee = buy_amt * buy_fee_ratio
        buy_vol = (max_amt_buy / self.__close[1:-6]).sum(axis=0)
        buy_min = ((max_amt_buy / self.__close[1:-6]).swapaxes(0, 2) * np.arange(239, 4, -1)).swapaxes(0, 2).sum(
            axis=0) / buy_vol
        buy_bench_price = buy_amt / (max_amt_buy.swapaxes(0, 2) / self.__bench[1:-6].swapaxes(0, 1)
                                     ).swapaxes(0, 2).sum(axis=0)

        hold_vol = buy_vol[:-1] * (1 + self.__share_ratio[1:])
        max_vol_sell = (self.__sell * (factor < -0.5)).cumsum(axis=0)[:, 1:, :]
        max_vol_sell[max_vol_sell > hold_vol] = hold_vol.repeat(max_vol_sell.shape[0], axis=0).reshape(
            max_vol_sell.swapaxes(0, 1).shape).swapaxes(1, 0)[max_vol_sell > hold_vol]
        max_vol_sell[1:] = max_vol_sell[1:] - max_vol_sell[:-1]

        sell_vol_mid = max_vol_sell.sum(axis=0)
        sell_vol_close = hold_vol - sell_vol_mid
        sell_amt = (max_vol_sell * self.__close[1:-6, 1:]).sum(axis=0) + sell_vol_close * self.__close[-1, 1:]
        sell_fee = sell_amt * sell_fee_ratio
        dividend = buy_vol[:-1] * (self.__payout_ratio[1:] * 0.9 - self.__receive_ratio[1:])
        sell_min = ((max_vol_sell.swapaxes(0, 2) * np.arange(1, 236)).swapaxes(0, 2).sum(
            axis=0) + sell_vol_close * 240) / hold_vol
        sell_bench_price = sell_amt / (((max_vol_sell * self.__close[1:-6, 1:]).swapaxes(0, 2) /
                                         self.__bench[1:-6, 1:].swapaxes(0, 1)).swapaxes(0, 2).sum(axis=0) +
                                       ((sell_vol_close * self.__close[-1, 1:]).T / self.__bench[-1, 1:]).T)

        ret = (sell_amt + dividend - buy_fee[:-1] - sell_fee) / (buy_amt[:-1] + buy_fee[:-1]) - 1
        active_ret = ret - sell_bench_price / buy_bench_price[:-1] + 1
        daily_ret = np.nanmean(ret, axis=1)
        daily_active_ret = np.nanmean(active_ret, axis=1)

        mean_ret = np.nanmean(ret)
        mean_active_ret = np.nanmean(active_ret)
        mean_hold_min = np.nanmean(sell_min + buy_min[:-1])
        win_rate_ret = (ret > 0).sum() / (ret > -1).sum()
        mean_pos_ret = ret[ret > 0].mean()
        mean_neg_ret = ret[ret < 0].mean()
        earn_loss_ratio_ret = - mean_pos_ret / mean_neg_ret
        win_rate_active_ret = (active_ret > 0).sum() / (active_ret > -1).sum()
        mean_pos_active_ret = active_ret[active_ret > 0].mean()
        mean_neg_active_ret = active_ret[active_ret < 0].mean()
        earn_loss_ratio_active_ret = - mean_pos_active_ret / mean_neg_active_ret
        buy_signal_ratio = (factor > 0.5).sum() / self.__stock_list.sum() / factor.shape[0]
        sell_signal_ratio = (factor < -0.5).sum() / self.__stock_list.sum() / factor.shape[0]
        buy_unfinished_rate = 1 - np.nanmean(buy_amt) / money
        sell_unfinished_rate = np.nanmean(sell_vol_close / hold_vol)

        daily_ret[np.isnan(daily_ret)] = 0
        annual_ret = np.nanmean(daily_ret) * 244
        annual_ret_std = np.nanstd(daily_ret) * np.sqrt(244)
        sharpe_ratio = annual_ret / annual_ret_std
        mdd_ret = (np.maximum.accumulate(np.nancumsum(daily_ret)) - np.nancumsum(daily_ret)).max()
        annual_active_ret = np.nanmean(daily_active_ret) * 244
        annual_active_ret_std = np.nanstd(daily_active_ret) * np.sqrt(244)
        info_ratio = annual_active_ret / annual_active_ret_std
        mdd_active_ret = (pd.Series(np.nancumsum(daily_active_ret)).cummax() - pd.Series(
            np.nancumsum(daily_active_ret))).max()

        date_list = get_date_range(self.__start_date, self.__end_date)

        self.hold_amt = pd.DataFrame(buy_amt, index=date_list, columns=self.__columns)
        self.hold_vol_exdiv = pd.DataFrame(hold_vol, index=date_list[:-1], columns=self.__columns)
        self.sell_vol_mid = pd.DataFrame(sell_vol_mid, index=date_list[1:], columns=self.__columns)
        self.sell_vol_close = pd.DataFrame(sell_vol_close, index=date_list[1:], columns=self.__columns)
        self.buy_min = pd.DataFrame(buy_min, index=date_list, columns=self.__columns)
        self.sell_min = pd.DataFrame(sell_min, index=date_list[1:], columns=self.__columns)
        self.ret = pd.DataFrame(ret, index=date_list[1:], columns=self.__columns)
        self.active_ret = pd.DataFrame(active_ret, index=date_list[1:], columns=self.__columns)
        self.daily_ret = pd.Series(daily_ret, index=date_list[1:])
        self.daily_active_ret = pd.Series(daily_active_ret, index=date_list[1:])

        self.mean_ret = mean_ret
        self.mean_active_ret = mean_active_ret
        self.mean_hold_min = mean_hold_min
        self.win_rate_ret = win_rate_ret
        self.win_rate_active_ret = win_rate_active_ret
        self.mean_pos_ret = mean_pos_ret
        self.mean_neg_ret = mean_neg_ret
        self.earn_loss_ratio_ret = earn_loss_ratio_ret
        self.mean_pos_active_ret = mean_pos_active_ret
        self.mean_neg_active_ret = mean_neg_active_ret
        self.earn_loss_ratio_active_ret = earn_loss_ratio_active_ret
        self.buy_stock_num = (buy_amt > 0.5).sum(axis=1).mean()
        self.buy_signal_ratio = buy_signal_ratio
        self.sell_signal_ratio = sell_signal_ratio
        self.buy_unfinished_rate = buy_unfinished_rate
        self.sell_unfinished_rate = sell_unfinished_rate
        self.annual_ret = annual_ret
        self.annual_ret_std = annual_ret_std
        self.sharpe_ratio = sharpe_ratio
        self.mdd_ret = mdd_ret
        self.annual_active_ret = annual_active_ret
        self.annual_active_ret_std = annual_active_ret_std
        self.info_ratio = info_ratio
        self.mdd_active_ret = mdd_active_ret

    @property
    def result(self):

        return pd.Series({
            '单笔收益': self.mean_ret,
            '单笔超额收益': self.mean_active_ret,
            '单笔持仓时间': self.mean_hold_min,
            '胜率': self.win_rate_ret,
            '超额胜率': self.win_rate_active_ret,
            '平均正收益': self.mean_pos_ret,
            '平均负收益': self.mean_neg_ret,
            '盈亏比': self.earn_loss_ratio_ret,
            '超额平均正收益': self.mean_pos_active_ret,
            '超额平均负收益': self.mean_neg_active_ret,
            '超额盈亏比': self.earn_loss_ratio_active_ret,
            '平均股票数量': self.buy_stock_num,
            '买入信号占比': self.buy_signal_ratio,
            '卖出信号占比': self.sell_signal_ratio,
            '买入未完成率': self.buy_unfinished_rate,
            '卖出未完成率': self.sell_unfinished_rate,
            '年化收益': self.annual_ret,
            '年化波动率': self.annual_ret_std,
            '年化夏普比': self.sharpe_ratio,
            '最大回撤': self.mdd_ret,
            '年化超额收益': self.annual_active_ret,
            '年化超额波动率': self.annual_active_ret_std,
            '年化信息比': self.info_ratio,
            '超额收益最大回撤': self.mdd_active_ret,
        })