# @Time : 2020/12/18 16:35
# @Author : Zhichen Lu
# @File : AloBackTest.py

# -*- coding: utf-8 -*-
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy
import os
from copy import deepcopy
from pandas.tseries.offsets import Day, MonthBegin
import matplotlib.pyplot as plt
import scipy.io as sio, datetime, time, pandas as pd, numpy as np, math, sys, os
from xquant.factordata import FactorData

s = FactorData()


class Backtester:
    def __init__(self, trading_days):
        self._Backtester__txt = './日间回测/backtest_history.txt'
        self._Backtester__minimum_delta_amount = np.nan
        self._Backtester__start = np.nan
        self._Backtester__end = np.nan
        self._Backtester__trade_dates = np.nan
        self._Backtester__universe = np.nan
        self._Backtester__weight = np.nan
        self._Backtester__amount = np.nan
        self._Backtester__isValid_and_missing_min_data = np.nan
        self._Backtester__price_type = np.nan
        self._Backtester__trade_on_price = np.nan
        self._Backtester__benchmark_type = np.nan
        self._Backtester__benchmark_index = np.nan
        self._Backtester__close = np.nan
        self._Backtester__open = np.nan
        self._Backtester__adjfactor = np.nan
        self._Backtester__is_valid = np.nan
        self._Backtester__other_bct_data = np.nan
        self._Backtester__refresh_rate = np.nan
        self._Backtester__day_before_cur_refresh = np.nan
        self._Backtester__last_refresh_date = np.nan
        self._Backtester__refresh_flag = np.nan
        self._Backtester__refresh_nights = np.nan
        self._Backtester__capital = np.nan
        self._Backtester__commission = np.nan
        self._Backtester__tax = np.nan
        self._Backtester__volume = np.nan
        self._Backtester__position = np.nan
        self._Backtester__cash = np.nan
        self._Backtester__portfolio_value = np.nan
        self._Backtester__portfolio_value_on_close = np.nan
        self._Backtester__silent = np.nan
        self._Backtester__keep_cap = np.nan
        self._Backtester__daily_return = np.nan
        self._Backtester__return_net = np.nan
        self._Backtester__return_net_on_close = np.nan
        self._Backtester__hedge_net_on_close = np.nan
        self._Backtester__turnover_rate = np.nan
        self._Backtester__all_in = np.nan
        self.trading_days = trading_days

    def set_up(self, weight, hold_period=1, price_type='open', benchmark_type='HS300', capital=100000000.0, keep_cap=False, commission=0.0, tax=0.0, silent=True, all_in=True,
               min_delta_amt=0, trading_days=None):
        self._Backtester__check_params(weight, price_type, benchmark_type)
        self._Backtester__reset(trading_days)
        self._Backtester__get_base_data(price_type, benchmark_type)
        self._Backtester__set_params(weight, hold_period, price_type, benchmark_type, capital, keep_cap, commission, tax, silent, all_in, min_delta_amt)

    def __check_params(self, weight, price_type, benchmark_type):
        if benchmark_type not in ('HS300', 'ZZ500'):
            raise AssertionError('Wrong benchmark type.')
        if price_type not in ('close', 'open', 'vwap'):
            raise AssertionError('Wrong price trading type.')

    def __reset(self, trading_days):
        self.__init__(trading_days)

    def __get_base_data(self, price_type, benchmark_type):
        print('Loading data, please wait...')
        self._Backtester__other_bct_data = {}
        if True:
            print('basic data loading-------------')
            allday = s.get_factor_value('Basic_factor', [], self.trading_days, ['close', 'volume', 'adjfactor', 'open', 'amt', 'vwap'])
            close = allday.iloc[:, 0].unstack()
            close.index = pd.to_datetime(close.index)
            volume = allday.iloc[:, 1].unstack()
            volume.index = pd.to_datetime(volume.index)
            adjfactor = allday.iloc[:, 2].unstack()
            adjfactor.index = pd.to_datetime(adjfactor.index)
            Open = allday.iloc[:, 3].unstack()
            Open.index = pd.to_datetime(Open.index)
            amount = allday.iloc[:, 4].unstack()
            amount.index = pd.to_datetime(amount.index)
            vwap = allday.iloc[:, 5].unstack()
            vwap.index = pd.to_datetime(vwap.index)
            print('basic data loading complete-----')
            self._Backtester__volume = volume
            self._Backtester__adjfactor = adjfactor
            self._Backtester__amount = amount * 1000
            self._Backtester__close = close
            self._Backtester__open = Open
            if price_type == 'close':
                self._Backtester__trade_on_price = close
            else:
                if price_type == 'open':
                    self._Backtester__trade_on_price = Open
                else:
                    if price_type == 'vwap':
                        self._Backtester__trade_on_price = vwap

        # with pd.HDFStore('D:/Programs/Python/ATLAS/data/basics/is_valid', 'r') as (data):
        # self._Backtester__other_bct_data['isValid_and_trigger_upper_price_limit'] = data['is_valid_trigger_high_limit']
        # self._Backtester__other_bct_data['isValid_and_trigger_lower_price_limit'] = data['is_valid_trigger_low_limit']
        is_valid = close.copy()
        is_valid[~is_valid.isna()] = 1
        is_valid[is_valid.isna()] = 0
        self._Backtester__other_bct_data['is_valid'] = is_valid

        if benchmark_type == 'HS300':
            hs300 = s.get_factor_value('Basic_factor', ['000300.SH'], self.trading_days, ['close']).iloc[:, 0].unstack()
            hs300.index = pd.to_datetime(hs300.index)
            self._Backtester__benchmark_index = hs300['000300.SH']
        else:
            if benchmark_type == 'ZZ500':
                zz500 = s.get_factor_value('Basic_factor', ['000905.SH'], self.trading_days, ['close']).iloc[:, 0].unstack()
                zz500.index = pd.to_datetime(zz500.index)
                self._Backtester__benchmark_index = zz500['000905.SH']
            else:
                zz500 = s.get_factor_value('Basic_factor', ['000905.SH'], self.trading_days, ['close']).iloc[:, 0].unstack()
                zz500.index = pd.to_datetime(zz500.index)
                self._Backtester__benchmark_index = zz500['000905.SH']
                # self._Backtester__benchmark_index = self._Backtester__benchmark_index[self._Backtester__benchmark_index.columns[0]]
        print('Data loaded.')

    def __set_params(self, weight, hold_period, price_type, benchmark_type, capital, keep_cap, commission, tax, silent, all_in, min_delta_amt):
        print('Setting up, please wait...')
        self._Backtester__start = weight.index[0]
        self._Backtester__end = weight.index[-1]
        self._Backtester__trade_dates = self._Backtester__trade_on_price.index[
            np.logical_and(self._Backtester__trade_on_price.index >= self._Backtester__start, self._Backtester__trade_on_price.index <= self._Backtester__end)]

        self._Backtester__universe = list(self._Backtester__trade_on_price.columns)
        self._Backtester__weight = weight.loc[self._Backtester__trade_dates].T.reindex(self._Backtester__universe).T
        for k in self._Backtester__other_bct_data:
            self._Backtester__other_bct_data[k] = self._Backtester__other_bct_data[k].loc[self._Backtester__trade_dates].T.reindex(self._Backtester__universe).T

        self._Backtester__is_valid = self._Backtester__other_bct_data['is_valid']
        self._Backtester__benchmark_type = benchmark_type
        self._Backtester__benchmark_index = self._Backtester__benchmark_index.loc[self._Backtester__trade_dates]
        self._Backtester__price_type = price_type
        self._Backtester__trade_on_price = self._Backtester__trade_on_price.loc[self._Backtester__trade_dates].T.reindex(self._Backtester__universe).T
        self._Backtester__close = self._Backtester__close.loc[self._Backtester__trade_dates].T.reindex(self._Backtester__universe).T
        self._Backtester__open = self._Backtester__open.loc[self._Backtester__trade_dates].T.reindex(self._Backtester__universe).T
        self._Backtester__amount = self._Backtester__amount.loc[self._Backtester__trade_dates].T.reindex(self._Backtester__universe).T
        self._Backtester__adjfactor = self._Backtester__adjfactor.loc[self._Backtester__trade_dates].T.reindex(self._Backtester__universe).T
        self._Backtester__refresh_rate = hold_period
        self._Backtester__day_before_cur_refresh = self._Backtester__trade_dates[0]
        self._Backtester__last_refresh_date = self._Backtester__trade_dates[0]
        refresh_idx = [i for i in range(0, len(self._Backtester__trade_dates), self._Backtester__refresh_rate)]
        self._Backtester__refresh_flag = pd.Series(index=self._Backtester__trade_dates, data=0)
        self._Backtester__refresh_flag.iloc[refresh_idx] = 1
        self._Backtester__refresh_nights = self._Backtester__trade_dates[refresh_idx]
        self._Backtester__capital = capital
        self._Backtester__commission = commission
        self._Backtester__minimum_commission = 5
        self._Backtester__tax = tax
        self._Backtester__volume = self._Backtester__volume.loc[self._Backtester__trade_dates].T.reindex(self._Backtester__universe).T
        self._Backtester__position = pd.DataFrame(index=self._Backtester__trade_dates, columns=self._Backtester__universe, data=0.0)
        self._Backtester__cash = pd.Series(index=self._Backtester__trade_dates, dtype='float64')
        self._Backtester__cash.iloc[0] = self._Backtester__capital
        self._Backtester__portfolio_value = pd.Series(index=self._Backtester__trade_dates, dtype='float64')
        self._Backtester__portfolio_value_on_close = pd.Series(index=self._Backtester__trade_dates, dtype='float64')
        self._Backtester__silent = silent
        self._Backtester__keep_cap = keep_cap
        if keep_cap:
            self._Backtester__daily_return = pd.Series(index=self._Backtester__trade_dates, dtype='float64')
        self._Backtester__return_net = pd.Series(index=self._Backtester__trade_dates, dtype='float64')
        self._Backtester__return_net_on_close = pd.Series(index=self._Backtester__trade_dates, dtype='float64')
        self._Backtester__hedge_net_on_close = pd.Series(index=self._Backtester__trade_dates, dtype='float64')
        self._Backtester__turnover_rate = pd.DataFrame(index=self._Backtester__refresh_nights, columns=['buy', 'sell'], data=0)
        self._Backtester__all_in = all_in
        self._Backtester__minimum_delta_amount = min_delta_amt
        print('Setup done.')

    def __key2timestamp(self, key):
        return pd.Timestamp.strptime(key, '/%Y%m%d')

    def __timestamp2key(self, ts):
        return pd.Timestamp.strftime(ts, '/%Y%m%d')

    def get_weight(self):
        return deepcopy(self._Backtester__weight)

    def get_trade_dates(self):
        return deepcopy(self._Backtester__trade_dates)

    def get_universe(self):
        return deepcopy(self._Backtester__universe)

    def get_trade_on_price(self):
        return deepcopy(self._Backtester__trade_on_price)

    def get_benchmark_index(self):
        return deepcopy(self._Backtester__benchmark_index)

    def get_refresh_flag(self):
        return deepcopy(self._Backtester__refresh_flag)

    def get_amount(self):
        return deepcopy(self._Backtester__amount)

    def get_position(self):
        return deepcopy(self._Backtester__position)

    def get_cash(self):
        return deepcopy(self._Backtester__cash)

    def get_turnover_rate(self):
        return deepcopy(self._Backtester__turnover_rate)

    def get_portfolio_value(self):
        return deepcopy(self._Backtester__portfolio_value)

    def get_portfolio_value_on_close(self):
        return deepcopy(self._Backtester__portfolio_value_on_close)

    def get_return_net(self):
        return deepcopy(self._Backtester__return_net)

    def get_return_net_on_close(self):
        return deepcopy(self._Backtester__return_net_on_close)

    def get_hedge_net_on_close(self):
        return deepcopy(self._Backtester__hedge_net_on_close)

    def run(self):
        print('Start backtesting.')
        f = open(self._Backtester__txt, 'w')
        f.write('Start backtesting.\n')
        len_date = 0
        for date in self._Backtester__trade_dates:
            f.write('=====================================\n')
            f.write('Today is %s\n' % date)
            len_date += 1
            if len_date % 90 == 0:
                print('running to: ', date)
            # flag position to record the end of hold period
            is_refresh = self._Backtester__refresh_flag.loc[date]
            last_night = self._Backtester__day_before_cur_refresh
            last_night_adjfactor = self._Backtester__adjfactor.loc[last_night]  # last adjust factor
            today_adjfactor = self._Backtester__adjfactor.loc[date]  # current adjust factor
            trade_price_today = self._Backtester__trade_on_price.loc[date]  # today's price for trading
            # today's position before trading (hands, not money)
            self._Backtester__position.loc[date] = self._Backtester__position.loc[last_night] * today_adjfactor / last_night_adjfactor
            # today's cash, whic equals to the cash of last trading day
            self._Backtester__cash.loc[date] = self._Backtester__cash.loc[last_night]
            # calculate portfolio value after market open
            portfolio_value_on_open = self._Backtester__cash.loc[date] + np.nansum(self._Backtester__position.loc[date] * self._Backtester__open.loc[date])
            f.write('Updating portfolio value after market open to {}\n'.format(portfolio_value_on_open))
            # if today is used to updateh the portfolio
            if is_refresh == 1:
                f.write('Adjusting positions on {}\n'.format(date))
                if not self._Backtester__silent:
                    print('Adjusting positions on ', date)
                # the price has been adjusted
                if np.sum(today_adjfactor != last_night_adjfactor) > 0:
                    delta_position_after_adj = self._Backtester__position.loc[date] - (self._Backtester__position.loc[date].fillna(0.0) / 100 + 1e-5).astype(int) * 100
                    self._Backtester__position.loc[date] = (self._Backtester__position.loc[date].fillna(0.0) / 100 + 1e-5).astype(int) * 100
                    self._Backtester__cash.loc[date] += np.dot(delta_position_after_adj.fillna(0.0), trade_price_today.fillna(0.0))
                # flag to record the stocks reaching low limit when openning
                # stk_trigger_lower_price_limit = self._Backtester__other_bct_data['isValid_and_trigger_lower_price_limit'].loc[date]
                # stk_trigger_lower_price_limit = stk_trigger_lower_price_limit[stk_trigger_lower_price_limit == 1].index.tolist()
                # flag to record the stocks reaching high limit when openning
                # stk_trigger_upper_price_limit = self._Backtester__other_bct_data['isValid_and_trigger_upper_price_limit'].loc[date]
                # stk_trigger_upper_price_limit = stk_trigger_upper_price_limit[stk_trigger_upper_price_limit == 1].index.tolist()
                # the designated amount of money assigned to different stocks
                w_today = self._Backtester__weight.loc[date]
                # if all in, adjust the total weight to 1
                if self._Backtester__all_in:
                    if w_today.sum() < 0.95:
                        f.write('Adjusting total weights to 1\n')
                        if not self._Backtester__silent:
                            print('Adjusting total weights to 1')
                        make_up_weights = 0.998 - w_today.sum()
                        w_today[(w_today > 0)] += make_up_weights * w_today[w_today > 0] / w_today.sum()
                # if the summation of assigned weight is larger than 1
                if w_today.sum() > 1.0:
                    w_today = w_today / w_today.sum()
                # initialize the position for all stocks (fill 0)
                hold_position = pd.Series(index=self._Backtester__universe, data=0)
                # initialize planned cash for all stocks (fill 0)
                plan_account_cash = pd.Series(index=self._Backtester__universe, data=0)
                # initialize planned postion for all stocks (fill 0)
                plan_refreshed_position = pd.Series(index=self._Backtester__universe, data=0)
                # no cash has been spent yet
                today_cash_before_trading = self._Backtester__cash.loc[date]
                # record the trading price for all stocks
                today_price = self._Backtester__trade_on_price.loc[date]
                # the valid to trade flag for all stocks
                today_isValid = self._Backtester__is_valid.loc[date]
                # stocks which can be traded
                today_stk_set = today_isValid[today_isValid == 1].index.tolist()
                # no stocks has been sold or bought yet
                today_position_before_trading = self._Backtester__position.loc[date]
                # calculate the value of all stocks before trading
                cash_in_stock = np.dot(today_position_before_trading.fillna(0.0), trade_price_today.fillna(0.0))
                # calculate the value of the portfolio
                capital = np.dot(today_price.loc[today_stk_set].fillna(0.0), today_position_before_trading.loc[today_stk_set].fillna(0.0)) + today_cash_before_trading
                # find the stocks with a non-zero weight, which indicates trading
                have_weight_stk = w_today[w_today > 0].index.tolist()
                # find the stocks which needs trading but cannot be traded,
                # their cash will be assigned to other stocks
                invalid_rebalance_stk = set(have_weight_stk) - set(today_stk_set)
                if len(invalid_rebalance_stk) > 0:
                    for invalid_stk in invalid_rebalance_stk:
                        f.write('Warning! {} cannot be traded on {}.\n'.format(invalid_stk, date))
                    if not self._Backtester__silent:
                        for invalid_stk in invalid_rebalance_stk:
                            print('Warning! ', invalid_stk, ' cannot be traded on ', date, '.')
                    invalid_weight = w_today.loc[invalid_rebalance_stk].sum()  # total weights for all invalid stocks
                    w_today.loc[invalid_rebalance_stk] = 0.0
                    w_today[(w_today > 0)] += invalid_weight * w_today[w_today > 0] / w_today.sum()
                plan_account_cash.loc[today_stk_set] = capital * w_today.loc[today_stk_set]  # planned cash for all stocks
                plan_refreshed_position.loc[today_stk_set] = plan_account_cash.loc[today_stk_set].fillna(0.0) / today_price.loc[today_stk_set].fillna(np.inf)
                plan_refreshed_position = ((plan_refreshed_position / 100) + 1e-5).astype(int) * 100  # stocks can be traded as the multiplier of 100
                trade_flag = self._Backtester__is_valid.loc[date]  # stocks valid for transaction
                today_valid_stk_set = trade_flag[trade_flag == 1].index.tolist()
                delta_position = plan_refreshed_position.loc[today_valid_stk_set] - today_position_before_trading.loc[today_valid_stk_set]  # changed positions
                # if related amount is smaller than a given threshold, the transaction will be cancelled
                transaction_amount = np.abs(delta_position) * today_price.loc[delta_position.index]
                delta_position[transaction_amount <= self._Backtester__minimum_delta_amount] = 0
                delta_position = delta_position.fillna(0.0)
                # Note that delta_position can be either positive or negative.
                # delta_position is a multiplier of 100 because plan_refreshed_position and today_position_before_trading are both multipliers of 100
                stk_too_many = self._Backtester__volume.loc[date] * 2.0 - abs(delta_position)  # the target delta position is larger than historical volume
                stk_too_many = stk_too_many[stk_too_many < 0].index.tolist()
                if len(stk_too_many) > 0:
                    f.write('Warning: , portfolio trading too much!, please reduce weight on stock: {}.\n'.format(date, stk_too_many))
                    if not self._Backtester__silent:
                        print('Warning: ', date, ', portfolio trading too much!, please reduce weight on stock: ', stk_too_many)
                sell_stk_set = delta_position[delta_position < 0].index.tolist()
                temp_set = sell_stk_set
                sell_stk_set = set(sell_stk_set)  # remove stocks reach low price limit
                for stk_to_sell in temp_set:
                    if stk_to_sell not in sell_stk_set:
                        f.write('Warning! {} has reach the low limit and cannot be sold.\n'.format(stk_to_sell))
                if not self._Backtester__silent:
                    for stk_to_sell in temp_set:
                        if stk_to_sell not in sell_stk_set:
                            print('Warning! ', stk_to_sell, 'has reach the low limit and cannot be sold.')
                # new cash has arrived after selling some of the stocks
                cash_add = np.abs(delta_position.loc[sell_stk_set].fillna(0.0) * trade_price_today.loc[sell_stk_set].fillna(0.0))
                tax_fee = cash_add * self._Backtester__tax
                commission_fee = np.maximum(cash_add * self._Backtester__commission, self._Backtester__minimum_commission)
                f.write('Sell stocks.\n')
                # added cash after selling some stocks, commissions and taxes have been removed.
                new_cash = cash_add - commission_fee - tax_fee
                cash_add = np.sum(new_cash)
                cash_after_selling = today_cash_before_trading + cash_add
                for stk_to_sell in sell_stk_set:
                    f.write('{} is sold at a price of {}, with {} hands and RMB {} (commission {} and tax {} incl.).\n'.format(stk_to_sell, trade_price_today.loc[stk_to_sell],
                                                                                                                               delta_position.loc[stk_to_sell],
                                                                                                                               new_cash.loc[stk_to_sell],
                                                                                                                               commission_fee.loc[stk_to_sell],
                                                                                                                               tax_fee.loc[stk_to_sell]))
                if not self._Backtester__silent:
                    print('Sell stocks.')
                    for stk_to_sell in sell_stk_set:
                        print(stk_to_sell, ' is sold at a price of ', trade_price_today.loc[stk_to_sell], ', with ', delta_position.loc[stk_to_sell], 'hands and RMB',
                              cash_add.loc[stk_to_sell] * (1 - self._Backtester__tax - self._Backtester__commission), ' (commission and tax incl.)')

                # calculate the ratio of sold stocks
                if cash_in_stock > 0:
                    sell_rate = cash_add / cash_in_stock
                else:
                    if cash_in_stock == 0:
                        sell_rate = np.float64(0.0)
                    else:
                        raise AssertionError('Wrong in selling stocks')
                # refresh the hold positions of all stocks
                hold_position.loc[sell_stk_set] = plan_refreshed_position.loc[sell_stk_set]
                buy_stk_set = delta_position[delta_position > 0].index.tolist()
                buy_stk_set = set(buy_stk_set)  # get buy valid stock set for transaction
                remaining_cash = 0.0
                cost_of_buying = 0.0
                if len(buy_stk_set) > 0:
                    f.write('Buy stocks.\n')
                    if not self._Backtester__silent:
                        print('Buy stocks.')
                    # stocks planned to buy, sorted in a decreasing order based on the proportion of value
                    buy_stk_set = (w_today.loc[buy_stk_set].sort_values(ascending=False)).index.tolist()
                    # total cost to buy stocks (commision included)
                    cost = trade_price_today.loc[buy_stk_set] * delta_position.loc[buy_stk_set]
                    commission_fee = np.maximum(cost * self._Backtester__commission, self._Backtester__minimum_commission)
                    cost += commission_fee
                    cost_cum = cost.cumsum()
                    # find the number of stocks avalaible to buy - 1
                    i_mark = len(cost_cum[cost_cum <= cash_after_selling]) - 1
                    if i_mark >= 0:  # buy more than one stock
                        buy_stk_set_current_buy = deepcopy(buy_stk_set[0:i_mark + 1])  # get all stocks to buy except the last one
                        for stk_to_buy in buy_stk_set_current_buy:
                            f.write('{} is bought at a price of {}, with {} hands and RMB {} (commission {} incl.).\n'.format(stk_to_buy, trade_price_today.loc[stk_to_buy],
                                                                                                                              delta_position.loc[stk_to_buy], cost.loc[stk_to_buy],
                                                                                                                              commission_fee.loc[stk_to_buy]))
                        if not self._Backtester__silent:
                            for stk_to_buy in buy_stk_set_current_buy:
                                print(stk_to_buy, ' is bought at a price of ', trade_price_today.loc[stk_to_buy], ', with ', delta_position.loc[stk_to_buy], 'hands and RMB',
                                      cost.loc[stk_to_buy], ' (commission incl.)')
                        remaining_cash = cash_after_selling - cost_cum.iloc[i_mark]  # find the remaining cash after selling

                        buy_remaining_position = 0.0
                        if remaining_cash > 0:  # the remaining money is used to buy the last stock
                            if i_mark + 1 < len(buy_stk_set):
                                stock_buy_use_remaining = buy_stk_set[i_mark + 1]
                                sufficient_money_buy = remaining_cash / (1 + self._Backtester__commission) / today_price.loc[stock_buy_use_remaining]
                                insufficient_money_buy = (remaining_cash - self._Backtester__minimum_commission) / today_price.loc[stock_buy_use_remaining]
                                if sufficient_money_buy < insufficient_money_buy:
                                    # enough money to buy, commission fee is higher
                                    buy_remaining_position = insufficient_money_buy
                                else:
                                    # enough money to buy, commission fee is higher
                                    buy_remaining_position = sufficient_money_buy
                                buy_remaining_position = int(np.float64(buy_remaining_position) / 100) * 100
                                buy_stk_set_current_buy.append(stock_buy_use_remaining)
                                buy_stk_set_current_buy = list(np.unique(buy_stk_set_current_buy))
                                plan_refreshed_position.loc[stock_buy_use_remaining] = self._Backtester__position.loc[(date, stock_buy_use_remaining)] + buy_remaining_position
                        buy_stk_set = buy_stk_set_current_buy

                        if buy_remaining_position > 0:
                            last_buy_stock_cost = buy_remaining_position * today_price.loc[stock_buy_use_remaining]
                            commission_fee = np.maximum(last_buy_stock_cost * self._Backtester__commission, self._Backtester__minimum_commission)
                            last_buy_stock_cost = last_buy_stock_cost + commission_fee
                            f.write('{} is bought at a price of {}, with {} hands and RMB {} (commission {} incl.).\n'.format(stock_buy_use_remaining,
                                                                                                                              today_price.loc[stock_buy_use_remaining],
                                                                                                                              buy_remaining_position, last_buy_stock_cost,
                                                                                                                              commission_fee))
                            if not self._Backtester__silent:
                                print(stock_buy_use_remaining, ' is bought by remaining money at a price of ', today_price.loc[stock_buy_use_remaining], ', with ',
                                      buy_remaining_position, 'hands and RMB', last_buy_stock_cost, ' (commission incl.)')
                            cost_of_buying = cost_cum.iloc[i_mark] + last_buy_stock_cost
                        else:
                            cost_of_buying = cost_cum.iloc[i_mark]
                    else:  # buy only one stock or no stock is bought
                        if len(buy_stk_set) == 1:  # buy only one stock
                            buy_stk_set_current_buy = []
                            remaining_cash = cash_after_selling
                            stock_buy_use_remaining = []
                            buy_remaining_position = 0.0
                            if remaining_cash > 0:  # there is cash to buy stocks
                                stock_buy_use_remaining = buy_stk_set[0]  # stock to buy
                                sufficient_money_buy = remaining_cash / (1 + self._Backtester__commission) / today_price.loc[stock_buy_use_remaining]
                                insufficient_money_buy = (remaining_cash - self._Backtester__minimum_commission) / today_price.loc[stock_buy_use_remaining]
                                if sufficient_money_buy < insufficient_money_buy:
                                    # enough money to buy, commission fee is higher
                                    buy_remaining_position = insufficient_money_buy
                                else:
                                    # enough money to buy, commission fee is higher
                                    buy_remaining_position = sufficient_money_buy
                                buy_remaining_position = int(np.float64(buy_remaining_position) / 100) * 100
                                buy_stk_set_current_buy.append(stock_buy_use_remaining)
                                buy_stk_set_current_buy = list(np.unique(buy_stk_set_current_buy))
                                plan_refreshed_position.loc[stock_buy_use_remaining] = self._Backtester__position.loc[(date, stock_buy_use_remaining)] + buy_remaining_position
                            buy_stk_set = buy_stk_set_current_buy
                            if len(stock_buy_use_remaining) == 0:
                                cost_of_buying = 0.0
                                f.write('No stock is bought.\n')
                                if not self._Backtester__silent:
                                    print('No stock is bought.')
                            else:
                                cost_of_buying = buy_remaining_position * today_price.loc[stock_buy_use_remaining]
                                commission_fee = np.maximum(cost_of_buying * self._Backtester__commission, self._Backtester__minimum_commission)
                                cost_of_buying += commission_fee
                                f.write('Only one stock is bought.\n')
                                f.write('{} is bought at a price of {}, with {} hands and RMB {} (commission {} incl.).\n'.format(stock_buy_use_remaining,
                                                                                                                                  today_price.loc[stock_buy_use_remaining],
                                                                                                                                  buy_remaining_position, cost_of_buying,
                                                                                                                                  commission_fee))
                                if not self._Backtester__silent:
                                    print('Only one stock is bought.')
                                    print(stock_buy_use_remaining, ' is bought by remaining at a price of ', today_price.loc[stock_buy_use_remaining], ', with ',
                                          buy_remaining_position, 'hands and RMB', cost_of_buying, ' (commission incl.)')
                else:
                    # nothing to buy
                    buy_stk_set = []
                    cost_of_buying = 0
                    f.write('Only one stock is bought.\n')
                    if not self._Backtester__silent:
                        print('No stock is bought.')
                cash = cash_after_selling - cost_of_buying
                # update positions for but stock set
                hold_position.loc[buy_stk_set] = plan_refreshed_position.loc[buy_stk_set]
                # calculate the ratio of bought stocks
                if cash_in_stock > 0:
                    buy_rate = cost_of_buying / (1 + self._Backtester__commission) / cash_in_stock
                else:
                    buy_rate = np.float64(0.0)
                self._Backtester__turnover_rate.loc[date] = [buy_rate, sell_rate]
                # the positions for stocks not in buy or sell stock set will remain unchanged
                non_stk_set = list(set(self._Backtester__universe) - set(sell_stk_set) - set(buy_stk_set))
                hold_position.loc[non_stk_set] = today_position_before_trading.loc[non_stk_set]
                f.write('Summary of today\'s transaction:\n')
                f.write('>> Date: {}\n'.format(date))
                f.write('>> Remaining cash: {:f}\n'.format(cash))
                f.write('>> Have stocks:\n{}\n'.format(hold_position[hold_position > 0]))

                if not self._Backtester__silent:
                    print('Summary of today\'s transaction:')
                    print('>> Date: ', date)
                    print('>> Remaining cash: {:f}'.format(cash))
                    print('>> Have stocks:')
                    print(hold_position[hold_position > 0])
                self._Backtester__cash.loc[date] = cash
                self._Backtester__position.loc[date] = hold_position
                self._Backtester__day_before_cur_refresh = date
            else:
                f.write('Skipping {}'.format(date))
                if not self._Backtester__silent:
                    print('Skipping ', date)
            self._Backtester__day_before_cur_refresh = date
            self._Backtester__last_refresh_date = date
            self._Backtester__portfolio_value.loc[date] = self._Backtester__cash.loc[date] + np.nansum(self._Backtester__position.loc[date] * trade_price_today)
            self._Backtester__return_net.loc[date] = self._Backtester__portfolio_value.loc[date] / self._Backtester__capital

            if not self._Backtester__keep_cap:
                # keep the market capital constant
                self._Backtester__portfolio_value_on_close.loc[date] = self._Backtester__cash.loc[date] + np.nansum(
                    self._Backtester__position.loc[date] * self._Backtester__close.loc[date])
                self._Backtester__return_net_on_close.loc[date] = self._Backtester__portfolio_value_on_close.loc[date] / self._Backtester__capital
            else:
                # do not keep the market capital constant
                temp_pf_value_on_close = self._Backtester__cash.loc[date] + np.nansum(self._Backtester__position.loc[date] * self._Backtester__close.loc[date])
                if len_date == 1:
                    self._Backtester__daily_return.loc[date] = temp_pf_value_on_close / self._Backtester__capital
                    self._Backtester__return_net_on_close.loc[date] = self._Backtester__daily_return.loc[date]
                else:
                    self._Backtester__daily_return.loc[date] = temp_pf_value_on_close / self._Backtester__portfolio_value_on_close.loc[last_night]
                    self._Backtester__return_net_on_close.loc[date] = self._Backtester__return_net_on_close.loc[last_night] * self._Backtester__daily_return.loc[date]
                if len_date == 1:
                    last_pf_value = self._Backtester__capital
                else:
                    last_pf_value = self._Backtester__portfolio_value_on_close.loc[last_night]
                self._Backtester__cash.loc[date] *= last_pf_value / temp_pf_value_on_close
                self._Backtester__position.loc[date] *= last_pf_value / temp_pf_value_on_close
                self._Backtester__portfolio_value_on_close.loc[date] = self._Backtester__cash.loc[date] + np.nansum(
                    self._Backtester__position.loc[date] * self._Backtester__close.loc[date])

            f.write('Updating portfolio value after market close to {}\n'.format(self._Backtester__portfolio_value_on_close.loc[date]))
        print('Backtesting complete.')

    def performance(self, trim_freq='WF', index_net_day1=0.0, save_path='', name='test_performance', show_plot=True):
        performance_path = save_path + name + '/'
        if not os.path.exists(performance_path):
            os.mkdir(performance_path)
        net_on_close = self.get_return_net_on_close()
        net_on_close.to_csv(performance_path + 'Nav_on_close.csv')
        perf_net = self._Backtester__cal_performance(net_on_close)
        bcm_net = self.get_benchmark_index()
        if trim_freq in ('wf', 'WF'):
            hedge_net_on_close = self._Backtester__hedge_plus(net_on_close, bcm_net, index_net_day1)
        else:
            if trim_freq in ('d', 'D'):
                hedge_net_on_close = self._Backtester__hedge(net_on_close, bcm_net, index_net_day1)
            else:
                hedge_net_on_close = self._Backtester__hedge(net_on_close, bcm_net, index_net_day1)
        self._Backtester__hedge_net_on_close = deepcopy(hedge_net_on_close)
        hedge_net_on_close.to_csv(performance_path + 'Hedging_Nav_on_close.csv')
        perf_hedge = self._Backtester__cal_performance(hedge_net_on_close)
        print('Strategy Performance')
        self._Backtester__plot_all(net_on_close, bcm_net, hedge_net_on_close, index_net_day1, performance_path, show_plot)
        print('Turnover')
        print(self._Backtester__turnover_rate.iloc[1:].mean())
        print('Long')
        print(perf_net)
        print('Hedging')
        print(perf_hedge)
        perf = (pd.DataFrame(columns=perf_net.index, index=['Long', 'Hedging'], data=[perf_net['Summary'], perf_hedge['Summary']])).T
        perf.to_csv(performance_path + 'Summary.csv')
        return perf

    def __cal_performance(self, net):
        period = 252
        ret = np.append(1, net.values)
        Total_return = ret[-1]
        Annualized_Return = math.pow(Total_return, period / (len(ret) - 1)) - 1
        net_chg = ret[1:] / ret[:-1] - 1
        Annualized_Volatility = np.std(net_chg) * np.sqrt(period)
        Sharpe = Annualized_Return / Annualized_Volatility
        drawndown = []
        for i in range(0, len(ret)):
            l = []
            for j in range(i, len(ret)):
                l.append((ret[j] - ret[i]) / ret[i])

            drawndown.append(np.nanmin(l))

        drawndown.append(0)
        Maxdrawndown = abs(np.min(drawndown))
        df = pd.Series(index=['Total_Net_Value', 'Annualized_Return', 'Annualized_Volatility', 'Sharpe', 'Maxdrawndown'])
        df.iloc[:] = [Total_return, Annualized_Return, Annualized_Volatility, Sharpe, Maxdrawndown]
        df = pd.DataFrame(df.values, columns=['Summary'], index=df.to_frame().index)
        return df

    def __hedge(self, net, bcm_index, index_net_day1=0.0):
        bcm_chg = bcm_index.iloc[1:] / bcm_index.iloc[:-1].values - 1
        net_chg = net.iloc[1:] / net.iloc[:-1].values - 1
        hedge_net = pd.Series(index=net.index)
        if index_net_day1 in ('off', 'OFF', 'Off'):
            index_net_day1 = net[0] / 1 - 1
        hedge_net.iloc[0] = net[0] / 1 - 1 - index_net_day1 + 1
        hedge_net.iloc[1:] = (net_chg - bcm_chg.loc[net_chg.index] + 1).cumprod() * hedge_net.iloc[0]
        return hedge_net

    def __hedge_plus(self, net, bcm_index, index_net_day1=0.0):
        net.index = pd.to_datetime(net.index)
        weekly_first_trading_day = pd.DataFrame(index=net.index, columns=['date'], data=net.index.tolist())
        weekly_first_trading_day = weekly_first_trading_day.groupby(pd.Grouper(key='date', freq='1w'))['date'].first()
        weekly_first_trading_day = weekly_first_trading_day[pd.notnull(weekly_first_trading_day)].tolist()
        net_rebalance = net.loc[weekly_first_trading_day]
        bcm_rebalance = bcm_index.loc[weekly_first_trading_day]
        net_rebalance_chg = net_rebalance.iloc[1:] / net_rebalance.iloc[:-1].values - 1
        bcm_rebalance_chg = bcm_rebalance.iloc[1:] / bcm_rebalance.iloc[:-1].values - 1
        hedge_net = pd.Series(index=net.index)
        if index_net_day1 in ('off', 'OFF', 'Off'):
            index_net_day1 = net[0] / 1 - 1
        hedge_net.iloc[0] = net[0] / 1 - 1 - index_net_day1 + 1
        hedge_net.loc[weekly_first_trading_day[1:]] = (net_rebalance_chg - bcm_rebalance_chg + 1).cumprod() * hedge_net.iloc[0]
        for i in range(len(weekly_first_trading_day)):
            this_rb_day = weekly_first_trading_day[i]
            if i + 1 < len(weekly_first_trading_day):
                next_rb_day = weekly_first_trading_day[i + 1]
            else:
                next_rb_day = net.index[-1]
            week_trading_dates = net.loc[this_rb_day:next_rb_day].index
            if i + 1 < len(weekly_first_trading_day):
                week_trading_dates = week_trading_dates[:-1]
            non_rb_dates = week_trading_dates[1:]
            if len(non_rb_dates) > 0:
                net_R = net.loc[week_trading_dates] / net.loc[this_rb_day]
                bcm_R = bcm_index.loc[week_trading_dates] / bcm_index.loc[this_rb_day]
                net_R_diff = net_R[1:] - net_R[:-1].values
                bcm_R_diff = bcm_R[1:] - bcm_R[:-1].values
                hedge_net.loc[non_rb_dates] = (net_R_diff - bcm_R_diff + 1).cumprod() * hedge_net.loc[this_rb_day]

        return hedge_net

    def __plot_all(self, net, bcm_index, hedge_net, index_net_day1, save_path, show_plot):
        bcm_price = bcm_index.loc[hedge_net.index]
        bcm_net = bcm_price / bcm_price.values[0]
        if index_net_day1 not in ('off', 'OFF', 'Off'):
            bcm_net[0] = 1 + index_net_day1
        start = pd.Series(index=['start'], data=[1])
        net.index = net.index.astype(str)
        net = start.append(net)
        hedge_net.index = hedge_net.index.astype(str)
        hedge_net = start.append(hedge_net)
        bcm_net.index = bcm_net.index.astype(str)
        bcm_net = start.append(bcm_net)
        if not show_plot:
            plt.switch_backend('agg')
        N = len(net)
        ind = np.arange(N)
        fig = plt.figure(figsize=(20, 8))
        ax = fig.add_subplot(111)
        lns0 = ax.plot(ind, net.values, '#ff0000', label='long')
        lns1 = ax.plot(ind, hedge_net.values, '#66ccff', label='hedge')
        lns2 = ax.plot(ind, bcm_net.values, '#0000ff', label='benchmark')
        maxd = [0]
        N = len(hedge_net)
        for i in range(1, N):
            maxd.append(1 - hedge_net[i] / max(hedge_net[0:i + 1]))

        maxd = pd.Series(index=hedge_net.index, data=maxd)
        plt.gca()
        ax.set_xlabel('Time')
        ax.set_ylabel('net')
        num = int(N / 20) + 1
        x1 = [i for i in range(0, N, num)]
        ax.set_xticks(x1)
        label = net.index.astype(str)[x1].tolist()
        ax.set_xticklabels(label, minor=False, rotation=30)
        ax.set_facecolor('#eeeeee')
        ax.legend(loc=2)
        ax.grid()
        plt.show()