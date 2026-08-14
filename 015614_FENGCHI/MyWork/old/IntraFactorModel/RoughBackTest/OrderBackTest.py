# @Time : 2020/5/8 11:08
# @Author : Zhichen Lu
# @File : 4.IntradayIntegration.py

import copy
import time

from dataApi.getData import get_minute_1factor, get_daily_1factor
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, trade_minutes
from dataApi.usefulTools import *


def shift_back(arr, n):
    arr_shift = arr.copy()
    arr_shift[:-n] = arr_shift[n:]
    arr_shift[-n:] = np.nan
    return arr_shift


def new_delay(arr, l):
    a = delay(l)
    a[:l] = np.nan
    return a


class IntradayBackTest():
    def __init__(self, interval=5, start_date=20170103, end_date=20191231, pool='COMMON'):
        e = time.time()
        if type(pool) == str:
            if pool not in ['COMMON', 'ZZ500', 'ZZ1000', 'ZZ800', 'HS300', 'ALL']:
                raise Exception('Wrong pool type')
            stock_pool = clean_stock_list(pool, no_ST=False, no_pause=True, no_limit_down=True, no_limit_up=True)
        elif type(pool) == pd.DataFrame:
            pass
        else:
            raise Exception('Wrong pool type')
        print(1, time.time() - e)
        date_list = get_date_range(start_date, end_date)
        stock_pool = stock_pool.loc[start_date:end_date]
        print(2, time.time() - e)
        close = get_minute_1factor('close', start_datetime=start_date, end_datetime=end_date, code_list=stock_pool.columns.tolist())
        index, columns = close.index.tolist(), close.columns.tolist()
        close = frame2arr(close)
        twap = get_daily_1factor('twap', date_list=date_list, code_list=columns)

        order_1_buy_price = pd.read_hdf('/data/group/800319/junkData/IntraFactorModel/MinutelyTickByFactor_from2017/Buy1Price.h5', 'Buy1Price')
        order_1_sell_price = pd.read_hdf('/data/group/800319/junkData/IntraFactorModel/MinutelyTickByFactor_from2017/Sell1Price.h5', 'Sell1Price')
        order_1_buy_price = order_1_buy_price.reindex(columns, axis=1).loc[(start_date, 925):(end_date, 1500)]
        order_1_sell_price = order_1_sell_price.reindex(columns, axis=1).loc[(start_date, 925):(end_date, 1500)]
        order_1_buy_price = frame2arr(order_1_buy_price)
        order_1_sell_price = frame2arr(order_1_sell_price)
        order_1_buy_price = shift_back(order_1_buy_price, 1)
        order_1_sell_price = shift_back(order_1_sell_price, 1)
        print(3, time.time() - e)

        self.index = index
        self.columns = columns
        self.date_list = date_list
        self.close = close
        self.order_1_buy_price = order_1_buy_price
        self.order_1_sell_price = order_1_sell_price
        # self.future_twap = shift_back(ts_mean(close, interval), interval)
        self.change_position_idx = [1 + 5 * i for i in range(43)]
        self.change_position_point = [trade_minutes[i] for i in self.change_position_idx]
        self.daily_twap = twap
        # self.future_deal_twap = self.future_twap[self.change_position_idx]
        # self.future_deal_twap[-1] = np.nanmean(close[self.change_position_idx[-1]:],axis=0)
        self.future_deal_markt_price = self.close[self.change_position_idx]
        self.future_deal_markt_price[-1] = np.nanmean(close[self.change_position_idx[-1]:], axis=0)
        self.future_buy_1_deal_price = self.order_1_buy_price[self.change_position_idx]
        self.future_sell_1_deal_price = self.order_1_sell_price[self.change_position_idx]
        self.future_buy_1_deal_price[-1] = self.future_deal_markt_price[-1].copy()
        self.future_sell_1_deal_price[-1] = self.future_deal_markt_price[-1].copy()
        self.daily_close_adj = get_daily_1factor('close_badj', date_list=date_list, code_list=columns)
        self.daily_close = get_daily_1factor('close', date_list=date_list, code_list=columns)
        print(4, time.time() - e)

    def get_deal_price(self,start,end,slippage_count,deal_type='default'):
        # TODO:盘口
        if deal_type=='default':
            if abs(slippage_count) > 0.01:
                raise Exception('Slippage_count too huge:',slippage_count)
            return self.future_deal_markt_price[:, self.date_list.index(start):self.date_list.index(end) + 1, :] * (1 + slippage_count)
        elif deal_type=='add':
            if abs(slippage_count)>0.1:
                raise Exception('Slippage_count too huge:',slippage_count)
            return self.future_deal_markt_price[:, self.date_list.index(start):self.date_list.index(end) + 1, :] + slippage_count
        elif deal_type == 'tick_B':
            return self.future_sell_1_deal_price[:, self.date_list.index(start):self.date_list.index(end) + 1, :]
        elif deal_type == 'tick_S':
            return self.future_buy_1_deal_price[:, self.date_list.index(start):self.date_list.index(end) + 1, :]
        elif deal_type == 'all_B':
            price = self.future_deal_markt_price.copy()
            price = np.where(self.future_deal_markt_price <= 10, self.future_sell_1_deal_price, price)
            price = np.where(self.future_deal_markt_price > 10, self.future_buy_1_deal_price + 0.01, price)
            return price
        elif deal_type == 'all_S':
            price = self.future_deal_markt_price.copy()
            price = np.where(self.future_deal_markt_price <= 10, self.future_buy_1_deal_price, price)
            price = np.where(self.future_deal_markt_price > 10, self.future_sell_1_deal_price - 0.01, price)
            return price
        else:
            raise Exception('Wrong type')

    def calc_deal_price_fix(self, signal, slippage, flag,deal_type='default'):
        signal_df = signal.reindex(self.columns, axis=1)
        start, end = signal_df.index[0][0], signal_df.index[-1][0]
        signal = frame2arr(signal_df)
        if flag == 'B':
            signal[signal == 0] = 1
            signal[signal == -1] = 0
            # slippage_count = 1 + slippage
            flag_sig = -1
        elif flag == 'S':
            signal[signal == 0] = -1
            signal[signal == 1] = 0
            signal = signal * -1
            # slippage_count = 1 - slippage
            flag_sig = 1
        else:
            raise Exception('Wrong flag type')
        if deal_type == 'tick':
            deal_type = deal_type + '_' + flag
        elif deal_type == 'all':
            deal_type = deal_type + '_' + flag
        slippage_count = -1 * flag_sig * slippage
        print(deal_type, flag, slippage_count)
        change_point_signal = signal.copy()[self.change_position_idx]
        # np.array(time_list)[change_position_point]
        tag = np.array([np.ones(signal.shape[1:]) * (i + 1.) for i in range(len(self.change_position_idx))])
        how = change_point_signal * tag
        target_fulfill = ts_cummax(how)
        target_fulfill[-1] = len(self.change_position_idx)
        previou_fulfill = delay(ts_cummax(how), 1)
        actual_amt = target_fulfill - previou_fulfill
        actual_amt[0] = how[0]
        change_point_deal_price = self.get_deal_price(start,end,slippage_count,deal_type)
        deal_amt = change_point_deal_price * actual_amt
        # 每日每只股票成交均价
        avg_price = np.nansum(deal_amt, axis=0) / len(self.change_position_idx)
        avg_price = pd.DataFrame(avg_price, index=self.date_list[self.date_list.index(start):self.date_list.index(end) + 1], columns=self.columns)
        avg_price[avg_price == 0] = self.daily_twap[avg_price == 0]
        daily_outperform = avg_price / self.daily_twap - 1
        avg_price[abs(daily_outperform) > 0.1] = self.daily_twap[abs(daily_outperform) > 0.1]
        daily_outperform[abs(daily_outperform) > 0.1] = 0
        daily_outperform = daily_outperform * flag_sig
        return avg_price, daily_outperform

    def calc_deal_price_unfix(self, signal, slippage, flag,deal_type='default', n=10):
        """
        43个下单点，每只股票每天分 n 次下单
        :param signal:
        :param slippage:
        :param flag:
        :return:
        """

        signal_df = signal.reindex(self.columns, axis=1)
        start, end = signal_df.index[0][0], signal_df.index[-1][0]
        signal = frame2arr(signal_df)
        if flag == 'B':
            signal[signal == 0] = 1
            signal[signal == -1] = 0
            # slippage_count = 1 + slippage
            flag_sig = -1
        elif flag == 'S':
            signal[signal == 1] = 0
            signal = signal * -1
            # slippage_count = 1 - slippage
            flag_sig = 1
        else:
            raise Exception('Wrong flag type')
        if deal_type == 'tick':
            deal_type = deal_type + '_' + flag
        elif deal_type == 'all':
            deal_type = deal_type + '_' + flag
        slippage_count = -1 * flag_sig * slippage
        print(deal_type, flag, slippage_count)
        change_point_signal = signal.copy()[self.change_position_idx]
        # np.array(time_list)[change_position_point]
        tag = np.array([np.ones(signal.shape[1:]) * (i + 1.) for i in range(len(self.change_position_idx))])
        how = change_point_signal * tag
        target_fulfill = ts_cummax(how)
        previou_fulfill = delay(target_fulfill, 1)
        target_fulfill[target_fulfill > n] = n
        previou_fulfill[previou_fulfill > n] = n
        target_fulfill[-1] = n
        actual_amt = target_fulfill - previou_fulfill
        actual_amt[0] = how[0]
        change_point_deal_price = self.get_deal_price(start,end,slippage_count,deal_type)
        deal_amt = change_point_deal_price * actual_amt
        # 每日每只股票成交均价
        avg_price = np.nansum(deal_amt, axis=0) / n
        avg_price = pd.DataFrame(avg_price, index=self.date_list[self.date_list.index(start):self.date_list.index(end) + 1], columns=self.columns)
        avg_price[avg_price == 0] = self.daily_twap[avg_price == 0]
        daily_outperform = avg_price / self.daily_twap - 1
        avg_price[abs(daily_outperform) > 0.1] = self.daily_twap[abs(daily_outperform) > 0.1]
        daily_outperform[abs(daily_outperform) > 0.1] = 0
        daily_outperform = daily_outperform * flag_sig
        # a = self.daily_twap
        ################
        # actual_amt[:,5,0]
        # self.get_deal_price(start,end,slippage_count,deal_type)[:,5,0]*actual_amt[:,5,0]
        # self.future_deal_markt_price[:,5,0]*actual_amt[:,5,0]
        # self.daily_twap.loc[20170110,1]
        ################
        return avg_price, daily_outperform

    def run_backtest(self, signal_df, buy_weight, sell_weight, slippage=0.0005, backtest_type='unfix',deal_type='default'):
        if len(signal_df) != len(self.index):
            signal_df = signal_df.reindex(self.index, axis=0)
        if backtest_type=='unfix':
            calc_deal_price = self.calc_deal_price_unfix
        elif backtest_type=='fix':
            calc_deal_price = self.calc_deal_price_fix
        else:
            raise Exception('Undefined RoughBackTest type')
        avg_buy, outperform_buy = calc_deal_price(signal_df, slippage, 'B',deal_type)
        avg_sell, outperform_sell = calc_deal_price(signal_df, slippage, 'S',deal_type)

        # buy_weight = (buy_weight.T / buy_weight.sum(axis=1)).T
        # sell_weight = (sell_weight.T / sell_weight.sum(axis=1)).T
        outperform_buy.loc[:, list(set(outperform_buy.columns) - set(signal_df.columns))] = np.nan
        outperform_sell.loc[:, list(set(outperform_sell.columns) - set(signal_df.columns))] = np.nan
        buy_improve = (outperform_buy.loc[buy_weight.index, buy_weight.columns] * buy_weight).sum(axis=1)
        sell_improve = (outperform_sell.loc[sell_weight.index, sell_weight.columns] * sell_weight).sum(axis=1)
        return buy_improve, sell_improve, avg_buy, avg_sell, outperform_buy.loc[buy_weight.index, buy_weight.columns], outperform_sell.loc[sell_weight.index, sell_weight.columns]

    def run_backtest_tick_twap(self, signal_df, buy_weight, sell_weight, slippage=0.0005, backtest_type='unfix', deal_type='tick'):
        if len(signal_df) != len(self.index):
            signal_df = signal_df.reindex(self.index, axis=0)
        if backtest_type == 'unfix':
            calc_deal_price = self.calc_deal_price_unfix
        elif backtest_type == 'fix':
            calc_deal_price = self.calc_deal_price_fix
        else:
            raise Exception('Undefined RoughBackTest type')

        signal_buy = copy.deepcopy(signal_df)
        signal_buy[signal_buy == 0] = -1
        signal_sell = copy.deepcopy(signal_df)
        signal_sell[signal_sell == 0] = -1

        avg_buy, outperform_buy = calc_deal_price(signal_buy, slippage, 'B', deal_type)
        avg_sell, outperform_sell = calc_deal_price(signal_sell, slippage, 'S', deal_type)

        # buy_weight = (buy_weight.T / buy_weight.sum(axis=1)).T
        # sell_weight = (sell_weight.T / sell_weight.sum(axis=1)).T
        outperform_buy.loc[:, list(set(outperform_buy.columns) - set(signal_df.columns))] = np.nan
        outperform_sell.loc[:, list(set(outperform_sell.columns) - set(signal_df.columns))] = np.nan
        buy_improve = (outperform_buy.loc[buy_weight.index, buy_weight.columns] * buy_weight).sum(axis=1)
        sell_improve = (outperform_sell.loc[sell_weight.index, sell_weight.columns] * sell_weight).sum(axis=1)
        return buy_improve, sell_improve, avg_buy, avg_sell, outperform_buy.loc[buy_weight.index, buy_weight.columns], outperform_sell.loc[sell_weight.index, sell_weight.columns]


    def calc_portfolio_improve(self, signal_df, weight_diff, val_g, val_b, val_net, slippage=0.0005, buy_improve=None,
                               sell_improve=None, backtest_type='unfix', deal_type='default', sinal_type='non_tick'):
        if type(buy_improve) == type(None) or type(sell_improve) == type(None):
            if type(weight_diff) == tuple:
                buy_weight, sell_weight = weight_diff
            elif type(weight_diff) == pd.DataFrame:
                buy_weight, sell_weight = (weight_diff > 0) * weight_diff, -1*(weight_diff < 0) * weight_diff
            else:
                raise Exception('Wrong weight_diff type')
            if sinal_type == 'tick':
                buy_improve, sell_improve, avg_buy, avg_sell, outperform_buy, outperform_sell = self.run_backtest_tick_twap(signal_df, buy_weight, sell_weight, slippage,
                                                                                                                            backtest_type=backtest_type, deal_type=deal_type)
            else:
                buy_improve, sell_improve, avg_buy, avg_sell, outperform_buy, outperform_sell = self.run_backtest(signal_df, buy_weight, sell_weight, slippage,
                                                                                                                  backtest_type=backtest_type, deal_type=deal_type)
        imprtove = buy_improve.shift(1).fillna(0) + sell_improve.fillna(0)
        actual_pct = val_g.pct_change() + imprtove.loc[val_g.index]
        net = (1 + actual_pct.fillna(0)).cumprod()  # .fillna(1)
        active = net - val_b
        compare = pd.DataFrame({'origin': val_net, 'with_intraday': active})
        compare['improve'] = active - val_net
        return compare, avg_buy, avg_sell, outperform_buy, outperform_sell

    """
            def calc_deal_price_old2(self, signal, slippage, flag):
            signal_df = signal.reindex(self.columns, axis=1)
            start, end = signal_df.index[0][0], signal_df.index[-1][0]
            signal = frame2arr(signal_df)
            if flag == 'B':
                signal[signal == 0] = 1
                signal[signal == -1] = 0
                slippage_count = 1 + slippage
                flag_sig = -1
            elif flag == 'S':
                signal[signal == 1] = 0
                signal = signal * -1
                slippage_count = 1 - slippage
                flag_sig = 1
            else:
                raise Exception('Wrong flag type')

            change_point_signal = signal.copy()[self.change_position_idx]
            # np.array(time_list)[change_position_point]
            actual_amt = change_point_signal.copy()
            actual_amt[-1] = 1
            actual_amt[delay(actual_amt) == 0] += 1

            change_point_deal_price = self.get_deal_price(start,end,slippage_count,deal_type)
            deal_amt = change_point_deal_price * actual_amt
            # 每日每只股票成交均价
            avg_price = np.nansum(deal_amt, axis=0) / len(self.change_position_idx)
            avg_price = pd.DataFrame(avg_price, index=self.date_list[self.date_list.index(start):self.date_list.index(end) + 1], columns=self.columns)
            avg_price[avg_price == 0] = self.daily_twap[avg_price == 0]
            daily_outperform = avg_price / self.daily_twap - 1
            daily_outperform = daily_outperform * flag_sig

            (daily_outperform > 0).mean(axis=1).mean()
            return avg_price, daily_outperform
        """













