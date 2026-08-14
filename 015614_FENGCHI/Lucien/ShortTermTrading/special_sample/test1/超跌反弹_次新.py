# coding: utf-8
# Author：fengchi863
# Date ：2023/8/25 16:24

"""
选择一批个股直接购买

筛选条件：
对最近两周未成交强势股K线图观察，发现存在多只个股上市时间不超过3年（类似次新股），且属于超跌反弹类型，测试此类样本。

条件：
1）超跌：最新收盘价位于近300个交易日15%分位数以下；
2）波动小：近60日最高价与最低价的价差涨跌幅不超过30%；
3）类次新：上市时间不超过750个交易日；
4）市值：剔除100亿市值以上个股（若不剔除，从结果中发现较多银行股）；

"""

from dataApi import tradeDate, getData, stockList
import pandas as pd
import numpy as np
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil

class Stock:
    def __init__(self, start_date, end_date):
        shift_start_date = tradeDate.get_pre_trade_date(start_date, 310)
        date_list = tradeDate.get_date_range(shift_start_date, end_date)
        close_badj = getData.get_daily_1factor('close_badj', date_list=date_list)
        high_badj = getData.get_daily_1factor('high_badj', date_list=date_list)
        open_badj = getData.get_daily_1factor('open_badj', date_list=date_list)
        low_badj = getData.get_daily_1factor('low_badj', date_list=date_list)
        pre_close_badj = getData.get_daily_1factor('pre_close_badj', date_list=date_list)
        stock_pool = stockList.clean_stock_list(least_live_days=5,
                                                start_date=date_list[0],
                                                end_date=date_list[-1],
                                                trade_mode=True,
                                                no_pause=False,
                                                least_recover_days=1,
                                                no_pause_limit=0.5,
                                                no_pause_stats_days=0)
        live_days = getData.get_daily_1factor('live_days', date_list=date_list)
        a_mkt_cap = getData.get_daily_1factor('a_mkt_cap', date_list=date_list)

        self.date_list = date_list
        self.start_date = start_date
        self.end_date = end_date
        self.str_date_list = list(map(str, date_list))
        self.close_badj = close_badj
        self.high_badj = high_badj
        self.open_badj = open_badj
        self.low_badj = low_badj
        self.pre_close_badj = pre_close_badj
        self.stock_pool = stock_pool
        self.live_days = live_days
        self.a_mkt_cap = a_mkt_cap

        self.all_samples = None

    def calc_daily_stock_pool(self):
        """日间条件"""
        cond1 = self.cond1()
        cond2 = self.cond2()
        cond3 = self.cond3()
        cond4 = self.cond4()
        inter_cond = cond1 & cond2 & cond3 & cond4
        inter_cond = inter_cond.loc[self.start_date:self.end_date]
        inter_cond.index = inter_cond.index.map(lambda x: pd.to_datetime(str(x)))
        inter_cond.columns = inter_cond.columns.map(lambda x: stockList.trans_int2windcode(x))
        inter_stk_pool = inter_cond.stack()
        inter_stk_pool = pd.DataFrame(inter_stk_pool)
        inter_stk_pool.index.names = ['dt', 'Ticker']
        inter_stk_pool.columns = ['inter_cond']

        """日内条件"""
        data = pd.read_pickle('/data/user/018107/share_file/for_fc/europa/20230329_new/factor_df_all_20160101_20230331.pkl')  # Europa因子数据
        inter_cond1 = data['Vwap'] < 50
        # inter_cond2 = data['ZT_Time'] <= 113000000
        data['intra_cond'] = inter_cond1

        """合并日间与日内信号，对齐"""
        all_samples = pd.merge(inter_stk_pool, data[['intra_cond']], how='inner', on=['dt', 'Ticker'])
        all_samples['signal'] = all_samples['inter_cond'] & all_samples['intra_cond']

        self.all_samples = all_samples

    def cond1(self):
        """价格分位数"""
        threshold15 = self.close_badj.rolling(300, min_periods=300).quantile(0.15)
        cond1 = self.close_badj < threshold15
        return cond1.shift(1)

    def cond2(self):
        """波动率"""
        close_max = self.close_badj.rolling(60).max()
        close_min = self.close_badj.rolling(60).min()
        max_pctchg = (close_max - close_min) / close_min
        cond2 = max_pctchg < 0.3
        return cond2.shift(1)

    def cond3(self):
        """上市时间不超过750个交易日"""
        cond3 = self.live_days < 750
        return cond3.shift(1)

    def cond4(self):
        """市值低于100亿"""
        cond4 = self.a_mkt_cap < 100 * 1e8
        return cond4.shift(1)

    def simple_backtest(self):
        profit_data = pd.read_hdf('/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5')

        signal_data = self.all_samples.copy()
        profit_data = signal_data.join(profit_data)
        """计算基本收益信息"""
        stats_dict = self.generate_bt_res(profit_data)
        return stats_dict

    def generate_bt_res(self, profit_data):
        """带有一个signal列"""
        stats_dict = dict()

        """日收益"""
        profit_data['trade_date'] = profit_data.index.get_level_values(0).map(lambda x: x.strftime('%Y%m%d'))
        profit_data['trade_year'] = profit_data['trade_date'].map(lambda x: x[:4])
        profit_data['profit'] = profit_data['buy_amt'] * profit_data['pct']

        daily_profit = pd.DataFrame()
        daily_profit['日收益'] = profit_data.query('signal == 1').groupby('trade_date')['profit'].sum()
        daily_profit = daily_profit.reindex(index=list(set(profit_data['trade_date'].unique()))).fillna(0).sort_index()
        daily_profit['累计收益'] = daily_profit['日收益'].cumsum()
        stats_dict['按日'] = daily_profit.copy()

        daily_profit['trade_year'] = daily_profit.index.map(lambda x: x[:4])
        yearly_stats = pd.DataFrame()
        yearly_stats['参与样本个数'] = profit_data.query('signal == 1').query('pct > 0').groupby('trade_year')['pct'].count()
        yearly_stats['平均收益率'] = profit_data.query('signal == 1').groupby('trade_year')['pct'].mean()
        yearly_stats['累计收益'] = profit_data.query('signal == 1').groupby('trade_year')['profit'].sum()
        yearly_stats['最大回撤'] = daily_profit.groupby('trade_year')['日收益'].apply(lambda x: self.calc_mdd(x))
        yearly_stats['收益风险比'] = -yearly_stats['累计收益'] / yearly_stats['最大回撤']
        yearly_stats['胜率'] = profit_data.query('signal == 1').groupby('trade_year')['pct'].apply(lambda x: (x > 0).sum() / len(x))

        all_profit = profit_data.copy()
        summray_stats = pd.Series()
        summray_stats['参与样本个数'] = all_profit.query('signal == 1').query('pct > 0')['pct'].count()
        summray_stats['平均收益率'] = profit_data.query('signal == 1')['pct'].mean()
        summray_stats['累计收益'] = profit_data.query('signal == 1')['profit'].sum()
        summray_stats['最大回撤'] = self.calc_mdd(daily_profit['日收益'])
        summray_stats['收益风险比'] = -summray_stats['累计收益'] / summray_stats['最大回撤']
        summray_stats['胜率'] = (profit_data.query('signal == 1')['pct'] > 0).sum() / len(profit_data.query('signal == 1'))

        origin_index_list = yearly_stats.index.tolist()
        yearly_stats = yearly_stats.append(summray_stats, ignore_index=True)
        yearly_stats.index = origin_index_list + ['all']

        stats_dict['按年'] = yearly_stats

        stats_dict['触发样本'] = profit_data.query('signal == 1')
        return stats_dict

    @staticmethod
    def calc_mdd(_s):
        mdd = (np.maximum.accumulate(np.nancumsum(_s)) - np.nancumsum(_s)).max()
        return -mdd

if __name__ == '__main__':
    v_inst = Stock(20160101, 20201231)
    # v_inst = Stock(20160101, 20230829)
    v_inst.calc_daily_stock_pool()
    stats_dict = v_inst.simple_backtest()
    FileUtil.save_dict2xls(stats_dict, '/data/user/015614/junkData/', 'bt_res.xlsx')
    send_file('/data/user/015614/junkData/bt_res.xlsx')