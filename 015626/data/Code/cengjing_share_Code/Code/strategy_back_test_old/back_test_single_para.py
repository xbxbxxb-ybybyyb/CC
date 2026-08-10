import pandas as pd

pd.set_option('max_rows', 200)
import pandas as pd
import numpy as np
import datetime
from multifactor.IO import IO
import itertools
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import multifactor.utility.dt as udt

import warnings
warnings.filterwarnings('ignore')


class TS_BACK_TEST:

    def __init__(self,signal_df, ticker = 'IC.CFE', price_kind='vwap', long_in=0.5, long_out=0.5, short_in=-100, short_out=-0.5,
              signal_down_t = 0.2, profit_down_t = 0.002, signal_inout_diff = 0.1, min_holding_period = 5, stop_profit=100,
                 stop_loss=-100, open_limit_intraday = 5, initial_cash=10000000, c_rate=2.5 / 100000, slippage=0.6,
             leverage_rate=1, hour_t=14, minute_t=30, save_path = '/data/user/', name_prefix = ''):
    # def __init__(self, signal_df, para_list, ticker='IC.CFE', price_kind='vwap',
    #              signal_down_t=0.2, profit_down_t=0.002, signal_inout_diff=0.1, min_holding_period=5, stop_profit=100,
    #              stop_loss=-100, open_limit_intraday=5, initial_cash=10000000, c_rate=2.5 / 100000, slippage=0.6,
    #              leverage_rate=1, hour_t=14, minute_t=30, save_path='/data/user/', name_prefix=''):
        """
        :param signal_df: 信号dataframe，index为分钟，如果只有一列，则认为此列为信号值，读取行情数据进行测试。
                            如果多列，则第一列需为信号值，在函数内读取行情数据
                            测试时不对信号值做任何处理，使用原始值。
        :param ticker: 交易品种，
        :param price_kind: 使用下一分钟的哪个字段作为买入卖出价格，默认vwap
        :param long_in: 开多进场阈值
        :param long_out: 开多出场阈值
        :param short_in: 开空进场阈值，默认设的极小表示不开空
        :param short_out: 开空出场阈值
        :param signal_down_t: 信号值从当前持仓周期内最大回撤阈值
        :param profit_down_t: 收益从当前持仓周期内最大回撤阈值
        :param signal_inout_diff: 刚开仓在min_holding_period内允许信号波动的幅度，如0.5进场，理论出场阈值为0.5，
                                  但可在min_holding_period内出场阈值设为0.4
        :param min_holding_period: 最小持仓周期，但触发止损除外
        :param stop_profit: 止盈
        :param stop_loss: 止损
        :param open_limit_intraday: 单日开仓上限
        :param initial_cash: 初始资金
        :param c_rate: 交易费用
        :param slippage: 交易价格滑点
        :param leverage_rate: 杠杆数
        :param hour_t: 表示几点
        :param minute_t: 几分后不开仓，默认是14:30后不开仓，只平仓
        :param save_path: 结果保存路径
        :param name_prefix: 结果csv命名前缀
        :back_test function return: 一个字典：'results': 策略评价指标,
                'pnl',每分钟累积收益，equity_curve字段表示资金曲线
                'trade_detail': 每笔交易细节，equity_curve字段表示资金曲线,
                'daily_return',每日收益,
                'monthly_return': 月度收益
        """
        assert signal_down_t >= 0
        assert signal_inout_diff >= 0
        self.signal_df = signal_df
        self.ticker = ticker
        self.price_kind = price_kind
        self.long_in = long_in
        self.long_out = long_out
        self.short_in = short_in
        self.short_out = short_out
        # self.long_in = para_list[0]
        # self.long_out = para_list[1]
        # self.short_in = para_list[2]
        # self.short_out = para_list[3]
        self.signal_down_t = signal_down_t
        self.profit_down_t = profit_down_t
        self.signal_inout_diff = signal_inout_diff
        self.min_holding_period = min_holding_period
        self.long_out_copy = long_out  # 备份， 持仓时可能会变动， 平仓后变为此值
        self.short_out_copy = short_out  # 备份， 持仓时可能会变动， 平仓后变为此值
        # self.long_out_copy = para_list[1]
        # self.short_out_copy = para_list[3]
        self.stop_profit = stop_profit
        self.stop_loss = stop_loss
        self.open_limit_intraday = open_limit_intraday
        self.initial_cash = initial_cash
        self.c_rate = c_rate
        self.slippage = slippage
        self.leverage_rate = leverage_rate
        self.hour_t = hour_t
        self.minute_t = minute_t
        face_value_dict = {'IC.CFE': 200,
                           'IF.CFE': 300,
                           'IH.CFE': 300}
        self.face_value = face_value_dict[self.ticker]
        self.save_path = save_path
        self.name_prefix = name_prefix

    # 只需要调用此函数，便可以得到策略回测结果
    def back_test(self):

        df = self.prepare_data()

        raw = df.iloc[0]['raw']
        pos_state = 0  # 当前持仓状态
        pre_signal = 0  # 上一分钟信号
        deal_count = 0  # 第几笔交易
        holding_period = 0  # 当前持仓时间
        max_signal = 0  # 当前持仓周期中最大的信号值
        min_signal = 0
        max_profit_ratio = 0
        trade_dict = {}
        pnl_dict = {}  # 记录每分钟的资金曲线
        open_num_intraday = 0  # 今日开仓了几次
        pre_date = datetime.date(1998, 1, 1)  # 初始前一天日期
        length = len(df) - 1

        for i in tqdm(range(1, length)):
            nowtime = df.iloc[i]['dt']

            now_date = nowtime.date()
            if now_date != pre_date:
                open_num_intraday = 0

            close = df.iloc[i]['close']

            pre_raw = raw
            raw = df.iloc[i]['raw']

            # 新增出场阈值变动逻辑
            if pos_state != 0:
                holding_period += 1  # 持仓时间+1
                if holding_period == 1:
                    holding_period += 1
                    if pos_state == 1:
                        if pre_raw > max_signal:
                            max_signal = pre_raw
                    elif pos_state == -1:
                        if pre_raw < min_signal:
                            min_signal = pre_raw
                if pos_state == 1:
                    if raw > max_signal:
                        max_signal = raw
                elif pos_state == -1:
                    if raw < min_signal:
                        min_signal = raw

            # 当持仓时间小于阈值时，出场阈值变动diff大小，否则为原值
            if self.min_holding_period > 0:
                if holding_period <= self.min_holding_period:
                    self.long_out = self.long_out_copy - self.signal_inout_diff
                    self.short_out = self.short_out_copy + self.signal_inout_diff
                else:
                    self.long_out = self.long_out_copy
                    self.short_out = self.short_out_copy
            # 将当前出场阈值与最大信号值回撤某个阈值计算出的出场阈值进行比较，做多时取最大值，做空时取最小值
            if self.signal_down_t > 0:
                self.long_out = max(self.long_out, max_signal - self.signal_down_t)
                self.short_out = min(self.short_out, min_signal + self.signal_down_t)

            signal = self.get_signal(pre_raw, raw, pos_state, pre_signal)
            if signal != 0:
                if (nowtime.hour == self.hour_t) & (nowtime.minute >= self.minute_t):  # 两点半后不开仓
                    signal = None
                if open_num_intraday >= self.open_limit_intraday:  # 超出单日开仓上限不开仓
                    signal = None
            # 如果当前没有仓位，看上一个分钟是否给出开仓信号
            if pos_state == 0:
                if (pre_signal == None) | (pre_signal == 0):
                    #                     pnl_df.loc[nowtime, 'profit'] = 0  # 此分钟收益为0
                    pnl_dict[nowtime] = 0
                    pre_signal = signal
                    pre_date = now_date
                    continue
                # 如果上一个分钟给出了开仓信号, 则本分钟进行开仓
                if pre_signal != 0:
                    open_time = nowtime
                    open_price = df.iloc[i][self.price_kind] + self.slippage * pre_signal
                    contract_num = np.floor(self.initial_cash * self.leverage_rate / (self.face_value * open_price))
                    # 开仓扣除手续费后, 我的账户余额以及合约共价值多少钱
                    open_fee = open_price * self.face_value * contract_num * self.c_rate
                    value = self.initial_cash - open_fee

                    # 开仓结束， 更新目前持仓状态
                    pos_state = pre_signal
                    open_signal = pre_raw
                    open_contract_num = contract_num
                    open_num_intraday += 1

                    pre_signal = signal
                    pre_date = now_date

                    nowprofit = self.face_value * contract_num * (close - open_price) * pos_state
                    pnl_dict[nowtime] = nowprofit - open_fee  # 此分钟盈亏应为此分钟收益减去手续费
                    continue

            # 如果当前有持仓，看上一个信号是否要平仓
            elif pos_state != 0:
                last_close = df.iloc[i - 1]['close']  # 上一分钟收盘价
                if pre_signal == None:  # 没信号，但是此时要看是否止盈止损
                    pnl_dict[nowtime] = self.face_value * contract_num * (close - last_close) * pos_state  # 此分钟收益
                    nowprofit = self.face_value * contract_num * (close - open_price) * pos_state

                    nowvalue = value + nowprofit
                    ratio = nowvalue / self.initial_cash - 1
                    #                     if ratio > max_profit_ratio:
                    #                         max_profit_ratio = ratio
                    #                     if max_profit_ratio > 0:
                    #                         if ratio >= self.stop_profit:
                    #                             pre_signal = 0
                    #                             trade_df.loc[deal_count, 'stop_state'] = 'stop_profit'
                    #                         elif ratio < max_profit_ratio - self.profit_down_t:
                    #                             pre_signal = 0
                    #                             trade_df.loc[deal_count, 'stop_state'] = 'profit_drawdown'
                    #                         else:
                    #                             pre_signal = signal
                    #                     else:
                    #                         if ratio <= self.stop_loss:
                    #                             pre_signal = 0
                    #                             trade_df.loc[deal_count, 'stop_state'] = 'stop_loss'
                    #                         else:
                    #                             pre_signal = signal
                    if (ratio >= self.stop_profit) | (ratio <= self.stop_loss):
                        pre_signal = 0  # 如果触发了止损止盈，则下一分钟进行平仓
                    else:
                        pre_signal = signal
                    pre_date = now_date
                    continue

                elif pre_signal == 0:

                    # 平仓
                    close_time = nowtime

                    close_price = df.iloc[i][self.price_kind] - self.slippage * pos_state
                    close_fee = close_price * self.face_value * contract_num * self.c_rate
                    deal_profit = self.face_value * contract_num * (close_price - open_price) * pos_state
                    net_value = value + deal_profit - close_fee

                    now_out_threshold = self.long_out if pos_state == 1 else self.short_out
                    trade_dict[deal_count] = {'pos': pos_state, 'open_time': open_time, 'open_price': open_price,
                                              'open_contract_num': open_contract_num, 'open_signal': open_signal,
                                              'close_time': close_time, 'close_price': close_price,
                                              'close_contract_num': contract_num,
                                              'net_value': net_value, 'out_threshold': now_out_threshold,
                                              'max_signal': max_signal,
                                              'pre_signal': pre_raw, 'now_signal': raw,
                                              'open_num_intraday': open_num_intraday}

                    nowprofit = self.face_value * contract_num * (close_price - last_close) * pos_state
                    #                     pnl_df.loc[nowtime, 'profit'] = nowprofit - close_fee  # 此分钟盈亏应为此分钟收益减去手续费
                    pnl_dict[nowtime] = nowprofit - close_fee
                    # 每一次平仓说明完成了一笔交易
                    pos_state = 0
                    deal_count += 1

                    # 平仓结束后将出场阈值归为原始的阈值
                    self.long_out = self.long_out_copy
                    self.short_out = self.short_out_copy
                    max_signal = 0
                    min_signal = 0
                    holding_period = 0

            pre_signal = signal
            pre_date = now_date

        trade_df = pd.DataFrame(trade_dict).T
        trade_df['change'] = trade_df.net_value / self.initial_cash - 1
        trade_df['equity_curve'] = trade_df.change.cumsum()
        trade_df['holding_time'] = trade_df.apply(lambda x: self.get_timediff_minutes(x.open_time, x.close_time),
                                                  axis=1)

        pnl_df = pd.DataFrame(pnl_dict, index=['profit']).T
        pnl_df = pnl_df.reset_index()
        pnl_df.columns = ['dt', 'profit']
        pnl_df['change'] = pnl_df['profit'] / self.initial_cash
        pnl_df['equity_curve'] = (pnl_df['profit'].cumsum() + self.initial_cash) / self.initial_cash

        results, daily_return, monthly_return = self.strategy_evaluate(pnl_df.copy(), trade_df.copy())
        daily_return.columns = ['daily_return']

        pnl_df = pnl_df.set_index('dt')
        pnl = pnl_df[['equity_curve']] - 1
        pnl.columns = ['profit']

        monthly_return = monthly_return.reset_index().rename(columns={'open_time': 'dt'}).set_index('dt')
        trade_df = trade_df[
            ['pos', 'open_time', 'open_price', 'open_contract_num', 'open_signal', 'close_time', 'close_price',
             'close_contract_num', 'net_value', 'out_threshold', 'max_signal', 'pre_signal', 'now_signal',
             'change', 'equity_curve', 'holding_time', 'open_num_intraday']]

        if self.save_path != None:
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            trade_df.to_csv(os.path.join(self.save_path, self.name_prefix + 'trade_detail.csv'), index=False)
            pnl.to_csv(os.path.join(self.save_path, self.name_prefix + 'pnl.csv'))
            daily_return.to_csv(os.path.join(self.save_path, self.name_prefix + 'daily_return.csv'))
            monthly_return.to_csv(os.path.join(self.save_path, self.name_prefix + 'monthly_return.csv'))
            results.to_csv(os.path.join(self.save_path, self.name_prefix + 'results.csv'), encoding='gbk')
            pnl.plot(figsize=(20, 10))
            plt.title('profit', fontsize='large')
            plt.savefig(os.path.join(self.save_path, self.name_prefix + 'profit.png'))

        return {'results': results,
                'pnl': pnl,
                'trade_detail': trade_df,
                'daily_return': daily_return,
                'monthly_return': monthly_return}

    def prepare_data(self):
        if isinstance(self.signal_df, pd.Series):
            self.signal_df = self.signal_df.to_frame()

        # 获取信号开始结束时间，获取行情数据
        start_time = int(str(self.signal_df.ix[[0]].index.values[0]).split('T')[0].replace('-', ''))
        end_time = str(self.signal_df.ix[[-1]].index.values[0]).split('T')[0]
        end_time = int(
            str((datetime.datetime.strptime(end_time, '%Y-%m-%d') + datetime.timedelta(1)).date()).replace('-', ''))
        if len(self.signal_df.columns.tolist()) == 1:
            self.signal_df.columns = ['raw']
            md = IO.read_data([start_time, end_time], columns=['open', 'high', 'low', 'close', 'vwap'],
                              alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5')
            md = md.xs(self.ticker, level=1)
            df = self.signal_df.join(md, how='inner')
            if self.price_kind == 'twap':
                md_twap = IO.read_data([start_time, end_time], columns=['twap'],
                                       alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5')
                md_twap = md_twap.xs(self.ticker, level=1)
                df = df.join(md_twap, how='inner')
        else:
            clist = ['raw'] + self.signal_df.columns.tolist()[1:]
            self.signal_df.columns = clist
            df = self.signal_df.copy()
        t_days_list = udt.get_trading_date_range(str(df.index[0].date()).replace('-', ''), str(df.index[-1].date()).replace('-', ''))
        t_days_list = [str(i)[:10] for i in t_days_list]
        t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00', '14:57:00', freq='min').to_list()
        t_mins_list = [str(i)[-8:] for i in t_mins_list]
        index_list = []
        for d in t_days_list:
            for m in t_mins_list:
                index_list.append(d + ' ' + m)
        index_min = pd.DataFrame({'dt': index_list})
        index_min['dt'] = pd.to_datetime(index_min['dt'])
        index_min = index_min.set_index('dt').sort_index()
        
        df = df.join(index_min,how = 'outer').sort_index()
        df['raw'] = df['raw'].fillna(0)

        # 每天只交易9:35-14:55时间段
        idx = df.index
        t1 = df.loc[(idx.hour == 9) & (idx.minute >= 34)]
        t2 = df.loc[(idx.hour == 10) | (idx.hour == 13)]
        t3 = df.loc[(idx.hour == 11) & (idx.minute < 30)]
        t4 = df.loc[(idx.hour == 14) & (idx.minute <= 57)]
        t = t1.append(t2).append(t3).append(t4)
        t = t.sort_index()
        t = t.reset_index()
        t['date'] = t['dt'].apply(lambda x: x.date())
        # 将每天数据的第一条以及后两条设置为0,确保不持隔夜仓
        alist = t.groupby('date').apply(lambda x: x.dt.iloc[0]).tolist()
        blist = t.groupby('date').apply(lambda x: x.dt.iloc[-2:]).tolist()
        t.loc[t.dt.isin(alist), 'raw'] = 0
        t.loc[t.dt.isin(blist), 'raw'] = 0
        t.drop(['date'], axis=1, inplace=True)
        t = t.set_index('dt')

        df = t.sort_index().reset_index()
        return df

    def get_signal(self, pre_raw, raw, pos_state, pre_signal):
        if (pre_raw <= self.long_in) and (raw > self.long_in):
            return 1
        if (pos_state == 1) and (raw < self.long_out):
            return 0
        if (pre_raw >= self.short_in) and (raw < self.short_in):
            return -1
        if (pos_state == -1) and (raw > self.short_out):
            return 0
        if (pre_signal == 1) and (pos_state == 0) and (raw < self.long_out):
            return 0
        if (pre_signal == -1) and (pos_state == 0) and (raw > self.short_out):
            return 0
        return None

    def get_timediff_minutes(self, a, b):
        m = (b - a).total_seconds() / 60
        if (a.hour <= 11) & (b.hour >= 13):
            return m - 90 + 1
        else:
            return m + 1

    # 计算策略评价指标
    def strategy_evaluate(self, pnl, trade):
        """
        :param trade: 每笔交易的df
        :return:
        """

        # ===新建一个dataframe保存回测指标
        results = pd.DataFrame()

        # ===计算累积净值
        results.loc[0, '累积净值'] = round(pnl['equity_curve'].iloc[-1], 3)

        # 计算夏普比率
        pnl['date'] = pnl['dt'].apply(lambda x: x.date())
        sharpedailyreturn = pnl.groupby('date')['change'].sum().to_frame()
        tradedays = len(sharpedailyreturn)
        sharpe_ratio = round(sharpedailyreturn['change'].mean() / sharpedailyreturn['change'].std() * np.sqrt(252), 3)
        results.loc[0, '夏普比率'] = sharpe_ratio

        # ===计算年化收益
        annual_return = (pnl['equity_curve'].iloc[-1] / pnl['equity_curve'].iloc[0] - 1) * (
                '365 days 00:00:00' / (pnl['dt'].iloc[-1] - pnl['dt'].iloc[0]))

        results.loc[0, '年化收益'] = format(round(annual_return, 3), '.2%')

        # ===计算最大回撤
        # 计算当日之前的资金曲线的最高点
        pnl['max2here'] = pnl['equity_curve'].expanding().max()
        # 计算到历史最高值到当日的跌幅，drowdwon
        #     pnl['dd2here'] = pnl['equity_curve'] / pnl['max2here'] - 1
        pnl['dd2here'] = pnl['equity_curve'] - pnl['max2here']
        # 计算最大回撤，以及最大回撤结束时间
        end_date, max_draw_down = tuple(pnl.sort_values(by=['dd2here']).iloc[0][['dt', 'dd2here']])
        # 计算最大回撤开始时间
        start_date = pnl[pnl['dt'] <= end_date].sort_values(by='equity_curve', ascending=False).iloc[0][
            'dt']
        # 将无关的变量删除
        pnl.drop(['max2here', 'dd2here'], axis=1, inplace=True)
        results.loc[0, '最大回撤'] = format(max_draw_down, '.2%')
        results.loc[0, '最大回撤开始时间'] = str(start_date)
        results.loc[0, '最大回撤结束时间'] = str(end_date)

        # ===年化收益/回撤比
        results.loc[0, '年化收益/回撤比'] = round(abs(annual_return / max_draw_down), 2)

        # ===统计每笔交易
        results.loc[0, '平均每天交易笔数'] = round(len(trade) / tradedays, 2)  # 盈利笔数
        results.loc[0, '亏损笔数'] = len(trade.loc[trade['change'] <= 0])  # 亏损笔数
        results.loc[0, '盈利笔数'] = len(trade.loc[trade['change'] > 0])  # 盈利笔数
        results.loc[0, '亏损笔数'] = len(trade.loc[trade['change'] <= 0])  # 亏损笔数
        results.loc[0, '胜率'] = format(results.loc[0, '盈利笔数'] / len(trade), '.2%')  # 胜率

        results.loc[0, '每笔交易平均盈亏'] = format(trade['change'].mean(), '.2%')  # 每笔交易平均盈亏
        results.loc[0, '盈亏收益比'] = round(trade.loc[trade['change'] > 0]['change'].mean() / \
                                        trade.loc[trade['change'] < 0][
                                            'change'].mean() * (-1), 2)  # 盈亏比

        results.loc[0, '单笔最大盈利'] = format(trade['change'].max(), '.2%')  # 单笔最大盈利
        results.loc[0, '单笔最大亏损'] = format(trade['change'].min(), '.2%')  # 单笔最大亏损

        # ===统计持仓时间
        trade['持仓时间'] = trade['holding_time']
        max_minutes = trade['持仓时间'].max()
        results.loc[0, '单笔最长持有时间'] = str(int(max_minutes)) + ' 分钟'  # 单笔最长持有时间

        min_minutes = trade['持仓时间'].min()
        results.loc[0, '单笔最短持有时间'] = str(int(min_minutes)) + ' 分钟'  # 单笔最短持有时间

        mean_minutes = trade['持仓时间'].mean()
        results.loc[0, '平均持仓周期'] = str(round(mean_minutes, 1)) + ' 分钟'  # 平均持仓周期

        # ===连续盈利亏算
        results.loc[0, '最大连续盈利笔数'] = max(
            [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] > 0, 1, np.nan))])  # 最大连续盈利笔数
        results.loc[0, '最大连续亏损笔数'] = max(
            [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] < 0, 1, np.nan))])  # 最大连续亏损笔数

        # ===每月收益率
        temp = trade.set_index('open_time')
        monthly_return = temp[['change']].resample(rule='M').apply(lambda x: x.sum())

        results = results.T
        results.columns = ['num']
        return results, sharpedailyreturn, monthly_return

# 以下为使用示例（信号范围为（-1，1）），建议只修改进出场阈值以及滑点与止损
'''
factor = pd.read_pickle('/data/user/016700/Data/factors_ew.pkl').loc['20210101':]

save_path = '/data/user/015626/data/share/factor/back_test/IC_ts/20210601/'
name_prefix = 'factors_ew'
ts = TS_BACK_TEST(factor,  price_kind='twap',long_in=0.5, long_out=0.5, short_in=-0.5, short_out=-0.5,slippage=0.6,
                  stop_loss=-0.005, signal_down_t=0, profit_down_t=0, signal_inout_diff=0, min_holding_period=0,
                  save_path=save_path, name_prefix=name_prefix)
c = ts.back_test()
'''