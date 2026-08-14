# @Time : 2020/12/15 9:19
# @Author : Zhichen Lu
# @File : run_StartWithLimitCashVolConsider.py

from backtest.StrategyBackTest.PortfolioStrategyBase import PortfolioStrategyBase, InitailCashBasedEvaluationHelper
from tqdm import tqdm
import gc
import pandas as pd
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path, root_path
from dataApi.getData import get_daily_1factor
import bottleneck
from dataApi.tradeDate import get_pre_trade_date
from dataApi.getData import get_minute_1factor

def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)

def delay(arr, l=1):
    return fill_nan(arr[:-l], l)

def calc_recent_count(signal,window=20):
    signal_arr = signal.values.reshape(signal.shape[0]//7, 7, signal.shape[-1])
    idx_arr = np.empty(signal_arr.shape)
    for idx in range(7):
        idx_arr[:, idx, :] = np.ones((idx_arr.shape[0], idx_arr.shape[-1])) * idx + 1
    idx_arr[~signal_arr] = np.nan
    first_signal = np.nanmin(idx_arr, axis=1)[:, None, :]
    is_triggered_first = np.isclose(first_signal, idx_arr)
    recent_20d_s_count = bottleneck.move_sum(np.where(is_triggered_first,1,0),axis=0,window=window)
    recent_20d_s_count = delay(recent_20d_s_count,2)
    recent_20d_s_count = pd.DataFrame(recent_20d_s_count.reshape(signal.shape),index=signal.index,columns=signal.columns)
    barly_recent_20d_s_count = recent_20d_s_count.sum(axis=1).unstack()
    barly_recent_20d_ratio = (barly_recent_20d_s_count.T/barly_recent_20d_s_count.sum(axis=1)).T
    return barly_recent_20d_ratio,barly_recent_20d_s_count


class StartWithLimitCashVolConsider(PortfolioStrategyBase):
    def __init__(self, signal,inter_signal, start=20140101, end=20181231, stock_pool=None, target_point=None,
                 buy_cost=0.001, sell_cost=0.001, per_amt_ratio=0.0025, append_param={}, initial_cash=200000000, barly_max_buy=100,
                 deal_percent=0.1, stk_min_amt=None, down_signal_ratio=None, signal_threshold=None,down_swing_threshold=0,
                 cash_added={},per_ratio_change={},max_trigger_num={},index_list=['SZZZ','SZCZ'],condition_series={}):
        per_amt = round(initial_cash * per_amt_ratio, -5)
        self.bar_signal_ratio_ratio, _ = calc_recent_count(np.isfinite(signal))
        super().__init__(start, end, stock_pool, target_point, buy_cost, sell_cost, per_amt, append_param=append_param)
        self.bar_signal_ratio_ratio = self.bar_signal_ratio_ratio.reindex(self.date_list)
        self.daily_high = get_daily_1factor('high', self.date_list, self.stk_list)
        self.daily_low = get_daily_1factor('low', self.date_list, self.stk_list)
        self.signal = signal.reindex(self.close.index)
        self.inter_signal = {x:inter_signal[x].reindex(self.close.index) for x in inter_signal}
        self.data_flow['signal'] = None
        self.data_flow['inter_signal'] = None
        self.last_buy_time = {}
        self.cash = initial_cash
        self.accout_value = initial_cash
        self.per_amt_ratio = per_amt_ratio
        self.barly_max_buy = barly_max_buy
        self.cash_series = pd.Series(np.nan, index=self.date_list)
        self.holding_value = pd.Series(np.nan, index=self.date_list)
        self.holding_num = pd.Series(np.nan, index=self.date_list)
        self.down_signal_ratio = down_signal_ratio
        self.signal_threshold = signal_threshold
        self.down_swing_threshold = down_swing_threshold
        # self.vol_cumsum = pd.read_pickle(deal_price_path + 'vol_rolling_30_sum.pkl').reindex(self.close.index)

        bench_close = get_minute_1factor('close', type='bench', start_datetime=get_pre_trade_date(start, 10), end_datetime=end, base_date=20100101).fillna(method='pad')

        self.MA5_minus_MA10 = {}
        self.MA5 = {}
        self.bench = {}
        self.bench_ret = {}
        for index_tag in index_list:
            bench_arr = bench_close[index_tag].values.reshape(bench_close.shape[0] // 242, 242)
            move_mean5, move_mean10 = [], []
            for i in range(1, 11):
                temp = delay(bench_arr[:, [-1], None], i)
                move_mean10.append(temp)
                if i < 6:
                    move_mean5.append(temp)
            move_mean5 = np.concatenate(move_mean5, axis=-1)
            move_mean5 = np.nanmean(move_mean5, axis=-1)
            move_mean10 = np.concatenate(move_mean10, axis=-1)
            move_mean10 = np.nanmean(move_mean10, axis=-1)
            move_mean10[:10, :] = np.nan
            move_mean5[:5, :] = np.nan
            bench_ret = bench_arr / move_mean5 - 1
            MA5_minus_MA10 = move_mean5 / move_mean10 - 1
            MA5_minus_MA10 = pd.Series(MA5_minus_MA10[:, 0], index=bench_close.index.levels[0])
            self.MA5_minus_MA10[index_tag] = MA5_minus_MA10.loc[self.date_list]
            self.MA5[index_tag] = pd.Series(move_mean5[:, 0], index=bench_close.index.levels[0]).loc[self.date_list]
            self.bench[index_tag] = pd.Series(bench_arr.flatten(), index=bench_close.index).shift(1).loc[self.close.index]
            self.bench_ret[index_tag] = pd.Series(bench_ret.flatten(), index=bench_close.index).shift(1).loc[self.close.index]

        if 'past_vol_path' in append_param:
            self.past_5day_future_30min_vol = pd.read_pickle(append_param['past_vol_path']).reindex(self.close.index)
        else:
            self.past_5day_future_30min_vol = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl').reindex(self.close.index)
        self.past_5day_future_30min_vol.columns = [int(str(x)[:6]) for x in self.past_5day_future_30min_vol.columns]
        if 'future_deal_vol' in append_param:
            self.future_30_min_vol = pd.read_pickle(append_param['future_deal_vol']).reindex(self.close.index)
        else:
            self.future_30_min_vol = pd.read_pickle(deal_price_path + 'vol_future_rolling_30_sum.pkl').reindex(self.close.index)
        self.daily_info['pre_close'] = self.daily_info['close'] * self.daily_info['close_badj'].shift(1) / self.daily_info['close_badj']
        self.deal_percent = deal_percent
        if stk_min_amt is None:
            self.stk_min_amt = self.per_amt * 0.2
        else:
            self.stk_min_amt = stk_min_amt
        print('min_stk_amt', self.stk_min_amt)
        self.order_info = {}
        self.barly_condition_indicator = {}

        self.cash_added = cash_added
        self.per_ratio_change = per_ratio_change
        self.sell_order_record = {}
        self.buy_order_record = {}
        self.max_triger_num = max_trigger_num
        self.condition_series = condition_series

    def buy(self, stk, vol=None, amt=None):
        if not self.isinpool(stk):
            """
            不在股票池内时不可买
            """
            return 0, np.nan
        if stk in self.holding:
            holding = self.holding[stk]
        else:
            holding = 0

        if stk in self.available:
            available = self.available[stk]
        else:
            available = 0
        deal_price = self.trade(stk)  # self.bar_dealprice[stk]
        if deal_price == 0 or np.isnan(deal_price):
            return 0, np.nan
        if vol is None and amt is None:
            vol = round(self.per_amt / deal_price, -2)
        elif vol is None:
            vol = round(amt / deal_price, -2)
        elif amt is None:
            pass
        else:
            raise Exception('One of amt and vol must be not None')
        if np.isnan(vol) or vol == 0:
            return 0, deal_price
        vol = min(vol, int(self.bar_actual_future_vol[stk] // 100 * 100))

        holding += vol
        self.holding[stk], self.available[stk] = holding, available
        if stk not in self.record:
            self.record[stk] = [[self.datetime[0], self.datetime[1], 'B', vol, deal_price, holding, available]]
        else:
            record = self.record[stk]
            record.append([self.datetime[0], self.datetime[1], 'B', vol, deal_price, holding, available])
            self.record[stk] = record
        return vol, deal_price

    def sell(self, stk, vol=None):
        available = self.available[stk]
        holding = self.holding[stk]
        if vol is None:
            vol = available
        else:
            vol = min(vol, available)
        if vol == 0 or np.isnan(vol):
            return 0, np.nan
        deal_price = self.trade(stk)
        if deal_price == 0 or np.isnan(deal_price):
            return 0, np.nan
        vol = min(vol, int(self.bar_actual_future_vol[stk] // 100 * 100))
        holding -= vol
        available -= vol
        if holding > 0:
            self.holding[stk] = holding
        else:
            del self.holding[stk]
        if available > 0:
            self.available[stk] = available
        else:
            del self.available[stk]
        if stk not in self.record:
            raise Exception('Sell without record')
        else:
            record = self.record[stk]
            record.append([self.datetime[0], self.datetime[1], 'S', -vol, deal_price, holding, available])
            self.record[stk] = record
        return vol, deal_price

    def sell_action(self, stk, vol=None):
        if stk not in self.last_buy_time:
            raise Exception('Last buy time is not recorded')
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        sell_flag = 0
        if (bar_date_idx - date_idx) > 1 or ((bar_date_idx - date_idx) == 1 and bar_time >= time_point):
            sell_flag = 1
        elif (bar_date_idx - date_idx)>0:
            window = time_idx - bar_time_idx
            if stk in self.data_flow['inter_signal'][window][bar_time]:
                sell_flag = 2
        if sell_flag:
            vol, deal_price = self.sell(stk, vol)
            if vol > 0:
                if not np.isnan(deal_price):
                    self.cash += vol * deal_price * (1 - self.sell_cost)
                else:
                    raise Exception('Unexpected')
        return sell_flag



    def buy_action(self, stk, vol=None):
        deal_vol, deal_price = self.buy(stk, vol)
        if deal_vol > 0:
            if not np.isnan(deal_price):
                self.last_buy_time[stk] = self.datetime
                self.cash -= deal_vol * deal_price * (1 + self.buy_cost)
            else:
                raise Exception('Unexpected')
        return deal_vol

    def holding_another_round(self, stk):
        date, time_point, date_idx, time_idx = self.last_buy_time[stk]
        bar_date, bar_time, bar_date_idx, bar_time_idx = self.datetime
        if (bar_date_idx - date_idx) == 1 and bar_time == time_point:
            self.last_buy_time[stk] = self.datetime

    def daily_update(self, idx, date):
        super().daily_update(idx, date)
        self.data_flow['signal'] = self.signal[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        self.data_flow['inter_signal'] = {x:self.inter_signal[x][self.date_idx * self.step:(self.date_idx + 1) * self.step] for x in self.inter_signal}
        self.data_flow['past_future_vol'] = self.past_5day_future_30min_vol[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        self.data_flow['actual_future_vol'] = self.future_30_min_vol[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        self.data_flow['bar_signal_ratio_ratio'] = self.bar_signal_ratio_ratio[self.date_idx:self.date_idx + 1].T[date]
        self.data_flow['bar_cum_signal_ratio_ratio'] = self.data_flow['bar_signal_ratio_ratio'].sort_index().cumsum().replace(0, np.nan)
        for each in self.bench_ret:
            self.data_flow[f'{each}_ret'] = self.bench_ret[each].iloc[self.date_idx * self.step:(self.date_idx + 1) * self.step]
            self.data_flow[f'{each}'] = self.bench[each].iloc[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        # 不在股票池里的股票
        date_pool = self.stock_pool[self.date_idx:self.date_idx + 1].T[date]
        date_pool = pd.Series(date_pool.tolist(), index=date_pool.index.tolist())
        self.pool_num = date_pool.sum()
        self.today_pool = set(date_pool[date_pool].index.tolist()).union(set(self.holding.keys())) - set(['cash'])
        self.today_pool2 = set(date_pool[date_pool].index.tolist())
        date_pool = date_pool[~date_pool]
        # 停牌、一字板的股票
        not_tradable = self.untradable_pool[self.date_idx:self.date_idx + 1].T[self.date]

        self.data_flow['not_tradable'] = set(not_tradable[not_tradable].index.tolist())
        self.data_flow['not_available'] = set(date_pool.index.tolist())
        self.data_flow['daily_high'] = self.daily_high[self.date_idx:self.date_idx + 1].T[self.date]
        self.data_flow['daily_low'] = self.daily_low[self.date_idx:self.date_idx + 1].T[self.date]
        self.data_flow['pre_close'] = self.daily_info['pre_close'][self.date_idx:self.date_idx + 1].T[self.date]

        if self.data_flow['signal'].index[0][0] != self.date or self.data_flow['signal'].index[-1][0] != self.date:
            raise Exception('Broadcast date and signal date are not match!')
        for i in self.data_flow['inter_signal']:
            if self.data_flow['inter_signal'][i].index[0][0] != self.date or self.data_flow['inter_signal'][i].index[-1][0] != self.date:
                raise Exception(f'Broadcast date and signal date are not match!')
        self.data_flow['inter_signal'] = {x:dict(self.data_flow['inter_signal'][x].T[self.date]) for x in self.data_flow['inter_signal']}
        for w_d in self.data_flow['inter_signal']:
            for t_point in self.data_flow['inter_signal'][w_d]:
                self.data_flow['inter_signal'][w_d][t_point] = self.data_flow['inter_signal'][w_d][t_point].dropna().index.tolist()

    def bar_handler(self):
        date, time_point, date_idx, time_idx = self.datetime
        signal = self.data_flow['signal'][time_idx:time_idx + 1].T[(date, time_point)]
        signal = signal.dropna()

        ##############Condition
        pool_signal = set(signal.index).intersection(set(self.today_pool))
        new_trigger = pool_signal - self.already_triggered
        eval_all_day_signal_count = len(new_trigger) / self.data_flow['bar_signal_ratio_ratio'][time_point]
        self.already_triggered = self.already_triggered.union(new_trigger)
        eval_all_day_signal_count2 = len(self.already_triggered) / self.data_flow['bar_cum_signal_ratio_ratio'][time_point]
        # 盘中涨跌停
        bar_close = self.data_flow['close'][time_idx:time_idx + 1].T[(date, time_point)]
        pre_close = self.data_flow['pre_close']
        ret = pd.Series(bar_close.values / pre_close.values, index=bar_close.index) - 1
        ret = ret.apply(lambda x: round(x, 4))
        down = ret[ret < -1 * self.down_swing_threshold]
        down_signal = set(down.index).intersection(pool_signal)
        # signal_condition = eval_all_day_signal_count>self.signal_threshold*len(self.today_pool) or eval_all_day_signal_count2 > self.signal_threshold * len(self.today_pool)
        # if (down_signal_condition or V6down_condition) and signal_condition:
        #     self.trading_flag = False

        # self.barly_condition_indicator[(date, time_point)] \
        bar_basic_indicator = {
            'bar_first_trigger_num': len(new_trigger),
            'bar_cum_first_trigger_num': len(self.already_triggered),
            'pool_num': len(self.today_pool),
            'bar_trigger_signal': len(pool_signal) if pool_signal else np.nan,
            'bar_down_trigger_signal': len(down_signal.intersection(self.today_pool)),

            'bar_first_trigger_num2': len(new_trigger.intersection(self.today_pool2)),
            'bar_cum_first_trigger_num2': len(self.already_triggered.intersection(self.today_pool2)),
            'pool_num2': len(self.today_pool2),
            'bar_trigger_signal2': len(pool_signal.intersection(self.today_pool2)),
            'bar_down_trigger_signal2': len(down_signal.intersection(self.today_pool2)),

            'bar_ratio': self.data_flow['bar_signal_ratio_ratio'][time_point],
            'barly_cum_ratio': self.data_flow['bar_cum_signal_ratio_ratio'][time_point]
        }

        for each in self.bench_ret:
            bar_basic_indicator[f'{each}'] = self.data_flow[f'{each}'][(date, time_point)]  # = self.bench_ret.iloc[self.date_idx * self.step:(self.date_idx + 1) * self.step]
            bar_basic_indicator[f'{each}_ret'] = self.data_flow[f'{each}_ret'][
                (date, time_point)]  # = self.bench_ret.iloc[self.date_idx * self.step:(self.date_idx + 1) * self.step]
            bar_basic_indicator[f'{each}_MA5'] = self.MA5[each].iloc[[date_idx]][date]  # = self.bench_ret.iloc[self.date_idx * self.step:(self.date_idx + 1) * self.step]
            bar_basic_indicator[f'{each}_MA5_to_MA10'] = self.MA5_minus_MA10[each].iloc[[date_idx]][
                date]  # = self.bench_ret.iloc[self.date_idx * self.step:(self.date_idx + 1) * self.step]
        bar_basic_indicator['terminal_flag'] = eval(self.condition, bar_basic_indicator)

        self.barly_condition_indicator[(date, time_point)] = bar_basic_indicator
        if bar_basic_indicator['terminal_flag']:
            self.trading_flag = False

        if not self.trading_flag:
            signal = pd.Series()

        ##################


        trigger_stk = set(signal.index)
        # 盘中涨跌停
        bar_close = self.data_flow['close'][time_idx:time_idx + 1].T[(date, time_point)]
        # 可卖出股票 = 持仓股票剔除 停牌and一字板
        avaliable_stk = set(self.available.keys())
        #############
        available_close = bar_close[list(avaliable_stk)]
        limit_down_judge = ((available_close.values / self.data_flow['pre_close'][list(avaliable_stk)].values - 1) <= -0.098) & (
                available_close.values == self.data_flow['daily_low'][list(avaliable_stk)].values)
        limit_down_judge = pd.Series(limit_down_judge, index=list(avaliable_stk))
        limit_up_judge = ((available_close.values / self.data_flow['pre_close'][list(avaliable_stk)].values - 1) >= 0.098) & (
                available_close.values == self.data_flow['daily_high'][list(avaliable_stk)].values)
        limit_up_judge = pd.Series(limit_up_judge, index=list(avaliable_stk))
        avaliable_stk = set(limit_down_judge[~(limit_down_judge | limit_up_judge)].index.tolist())
        ##########
        avaliable_stk = avaliable_stk - self.data_flow['not_tradable']
        avaliable_trigger_stk = avaliable_stk.intersection(trigger_stk)
        sell_stk = list(avaliable_stk - trigger_stk)
        # 可买入股票 = 触发股票 剔除 不在股票池的股票 以及 有持仓个股
        trigger_stk = trigger_stk - self.data_flow['not_available']  # print({str(x).zfill(6)+'.SZ' if x <400000 else str(x)+'.SH' for x in trigger_stk})
        trigger_stk = list(trigger_stk - set(self.holding.keys()))
        historical_future_vol = round(self.data_flow['past_future_vol'][time_idx:time_idx + 1].T[(date, time_point)] * self.deal_percent, -2)
        for stk in avaliable_trigger_stk:
            self.holding_another_round(stk)

        if self.cash < self.per_amt:
            not_buy = True
            for stk in sell_stk:
                sell_vol = min(historical_future_vol[stk], self.holding[stk])
                self.sell_action(stk, sell_vol)
            return
        elif trigger_stk:
            not_buy = False
            target_close = bar_close[trigger_stk]
            limit_up_judge = ((target_close.values / self.data_flow['pre_close'][trigger_stk].values - 1) >= 0.098) & (
                    target_close.values == self.data_flow['daily_high'][trigger_stk].values)
            limit_up_judge = pd.Series(limit_up_judge, index=trigger_stk)
            trigger_stk = limit_up_judge[~limit_up_judge].index.tolist()
            target_vol = round(self.per_amt / target_close, -2)
            orderable_vol = pd.concat([target_vol, historical_future_vol[list(trigger_stk)]], axis=1).min(axis=1)
            orderable_vol = pd.DataFrame({'target': target_vol, 'orderable': orderable_vol})
            target_vol = orderable_vol['orderable']
            target_vol = target_vol // 100 * 100
            orderable_vol['sent_order'] = target_vol
            target_amt = target_vol * target_close
            target_amt = target_amt.loc[signal[trigger_stk].sort_values(ascending=False).index.tolist()]
            target_amt = target_amt[target_amt >= self.stk_min_amt]
            target_amt = target_amt[target_amt.cumsum() < self.cash]
            trigger_stk = target_amt.index.tolist()
            trigger_num = min(len(trigger_stk), int(self.cash // self.per_amt), self.barly_max_buy)
            trigger_stk = trigger_stk[:trigger_num]
            target_vol = target_vol[trigger_stk]
            orderable_vol = orderable_vol.T[target_vol.index].T
        else:
            target_vol = pd.Series()
            orderable_vol = pd.DataFrame()

        for stk in sell_stk:  # to_sell = set(sell_stk)
            sell_vol = min(historical_future_vol[stk], self.holding[stk])
            self.sell_action(stk, sell_vol)
        # sold = to_sell - {x for x in self.holding}

        deal_list = []
        for stk in target_vol.index:
            if stk in self.holding:
                raise Exception('Buying a holding stock')
            deal_vol = self.buy_action(stk, target_vol[stk])
            deal_list.append(deal_vol)
        orderable_vol['deal_vol'] = deal_list
        self.order_info[self.datetime[:2]] = orderable_vol


    def run_backtest(self, kernel=10):
        self.re_initial()
        self.daily_holding = {}
        self.daily_buy_time_info = {}
        self.daily_conf = {}
        bar = tqdm(self.date_list)
        start_condition_date = min(list(self.condition_series.keys()))
        if start_condition_date > self.date_list[0]:
            raise Exception('No initial condition')
        self.condition = self.condition_series[start_condition_date]
        for date_idx, date in enumerate(bar):
            bar.set_description('%d | holding:%d' % (date, len(self.holding)))
            self.daily_update(date_idx, date)
            self.daily_conf[date] = {
                'date': date,
                'pre_date': self.pre_date,
                'barly_max_buy': self.barly_max_buy,
                'stk_min_amt': self.stk_min_amt,
                'per_amt': self.per_amt,
                'cash': self.cash,
                'portfolio_id': '201001',
                'order_ratio': 0.1
            }
            self.already_triggered = set([])
            self.trading_flag = True
            for time_idx, time_point in enumerate(self.trading_point):
                self.bar_dealprice = self.data_flow['deal_price'][time_idx:time_idx + 1].T[(date, time_point)]
                self.bar_actual_future_vol = self.data_flow['actual_future_vol'][time_idx:time_idx + 1].T[(date, time_point)] * self.deal_percent
                self.datetime = (date, time_point, date_idx, time_idx)
                self.bar_point = date_idx * self.step + time_idx
                self.bar_handler()
                # print(self.datetime)
            if date in self.cash_added:
                self.cash += self.cash_added[date]
            if date in self.per_ratio_change:
                self.per_amt_ratio = self.per_ratio_change[date]
            if date in self.max_triger_num:
                self.barly_max_buy = self.max_triger_num[date]
            if date in self.condition_series:
                self.condition = self.condition_series[date]
            self.cash_series[self.date] = self.cash
            self.holding_num[self.date] = len(self.holding)
            daily_close = self.daily_info['close'][self.date_idx:self.date_idx + 1].T[self.date][list(self.holding.keys())]
            self.accout_value = (daily_close * pd.Series(self.holding)).sum() + self.cash
            self.holding_value[self.date] = self.accout_value
            self.per_amt = max(self.accout_value * self.per_amt_ratio // 10000 * 10000, 10000)

            self.daily_holding[date] = self.holding.copy()
            self.daily_buy_time_info[date] = self.last_buy_time

        pre_close_padj, pre_close, pre_adj_ratio = self.daily_info['close_padj'][self.date_idx:self.date_idx + 1].T[date], \
                                                   self.daily_info['close'][self.date_idx:self.date_idx + 1].T[date], \
                                                   self.daily_info['adj_ratio'][self.date_idx:self.date_idx + 1].T[date]
        for stk in self.holding:
            holding = self.holding[stk]
            stk_close_padj, stk_close, stk_adj_ratio = pre_close_padj[stk], pre_close[stk], pre_adj_ratio[stk]
            available = self.available[stk] if stk in self.available else 0
            if holding > 0:
                record = self.record[stk]
                record.append([self.date, 1500, 'H', stk_close_padj, stk_close, holding, available])
                self.record[stk] = record

        record = list(self.record.keys())
        for each in record:
            self.record[each] = pd.DataFrame(self.record[each], columns=['date', 'time', 'flag', 'vol', 'deal_price', 'holding', 'available']).set_index(['date', 'time'])
        gc.collect()
        return self.record._getvalue()

# import os
# import pandas as pd
#
# file_list = os.listdir('/data/group/800319/strategy_local_path/buy_time_info_old/')
# for each in file_list:
#     buy_time_info_origin = pd.read_pickle('/data/group/800319/strategy_local_path/buy_time_info_old/%s'%each)
#     buy_time_info = {}
#     for stk in buy_time_info_origin:
#         code = str(stk).zfill(6) + '.SZ' if stk < 400000 else str(stk) + '.SH'
#         buy_time_info[code] = buy_time_info_origin[stk]
#     pd.to_pickle(buy_time_info,'/data/group/800319/strategy_local_path/buy_time_info/%s'%each)
