# coding: utf-8
# Author：fengchi863
# Date ：2023/11/20 11:04

import pandas as pd
import numpy as np
from Zeus.JupiterN.v3_0_1.config.strat_conf import *
import math
import time
import os
from tqdm import tqdm
from LucienUtil.FileUtil import FileUtil
from xquant.factordata import FactorData

fd = FactorData()

def calc_stats_df(stats_df, stats_df2, model_test_mingan, model_fit_mingan):
    stats_df['平均收益风险比'] = model_test_mingan['收益风险比'].mean()
    stats_df['平均收益夏普比率'] = model_test_mingan['收益夏普比率'].mean()
    # stats_df['累计扣费总收益'] /= 1e8
    # stats_df['最大回撤'] /= 1e8
    # stats_df = stats_df.map(lambda x: round(x, 2))
    stats_df['基础样本数量'] = int(stats_df['基础样本数量'])
    stats_df['因子数量'] = 0

    stats_df2['平均收益风险比'] = model_fit_mingan['收益风险比'].mean()
    stats_df2['平均收益夏普比率'] = model_fit_mingan['收益夏普比率'].mean()
    # stats_df2['累计扣费总收益'] /= 1e8
    # stats_df2['最大回撤'] /= 1e8
    stats_df = stats_df.map(lambda x: round(x, 2))
    stats_df2['基础样本数量'] = int(stats_df2['基础样本数量'])

    print(stats_df[['收益风险比', '收益夏普比率', '平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '最大回撤', '预测值与标签IC', '扣费后收益率胜率', '基础样本数量', '因子数量']].to_dict())
    stats_df = stats_df[['因子数量', '基础样本数量', '平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '最大回撤', '样本参与率', '收益风险比', '夏普比率', '收益夏普比率', '预测值与标签IC']]
    stats_df2 = stats_df2[['基础样本数量', '平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '最大回撤', '样本参与率', '收益风险比', '夏普比率', '收益夏普比率', '预测值与标签IC']]
    stats_df2 = stats_df2.rename(dict(zip(stats_df2.index.tolist(), [x + '_fit' for x in stats_df2.index])))

    stats_df = pd.concat([stats_df, stats_df2])
    output_dict = {'汇总结果': stats_df, 'test': model_test_mingan, 'fit': model_fit_mingan}
    return output_dict

class SimBackTest:
    def __init__(self, pred_fpath_list, fit_fpath_list, date_dict, period, profit_data_fpath=None, data_fpath=None, attend_ratio_range=(10, 45), save_flag=True, multi_attend=True):
        self.attend_ratio_range = attend_ratio_range
        self.attend_min = attend_ratio_range[0]
        self.attend_max = attend_ratio_range[1]
        self.profit_data_fpath = profit_data_fpath
        self.data_fpath = data_fpath
        self.period = period
        self.pred_fpath_list = pred_fpath_list
        self.fit_fpath_list = fit_fpath_list
        self.save_flag = save_flag

        self.multi_attend = multi_attend
        self.attend_ratio = 40

        self.train_start_date = date_dict['train_start_date']
        self.train_end_date = date_dict['train_end_date']
        self.test_start_date = date_dict['test_start_date']
        self.test_end_date = date_dict['test_end_date']
        self.fit_start_date = date_dict['fit_start_date']
        self.fit_end_date = date_dict['fit_end_date']

        self.profit_df, self.label_df = None, None

        self.state_machine()

    def state_machine(self):
        self.profit_fpath = self.profit_data_fpath
        self.label_fpath = self.data_fpath

        # 这里不对策略做区分
        self.cost_pct = 0
        self.extreme_thres = 0.2

        if str(self.profit_fpath).endswith('.h5'):
            profit_df = pd.read_hdf(self.profit_fpath)
        else:
            profit_df = pd.read_pickle(self.profit_fpath)
        label_df = pd.read_pickle(self.label_fpath)

        if STRATEGY_NAME == 'ProjectSell':
            profit_df['pct'] = profit_df['label_diff_pct']

        if 'label_pct_cost' not in profit_df.columns:
            profit_df.columns = ['label_' + i for i in profit_df.columns]
            # if STRATEGY_NAME == 'Jupi___terZ':    # 下方加下划线防止被改变
            #     profit_df['label_pct'] = -profit_df['label_pct']
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

    def _concat_label_profit(self, df):
        df_copy = df.copy()
        df_copy['label_pct_cost'] = self.profit_df['label_pct'] - self.cost_pct
        df_copy['label_profit_cost'] = self.profit_df['label_pct_cost'] * self.profit_df['label_buy_amt']
        df_copy['label_pct'] = self.profit_df['label_pct']
        df_copy['label_buy_amt'] = self.profit_df['label_buy_amt']

        df_copy['datelist'] = df_copy['datelist'].astype(int)
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
                      # 'ZT_Time': '突破时间',
                      }
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
        attend_pct = None
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
        date_list = [int(x) for x in fd.tradingday(str(self.test_start_date), str(self.test_end_date))]

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
        date_list = [int(x) for x in fd.tradingday(str(self.fit_start_date), str(self.fit_end_date))]
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

    def single_backtest(self, pred_fpath, fit_fpath):
        # 在不同模式下，这里传进来的类型不一样，也就是SimBackTest可以传进预测值路径，也可以直接传进预测值的dataframe
        if type(pred_fpath) == str:
            try:
                test_df = pd.read_csv(pred_fpath, index_col=0)
            except:
                print(1)
        else:
            test_df = pred_fpath

        if type(fit_fpath) == str:
            fit_df = pd.read_csv(fit_fpath, index_col=0)
        else:
            fit_df = fit_fpath

        test_df = self._concat_label_profit(test_df)
        fit_df = self._concat_label_profit(fit_df)

        test_stats_by_samples_all = self.calc_samples_by_times(test_df)
        test_stats_by_samples1 = test_stats_by_samples_all.query('prediction == 1')
        test_stats_by_day, test_stats_by_samples1 = self.fun_stats_by_day(test_stats_by_samples1, self.test_start_date, self.test_end_date)

        fit_stats_by_samples_all = self.calc_samples_by_times(fit_df)
        fit_stats_by_samples1 = fit_stats_by_samples_all.query('prediction == 1')
        fit_stats_by_day, fit_stats_by_samples1 = self.fun_stats_by_day(fit_stats_by_samples1, self.fit_start_date, self.fit_end_date)

        stats_df = self.calc_model_bt_result(test_df, test_stats_by_samples1, test_stats_by_day)    # test
        stats_df2 = self.calc_model_bt_result(fit_df, fit_stats_by_samples1, fit_stats_by_day)  # fit
        model_test_mingan, model_fit_mingan = self.calc_model_mingan(_test_df=test_df, _fit_df=fit_df)

        if self.save_flag:
            save_dict = {'模型结果': stats_df, '样本内不同参与率统计': model_test_mingan, '样本外不同参与率统计': model_fit_mingan}

        return stats_df, stats_df2, model_test_mingan, model_fit_mingan

    def wrapper(self, pred_fpath_tuple_list):
        for idx in tqdm(range(len(pred_fpath_tuple_list))):
            pred_fpath, fit_fpath = pred_fpath_tuple_list[idx][0], pred_fpath_tuple_list[idx][1]
            test_stats_df, fit_stats_df, model_test_mingan, model_fit_mingan = self.single_backtest(pred_fpath, fit_fpath)
            output_dict = {'汇总结果': test_stats_df, '汇总结果fit': fit_stats_df, 'test': model_test_mingan, 'fit': model_fit_mingan}
            FileUtil.save_dict2xls(output_dict, os.path.dirname(pred_fpath) + '/', f'bt_result_{self.period}.xlsx', verbose=False)

    def start_backtest(self, multi=True):
        stats_df, stats_df2, model_test_mingan, model_fit_mingan = None, None, None, None
        if multi:
            pred_fpath_tuple_list = list(tuple(zip(self.pred_fpath_list, self.fit_fpath_list)))
            from LucienUtil.SpeedUtil import SpeedUtil
            SpeedUtil.multiprocess(24, self.wrapper, pred_fpath_tuple_list)
        else:
            for idx in range(len(self.pred_fpath_list)):
                pred_fpath = self.pred_fpath_list[idx]
                fit_fpath = self.fit_fpath_list[idx]
                stats_df, stats_df2, model_test_mingan, model_fit_mingan = self.single_backtest(pred_fpath, fit_fpath)
                stats_dict = calc_stats_df(stats_df, stats_df2, model_test_mingan, model_fit_mingan)
                FileUtil.save_dict2xls(stats_dict, os.path.dirname(pred_fpath) + '/', f'bt_result_{self.period}.xlsx', verbose=False)
        return stats_df, stats_df2, model_test_mingan, model_fit_mingan

if __name__ == '__main__':
    sbt = SimBackTest(pred_fpath_list=['/data/user/015614/Zeus/pred/JupiterZ/v2_0_7/fsrs_pct_AllXgbRegModel/model/period3/seed_0/20201201~20210531.csv'],
                      fit_fpath_list=['/data/user/015614/Zeus/pred/JupiterZ/v2_0_7/fsrs_pct_AllXgbRegModel/model/period3/seed_0/20210501~20210531.csv'],
                      date_dict=DATE_CONFIG['period2'],
                      attend_ratio_range=(20, 50),
                      save_flag=True,
                      multi_attend=True)
    stats_df, stats_df2, model_test_mingan, model_fit_mingan = sbt.start_backtest(multi=False)