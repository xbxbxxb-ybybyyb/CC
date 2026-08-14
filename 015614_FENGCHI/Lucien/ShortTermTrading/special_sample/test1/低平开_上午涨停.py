# coding: utf-8
# Author：fengchi863
# Date ：2023/8/29 13:32

"""
针对之前发现的VWAP因子影响过大的问题，考虑对特定样本进行测试：

条件：低平开 + 快速涨停 + 涨停时间不要太晚
1）开盘涨跌幅低于1%
2）Vwap低于3.6
3）涨停时间为上午

"""

from dataApi import tradeDate, getData, stockList
import pandas as pd
import numpy as np
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil

class Vwap2:
    def __init__(self):
        date_list = tradeDate.get_date_range(20160101, 20201231)
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

        self.date_list = date_list
        self.str_date_list = list(map(str, date_list))
        self.close_badj = close_badj
        self.high_badj = high_badj
        self.open_badj = open_badj
        self.low_badj = low_badj
        self.pre_close_badj = pre_close_badj
        self.stock_pool = stock_pool

        self.all_samples = None

    def calc_daily_stock_pool(self):
        """日间条件"""
        cond1 = self.cond1()
        cond1.index = cond1.index.map(lambda x: pd.to_datetime(str(x)))
        cond1.columns = cond1.columns.map(lambda x: stockList.trans_int2windcode(x))
        inter_stk_pool = cond1.stack()
        inter_stk_pool = pd.DataFrame(inter_stk_pool)
        inter_stk_pool.index.names = ['dt', 'Ticker']
        inter_stk_pool.columns = ['inter_cond']

        """日内条件"""
        data = pd.read_pickle('/data/user/018107/share_file/for_fc/europa/20230329_new/factor_df_all_20160101_20230331.pkl')  # Europa因子数据
        inter_cond1 = data['Vwap'] < 3.6
        inter_cond2 = data['ZT_Time'] <= 113000000
        data['intra_cond'] = inter_cond1 & inter_cond2

        """合并日间与日内信号，对齐"""
        all_samples = pd.merge(inter_stk_pool, data[['intra_cond']], how='inner', on=['dt', 'Ticker'])
        all_samples['signal'] = all_samples['inter_cond'] & all_samples['intra_cond']

        self.all_samples = all_samples

    def cond1(self):
        """早盘低平开"""
        opn_pct = self.open_badj / self.pre_close_badj - 1
        cond1 = opn_pct < 0.01
        return cond1

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

        yearly_stats = yearly_stats.append(summray_stats, ignore_index=True)
        yearly_stats.index = [2016, 2017, 2018, 2019, 2020, 'all']

        stats_dict['按年'] = yearly_stats
        stats_dict['触发样本'] = profit_data.query('signal == 1')
        return stats_dict

    @staticmethod
    def calc_mdd(_s):
        mdd = (np.maximum.accumulate(np.nancumsum(_s)) - np.nancumsum(_s)).max()
        return -mdd

if __name__ == '__main__':
    v_inst = Vwap2()
    v_inst.calc_daily_stock_pool()
    stats_dict = v_inst.simple_backtest()
    FileUtil.save_dict2xls(stats_dict, '/data/user/015614/junkData/', 'bt_res.xlsx')
    send_file('/data/user/015614/junkData/bt_res.xlsx')