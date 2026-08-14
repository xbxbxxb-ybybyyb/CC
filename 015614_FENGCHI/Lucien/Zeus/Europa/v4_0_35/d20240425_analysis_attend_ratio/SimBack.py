# coding: utf-8
# Author：fengchi863
# Date ：2024/4/25 13:54

import pandas as pd
import numpy as np
import math
from xquant.factordata import FactorData

fd = FactorData()

class SimBack:
    def __init__(self, fit_df):
        self.fit_df = fit_df
        self.cost_pct = 0.002
        # profit_df = pd.read_hdf('/data/group/800463/sunss/profit/europa/20240401/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5')
        profit_df = pd.read_hdf('/data/group/800463/project/project1_prod/LabelProfit_fix/001/LabelProfit_zt_twap_0.15_2000_300_SH250_SZ20.h5')
        if 'label_pct_cost' not in profit_df.columns:
            profit_df.columns = ['label_' + i for i in profit_df.columns]
            profit_df['label_pct_cost'] = profit_df['label_pct'] - self.cost_pct
            profit_df['label_profit_cost'] = profit_df['label_pct_cost'] * profit_df['label_buy_amt']
            profit_df = profit_df.reset_index()
            profit_df['stockID'] = profit_df['Ticker']
            profit_df['datelist'] = profit_df['dt'].apply(lambda x: int(x.to_pydatetime().strftime("%Y%m%d")))
            profit_df['Indexs'] = profit_df['stockID'].astype(str) + ' ' + (profit_df['datelist'].astype(int)).astype(str)
            profit_df = profit_df.set_index(['Indexs'])
        self.profit_df = profit_df

    def _concat_label_profit(self, df):
        df_copy = df.copy()
        df_copy['label_pct_cost'] = self.profit_df['label_pct'] - self.cost_pct
        df_copy['label_profit_cost'] = self.profit_df['label_pct_cost'] * self.profit_df['label_buy_amt']
        df_copy['label_pct'] = self.profit_df['label_pct']
        df_copy['label_buy_amt'] = self.profit_df['label_buy_amt']

        df_copy['datelist'] = df_copy['datelist'].astype(int)
        return df_copy

    @staticmethod
    def _remove_extreme(_df):
        df = _df.copy()
        thres = 0.2
        by = '收益率(扣除成本)'

        if df[by][df[by].abs() > thres].shape[0] > 0:
            df[by][df[by] > thres] = thres
            df[by][df[by] < -thres] = -thres

        df['盈亏金额(扣除成本)'] = df[by] * df['投资金额']
        df['label_profit_cost'] = df[by] * df['投资金额']
        return df

    @staticmethod
    def calc_samples_by_times(_df):
        df = _df.copy()
        rename_col = {'label_buy_amt': '投资金额',
                      'label_pct': '收益率',
                      'label_pct_cost': '收益率(扣除成本)',
                      'label_profit_cost': '盈亏金额(扣除成本)',
                      # 'ZT_Time': '突破时间',
                      }
        df = df.rename(columns=rename_col)
        df['盈亏金额'] = df['收益率'] * df['投资金额']
        return df

    def calc_model_mingan(self, _test_df):
        test_df = _test_df.copy()
        attend_pct_list = list(range(20, 50, 1))
        test_attend_df = pd.DataFrame(index=attend_pct_list)
        test_df = test_df.sort_values(by='pred_Reg', ascending=False)
        test_totalnum = test_df.shape[0]

        # 分配group_id
        group_id_list = []  # 分成从20-50之间(不同策略不同)
        attend_pct = None
        for attend_pct in attend_pct_list:
            ratio_num = math.ceil(test_totalnum * attend_pct / 100)
            if attend_pct == 20:
                tmp_num = ratio_num
            elif ratio_num >= test_totalnum:
                tmp_num = test_totalnum - math.ceil(test_totalnum * (attend_pct - 1) / 100)
            else:
                tmp_num = ratio_num - math.ceil(test_totalnum * (attend_pct - 1) / 100)

            group_id_list = group_id_list + [attend_pct] * tmp_num
        group_id_list = group_id_list + (test_totalnum - len(group_id_list)) * [attend_pct + 1]
        test_df['group_id'] = group_id_list
        date_list = [int(x) for x in fd.tradingday(str(20230421), str(20240424))]

        for attend_pct in attend_pct_list:
            group_df = test_df.query(f'group_id <= {attend_pct}')
            group_df_daily = group_df.groupby('datelist').sum()[['label_profit_cost']].reindex(date_list).fillna(0)
            test_attend_df.loc[attend_pct, '实际参与率'] = round(len(group_df) / test_totalnum, 4)
            test_attend_df.loc[attend_pct, '因子值范围'] = str(float(group_df.min()['pred_Reg']))
            test_attend_df.loc[attend_pct, '扣费收益率胜率'] = round((group_df['label_pct_cost'] > 0).mean(), 4)
            test_attend_df.loc[attend_pct, '扣费收益率'] = round(group_df['label_pct_cost'].mean(), 4)
            test_attend_df.loc[attend_pct, '累计盈利'] = int(group_df.sum()['label_profit_cost'])
            test_attend_df.loc[attend_pct, '最大回撤'] = int(self.calc_mdd(group_df_daily['label_profit_cost'].values))
            test_attend_df.loc[attend_pct, '收益风险比'] = round(abs(test_attend_df.loc[attend_pct, '累计盈利'] / test_attend_df.loc[attend_pct, '最大回撤']), 4)
            test_attend_df.loc[attend_pct, '夏普比率'] = self.calc_sharp(group_df, ref_col='收益率(扣除成本)')
            test_attend_df.loc[attend_pct, '收益夏普比率'] = self.calc_sharp(group_df, ref_col='盈亏金额(扣除成本)')

        test_attend_df = test_attend_df.set_index(['因子值范围'])

        return test_attend_df

    @staticmethod
    def fun_stats_by_day(_df, _start_date, _end_date):
        stats_by_samples1 = _df.reset_index().copy()
        stats_by_samples1['datelist'] = stats_by_samples1['datelist'].astype(int)
        date_list = list(map(int, fd.tradingday(str(_start_date), str(_end_date))))

        stats_by_day = pd.DataFrame(index=date_list)
        stats_by_day = stats_by_day.join(stats_by_samples1.query('投资金额 > 0').groupby('datelist')['投资金额', '盈亏金额', '盈亏金额(扣除成本)'].sum())
        stats_by_day['收益率'] = stats_by_day['盈亏金额'] / stats_by_day['投资金额']
        stats_by_day['收益率(扣除成本)'] = stats_by_day['盈亏金额(扣除成本)'] / stats_by_day['投资金额']
        stats_by_day['滚动5日收益率(扣除成本)'] = (stats_by_samples1.groupby('datelist')['收益率(扣除成本)'].sum().reindex(stats_by_day.index).fillna(0)).rolling(5, 5).sum() / (
            stats_by_samples1.groupby('datelist')['stockID'].count().reindex(stats_by_day.index).fillna(0)).rolling(5, 5).sum()
        stats_by_day['累计盈亏(扣除成本)'] = stats_by_day['盈亏金额(扣除成本)'].fillna(0).cumsum()

        stats_by_day = stats_by_day.fillna(0)
        stats_by_samples1 = stats_by_samples1.fillna(0).set_index('Indexs')
        return stats_by_day, stats_by_samples1

    @staticmethod
    def calc_sharp(_df, ref_col=None):
        df = _df.copy()

        if 'label_pct_cost' in df.columns.tolist():
            rename_col = {'label_pct_cost': '收益率(扣除成本)',
                          'label_profit_cost': '盈亏金额(扣除成本)',
                          'label_buy_amt': '投资金额'}
            df = df.rename(rename_col, axis=1)

        date_list = list(map(int, fd.tradingday(int(df['datelist'].min()), int(df['datelist'].max()))))
        daily_data = df.groupby('datelist')['投资金额', '盈亏金额(扣除成本)'].sum().reindex(date_list)
        daily_data['近3日盈亏金额(扣除成本)'] = daily_data['盈亏金额(扣除成本)'].rolling(3, 1).sum()
        daily_data['近3日投资金额'] = daily_data['投资金额'].rolling(3, 1).sum()
        daily_data['收益率(扣除成本)'] = daily_data['近%s日盈亏金额(扣除成本)' % str(3)] / daily_data['近3日投资金额']
        daily_data['滚动3日盈亏金额(扣除成本)'] = daily_data['盈亏金额(扣除成本)'].rolling(3, 1).mean()

        if ref_col == '收益率(扣除成本)':
            daily_data['投资金额'] = daily_data['近3日投资金额']

        daily_data = daily_data.fillna(0)
        mean_ret = daily_data.query('投资金额 > 0')[ref_col].mean()
        std_ret = daily_data.query('投资金额 > 0')[ref_col].std()
        sharp = abs(mean_ret / std_ret) * math.sqrt(250)
        return sharp

    @staticmethod
    def calc_mdd(_s):
        mdd = (np.maximum.accumulate(np.nancumsum(_s)) - np.nancumsum(_s)).max()
        return -mdd

    def calc_model_bt_result(self, _fit_df, _test_stats_by_samples1, _test_stats_by_day):
        """
        :param _fit_df: 保存的预测记录prediction|pred_Reg|stockID|datelist，拼接了一部分列，如label_pct_cost|label_profit_cost|label_buy_amt|label_pct|ZT_Time
        :param _test_stats_by_samples1: 预测为1的部分，prediction|pred_Reg|stockID|datelist|收益率(扣除成本)|盈亏金额(扣除成本)|收益率|投资金额|突破时间|盈亏金额
        :param _test_stats_by_day: 按日统计：投资金额|盈亏金额|盈亏金额(扣除成本)|收益率|收益率(扣除成本)|滚动5日收益率(扣除成本)|累计盈亏(扣除成本)
        :return:
        """
        fit_df, test_stats_by_samples1, test_stats_by_day = _fit_df.copy(), _test_stats_by_samples1.copy(), _test_stats_by_day.copy()
        fit_df['盈亏金额(扣除成本)'] = test_stats_by_samples1['盈亏金额(扣除成本)']
        stats_s = pd.Series()

        stats_s['基础样本数量'] = fit_df.shape[0]
        stats_s['扣费后收益率胜率'] = test_stats_by_samples1[(test_stats_by_samples1['投资金额'] > 0) & (test_stats_by_samples1['收益率(扣除成本)'] > 0)].shape[0] / \
                              test_stats_by_samples1.query('投资金额 > 0').shape[0]
        stats_s['样本参与率'] = test_stats_by_samples1.query('prediction == 1').shape[0] / fit_df.shape[0]
        stats_s['实际参与次数'] = test_stats_by_samples1.query('投资金额 > 0').shape[0]
        stats_s['累计扣费总收益'] = int(test_stats_by_samples1.query('投资金额 > 0')['盈亏金额(扣除成本)'].sum())
        stats_s['最大回撤'] = int(self.calc_mdd(test_stats_by_day['盈亏金额(扣除成本)'].values))
        stats_s['收益风险比'] = -stats_s['累计扣费总收益'] / stats_s['最大回撤']
        stats_s['夏普比率'] = self.calc_sharp(test_stats_by_samples1, ref_col='收益率(扣除成本)')
        stats_s['收益夏普比率'] = self.calc_sharp(test_stats_by_samples1, ref_col='盈亏金额(扣除成本)')
        stats_s['预测值与标签IC'] = fit_df.query('label_buy_amt>0')[['label_pct_cost', 'pred_Reg']].corr().iloc[0, 1]
        stats_s['预测值与标签RankIC'] = fit_df.query('label_buy_amt>0')[['label_pct_cost', 'pred_Reg']].corr('spearman').iloc[0, 1]
        return stats_s

    def single_backtest(self):
        fit_df = self._concat_label_profit(self.fit_df)
        test_stats_by_samples_all = self.calc_samples_by_times(fit_df)
        test_stats_by_samples1 = test_stats_by_samples_all.query('prediction == 1')
        test_stats_by_day, test_stats_by_samples1 = self.fun_stats_by_day(test_stats_by_samples1, 20230421, 20240424)
        stats_df = self.calc_model_bt_result(fit_df, test_stats_by_samples1, test_stats_by_day)
        model_fit_mingan = self.calc_model_mingan(fit_df)

        return stats_df, model_fit_mingan