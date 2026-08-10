import pandas as pd
pd.set_option('max_rows', 200)
import pandas as pd
import numpy as np
import datetime
from multifactor.IO import IO
import itertools
from tqdm import tqdm

import warnings
warnings.filterwarnings('ignore')

class TS_BACK_TEST:

    def __init__(self,signal_df, ticker, price_kind='vwap', long_in=0.5, long_out=0.5, short_in=-100, short_out=-0.5,
             stop_profit=100, stop_loss=-100, initial_cash=10000000, c_rate=2.5 / 100000, slippage=0.6,
             leverage_rate=1, hour_t=14, minute_t=30):
        self.signal_df = signal_df
        self.ticker = ticker
        self.price_kind = price_kind
        self.long_in = long_in
        self.long_out = long_out
        self.short_in = short_in
        self.short_out = short_out
        self.stop_profit = stop_profit
        self.stop_loss = stop_loss
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

    # 只需要调用此函数，便可以得到策略回测结果
    def back_test(self):
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
        :param stop_profit: 止盈
        :param stop_loss: 止损
        :param initial_cash: 初始资金
        :param c_rate: 交易费用
        :param slippage: 交易价格滑点
        :param leverage_rate: 杠杆数
        :param hour_t: 表示几点
        :param minute_t: 几分后不开仓，默认是14:30后不开仓，只平仓
        :return: 一个字典：'results': 策略评价指标,
                'pnl',每分钟累积收益，equity_curve字段表示资金曲线
                'trade_detail': 每笔交易细节，equity_curve字段表示资金曲线,
                'daily_return',每日收益,
                'monthly_return': 月度收益
        """
        df = self.prepare_data(self.signal_df, ticker=self.ticker)

        raw = df.iloc[0]['raw']
        pos_state = 0  # 当前持仓状态
        pre_signal = 0  # 上一分钟信号
        deal_count = 0  # 第几笔交易
        trade_df = pd.DataFrame()
        pnl_df = pd.DataFrame()  # 记录每分钟的资金曲线
        length = len(df) - 1
        for i in tqdm(range(1, length)):
            nowtime = df.iloc[i]['dt']
            close = df.iloc[i]['close']

            pre_raw = raw
            raw = df.iloc[i]['raw']
            signal = self.get_signal(pre_raw, raw)
            if signal != 0:
                if (nowtime.hour == self.hour_t) & (nowtime.minute > self.minute_t):
                    signal = None
            # 如果当前没有仓位，看上一个分钟是否给出开仓信号
            if pos_state == 0:
                if (pre_signal == None) | (pre_signal == 0):
                    pnl_df.loc[nowtime, 'profit'] = 0  # 此分钟收益为0
                    pre_signal = signal
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
                    trade_df.loc[deal_count, 'pos'] = pos_state
                    trade_df.loc[deal_count, 'open_time'] = open_time
                    trade_df.loc[deal_count, 'open_price'] = open_price
                    trade_df.loc[deal_count, 'open_contract_num'] = contract_num

                    pre_signal = signal

                    nowprofit = self.face_value * contract_num * (close - open_price) * pos_state
                    pnl_df.loc[nowtime, 'profit'] = nowprofit - open_fee  # 此分钟盈亏应为此分钟收益减去手续费
                    continue

            # 如果当前有持仓，看上一个信号是否要平仓
            elif pos_state != 0:
                last_close = df.iloc[i - 1]['close']  # 上一分钟收盘价
                if pre_signal == None:  # 没信号，但是此时要看是否止盈止损
                    pnl_df.loc[nowtime, 'profit'] = self.face_value * contract_num * (close - last_close) * pos_state  # 此分钟收益
                    nowprofit = self.face_value * contract_num * (close - open_price) * pos_state

                    nowvalue = value + nowprofit
                    ratio = nowvalue / self.initial_cash - 1
                    if (ratio >= self.stop_profit) | (ratio <= self.stop_loss):
                        pre_signal = 0  # 如果触发了止损止盈，则下一分钟进行平仓
                    else:
                        pre_signal = signal
                    continue
                close_time = nowtime

                close_price = df.iloc[i][self.price_kind] - self.slippage * pos_state
                close_fee = close_price * self.face_value * contract_num * self.c_rate
                deal_profit = self.face_value * contract_num * (close_price - open_price) * pos_state
                net_value = value + deal_profit - close_fee

                trade_df.loc[deal_count, 'close_time'] = close_time
                trade_df.loc[deal_count, 'close_price'] = close_price
                trade_df.loc[deal_count, 'close_contract_num'] = contract_num
                trade_df.loc[deal_count, 'net_value'] = net_value

                nowprofit = self.face_value * contract_num * (close_price - last_close) * pos_state
                pnl_df.loc[nowtime, 'profit'] = nowprofit - close_fee  # 此分钟盈亏应为此分钟收益减去手续费
                # 每一次平仓说明完成了一笔交易
                pos_state = 0
                deal_count += 1

            pre_signal = signal

        trade_df['change'] = trade_df.net_value / self.initial_cash - 1
        trade_df['equity_curve'] = trade_df.change.cumsum() + 1
        trade_df['holding_time'] = trade_df.apply(lambda x: self.get_timediff_minutes(x.open_time, x.close_time), axis=1)

        pnl_df = pnl_df.reset_index()
        pnl_df.columns = ['dt', 'profit']
        pnl_df['change'] = pnl_df['profit'] / self.initial_cash
        pnl_df['equity_curve'] = (pnl_df['profit'].cumsum() + self.initial_cash) / self.initial_cash

        results, daily_return, monthly_return = self.strategy_evaluate(pnl_df.copy(), trade_df.copy())
        daily_return.columns = ['daily_return']

        pnl_df = pnl_df.set_index('dt')

        monthly_return = monthly_return.reset_index().rename(columns={'open_time': 'dt'}).set_index('dt')

        return {'results': results,
                'pnl': pnl_df[['equity_curve']] - 1,
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
                              alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5')
            md = md.xs(self.ticker, level=1)
            df = self.signal_df.join(md)
        else:
            clist = ['raw'] + self.signal_df.columns.tolist()[1:]
            self.signal_df.columns = clist
            df = self.signal_df.copy()

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


    def get_signal(self, pre_raw, raw):
        if (pre_raw <= self.long_in) and (raw > self.long_in):
            return 1
        if (pre_raw >= self.long_out) and (raw < self.long_out):
            return 0
        if (pre_raw >= self.short_in) and (raw < self.short_in):
            return -1
        if (pre_raw <= self.short_out) and (raw > self.short_out):
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
