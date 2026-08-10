import pandas as pd

pd.set_option('max_columns', 200)
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
from multifactor.IO import IO
import multifactor.utility.dt as udt

import warnings

warnings.filterwarnings('ignore')


class SIF_Factor_Test:
    def __init__(self, df, factor_name, future_kind='contract_main', factor_kind='1min', layers=4,
                 return_price_kind='vwap', ticker='IC.CFE',
                 signal_lims=(-1, 1), time_range=[935, 1450],
                 save_image=True, show_image=True, starttime=20160101, endtime=20220101,
                 savepath='/data/user/015626/data/share/factor/factor_test/'):
        """
        :param df:因子单列，也可以双列，但是第一列需为因子值，第二列为return，这样此程序就不会再读取return数据，可以节省时间
        :param factor_name: 因子名称
        :param future_kind: 期货数据种类，'contract_00'表示近月连续, 'contract_main'表示主力连续,
        :param factor_kind: 因子品种，1min还是5s, 5s时futurekind只能是'conntract_main'
        :param layers: 分层
        :param fee: 手续费
        :param return_price_kind: 使用哪一列计算return，比如说'vwap'，或者'twap'，默认为'vwap'
        :param ticker: 测试的品种
        :param signal_lims: 因子值范围，需要以0左右对称
        :param time_range: 筛选哪个时间段进行测试，最多可支持2个用来筛选的时间段，如[[935,1100],[1330,1450]]
        :param save_image: 是否需要保存图片
        :param show_image: 是否需要展示图片
        :param starttime: 读取数据开始时间
        :param endtime: 读取数据结束时间
        :param savepath: 图片保存路径
        """
        assert (-1 * min(signal_lims)) == max(signal_lims), 'signal_lims must be central symmetry'
        assert factor_kind in ['1min', '5s'], 'factor_kind must be 1min or 5s'
        self.factor_kind = factor_kind
        self.future_kind = future_kind
        self.ticker = ticker
        if len(df.columns.tolist()) == 1:
            h5path = '/data/user/015626/data/share/MD/CHINA_FUTURES/'
            freq = 'MINUTE'
            if self.future_kind == 'contract_main':
                if self.factor_kind == '1min':
                    if return_price_kind == 'twap':
                        dataname = 'MD_STOCK_INDEX_FUTURES_TICK_TO_MINUTE.h5'
                    else:
                        dataname = 'MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5'
                elif self.factor_kind == '5s':
                    freq = '5s'
                    dataname = 'MD_STOCK_INDEX_FUTURES_5S_MAIN.h5'
            elif self.future_kind == 'contract_00':
                dataname = 'MD_STOCK_INDEX_FUTURES_RECENT_MONTH.h5'
            origindata = IO.read_data([starttime, endtime], columns=[return_price_kind],
                                      alt=os.path.join(h5path, freq, dataname))
            origindata = origindata.xs(self.ticker, level=1)
            origindata['ret'] = origindata[return_price_kind].shift(-2) / origindata[return_price_kind].shift(-1) - 1
            origindata = origindata[['ret']]
            df = df.join(origindata, how='inner')

        df.columns = ['raw', 'ret']

        self.df = self.slice_by_minute(df, time_range)
        self.factor_name = factor_name

        self.layers = layers
        # self.fee = fee  # 单次开平仓总成本
        self.threshold = max(signal_lims) - 2 * max(signal_lims) / layers
        self.signal_lims = signal_lims
        self.save_image = save_image
        self.show_image = show_image
        self.savepath = savepath
        if self.save_image:
            if not os.path.exists(savepath):
                os.makedirs(savepath)

    def slice_by_minute(self, dat, slice_range=[935, 1450]):
        if isinstance(dat.index, pd.MultiIndex):
            index_list = dat.index.get_level_values(0)
        else:
            index_list = dat.index
        hour_list = ['%s' % (i) if i > 9 else '0%s' % (i) for i in index_list.hour]
        minute_list = ['%s' % (i) if i > 9 else '0%s' % (i) for i in index_list.minute]
        hour_minute_list = [int('%s%s' % (i, j)) for i, j in zip(hour_list, minute_list)]
        if isinstance(slice_range[0], list):
            range_a = slice_range[0]
            range_b = slice_range[1]
            range_a.sort()
            range_b.sort()
            finaltime = range_b[-1]
            slice_mask = [(i <= range_a[-1] and i >= range_a[0]) or (i <= range_b[-1] and i >= range_b[0]) for i in
                          hour_minute_list]
        else:
            slice_range.sort()
            finaltime = slice_range[-1]
            slice_mask = [i <= slice_range[-1] and i >= slice_range[0] for i in hour_minute_list]
        dat_slice = dat[slice_mask].sort_index()
        finalhour = finaltime // 100
        finalminute = finaltime % 100

        idx = dat_slice.index
        dat_slice.loc[(idx.hour == finalhour) & (idx.minute == finalminute), 'raw'] = 0
        dat_slice = dat_slice.sort_index()
        return dat_slice

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

    def ts_segment_test(self, ps_raw, ps_return, layers, layer_lims=None, normalize=False,
                        return_segment_time_series=False,
                        **kwargs):

        assert isinstance(ps_raw, pd.Series)
        assert isinstance(ps_return, pd.Series)
        if layer_lims is not None:
            _up, _down = max(layer_lims), min(layer_lims)
            bins = [i for i in np.arange(_down, _up, (_up - _down) / layers)]
            bins[0] = -np.inf
            bins.append(np.inf)
            ps_bin = self.layer_chopper(ps_raw, layers=bins, rank=False)
        else:
            ps_bin = self.layer_chopper(ps_raw, layers=layers, rank=False)
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
        signals.loc[signals >= self.threshold] = self.threshold
        signals.loc[signals <= -self.threshold] = -self.threshold
        signals.loc[(signals < self.threshold) & (signals > - self.threshold)] = 0
        signals = signals / self.threshold
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
        stats['avg_long_bars'] = round(stats['long_num'] / stats['long_deal_num'], 2)
        stats['avg_short_bars'] = round(stats['short_num'] / stats['short_deal_num'], 2)
        return stats

    def get_max_drawdone(self, pnl):
        pnl['max2here'] = pnl['ret_cumprod'].expanding().max()
        pnl['dd2here'] = pnl['ret_cumprod'] - pnl['max2here']
        return pnl['dd2here'].min()

    def draw_result(self):
        IC = round(self.df['raw'].corr(self.df['ret']), 5)
        self_corr = round(self.df['raw'].corr(self.df['raw'].shift(5)), 3)

        df_copy = self.df.copy()
        ps_raw = df_copy['raw']
        ps_return = df_copy['ret']

        pd_res, magic = self.ts_segment_test(ps_raw, ps_return, layers=self.layers, layer_lims=self.signal_lims)
        pd_res30, magic30 = self.ts_segment_test(ps_raw, ps_return, layers=30, layer_lims=self.signal_lims)
        # 计算每组占据多长时间
        Q_counts = magic.bins.value_counts().to_frame().sort_index().reset_index()
        Q_counts['Q'] = Q_counts['index'].apply(lambda x: 'Q' + str(int(x)))
        Q_counts = Q_counts.drop('index', axis=1).set_index('Q')

        maxQ = self.layers - 1
        c = magic[(magic.bins == 0) | (magic.bins == maxQ)]
        c.loc[c.bins == 0, 'ret'] = 1 - c.loc[c.bins == 0, 'ret']
        c.loc[c.bins == maxQ, 'ret'] += 1

        c_long = c[c.bins == maxQ]
        c_short = c[c.bins == 0]
        c['ret_cumprod'] = c['ret'].cumprod()
        c_long['ret_cumprod'] = c_long['ret'].cumprod()
        c_short['ret_cumprod'] = c_short['ret'].cumprod()
        long_short_mdd = self.get_max_drawdone(c)
        long_mdd = self.get_max_drawdone(c_long)
        short_mdd = self.get_max_drawdone(c_short)

        sharpe = c['ret'].to_frame().reset_index()
        sharpe['date'] = sharpe.dt.apply(lambda x: x.date())
        sharpedailyreturn = sharpe.groupby('date')['ret'].prod().to_frame()
        sharpedailyreturn['ret'] -= 1
        sharpe_ratio = round(
            sharpedailyreturn['ret'].mean() / sharpedailyreturn['ret'].std() * np.sqrt(242), 3)

        stats = self.signal_stats(self.signal_reshaper(ps_raw))

        long_deal_num = stats['long_deal_num']
        short_deal_num = stats['short_deal_num']
        ret_long = c_long.iloc[-1]['ret_cumprod'] - 1 if len(c_long) > 0 else np.nan
        ret_short = c_short.iloc[-1]['ret_cumprod'] - 1 if len(c_short) > 0 else np.nan
        ret_per_deal_long = round(ret_long / long_deal_num, 6)
        ret_per_deal_short = round(ret_short / short_deal_num, 6)

        # 累计盈利点数，与扣费后盈利点数
        cumualtive_long_short_ret = round(c.iloc[-1]['ret_cumprod'] - 1, 6)
        ret_per_deal = round(cumualtive_long_short_ret / (long_deal_num + short_deal_num), 6)
        # after_fee_cumualtive_long_short_point = cumualtive_long_short_point - (
        #         long_deal_num + short_deal_num) * self.fee

        stats['ret_long_short'] = round(cumualtive_long_short_ret, 3)
        stats['ret_long'] = round(ret_long, 3)
        stats['ret_short'] = round(ret_short, 3)
        stats['ret_per_deal'] = ret_per_deal
        stats['ret_per_deal_long'] = ret_per_deal_long
        stats['ret_per_deal_short'] = ret_per_deal_short
        stats['IC-1min'] = IC
        stats['self_corr-shift(5)'] = self_corr
        stats['sharpe_Q' + str(maxQ) + '-Q0'] = sharpe_ratio
        stats['long_short_mdd'] = round(long_short_mdd, 4)
        stats['long_mdd'] = round(long_mdd, 4)
        stats['short_mdd'] = round(short_mdd, 4)

        fig = plt.figure(figsize=(14, 30))

        ax1 = fig.add_subplot(6, 1, 1)
        ax1.spines['top'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)

        plt.text(0.2, 1.2, self.factor_name + ' factor report', fontsize=28)
        timelist = self.df.index.tolist()
        datelist = [x.date() for x in timelist]
        datenum = len(set(datelist))
        plt.text(0.2, 1.1, 'longshort threshold: ' + str(self.threshold), fontsize=14)
        plt.text(0.2, 1.0,
                 'time period: ' + str(timelist[0].date()).replace('-', '') + ' - ' + str(timelist[-1].date()).replace(
                     '-', '') + '    total ' + str(datenum) + ' days', fontsize=14)
        plt.text(0.2, 0.9, 'IC-1min: ' + str(IC), fontsize=14)
        plt.text(0.2, 0.8, 'self_corr-shift(5): ' + str(self_corr), fontsize=14)
        plt.text(0.2, 0.7, 'sharpe_Q' + str(maxQ) + '-Q0: ' + str(sharpe_ratio), fontsize=14)
        if self.factor_kind == '1min':
            plt.text(0.2, 0.6, 'avg_long_bars: ' + str(round(stats['avg_long_bars'], 2)) + ' mins', fontsize=14)
            plt.text(0.2, 0.5, 'avg_short_bars: ' + str(round(stats['avg_short_bars'], 2)) + ' mins', fontsize=14)
        elif self.factor_kind == '5s':
            plt.text(0.2, 0.6, 'avg_long_bars: ' + str(round(stats['avg_long_bars'] * 5 / 60, 2)) + ' mins',
                     fontsize=14)
            plt.text(0.2, 0.5, 'avg_short_bars: ' + str(round(stats['avg_short_bars'] * 5 / 60, 2)) + 'mins',
                     fontsize=14)
        plt.text(0.2, 0.3, 'long_deal_num: ' + str(stats['long_deal_num']), fontsize=14)
        plt.text(0.2, 0.2, 'long_num: ' + str(stats['long_num']), fontsize=14)
        plt.text(0.2, 0.1, 'short_deal_num: ' + str(stats['short_deal_num']), fontsize=14)
        plt.text(0.2, 0, 'short_num: ' + str(stats['short_num']), fontsize=14)

        dealnum_per_day = (stats['long_deal_num'] + stats['short_deal_num']) / datenum
        plt.text(0.2, 0.4, 'dealnum_per_day: ' + str(round(dealnum_per_day, 1)), fontsize=14)
        stats['dealnum_per_day'] = round(dealnum_per_day, 1)

        plt.text(0.6, 0.9, 'skew: ' + str(round(self.df['raw'].skew(), 3)), fontsize=14)
        plt.text(0.6, 0.8, 'kurt: ' + str(round(self.df['raw'].kurt(), 3)), fontsize=14)

        plt.text(0.6, 0.7, 'Ret_before_fee: ' + str(format(cumualtive_long_short_ret, '.1%')), fontsize=14)
        # if self.fee > 0:
        #     plt.text(0.6, 0.5, 'profit_after_fee: ' + str(after_fee_cumualtive_long_short_point), fontsize=14)

        plt.text(0.6, 0.5, 'ret_per_deal: ' + str(format(ret_per_deal, '.3%')), fontsize=14)
        plt.text(0.6, 0.4, 'ret_per_deal_long: ' + str(format(ret_per_deal_long, '.3%')), fontsize=14)
        plt.text(0.6, 0.3, 'ret_per_deal_short: ' + str(format(ret_per_deal_short, '.3%')), fontsize=14)
        plt.text(0.6, 0.2, 'long_short_mdd: ' + str(format(long_short_mdd, '.2%')), fontsize=14)
        plt.text(0.6, 0.1, 'long_mdd: ' + str(format(long_mdd, '.2%')), fontsize=14)
        plt.text(0.6, 0.0, 'short_mdd: ' + str(format(short_mdd, '.2%')), fontsize=14)

        # plt.text(0.6, 0, 'invalid_deal_num: ' + str(stats['invalid_deal_num']), fontsize=14)

        plt.xticks([])  # 去掉x轴
        plt.yticks([])  # 去掉y轴

        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：分组收益
        ax1 = fig.add_subplot(6, 2, 3)
        xlist = pd_res.index.tolist()
        ylist = pd_res['ret'].tolist()
        ax1.bar(np.arange(len(xlist)), ylist, color='dodgerblue')
        ax1.set_xticks(np.arange(len(xlist)))
        ax1.set_xticklabels(xlist)
        plt.xlabel('Segment', fontsize='medium')
        plt.ylabel('Return', fontsize='medium')
        plt.title(self.factor_name + ' Segment Return', fontsize='large')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：每组时间
        ax1 = fig.add_subplot(6, 2, 4)
        xlist = Q_counts.index.tolist()
        ylist = Q_counts[Q_counts.columns.tolist()[0]].tolist()
        ax1.bar(np.arange(len(xlist)), ylist, color='dodgerblue')
        ax1.set_xticks(np.arange(len(xlist)))
        ax1.set_xticklabels(xlist)
        plt.xlabel('Segment', fontsize='medium')
        plt.ylabel('Bars', fontsize='medium')
        plt.title(self.factor_name + ' Segment Period', fontsize='large')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：30分组收益
        ax30 = fig.add_subplot(6, 1, 3)
        xlist = pd_res30.index.tolist()
        ylist = pd_res30['ret'].tolist()
        ax30.bar(np.arange(len(xlist)), ylist, color='dodgerblue')
        ax30.set_xticks(np.arange(len(xlist)))
        ax30.set_xticklabels(xlist)
        plt.xlabel('Segment', fontsize='medium')
        plt.ylabel('Return', fontsize='medium')
        plt.title(self.factor_name + ' Segment_30 Return', fontsize='large')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：多仓收益曲线
        ax2 = fig.add_subplot(6, 2, 7)
        ax2.plot(c_long['ret_cumprod'] - 1)
        plt.title(self.factor_name + ' Long Cumulative Ret', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Ret', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：空仓收益曲线
        ax2 = fig.add_subplot(6, 2, 8)
        ax2.plot(1 - c_short['ret_cumprod'])
        plt.title(self.factor_name + ' Short Cumulative Ret', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Ret', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：多空收益曲线
        ax2 = fig.add_subplot(6, 1, 5)
        ax2.plot(c['ret_cumprod'] - 1)
        plt.title(self.factor_name + ' Long-Short Cumulative Ret', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Ret', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：因子值分布图
        ax4 = fig.add_subplot(6, 1, 6)
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
