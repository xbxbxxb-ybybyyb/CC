import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime
from multifactor.IO import IO
import warnings

warnings.filterwarnings('ignore')
pd.set_option('max_columns', 200)


class SIF_Factor_Test:
    def __init__(self, df, factor_name, layers=4, fee=0, ticker='IF.CFE', signal_lims=(-1, 1),
                 save_image=True, show_image=True, starttime=20160101, endtime=20220101,
                 savepath='/data/user/015626/data/share/factor/factor_test/'):
        assert (-1 * min(signal_lims)) == max(signal_lims)
        if len(df.columns.tolist()) == 1:
            origindata = IO.read_data([starttime, endtime], columns=['vwap'],
                                      alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5')
            origindata = origindata.xs(ticker, level=1)
            origindata['return_points'] = origindata['vwap'].shift(-2) - origindata['vwap'].shift(-1)
            origindata = origindata[['return_points']]
            df = df.join(origindata, how='inner')
        df.columns = ['raw', 'return_points']
        idx = df.index
        t1 = df.loc[(idx.hour == 9) & (idx.minute >= 35)]
        t2 = df.loc[(idx.hour == 10) | (idx.hour == 13)]
        t3 = df.loc[(idx.hour == 11) & (idx.minute < 30)]
        t4 = df.loc[(idx.hour == 14) & (idx.minute <= 50)]
        t = t1.append(t2).append(t3).append(t4)
        idx = t.index
        t.loc[(idx.hour == 14) & (idx.minute == 50), 'raw'] = 0
        t = t.sort_index()

        self.df = t
        self.factor_name = factor_name
        self.layers = layers
        self.fee = fee  # 单次开平仓总成本
        self.threshold = max(signal_lims) - 2 * max(signal_lims) / layers
        self.signal_lims = signal_lims
        self.save_image = save_image
        self.show_image = show_image
        self.savepath = savepath
        if self.save_image:
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
            pd_res = _magic.groupby('bins').mean()
            pd_res.index = ['Q' + str(int(col)) for col in pd_res.index]
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
        IC = round(self.df['raw'].corr(self.df['return_points']), 5)
        self_corr = round(self.df['raw'].corr(self.df['raw'].shift(5)), 3)

        df_copy = self.df.copy()
        ps_raw = df_copy['raw']
        ps_return = df_copy['return_points']

        pd_res, magic = self.ts_segment_test(ps_raw, ps_return, layer_lims=self.signal_lims)
        # 计算每组占据多长时间
        Q_counts = magic.bins.value_counts().to_frame().sort_index().reset_index()
        Q_counts['Q'] = Q_counts['index'].apply(lambda x: 'Q' + str(int(x)))
        Q_counts = Q_counts.drop('index', axis=1).set_index('Q')

        maxQ = self.layers - 1
        c = magic[(magic.bins == 0) | (magic.bins == maxQ)]
        # temp_c = c.groupby('bins').sum()
        # if temp_c.iloc[0, 0] > temp_c.loc[maxQ, 0]:
        #     c['bins'].cat.categories = [abs(i - maxQ) for i in c['bins'].cat.categories]
        c.loc[c.bins == 0, 'return_points'] *= -1

        sharpe = c['return_points'].to_frame().reset_index()
        sharpe['date'] = sharpe.dt.apply(lambda x: x.date())
        sharpedailyreturn = sharpe.groupby('date')['return_points'].sum().to_frame()
        sharpe_ratio = round(
            sharpedailyreturn['return_points'].mean() / sharpedailyreturn['return_points'].std() * np.sqrt(252), 3)

        stats = self.signal_stats(self.signal_reshaper(ps_raw))

        long_deal_num = stats['long_deal_num']
        short_deal_num = stats['short_deal_num']
        rp_long = magic['return_points'][magic['bins'] == maxQ].sum()
        rp_short = magic['return_points'][magic['bins'] == 0].sum() * -1
        rp_per_deal_long = round(rp_long / long_deal_num, 3)
        rp_per_deal_short = round(rp_short / short_deal_num, 3)
        rp_per_deal = round((rp_long + rp_short) / (long_deal_num + short_deal_num), 3)

        # 累计盈利点数，与扣费后盈利点数
        cumualtive_long_short_point = int(rp_long + rp_short)
        after_fee_cumualtive_long_short_point = cumualtive_long_short_point - (
                long_deal_num + short_deal_num) * self.fee

        stats['rp_per_deal'] = rp_per_deal
        stats['rp_per_deal_long'] = rp_per_deal_long
        stats['rp_per_deal_short'] = rp_per_deal_short
        stats['IC-1min'] = IC
        stats['self_corr-shift(5)'] = self_corr
        stats['sharpe_Q' + str(maxQ) + '-Q0'] = sharpe_ratio

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
        plt.text(0.2, 0.9, 'IC-1min: ' + str(IC), fontsize=14)
        plt.text(0.2, 0.8, 'self_corr-shift(5): ' + str(self_corr), fontsize=14)
        plt.text(0.2, 0.7, 'sharpe_Q' + str(maxQ) + '-Q0: ' + str(sharpe_ratio), fontsize=14)
        plt.text(0.2, 0.6, 'avg_long_bars: ' + str(round(stats['avg_long_bars'], 2)), fontsize=14)
        plt.text(0.2, 0.5, 'avg_short_bars: ' + str(round(stats['avg_short_bars'], 2)), fontsize=14)
        plt.text(0.2, 0.4, 'invalid_deal_num: ' + str(stats['invalid_deal_num']), fontsize=14)
        plt.text(0.2, 0.3, 'long_deal_num: ' + str(stats['long_deal_num']), fontsize=14)
        plt.text(0.2, 0.2, 'long_num: ' + str(stats['long_num']), fontsize=14)
        plt.text(0.2, 0.1, 'short_deal_num: ' + str(stats['short_deal_num']), fontsize=14)
        plt.text(0.2, 0, 'short_num: ' + str(stats['short_num']), fontsize=14)

        plt.text(0.6, 0.9, 'skew: ' + str(round(self.df['raw'].skew(), 3)), fontsize=14)
        plt.text(0.6, 0.8, 'kurt: ' + str(round(self.df['raw'].kurt(), 3)), fontsize=14)

        plt.text(0.6, 0.6, 'profit_befor_fee: ' + str(cumualtive_long_short_point), fontsize=14)
        if self.fee > 0:
            plt.text(0.6, 0.5, 'profit_after_fee: ' + str(after_fee_cumualtive_long_short_point), fontsize=14)

        plt.text(0.6, 0.4, 'rp_per_deal: ' + str(rp_per_deal), fontsize=14)
        plt.text(0.6, 0.3, 'rp_per_deal_long: ' + str(rp_per_deal_long), fontsize=14)
        plt.text(0.6, 0.2, 'rp_per_deal_short: ' + str(rp_per_deal_short), fontsize=14)

        plt.xticks([])  # 去掉x轴
        plt.yticks([])  # 去掉y轴

        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：分组收益
        ax1 = fig.add_subplot(5, 2, 3)
        xlist = pd_res.index.tolist()
        ylist = pd_res['return_points'].tolist()
        ax1.bar(np.arange(len(xlist)), ylist, color='dodgerblue')
        ax1.set_xticks(np.arange(len(xlist)))
        ax1.set_xticklabels(xlist)
        plt.xlabel('Segment', fontsize='medium')
        plt.ylabel('Return', fontsize='medium')
        plt.title(self.factor_name + ' Segment Return', fontsize='large')
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
        ax2.plot(magic['return_points'][magic['bins'] == maxQ].cumsum())
        plt.title(self.factor_name + ' Long Cumulative Points', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Points', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：空仓收益曲线
        ax2 = fig.add_subplot(5, 2, 6)
        ax2.plot(magic['return_points'][magic['bins'] == 0].cumsum())
        plt.title(self.factor_name + ' Short Cumulative Points', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Points', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：多空收益曲线
        ax2 = fig.add_subplot(5, 1, 4)
        ax2.plot(c['return_points'].cumsum())
        plt.title(self.factor_name + ' Long-Short Cumulative Points', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Points', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：因子值分布图
        ax4 = fig.add_subplot(5, 1, 5)
        ax4.hist(ps_raw.dropna(), bins=100)
        plt.title(self.factor_name + ' hist', fontsize='large')
        plt.xlabel('Factor value', fontsize='medium')
        plt.ylabel('Num', fontsize='medium')
        plt.subplots_adjust(hspace=0.3)
        if self.save_image:
            plt.savefig(os.path.join(self.savepath, self.factor_name + '.png'), format='png')  # 存储图片
        if self.show_image:
            plt.show()
        plt.close()
        return stats


# 检查因子是否符合入库条件
def check_factor_into_lib(factor, ticker='IF.CFE', start_time=20170101, end_time=20200101,
                          avg_bars_t=5,
                          rp_per_deal_t=0.5,
                          IC_t=0.005,
                          self_corr_t=0.75,
                          sharpe_outsample_t=0.4,
                          sharpe_insample_t=0.8,
                          corr_t=0.95,
                          factor_lib_path='/data/user/012398/data/alpha/CHINA_FUTURES/MINUTE/IF_prod/'):
    """
    :param factor: 因子dataframe, index为分钟, 列为因子值。如果批量测试的话，可以先将returnpoints设置为第二列。
    :param ticker: 因子对应品种
    :param start_time: 测试开始时间
    :param end_time: 测试结束时间, 因样本外测试标准制定使用的是2019年全年，所以开始结束时间最好包括2019年
    :param avg_bars_t: 平均持仓时间阈值
    :param rp_per_deal_t: 单笔收益阈值
    :param IC_t: IC阈值
    :param self_corr_t: 自相关性阈值
    :param sharpe_outsample_t: 样本外夏普率阈值
    :param sharpe_insample_t: 样本内夏普率阈值
    :param corr_t: 与因子库内因子最高相关性阈值
    :param factor_lib_path: 因子库路径
    :return: True为可以入库， False为不符合入库标准。
    """
    factor_name = factor.columns.tolist()[0]
    if len(factor.columns.tolist()) == 1:
        origindata = IO.read_data([start_time, end_time], columns=['vwap'],
                                  alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5')
        origindata = origindata.xs(ticker, level=1)
        origindata['return_points'] = origindata['vwap'].shift(-2) - origindata['vwap'].shift(-1)
        origindata = origindata[['return_points']]
        df = factor.join(origindata, how='inner')
        raw_factor = factor.copy()
    else:
        raw_factor = factor[factor_name].to_frame()
        df = factor.copy()

    # test insample
    df_full_history = df.copy()
    sif_full = SIF_Factor_Test(df_full_history, factor_name=factor_name, layers=4, save_image=False, show_image=False,
                               starttime=start_time, endtime=end_time)
    stats_full = sif_full.draw_result()
    avg_bars = (stats_full['avg_long_bars'] + stats_full['avg_short_bars']) / 2
    if (avg_bars < avg_bars_t) | (stats_full['rp_per_deal'] < rp_per_deal_t) | (stats_full['IC-1min'] < IC_t) \
            | (stats_full['self_corr-shift(5)'] < self_corr_t) | (stats_full['sharpe_Q3-Q0'] < sharpe_insample_t):
        # print('insample test results are not satisfiable')
        # print('insample test results are as follows')
        # print('avg_bars: ', avg_bars)
        # print('rp_per_deal: ', stats_full['rp_per_deal'])
        # print('IC: ', stats_full['IC-1min'])
        # print('self_corr-shift(5): ', stats_full['self_corr-shift(5)'])
        # print('sharpe_Q3-Q0: ', stats_full['sharpe_Q3-Q0'])
        return False

    # test outsample
    idx = df.index
    df_2019 = df.loc[idx.year == 2019]
    df_2019 = df_2019.sort_index()
    sif_2019 = SIF_Factor_Test(df_2019, factor_name=factor_name, layers=4, save_image=False, show_image=False)
    stats_2019 = sif_2019.draw_result()
    avg_bars = (stats_2019['avg_long_bars'] + stats_2019['avg_short_bars']) / 2
    if (avg_bars < avg_bars_t) | (stats_2019['rp_per_deal'] < rp_per_deal_t) | (stats_2019['IC-1min'] < IC_t) \
            | (stats_2019['self_corr-shift(5)'] < self_corr_t) | (stats_2019['sharpe_Q3-Q0'] < sharpe_outsample_t):
        # print('outsample test results are not satisfiable')
        # print('outsample test results are as follows')
        # print('avg_bars: ', avg_bars)
        # print('rp_per_deal: ', stats_2019['rp_per_deal'])
        # print('IC: ', stats_2019['IC-1min'])
        # print('self_corr-shift(5): ', stats_2019['self_corr-shift(5)'])
        # print('sharpe_Q3-Q0: ', stats_2019['sharpe_Q3-Q0'])
        return False

    # test corr with factorlib
    highcorrlist = []
    for x in os.listdir(factor_lib_path):
        if not x.endswith('h5'):
            continue
        f = IO.read_data([start_time, end_time], alt=os.path.join(factor_lib_path, x)).xs(ticker, level=1)
        newf = raw_factor.join(f, how='inner')
        corr = newf[x[:-3]].corr(newf[factor_name])
        if corr > corr_t:
            highcorrlist.append(x[:-3])
    if len(highcorrlist) > 0:
        print('factor is very relevant to those factors: ', highcorrlist)
        return False

    return True


# 检查因子是否符合入库条件
def check_factor_into_lib_no_corr(factor, ticker='IF.CFE', start_time=20170101, end_time=20200101,
                                  avg_bars_t=5,
                                  rp_per_deal_t=0.5,
                                  IC_t=0.005,
                                  self_corr_t=0.75,
                                  sharpe_outsample_t=0.4,
                                  sharpe_insample_t=0.8,
                                  corr_t=0.95,
                                  factor_lib_path='/data/user/012398/data/alpha/CHINA_FUTURES/MINUTE/IF_prod/'):
    """
    :param factor: 因子dataframe, index为分钟, 列为因子值。如果批量测试的话，可以先将returnpoints设置为第二列。
    :param ticker: 因子对应品种
    :param start_time: 测试开始时间
    :param end_time: 测试结束时间, 因样本外测试标准制定使用的是2019年全年，所以开始结束时间最好包括2019年
    :param avg_bars_t: 平均持仓时间阈值
    :param rp_per_deal_t: 单笔收益阈值
    :param IC_t: IC阈值
    :param self_corr_t: 自相关性阈值
    :param sharpe_outsample_t: 样本外夏普率阈值
    :param sharpe_insample_t: 样本内夏普率阈值
    :param corr_t: 与因子库内因子最高相关性阈值
    :param factor_lib_path: 因子库路径
    :return: True为可以入库， False为不符合入库标准。
    """
    factor_name = factor.columns.tolist()[0]
    if len(factor.columns.tolist()) == 1:
        origindata = IO.read_data([start_time, end_time], columns=['vwap'],
                                  alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5')
        origindata = origindata.xs(ticker, level=1)
        origindata['return_points'] = origindata['vwap'].shift(-2) - origindata['vwap'].shift(-1)
        origindata = origindata[['return_points']]
        df = factor.join(origindata, how='inner')
        raw_factor = factor.copy()
    else:
        raw_factor = factor[factor_name].to_frame()
        df = factor.copy()

    # test insample
    df_full_history = df.copy()
    sif_full = SIF_Factor_Test(df_full_history, factor_name=factor_name, layers=4, save_image=False, show_image=False,
                               starttime=start_time, endtime=end_time)
    stats_full = sif_full.draw_result()
    avg_bars = (stats_full['avg_long_bars'] + stats_full['avg_short_bars']) / 2
    if (avg_bars < avg_bars_t) | (stats_full['rp_per_deal'] < rp_per_deal_t) | (stats_full['IC-1min'] < IC_t) \
            | (stats_full['self_corr-shift(5)'] < self_corr_t) | (stats_full['sharpe_Q3-Q0'] < sharpe_insample_t):
        # print('insample test results are not satisfiable')
        # print('insample test results are as follows')
        # print('avg_bars: ', avg_bars)
        # print('rp_per_deal: ', stats_full['rp_per_deal'])
        # print('IC: ', stats_full['IC-1min'])
        # print('self_corr-shift(5): ', stats_full['self_corr-shift(5)'])
        # print('sharpe_Q3-Q0: ', stats_full['sharpe_Q3-Q0'])
        return False

    # test outsample
    idx = df.index
    df_2019 = df.loc[idx.year == 2019]
    df_2019 = df_2019.sort_index()
    sif_2019 = SIF_Factor_Test(df_2019, factor_name=factor_name, layers=4, save_image=False, show_image=False)
    stats_2019 = sif_2019.draw_result()
    avg_bars = (stats_2019['avg_long_bars'] + stats_2019['avg_short_bars']) / 2
    if (avg_bars < avg_bars_t) | (stats_2019['rp_per_deal'] < rp_per_deal_t) | (stats_2019['IC-1min'] < IC_t) \
            | (stats_2019['self_corr-shift(5)'] < self_corr_t) | (stats_2019['sharpe_Q3-Q0'] < sharpe_outsample_t):
        # print('outsample test results are not satisfiable')
        # print('outsample test results are as follows')
        # print('avg_bars: ', avg_bars)
        # print('rp_per_deal: ', stats_2019['rp_per_deal'])
        # print('IC: ', stats_2019['IC-1min'])
        # print('self_corr-shift(5): ', stats_2019['self_corr-shift(5)'])
        # print('sharpe_Q3-Q0: ', stats_2019['sharpe_Q3-Q0'])
        return False

    # # test corr with factorlib
    # highcorrlist = []
    # for x in os.listdir(factor_lib_path):
    #     if not x.endswith('h5'):
    #         continue
    #     f = IO.read_data([start_time, end_time], alt=os.path.join(factor_lib_path, x)).xs(ticker, level=1)
    #     newf = raw_factor.join(f, how='inner')
    #     corr = newf[x[:-3]].corr(newf[factor_name])
    #     if corr > corr_t:
    #         highcorrlist.append(x[:-3])
    # if len(highcorrlist) > 0:
    #     print('factor is very relevant to those factors: ', highcorrlist)
    #     return False

    return True
