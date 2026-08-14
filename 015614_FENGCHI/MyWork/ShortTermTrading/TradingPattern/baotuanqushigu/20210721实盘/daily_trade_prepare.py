# coding: utf-8
# Author：fengchi863
# Date ：2021/7/23 11:09

'''
盘前根据日间选股以及昨日O32持仓进行配置文件的设置
每天当天盘前或盘中运行
'''
from ShortTermTrading.dataApi import getData, stockList, tradeDate
from FaaMonitor.Util.DtUtil import DtUtil
import pandas as pd, numpy as np
from ShortTermTrading.conf.path_conf import junk_path, daily_monitor_path


class TradePrepare:
    def __init__(self):
        today_date = DtUtil.get_today_date()
        yes_date = DtUtil.get_yesterday_date()

        date_list = tradeDate.get_date_range(tradeDate.get_pre_trade_date(yes_date, 30), yes_date)
        daily_close = getData.get_daily_1factor('close_badj', date_list=date_list)
        ma5 = daily_close.rolling(5).mean()
        pre_close = getData.get_daily_1factor('pre_close_badj', date_list=date_list)
        adjfactor = getData.get_daily_1factor('adjfactor')  # 每日8:50更新当日复权因子数据

        if adjfactor.iloc[-1].name != today_date:
            raise IndexError('当日%d权重信息尚未更新' % today_date)

        # self.today_date = 20210729
        # self.yes_date = tradeDate.get_pre_trade_date(self.today_date)
        # self.yes_date = tradeDate.get_pre_trade_date(self.today_date)
        self.today_date = today_date
        self.yes_date = yes_date
        self.date_list = date_list
        self.daily_close = daily_close
        self.ma5 = ma5
        self.ma5_boost = ma5 * 1.002
        self.pre_close = pre_close
        self.adjfactor = adjfactor

    def buy_prepare(self):
        tmp_df = pd.read_excel('/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/'
                               'daily_trade_prepare/daily_trade_prepare.xlsx',
                               sheet_name='交易准备')
        df = pd.DataFrame()
        buy_df = tmp_df[['买入股票代码', '买入股票名称']].dropna().drop_duplicates()
        buy_df['买入股票代码'] = buy_df['买入股票代码'].map(int)
        buy_df = buy_df.reset_index(drop=True)
        for idx in range(len(buy_df)):
            stk_id = buy_df.loc[idx, '买入股票代码']
            stk_name = buy_df.loc[idx, '买入股票名称']
            ma = self.ma5.loc[self.yes_date, stk_id]
            ma_boost = self.ma5_boost.loc[self.yes_date, stk_id]
            per_amt = 1000000
            pre_close = self.daily_close.loc[self.yes_date, stk_id]
            adjfactor = self.adjfactor.loc[self.today_date, stk_id]
            append_content = [stk_id, stk_name, ma, ma_boost, per_amt, pre_close, adjfactor]
            df = df.append([append_content])
        df.columns = ['stk_id', 'stk_name', 'ma', 'ma_boost', 'per_amt', 'pre_close', 'adjfactor']
        df = df.set_index('stk_id', drop=True)
        return df

    def sell_prepare(self):
        tmp_df = pd.read_excel('/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/'
                               'daily_trade_prepare/daily_trade_prepare.xlsx',
                               sheet_name='交易准备')
        df = pd.DataFrame()
        sell_df = tmp_df[['卖出股票代码', '卖出股票名称']].dropna().drop_duplicates()
        sell_df['卖出股票代码'] = sell_df['卖出股票代码'].map(int)
        sell_df = sell_df.reset_index(drop=True)
        for idx in range(len(sell_df)):
            stk_id = sell_df.loc[idx, '卖出股票代码']
            stk_name = sell_df.loc[idx, '卖出股票名称']
            buy_price = 100
            ma = self.ma5.loc[self.yes_date, stk_id]
            vol = 2000
            gain_closeout = 0.05
            loss_closeout = -0.05
            adjfactor = self.adjfactor.loc[self.today_date, stk_id]
            append_content = [stk_id, stk_name, buy_price, ma, vol, gain_closeout, loss_closeout, adjfactor]
            df = df.append([append_content])
        df.columns = ['stk_id', 'stk_name', 'buy_price', 'ma', 'vol', 'gain_closeout', 'loss_closeout', 'adjfactor']
        df = df.set_index('stk_id', drop=True)
        return df

    def strategy_param_prepare(self):
        param = dict()
        param['强制平仓线'] = MARGIN_CLOSEOUT
        param['持仓组合号'] = '201001'
        df = pd.DataFrame(pd.Series(param))
        return df


MARGIN_CLOSEOUT = -0.08


if __name__ == '__main__':
    tp = TradePrepare()
    sell_df = tp.sell_prepare()
    buy_df = tp.buy_prepare()
    stat_param = tp.strategy_param_prepare()
    output_path = '/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/' + \
                  'daily_trade_prepare/trend_stock_param_%d.xlsx' % tp.today_date
    with pd.ExcelWriter(output_path) as writer:
        buy_df.to_excel(writer, '买入股票池')
        sell_df.to_excel(writer, '卖出股票池')
        stat_param.to_excel(writer, '策略参数')
    print('已保存至%s' % output_path)

