from multifactor.IO import IO
import pandas as pd

pd.set_option('max_columns', 200)

import pandas as pd
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime
from multifactor.IO import IO

import warnings

warnings.filterwarnings('ignore')


class SIF_Factor_Test:
    def __init__(self, factor, retdf, factor_name, layers=4, threshold=0,
                 signal_lims=(-1, 1), self_corr_minute=5, save_image=True, show_image=True,
                 starttime=20160101, endtime=20220101, savepath='/data/user/015626/data/share/factor/factor_test/'):
        factordf = factor.copy()
        returndf = retdf.copy()
        factor_cols = factordf.columns.tolist()
        return_cols = returndf.columns.tolist()
        assert (set(factor_cols) == set(return_cols)), 'factordf is mismatching with returndf'
        new_factor_cols = [x + '_factor' for x in factor_cols]
        new_return_cols = [x + '_return' for x in return_cols]
        factordf.columns = new_factor_cols
        returndf.columns = new_return_cols

        df = factordf.join(returndf, how='inner')
        idx = df.index
        t1 = df.loc[(idx.hour == 9) & (idx.minute >= 35)]
        t2 = df.loc[(idx.hour >= 10) & (idx.hour <= 13)]
        t3 = df.loc[(idx.hour == 14) & (idx.minute <= 50)]
        t = t1.append(t2).append(t3)
        idx = t.index
        t.loc[(idx.hour == 14) & (idx.minute == 50), new_factor_cols] = 0
        t = t.sort_index()

        self.df = t
        self.cols = factor_cols
        self.factor_name = factor_name
        self.layers = layers
        if threshold > 0:
            self.threshold = threshold
        else:
            self.threshold = (max(signal_lims) - min(signal_lims)) / layers

        self.signal_lims = signal_lims
        self.self_corr_minute = self_corr_minute
        self.save_image = save_image
        self.show_image = show_image
        self.savepath = savepath
        if not os.path.exists(savepath):
            os.makedirs(savepath)

    def layer_chopper(self, ps_raw, layers, rank=True):
        # return pd.Series with categorical tags representing bins to which raw data has been assigned
        # use rank to ensure that each bin contains equal numbers of samples at best situation
        if isinstance(layers, int):
            _labels = range(layers)
        else:
            _labels = range(len(layers) - 1)
        if rank:
            return pd.cut(ps_raw.rank(), layers, retbins=False, labels=_labels)
        else:
            return pd.cut(ps_raw, layers, retbins=False, labels=_labels)

    def ts_segment_test(self, ps_raw, ps_return, layer_lims=None, normalize=False, return_segment_time_series=False,
                        **kwargs):

        assert isinstance(ps_raw, pd.Series)
        assert isinstance(ps_return, pd.Series)
        if layer_lims is not None:
            _up, _down = max(layer_lims), min(layer_lims)
            bins = [i for i in np.arange(_down, _up, (_up - _down) / self.layers)]
            bins[0] = -np.inf
            bins.append(np.inf)
            ps_bin = self.layer_chopper(ps_raw, layers=bins, rank=False)
        else:
            ps_bin = self.layer_chopper(ps_raw, layers=self.layers, rank=False)
        ps_bin.name = 'bins'
        ps_return.name = ps_return.name if ps_return.name is not None else 'return'
        _magic = pd.DataFrame(ps_bin).merge(pd.DataFrame(ps_return), how='left', left_index=True,
                                            right_index=True).dropna()
        if not return_segment_time_series:
            clist = _magic.columns.to_list()
            _magic[clist[-1]] = _magic[clist[-1]] + 1
            pd_res = _magic.groupby('bins').prod() - 1
            pd_res.index = ['Q' + str(int(col)) for col in pd_res.index]
            _magic[clist[-1]] = _magic[clist[-1]] - 1
            return pd_res, _magic
        else:
            segment_dict = dict()
            for nbin, group in _magic.groupby('bins'):
                _ = group[ps_return.name]
                _.name = 'Q' + str(nbin)
                segment_dict[_.name] = _
            return segment_dict

    def signal_reshaper(self, signals, print_stats=True):
        signal_lims = self.signal_lims
        assert isinstance(signals, pd.Series)
        assert isinstance(signal_lims, tuple)
        assert 0 < self.threshold < 1
        signals = signals.copy()
        signals.index.name = 'dt'
        signals.name = 'signals'
        # signal_mean = np.mean(signal_lims)
        # signal_amp = (max(signal_lims) - min(signal_lims)) / 2
        # signals = (signals - signal_mean) / signal_amp
        signals.loc[signals >= self.threshold] = self.threshold
        signals.loc[signals <= -self.threshold] = -self.threshold
        signals.loc[(signals < self.threshold) & (signals > - self.threshold)] = 0
        signals = signals / self.threshold
        #     signals = signal_filter(signals, smooth_period)
        # if print_stats:
        # print(pd.Series(self.signal_stats(signals)))
        return signals

    def signal_stats(self, sig):
        stats = dict()
        assert isinstance(sig, pd.Series)
        sig = sig.fillna(0)
        assert np.all([item in [-1, 0, 1] for item in sig.unique()])
        flag = sig * sig.shift(-1)
        sig.name = 'sig'
        flag.name = 'flag'
        data = pd.DataFrame(sig).merge(pd.DataFrame(flag), how='left', left_index=True, right_index=True)
        stats['invalid_deal_num'] = (flag == -1).sum()
        stats['long_deal_num'] = ((data['sig'] == 1) & (data['flag'] != 1)).sum()
        stats['short_deal_num'] = ((data['sig'] == -1) & (data['flag'] != 1)).sum()
        stats['long_num'] = (sig == 1).sum()
        stats['short_num'] = (sig == -1).sum()
        stats['avg_long_bars'] = stats['long_num'] / stats['long_deal_num']
        stats['avg_short_bars'] = stats['short_num'] / stats['short_deal_num']
        return stats

    def draw_result(self):
        total_dict = {}

        maxQ = self.layers - 1
        df_copy = self.df.copy()
        for col in self.cols:
            ps_raw = df_copy[col + '_factor']
            ps_return = df_copy[col + '_return']

            IC = round(ps_raw.corr(ps_return), 3)
            self_corr = round(ps_raw.corr(ps_raw.shift(self.self_corr_minute)), 3)

            pd_res, magic = self.ts_segment_test(ps_raw, ps_return)

            # 计算每组占据多长时间
            Q_counts = magic.bins.value_counts().to_frame().sort_index().reset_index()
            Q_counts['Q'] = Q_counts['index'].apply(lambda x: 'Q' + str(int(x)))
            Q_counts = Q_counts.drop('index', axis=1).set_index('Q')

            c = magic[(magic.bins == 0) | (magic.bins == maxQ)]
            c.loc[c.bins == 0, col + '_return'] *= -1

            c[col + '_return'] = c[col + '_return'] + 1

            sharpe = c[['bins', col + '_return']].reset_index()
            sharpe['date'] = sharpe.dt.apply(lambda x: x.date())

            sharpedailyreturn = sharpe.groupby('date')[col + '_return'].prod().to_frame()
            sharpedailyreturn[col + '_return'] = sharpedailyreturn[col + '_return'] - 1
            sharpe_ratio = round(
                sharpedailyreturn[col + '_return'].mean() / sharpedailyreturn[col + '_return'].std() * np.sqrt(252), 3)

            stats = self.signal_stats(self.signal_reshaper(ps_raw))

            long_deal_num = stats['long_deal_num']
            short_deal_num = stats['short_deal_num']
            rp_long = (magic[col + '_return'][magic['bins'] == maxQ] + 1).prod()
            rp_short = (magic[col + '_return'][magic['bins'] == 0] + 1).prod() * -1
            rp_per_deal_long = round(rp_long / long_deal_num, 3)
            rp_per_deal_short = round(rp_short / short_deal_num, 3)
            rp_per_deal = round((rp_long * rp_short) / (long_deal_num + short_deal_num), 3)

            # 累计盈利点数，与扣费后盈利点数
            cumualtive_long_short_return = round(rp_long * rp_short, 3)

            stats['rp_per_deal'] = rp_per_deal
            stats['rp_per_deal_long'] = rp_per_deal_long
            stats['rp_per_deal_short'] = rp_per_deal_short
            stats['IC-1min'] = IC
            stats['self_corr-shift(5)'] = self_corr
            stats['sharpe_Q' + str(maxQ) + '-Q0'] = sharpe_ratio

            stats['pd_res'] = pd_res
            stats['Q_counts'] = Q_counts
            stats['daily_return'] = sharpe

            total_dict[col] = stats

        colnum = len(self.cols)
        Q_counts = pd.DataFrame(np.zeros_like(Q_counts), index=Q_counts.index, columns=Q_counts.columns)

        IC = 0
        self_corr = 0
        sharpe_ratio = 0
        avg_long_bars = 0
        avg_short_bars = 0
        invalid_deal_num = 0
        long_deal_num = 0
        long_num = 0
        short_deal_num = 0
        short_num = 0

        pd_res = pd.DataFrame()
        for col in self.cols:
            if len(pd_res) == 0:
                pd_res = total_dict[col]['pd_res']
            else:
                pd_res = pd_res.join(total_dict[col]['pd_res'])

            Q_counts += total_dict[col]['Q_counts']
            IC += total_dict[col]['IC-1min']
            self_corr += total_dict[col]['self_corr-shift(5)']
            sharpe_ratio += total_dict[col]['sharpe_Q' + str(maxQ) + '-Q0']
            avg_long_bars += total_dict[col]['avg_long_bars']
            avg_short_bars += total_dict[col]['avg_short_bars']
            invalid_deal_num += total_dict[col]['invalid_deal_num']
            long_deal_num += total_dict[col]['long_deal_num']
            long_num += total_dict[col]['long_num']
            short_deal_num += total_dict[col]['short_deal_num']
            short_num += total_dict[col]['short_num']

        pd_res['return_mean'] = pd_res.mean(axis=1)
        print(pd_res)
        Q_counts = Q_counts / colnum
        IC = IC / colnum
        self_corr = self_corr / colnum
        sharpe_ratio = sharpe_ratio / colnum
        avg_long_bars = avg_long_bars / colnum
        avg_short_bars = avg_short_bars / colnum
        invalid_deal_num = invalid_deal_num / colnum
        long_deal_num = long_deal_num / colnum
        long_num = long_num / colnum
        short_deal_num = short_deal_num / colnum
        short_num = short_num / colnum

        # 计算每日收益均值 分为多空 多 空
        long_short_daily_return = pd.DataFrame()
        long_daily_return = pd.DataFrame()
        short_daily_return = pd.DataFrame()
        for col in self.cols:
            daily_return = total_dict[col]['daily_return']
            daily_return_date = daily_return.groupby('date')[col + '_return'].prod().to_frame()
            long_short_daily_return = long_short_daily_return.join(daily_return_date, how='outer')

            long_daily_return2 = daily_return[daily_return.bins == maxQ]
            long_daily_return2 = long_daily_return2.groupby('date')[col + '_return'].prod().to_frame()
            long_daily_return = long_daily_return.join(long_daily_return2, how='outer')

            short_daily_return2 = daily_return[daily_return.bins == 0]
            short_daily_return2 = short_daily_return2.groupby('date')[col + '_return'].prod().to_frame()
            #             short_daily_return2[col + '_return'] = short_daily_return2[col + '_return'] * -1
            short_daily_return = short_daily_return.join(short_daily_return2, how='outer')

        long_short_daily_return = long_short_daily_return.fillna(1)
        long_daily_return = long_daily_return.fillna(1)
        short_daily_return = short_daily_return.fillna(1)

        long_short_daily_return['long_short_daily_return_mean'] = long_short_daily_return.mean(axis=1)
        long_daily_return['long_daily_return_mean'] = long_daily_return.mean(axis=1)
        short_daily_return['short_daily_return_mean'] = short_daily_return.mean(axis=1)

        long_short_daily_return['cumprod_return'] = long_short_daily_return[
                                                        'long_short_daily_return_mean'].cumprod() - 1
        long_daily_return['cumprod_return'] = long_daily_return['long_daily_return_mean'].cumprod() - 1
        short_daily_return['cumprod_return'] = 1 - short_daily_return['short_daily_return_mean'].cumprod()

        final_long_short_return = long_short_daily_return.iloc[-1]['cumprod_return']
        final_long_return = long_daily_return.iloc[-1]['cumprod_return']
        final_short_return = short_daily_return.iloc[-1]['cumprod_return']

        fig = plt.figure(figsize=(14, 25))

        ax1 = fig.add_subplot(5, 1, 1)
        ax1.spines['top'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)

        plt.text(0.2, 1.2, self.factor_name + ' factor report', fontsize=28)
        timelist = self.df.index.tolist()
        plt.text(0.2, 1.1, 'longshort threshold: ' + str(self.threshold), fontsize=14)
        plt.text(0.2, 1.0,
                 'time period: ' + str(timelist[0].date()).replace('-', '') + ' - ' + str(timelist[-1].date()).replace(
                     '-', ''), fontsize=14)
        plt.text(0.2, 0.9, 'IC-1min: ' + str(round(IC, 3)), fontsize=14)
        plt.text(0.2, 0.8, 'self_corr-shift(5): ' + str(round(self_corr, 3)), fontsize=14)
        plt.text(0.2, 0.7, 'sharpe_Q' + str(maxQ) + '-Q0: ' + str(round(sharpe_ratio, 3)), fontsize=14)
        plt.text(0.2, 0.6, 'avg_long_bars: ' + str(round(avg_long_bars, 2)), fontsize=14)
        plt.text(0.2, 0.5, 'avg_short_bars: ' + str(round(avg_short_bars, 2)), fontsize=14)
        plt.text(0.2, 0.4, 'invalid_deal_num: ' + str(int(invalid_deal_num)), fontsize=14)
        plt.text(0.2, 0.3, 'long_deal_num: ' + str(int(long_deal_num)), fontsize=14)
        plt.text(0.2, 0.2, 'long_num: ' + str(int(long_num)), fontsize=14)
        plt.text(0.2, 0.1, 'short_deal_num: ' + str(int(short_deal_num)), fontsize=14)
        plt.text(0.2, 0, 'short_num: ' + str(int(short_num)), fontsize=14)

        #         plt.text(0.6,0.9,'skew: ' + str(round(self.df['raw'].skew(), 3)),fontsize=14)
        #         plt.text(0.6,0.8,'kurt: ' + str(round(self.df['raw'].kurt(), 3)),fontsize=14)

        #         plt.text(0.6,0.6,'return_befor_fee: ' + str(cumualtive_long_short_point),fontsize=14)

        plt.text(0.6, 0.4, 'final_long_short_return: ' + str(round(final_long_short_return * 100, 1)) + '%', fontsize=14)
        plt.text(0.6, 0.3, 'final_long_return: ' + str(round(final_long_return * 100, 1)) + '%', fontsize=14)
        plt.text(0.6, 0.2, 'final_short_return: ' + str(round(final_short_return * 100, 1)) + '%', fontsize=14)

        plt.xticks([])  # 去掉x轴
        plt.yticks([])  # 去掉y轴

        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：分组收益
        ax1 = fig.add_subplot(5, 2, 3)
        xlist = pd_res.index.tolist()
        ylist = pd_res['return_mean'].tolist()
        ax1.bar(np.arange(len(xlist)), ylist, color='dodgerblue')
        ax1.set_xticks(np.arange(len(xlist)))
        ax1.set_xticklabels(xlist)
        plt.xlabel('Segment', fontsize='medium')
        plt.ylabel('Mean Return', fontsize='medium')
        plt.title(self.factor_name + ' Segment Mean Return', fontsize='large')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：每组时间
        ax1 = fig.add_subplot(5, 2, 4)
        xlist = Q_counts.index.tolist()
        ylist = Q_counts[Q_counts.columns.tolist()[0]].tolist()
        ax1.bar(np.arange(len(xlist)), ylist, color='dodgerblue')
        ax1.set_xticks(np.arange(len(xlist)))
        ax1.set_xticklabels(xlist)
        plt.xlabel('Segment', fontsize='medium')
        plt.ylabel('Minutes', fontsize='medium')
        plt.title(self.factor_name + ' Segment Period', fontsize='large')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：多仓收益曲线
        ax2 = fig.add_subplot(5, 2, 5)
        ax2.plot(long_daily_return['cumprod_return'])
        plt.title(self.factor_name + ' Long Cumulative Return', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Return', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：空仓收益曲线
        ax2 = fig.add_subplot(5, 2, 6)
        ax2.plot(short_daily_return['cumprod_return'])
        plt.title(self.factor_name + ' Short Cumulative Return', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Return', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：多空收益曲线
        ax2 = fig.add_subplot(5, 1, 4)
        ax2.plot(long_short_daily_return['cumprod_return'])
        plt.title(self.factor_name + ' Long-Short Cumulative Return', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Return', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：因子值分布图
        histdf = pd.DataFrame()
        for col in self.cols:
            if len(histdf) == 0:
                histdf = df_copy[col + '_factor']
            else:
                histdf = histdf.append(df_copy[col + '_factor'])
        ax4 = fig.add_subplot(5, 1, 5)
        ax4.hist(histdf.dropna(), bins=100)
        plt.title(self.factor_name + ' hist', fontsize='large')
        plt.xlabel('Factor value', fontsize='medium')
        plt.ylabel('Num', fontsize='medium')
        plt.subplots_adjust(hspace=0.3)
        if self.show_image:
            plt.show()
        if self.save_image:
            plt.savefig(os.path.join(self.savepath, self.factor_name + '.png'), format='png')  # 存储图片

        plt.close()
        return stats

factorpath = '/data/user/015626/data/share/factor/prod/group_factor/aa.h5'
factor1 = pd.read_hdf('/data/user/012245/factors_ts/prod/futures/IC.CFE/S1/fresh/fct_0d627f0ffd3f261baf4ed2b6c5e6f6f231247cbf2045fa0dce1c8103553317b3.h5')
factor2 = pd.read_hdf('/data/user/012245/factors_ts/prod/futures/IF.CFE/S1/fresh/fct_02a8e3df4297a04ee5870b061a1c07ca637e8e01204c7ac78556f4e0cd66221a.h5')
factor3 = pd.read_hdf('/data/user/012245/factors_ts/prod/futures/IH.CFE/S1/fresh/fct_2a35d3b7bf0a5774331e86099ac77abb80a694c48ec12032d5f6bbea5284bd98.h5')

factor1 = factor1.xs('IC.CFE',level = 1)
factor2 = factor2.xs('IF.CFE',level = 1)
factor3 = factor3.xs('IH.CFE',level = 1)

factor1 = factor1 * 2 - 1
factor2 = factor2 * 2 - 1
factor3 = factor3 * 2 - 1

factor = factor1.join(factor2).join(factor3)

factor.columns = ['IC.CFE','IF.CFE', 'IH.CFE']

origindata = IO.read_data([20120101, 20200701], columns = ['close'], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/MINUTE/MAIN/MD_CHINA_FUTURES_MINUTE_MAIN.h5')
icreturn = origindata.xs('IC.CFE', level = 1)
icreturn['return_points'] = icreturn['close'].shift(-2) / icreturn['close'].shift(-1) - 1
icreturn = icreturn[['return_points']]


ifreturn = origindata.xs('IF.CFE', level = 1)
ifreturn['return_points'] = ifreturn['close'].shift(-2) / ifreturn['close'].shift(-1) - 1
ifreturn = ifreturn[['return_points']]


ihreturn = origindata.xs('IH.CFE', level = 1)
ihreturn['return_points'] = ihreturn['close'].shift(-2) / ihreturn['close'].shift(-1) - 1
ihreturn = ihreturn[['return_points']]

icreturn.columns = ['IC.CFE']
ifreturn.columns = ['IF.CFE']
ihreturn.columns = ['IH.CFE']

returndf = icreturn.join(ifreturn).join(ihreturn)

sif = SIF_Factor_Test(factor, returndf, 'test', save_image=False)
a = sif.draw_result()