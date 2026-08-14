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
from FaaMonitor.conf.path_conf import ths_reverse_path, ths_concept_rank_path


class TradePrepare:
    def __init__(self):
        today_date = DtUtil.get_today_date()
        yes_date = DtUtil.get_yesterday_date()

        date_list = tradeDate.get_date_range(tradeDate.get_pre_trade_date(yes_date, 30), yes_date)
        daily_close = getData.get_daily_1factor('close_badj', date_list=date_list)
        ma5 = daily_close.rolling(5).mean()
        pre_close = getData.get_daily_1factor('pre_close_badj', date_list=date_list)
        adjfactor = getData.get_daily_1factor('adjfactor')  # 每日8:50更新当日复权因子数据

        # ths_concept = np.load(ths_reverse_path).item()
        ths_concept = pd.read_json(ths_concept_rank_path + f'同花顺概念排名{today_date}.json', typ='dict').to_dict()

        if adjfactor.iloc[-1].name != today_date:
            raise IndexError('当日%d权重信息尚未更新' % today_date)

        # self.today_date = 20210729
        # self.yes_date = tradeDate.get_pre_trade_date(self.today_date)
        self.today_date = today_date
        self.yes_date = yes_date
        self.date_list = date_list
        self.daily_close = daily_close
        self.ma5 = ma5
        self.ma5_boost = ma5 * 1.002
        self.pre_close = pre_close
        self.adjfactor = adjfactor

        self.ths_concept = ths_concept

    def trend_buy_prepare(self):
        tmp_df = pd.read_excel('/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/'
                               'daily_trade_prepare/daily_trade_prepare.xlsx',
                               sheet_name='交易准备')
        df = pd.DataFrame()
        buy_df = tmp_df[['买入股票代码', '买入股票名称']].dropna().drop_duplicates()
        if len(buy_df) == 0:
            return pd.DataFrame(columns=['stk_id', 'stk_name', 'ma', 'ma_boost', 'per_amt', 'pre_close', 'adjfactor'])
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
        df = self.add_concept_col(df)
        return df

    def trend_sell_prepare(self):
        tmp_df = pd.read_excel('/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/'
                               'daily_trade_prepare/daily_trade_prepare.xlsx',
                               sheet_name='交易准备')
        df = pd.DataFrame()
        sell_df = tmp_df[['卖出股票代码', '卖出股票名称']].dropna().drop_duplicates()
        if len(sell_df) == 0:
            return pd.DataFrame(columns=['stk_id', 'stk_name', 'buy_price', 'ma', 'vol', 'gain_closeout',
                                         'loss_closeout', 'adjfactor']).set_index('stk_id')
        sell_df['卖出股票代码'] = sell_df['卖出股票代码'].map(int)
        sell_df = sell_df.reset_index(drop=True)
        for idx in range(len(sell_df)):
            stk_id = sell_df.loc[idx, '卖出股票代码']
            stk_name = sell_df.loc[idx, '卖出股票名称']
            ma = self.ma5.loc[self.yes_date, stk_id]
            gain_closeout = 0.05
            loss_closeout = -0.05
            adjfactor = self.adjfactor.loc[self.today_date, stk_id]
            buy_price = ma / adjfactor
            vol = np.floor(1000000 / buy_price / 100) * 100  # 暂时设置为这么多进行测试
            append_content = [stk_id, stk_name, buy_price, ma, vol, gain_closeout, loss_closeout, adjfactor]
            df = df.append([append_content])
        df.columns = ['stk_id', 'stk_name', 'buy_price', 'ma', 'vol', 'gain_closeout', 'loss_closeout', 'adjfactor']
        df = df.set_index('stk_id', drop=True)
        df = self.add_concept_col(df)
        return df

    def trend_strategy_param_prepare(self):
        param = dict()
        param['强制平仓线'] = MARGIN_CLOSEOUT
        param['持仓组合号'] = '201001'
        df = pd.DataFrame(pd.Series(param))
        return df

    def zhaban_buy_prepare(self):
        tmp_df = pd.read_excel('/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/'
                               'daily_trade_prepare/daily_trade_prepare.xlsx',
                               sheet_name='交易准备')
        df = pd.DataFrame()
        buy_df = tmp_df[['炸板股买入股票代码', '炸板股买入股票名称']].dropna().drop_duplicates()
        buy_df['炸板股买入股票代码'] = buy_df['炸板股买入股票代码'].map(int)
        buy_df = buy_df.reset_index(drop=True)
        for idx in range(len(buy_df)):
            stk_id = buy_df.loc[idx, '炸板股买入股票代码']
            stk_name = buy_df.loc[idx, '炸板股买入股票名称']
            per_amt = 1000000
            pre_close = self.daily_close.loc[self.yes_date, stk_id]
            adjfactor = self.adjfactor.loc[self.today_date, stk_id]
            append_content = [stk_id, stk_name, per_amt, pre_close, adjfactor]
            df = df.append([append_content])
        df.columns = ['stk_id', 'stk_name', 'per_amt', 'pre_close', 'adjfactor']
        df = df.set_index('stk_id', drop=True)
        return df

    def zhaban_sell_prepare(self):
        tmp_df = pd.read_excel('/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/'
                               'daily_trade_prepare/daily_trade_prepare.xlsx',
                               sheet_name='交易准备')
        df = pd.DataFrame()
        sell_df = tmp_df[['炸板股卖出股票代码', '炸板股卖出股票名称']].dropna().drop_duplicates()
        if len(sell_df) == 0:
            return pd.DataFrame(columns=['stk_id', 'stk_name', 'buy_price', 'vol', 'pre_close', 'gain_closeout',
                                         'loss_closeout', 'adjfactor']).set_index('stk_id')
        sell_df['炸板股卖出股票代码'] = sell_df['炸板股卖出股票代码'].map(int)
        sell_df = sell_df.reset_index(drop=True)

        # 计算买入均价
        minute_amount = getData.get_minute_1factor('amt', start_datetime=self.yes_date,
                                                   end_datetime=self.yes_date, code_list=sell_df['炸板股卖出股票代码'].tolist())
        minute_vol = getData.get_minute_1factor('vol', start_datetime=self.yes_date,
                                                end_datetime=self.yes_date, code_list=sell_df['炸板股卖出股票代码'].tolist())

        for idx in range(len(sell_df)):
            stk_id = sell_df.loc[idx, '炸板股卖出股票代码']
            stk_name = sell_df.loc[idx, '炸板股卖出股票名称']

            total_amt = minute_amount.loc[(self.yes_date, 930):(self.yes_date, 1000), stk_id].sum()
            total_vol = minute_vol.loc[(self.yes_date, 930):(self.yes_date, 1000), stk_id].sum()
            vwap = total_amt / total_vol
            buy_price = vwap

            vol = np.floor(1000000 / buy_price / 100) * 100   # 暂时设置为这么多进行测试
            pre_close = self.daily_close.loc[self.yes_date, stk_id]
            gain_closeout = 0.05
            loss_closeout = -0.05
            adjfactor = self.adjfactor.loc[self.today_date, stk_id]
            append_content = [stk_id, stk_name, buy_price, vol, pre_close, gain_closeout, loss_closeout, adjfactor]
            df = df.append([append_content])
        df.columns = ['stk_id', 'stk_name', 'buy_price', 'vol', 'pre_close', 'gain_closeout', 'loss_closeout', 'adjfactor']
        df = df.set_index('stk_id', drop=True)
        return df

    def zhaban_strategy_param_prepare(self):
        param = dict()
        param['强制平仓线'] = MARGIN_CLOSEOUT
        param['持仓组合号'] = '201001'
        param['止损阈值'] = 0.96
        param['日内回撤阈值'] = 0.035
        df = pd.DataFrame(pd.Series(param))
        return df

    def add_concept_col(self, df):
        concept_str = df.index.to_series().apply(lambda x: self.ths_concept[stockList.trans_int2windcode(x)])
        for stk_id in concept_str.index:
            tmp = concept_str[stk_id]
            # concept_str[stk_id] = ','.join(self.del_concept(tmp.split('，')))
            concept_str[stk_id] = ','.join(self.del_concept(tmp.split(',')))
        df['concept'] = concept_str
        return df

    @staticmethod
    def del_concept(concept_list):
        def contain_strs(x, strs):
            for str in strs:
                if str in x:
                    return False
            return True
        del_concept = ['融资融券', '标普', '深股通', '半年报预增', '沪股通', 'MSCI', '新股与次新股',
                       '央企', '次新股', '创投', '参股', '同花顺']
        concept_list = list(filter(lambda x: contain_strs(x, del_concept), concept_list))
        return concept_list


MARGIN_CLOSEOUT = -0.08


if __name__ == '__main__':
    tp = TradePrepare()

    ## 趋势股
    sell_df = tp.trend_sell_prepare()
    buy_df = tp.trend_buy_prepare()
    stat_param = tp.trend_strategy_param_prepare()
    output_path = '/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/' + \
                  'daily_trade_prepare/trend_stock_param_%d.xlsx' % tp.today_date
    with pd.ExcelWriter(output_path) as writer:
        buy_df.to_excel(writer, '买入股票池')
        sell_df.to_excel(writer, '卖出股票池')
        stat_param.to_excel(writer, '策略参数')
    print('趋势股每日参数已保存至%s' % output_path)

    ## 炸板股
    sell_df = tp.zhaban_sell_prepare()
    buy_df = tp.zhaban_buy_prepare()
    stat_param = tp.zhaban_strategy_param_prepare()
    output_path = '/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/' + \
                  'daily_trade_prepare/zhaban_stock_param_%d.xlsx' % tp.today_date
    with pd.ExcelWriter(output_path) as writer:
        buy_df.to_excel(writer, '买入股票池')
        sell_df.to_excel(writer, '卖出股票池')
        stat_param.to_excel(writer, '策略参数')
    print('炸板股每日参数已保存至%s' % output_path)

###################下面用来拿固定日期的历史时间测试仓位管理模块能否成功使用
    # buy_df = pd.read_excel('/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/' + \
    #                    'daily_trade_prepare/trend_stock_param_20210917.xlsx', sheet_name='买入股票池', index_col=0)
    # sell_df = pd.read_excel('/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/' + \
    #                    'daily_trade_prepare/trend_stock_param_20210917.xlsx', sheet_name='卖出股票池', index_col=0)
    # stat_param = pd.read_excel('/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/' + \
    #                    'daily_trade_prepare/trend_stock_param_20210917.xlsx', sheet_name='策略参数', index_col=0)
    # buy_df = tp.add_concept_col(buy_df)
    # sell_df = tp.add_concept_col(sell_df)
    #
    # output_path = '/data/user/015614/MyWork/FaaMonitor/personal/fengchi/ftp_ssh/' + \
    #               'daily_trade_prepare/trend_stock_param_20210917.xlsx'
    # with pd.ExcelWriter(output_path) as writer:
    #     buy_df.to_excel(writer, '买入股票池')
    #     sell_df.to_excel(writer, '卖出股票池')
    #     stat_param.to_excel(writer, '策略参数')
    # print('趋势股每日参数已保存至%s' % output_path)

