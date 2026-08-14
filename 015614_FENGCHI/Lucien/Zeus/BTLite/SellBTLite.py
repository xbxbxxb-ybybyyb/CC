# coding: utf-8
# Author：fengchi863
# Date ：2023/4/4 13:57

from Zeus.Europa.v2_0_12.path_conf import date_config, junk_path
import pandas as pd
import numpy as np
import math
import time
from LucienUtil.FileUtil import FileUtil
from xquant.factordata import FactorData

fd = FactorData()


class SellBTLite2:
    def __init__(self, strategy_name, model_name, date_dict, bt_save_path, mode='serial', save_flag=False, test_fpath=None, fit_fpath=None):
        """
        :param mode: mode可选multi和serial
        """
        self.test_fpath = test_fpath
        self.fit_fpath = fit_fpath
        self.strategy_name = strategy_name
        self.model_name = model_name
        self.date_dict = date_dict
        self.bt_save_path = bt_save_path
        self.save_flag = save_flag

        self.train_start_date = date_dict['train_start_date']
        self.train_end_date = date_dict['train_end_date']
        self.test_start_date = date_dict['test_start_date']
        self.test_end_date = date_dict['test_end_date']
        self.fit_start_date = date_dict['fit_start_date']
        self.fit_end_date = date_dict['fit_end_date']
        self.mode = mode

        self.profit_fpath, self.label_fpath = None, None
        self.test_df, self.fit_df, self.profit_df, self.label_df, self.cost_pct = None, None, None, None, None
        self.extreme_thres, self.attend_min, self.attend_max = None, None, None
        self.state_machine()

    def set_test_fpath(self, value):
        self.test_fpath = value

    def set_fit_fpath(self, value):
        self.fit_fpath = value

    def set_bt_save_path(self, value):
        self.bt_save_path = value

    def state_machine(self):
        if self.strategy_name is 'Europa':
            self.profit_fpath = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5'
            self.label_fpath = '/data/group/800463/sunss/for_xly/europa/20221116_new/factor_df_all_20160101_20220630.pkl'
            self.cost_pct = 0
            self.extreme_thres = 0.2
            self.attend_min = 20
            self.attend_max = 51  # 20230317 选择收益最大的阈值，降低此时的回撤
        elif self.strategy_name is 'JupiterN':
            self.profit_fpath = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.h5'
            self.label_fpath = '/data/group/800463/sunss/jupiter/20221220/factor_df_all_20160101_20220630.pkl'
            self.cost_pct = 0.002
            self.attend_min = 10
            self.attend_max = 51  # TODO：change
            self.extreme_thres = 0.2
        elif self.strategy_name is 'JupiterNSell':
            self.profit_fpath = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/LabelProfit_zt_pct_931_0.10_800_190_SH450_SZ100.h5'
            self.label_fpath = '/data/group/800463/sunss/jupiter_931o2ul/20230201/factor_df_all_20160101_20201231.pkl'
            self.cost_pct = 0.003
            self.attend_min = 10
            self.attend_max = 41
            self.extreme_thres = 0.2

        profit_df = pd.read_hdf(self.profit_fpath)
        label_df = pd.read_pickle(self.label_fpath)
        if 'label_pct_cost' not in profit_df.columns:
            profit_df.columns = ['label_' + i for i in profit_df.columns]
            profit_df['label_pct_cost'] = profit_df['label_pct'] - self.cost_pct
            profit_df['label_profit_cost'] = profit_df['label_pct_cost'] * profit_df['label_buy_amt']
            profit_df = profit_df.reset_index()
            profit_df['stockID'] = profit_df['Ticker']
            profit_df['datelist'] = profit_df['dt'].apply(lambda x: int(x.to_pydatetime().strftime("%Y%m%d")))
            profit_df['Indexs'] = profit_df['stockID'].astype(str) + ' ' + (profit_df['datelist'].astype(int)).astype(str)
            profit_df = profit_df.set_index(['Indexs'])

        label_df = label_df.reset_index()
        label_df['stockID'] = label_df['Ticker']
        label_df['datelist'] = label_df['dt'].apply(lambda x: int(x.to_pydatetime().strftime("%Y%m%d")))
        label_df['Indexs'] = label_df['stockID'].astype(str) + ' ' + (label_df['datelist'].astype(int)).astype(str)
        label_df = label_df.set_index(['Indexs'])

        self.profit_df = profit_df
        self.label_df = label_df

    def data_prepare(self):
        samples = pd.read_csv(self.test_fpath, index_col=0)
        samples['dt'] = samples['datelist'].apply(lambda x: pd.to_datetime(str(x)))

        # profit与所有Europa买入样本合并
        profit = pd.read_hdf('/data/group/800463/sunss/project_sell/newData/Sell_pct_0.10_800_190_SH450_SZ100.h5')
        europa_samples = pd.read_pickle('/data/group/800463/sunss/europa/20230317/factor_df_all_20160101_20211231.pkl')
        profit['sell_date'] = profit.index.get_level_values(0)
        profit['Ticker'] = profit.index.get_level_values(1)
        profit['dt'] = profit['dt_last_zt_1_ts']
        profit['buy_datelist'] = profit['dt_last_zt_1_ts'].apply(lambda x: int(x.strftime('%Y%m%d')))
        profit = profit.query(f'buy_datelist >= 20210701 & buy_datelist <= 20211231')
        profit = profit.set_index(['dt', 'Ticker'])
        profit = profit.loc[list(set(europa_samples.index).intersection(set(profit.index)))].sort_index()

        # 合并信号
        samples['dt'] = samples['datelist'].apply(lambda x: pd.to_datetime(str(x)))
        samples['Ticker'] = samples['stockID']
        samples = samples.set_index(['dt', 'Ticker'])
        profit['dt'] = profit['sell_date']
        profit['Ticker'] = profit.index.get_level_values(1)
        profit = profit.set_index(['dt', 'Ticker'])
        combine = pd.merge(profit, samples, on=['dt', 'Ticker'])

        combine['label_pct_cost'] = combine['label_diff_pct'] - self.cost_pct
        combine['label_profit_cost'] = combine['label_pct_cost'] * combine['buy_amt']
        combine['label_pct'] = combine['label_diff_pct']
        combine['label_buy_amt'] = combine['buy_amt']
        combine['ZT_Time'] = 0

        combine['Indexs'] = combine[['stockID', 'datelist']].apply(lambda x: x['stockID'] + ' ' + str(x['datelist']), axis=1)
        combine = combine.set_index('Indexs')

        self.test_df = combine
        self.fit_df = combine

    def _concat_label_profit(self, df):
        df_copy = df.copy()
        df_copy['label_pct_cost'] = self.profit_df['label_diff_pct'] - self.cost_pct
        df_copy['label_profit_cost'] = self.profit_df['label_pct_cost'] * self.profit_df['label_buy_amt']
        df_copy['label_pct'] = self.profit_df['label_diff_pct']
        df_copy['label_buy_amt'] = self.profit_df['label_buy_amt']
        df_copy['ZT_Time'] = 0
        return df_copy

    def _remove_extreme(self, _df):
        df = _df.copy()
        thres = self.extreme_thres
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
                      'ZT_Time': '突破时间'}
        df = df.rename(columns=rename_col)
        df['盈亏金额'] = df['收益率'] * df['投资金额']
        return df

    def calc_model_mingan(self, _test_df, _fit_df):
        test_df = _test_df.copy()
        fit_df = _fit_df.copy()
        attend_pct_list = list(range(self.attend_min, self.attend_max, 1))
        test_attend_df = pd.DataFrame(index=attend_pct_list)
        test_df = test_df.sort_values(by='pred_Reg', ascending=False)
        fit_df = fit_df.sort_values(by='pred_Reg', ascending=False)
        test_totalnum = test_df.shape[0]
        fit_totalnum = fit_df.shape[0]

        # 分配group_id
        group_id_list = []  # 分成从20-40之间(不同策略不同)
        for attend_pct in attend_pct_list:
            ratio_num = math.ceil(test_totalnum * attend_pct / 100)
            if attend_pct == self.attend_min:
                tmp_num = ratio_num
            elif ratio_num >= test_totalnum:
                tmp_num = test_totalnum - math.ceil(test_totalnum * (attend_pct - 1) / 100)
            else:
                tmp_num = ratio_num - math.ceil(test_totalnum * (attend_pct - 1) / 100)

            group_id_list = group_id_list + [attend_pct] * tmp_num
        group_id_list = group_id_list + (test_totalnum - len(group_id_list)) * [attend_pct + 1]
        test_df['group_id'] = group_id_list
        date_list = [int(x) for x in fd.tradingday(str(20210701), str(20211231))]

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

        # 开始计算fit_df
        fit_attend_df = pd.DataFrame(index=test_attend_df.index)
        date_list = [int(x) for x in fd.tradingday(str(20210701), str(20211231))]
        for pred_reg in test_attend_df.index.tolist():
            group_df = fit_df.query(f'pred_Reg >= {pred_reg}')
            group_df_daily = group_df.groupby('datelist')[['label_profit_cost']].sum().reindex(date_list).fillna(0)
            fit_attend_df.loc[pred_reg, '实际参与率'] = round(len(group_df) / fit_totalnum, 4)
            fit_attend_df.loc[pred_reg, '因子值范围'] = str(float(group_df.min()['pred_Reg']))
            fit_attend_df.loc[pred_reg, '扣费收益率胜率'] = round((group_df['label_pct_cost'] > 0).mean(), 4)
            fit_attend_df.loc[pred_reg, '扣费收益率'] = round(group_df['label_pct_cost'].mean(), 4)
            fit_attend_df.loc[pred_reg, '累计盈利'] = int(group_df.sum()['label_profit_cost'])
            fit_attend_df.loc[pred_reg, '最大回撤'] = int(self.calc_mdd(group_df_daily['label_profit_cost'].values))
            fit_attend_df.loc[pred_reg, '收益风险比'] = round(abs(fit_attend_df.loc[pred_reg, '累计盈利'] / fit_attend_df.loc[pred_reg, '最大回撤']), 4)
            fit_attend_df.loc[pred_reg, '夏普比率'] = self.calc_sharp(group_df, ref_col='收益率(扣除成本)')
            fit_attend_df.loc[pred_reg, '收益夏普比率'] = self.calc_sharp(group_df, ref_col='盈亏金额(扣除成本)')

        return test_attend_df, fit_attend_df

    @staticmethod
    def fun_stats_by_day(_df, _start_date, _end_date):
        stats_by_samples1 = _df.reset_index().copy()
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

    def start_backtest(self):
        self.data_prepare()
        test_df = self.test_df.copy()
        fit_df = self.fit_df.copy()

        test_stats_by_samples_all = self.calc_samples_by_times(test_df)
        test_stats_by_samples1 = test_stats_by_samples_all.query('prediction == 1')
        test_stats_by_day, test_stats_by_samples1 = self.fun_stats_by_day(test_stats_by_samples1, 20210701, 20211231)
        stats_df = self.calc_model_bt_result(test_df, test_stats_by_samples1, test_stats_by_day)
        model_test_mingan, model_fit_mingan = self.calc_model_mingan(_test_df=test_df, _fit_df=fit_df)

        if self.save_flag:
            save_dict = {'模型结果': stats_df, '样本内不同参与率统计': model_test_mingan, '样本外不同参与率统计': model_fit_mingan}
            FileUtil.save_dict2xls(save_dict, self.bt_save_path)

        return stats_df, model_test_mingan, model_fit_mingan


if __name__ == '__main__':

    period4_test_fpath_list = [
        '/data/user/015614/Zeus/pred/ProjectSell/v1_0_2/LgbRegModelV2/20210701~20211231_LgbRegModelV2_v4.csv',
        '/data/user/015614/Zeus/pred/ProjectSell/v1_0_2/LgbRegModelV3/20210701~20211231_LgbRegModelV3_v4.csv',
        '/data/user/015614/Zeus/pred/ProjectSell/v1_0_2/XgbRegModelV2/20210701~20211231_XgbRegModelV2_v4.csv',
        '/data/user/015614/Zeus/pred/ProjectSell/v1_0_2/XgbRegModelV3/20210701~20211231_XgbRegModelV3_v4.csv',
    ]
    for test_fpath in period4_test_fpath_list:
        btl = SellBTLite2(test_fpath=test_fpath,
                      fit_fpath=test_fpath,
                      strategy_name='Europa',
                      model_name='SingleTestModel',
                      date_dict=date_config['period2'],
                      bt_save_path=junk_path + '回测结果/')

        stats_df, model_test_mingan, model_fit_mingan = btl.start_backtest()
        res_dict = {'回测结果': pd.DataFrame(stats_df),
                    'test结果：': model_test_mingan}
        from LucienUtil.FileUtil import FileUtil
        FileUtil.save_dict2xls(res_dict, junk_path, f'{test_fpath[-20:-7]}.xlsx')