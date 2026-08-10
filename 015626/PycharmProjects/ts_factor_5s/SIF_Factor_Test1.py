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
    def __init__(self, df, factor_name=None, future_kind='contract_00', factor_kind='1min', layers=4,
                 return_price_kind='close', ticker='B', direction = None,
                 signal_lims=(-1, 1), time_range=None,
                 save_image=True, show_image=True, starttime=20180101, endtime=20200601,
                 savepath='/data/user/015626/data/share/factor/factor_test/'):
        """
        :param df:因子单列，也可双列但是第一列需为因子值，第二列为return，这样此程序就不会再读取return数据，可以节省时间
                    future_kind为'overnight'时只能是单列
        :param factor_name: 因子名称，为None时默认为第一列的列名
        :param future_kind: 期货数据种类，'contract_00'表示近月连续, 'contract_main'表示主力连续
        :param factor_kind: 因子品种，1min、5s、overnight, 5s时futurekind只能是'conntract_main',
                        overnight表示隔夜收益因子，open_to_open表示open_to_open因子，此时futurekind随便设置，不会使用到
        :param layers: 分层
        :param fee: 手续费
        :param return_price_kind: 使用哪一列计算return，比如说'vwap'，或者'twap'，默认为'vwap'
                                future_kind为'overnight'时return_price_kind必须 in ['10minstickvwap', '10minsvwap', '10minsindexret']
                                future_kind为'open_to_open'时，return_price_kind用不到, 使用每日早上10分钟LastPx的均值计算ret
        :param ticker: 测试的品种
        :param direction：需要测试的方向，当为None时多空都测，当为long时只测做多，当为short时只测做空
        :param signal_lims: 因子值范围，需要以0左右对称
        :param time_range: 筛选哪个时间段进行测试，最多可支持2个用来筛选的时间段，如[[935,1100],[1330,1450]]
        :param save_image: 是否需要保存图片
        :param show_image: 是否需要展示图片
        :param starttime: 读取数据开始时间
        :param endtime: 读取数据结束时间
        :param savepath: 图片保存路径
        """
        if isinstance(df, pd.Series):
            df = df.to_frame()
        if len(df.columns.tolist()) == 1:
            df.columns = [str(df.columns[0])]
        if factor_kind in ['overnight']:
            assert len(df.columns.tolist()) == 1, 'overnight factor must be one column'
        if factor_kind == 'overnight':
            assert return_price_kind in ['10minstickvwap', '10minsvwap', '10minsindexret']
        else:
            assert return_price_kind in ['twap', 'vwap', 'close', 'open', 'high', 'low', 'close']
        if isinstance(df.index, pd.MultiIndex):
            # assert len(df.index.get_level_values(1).unique().tolist()) == 1, 'ticker must be unique'
            df = df.reset_index(level = 1, drop = True)
        assert (-1 * min(signal_lims)) == max(signal_lims), 'signal_lims must be central symmetry'
        assert factor_kind in ['1min', '5min', 'overnight', 'open_to_open'], 'factor_kind must be in [1min, 5min, overnight, open_to_open]'
        col0name = df.columns[0]
        if factor_name == None:
            factor_name = col0name

        self.factor_kind = factor_kind
        self.future_kind = future_kind
        self.ticker = ticker
        h5path = '/data/user/015626/data/share/LOCAL_DATA/CSV/testdata/'
        if factor_kind in ['1min', '5min']:
            if len(df.columns.tolist()) == 1:

                datapath = os.path.join(h5path,'data_1m.h5')

                if self.factor_kind == '5min':
                    datapath = os.path.join(h5path,'data_5m.h5')

                origindata = IO.read_data([starttime, endtime], columns=[return_price_kind], alt=datapath)
                origindata = origindata.xs(self.ticker, level=1)
                origindata['ret'] = origindata[return_price_kind].shift(-2) / origindata[return_price_kind].shift(-1) - 1
                origindata = origindata[['ret']]
                df = df.join(origindata, how='inner')
        elif factor_kind == 'overnight':
            if return_price_kind == '10minstickvwap':
                overnightret = IO.read_data([starttime, endtime], columns = ['long_ret','short_ret'],alt = os.path.join(h5path,'daily','overnight_ret.h5')).xs(ticker,level = 1)
                df = df.join(overnightret, how = 'inner').sort_index()
                df.loc[df[col0name] >= 0,'ret'] = df.long_ret
                df.loc[df[col0name] < 0, 'ret'] = df.short_ret
                df = df[[col0name,'ret']]
            elif return_price_kind == '10minsvwap':
                overnightret = IO.read_data([starttime, endtime], 
                                            alt=os.path.join(h5path, 'daily', 'overnight_ret_10minsvwap.h5')).xs(ticker, level=1)
                df = df.join(overnightret, how='inner').sort_index()
                df = df[[col0name, 'ret']]
            elif return_price_kind == '10minsindexret':
                overnightret = IO.read_data([starttime, endtime],
                                            alt=os.path.join(h5path, 'daily', 'overnight_indexret_10minsclose.h5')).xs(ticker, level=1)
                df = df.join(overnightret, how='inner').sort_index()
                df = df[[col0name, 'ret']]
        elif factor_kind == 'open_to_open':
            if len(df.columns.tolist()) == 1:
                otoret = IO.read_data([starttime, endtime], columns=['ret'],
                                            alt=os.path.join(h5path, 'daily', 'open_to_open_ret.h5')).xs(ticker, level=1)
                df = df.join(otoret, how='inner').sort_index()

        df.columns = ['raw', 'ret']
        if direction == 'long':
            df.loc[df.raw < 0, 'raw'] = 0
        elif direction == 'short':
            df.loc[df.raw > 0, 'raw'] = 0

        if factor_kind in ['overnight', 'open_to_open']:
            self.df = df
        else:
            self.df = self.slice_by_minute(df, time_range) if time_range is not None else df

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
        if self.factor_kind == 'overnight':
            stats['long_deal_num'] = stats['long_num']
            stats['short_deal_num'] = stats['short_num']
            stats['avg_long_bars'] = 0 if stats['long_num'] == 0 else round(stats['long_num'] / stats['long_num'], 2)
            stats['avg_short_bars'] = 0 if stats['short_num'] == 0 else round(stats['short_num'] / stats['short_num'], 2)
        else:
            stats['avg_long_bars'] = 0 if stats['long_deal_num'] == 0 else round(stats['long_num'] / stats['long_deal_num'], 2)
            stats['avg_short_bars'] = 0 if stats['short_deal_num'] == 0 else round(stats['short_num'] / stats['short_deal_num'], 2)
        return stats

    def get_win_ratio(self, sig_reshape, ps_return):
        sig = sig_reshape.to_frame().join(ps_return.to_frame())
        sig['open_flag'] = sig.signals != sig.signals.shift(1)
        sig['open_flag'] = sig['open_flag'].astype('int')
        sig['open_flag'] = abs(sig['open_flag'] * sig['signals'])
        sig['open_flag'] = sig['open_flag'].cumsum()
        sig['trade_flag'] = sig['open_flag'] * sig['signals']
        sig = sig.dropna(subset=['trade_flag'])
        sig = sig[sig.trade_flag != 0]
        trade = sig.groupby('trade_flag')['ret'].sum().to_frame().reset_index()
        trade['trade_ret'] = np.sign(trade['trade_flag']) * trade['ret']

        win_ratio = len(trade[trade.trade_ret > 0]) / len(trade) if len(trade) > 0 else np.nan
        lossmean = trade[trade.trade_ret < 0]['trade_ret'].mean()
        winloss_ratio = trade[trade.trade_ret > 0]['trade_ret'].mean() / (lossmean * -1) if lossmean != 0 else np.nan
        return win_ratio, winloss_ratio

    def get_win_ratio_overnight(self, sig_reshape, ps_return):
        sig = sig_reshape.to_frame().join(ps_return.to_frame())
        sig = sig.dropna(subset = ['signals'])
        sig = sig[sig.signals != 0]
        sig['win_flag'] = np.sign(sig.signals * sig.ret)
        sig['trade_ret'] = np.sign(sig['signals']) * sig['ret']
        lossmean = sig[sig.trade_ret < 0]['trade_ret'].mean()
        win_ratio = len(sig[sig.win_flag == 1]) / len(sig) if len(sig) > 0 else np.nan
        winloss_ratio = sig[sig.trade_ret > 0]['trade_ret'].mean() / (lossmean * -1) if lossmean != 0 else np.nan
        return win_ratio, winloss_ratio

    def get_max_drawdone(self, sharpedailyreturn):
        sharpedailyreturn['equity_curve'] = sharpedailyreturn['ret'].cumsum()
        sharpedailyreturn = sharpedailyreturn.reset_index()
        # ===计算最大回撤
        # 计算当日之前的资金曲线的最高点
        sharpedailyreturn['max2here'] = sharpedailyreturn['equity_curve'].expanding().max()
        # 计算到历史最高值到当日的跌幅，drowdwon
        sharpedailyreturn['dd2here'] = sharpedailyreturn['equity_curve'] - sharpedailyreturn['max2here']
        # 计算最大回撤，以及最大回撤结束时间
        end_date, max_draw_down = tuple(sharpedailyreturn.sort_values(by=['dd2here']).iloc[0][['date', 'dd2here']])
        # 计算最大回撤开始时间
        start_date = \
        sharpedailyreturn[sharpedailyreturn['date'] <= end_date].sort_values(by='equity_curve', ascending=False).iloc[0]['date']
        # 将无关的变量删除
        sharpedailyreturn.drop(['max2here', 'dd2here'], axis=1, inplace=True)
        return min(max_draw_down,0), start_date, end_date

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
        c.loc[c.bins == 0, 'ret'] = c.loc[c.bins == 0, 'ret'] * -1

        c_long = c[c.bins == maxQ]
        c_short = c[c.bins == 0]
        c['ret_cumsum'] = c['ret'].cumsum()
        c_long['ret_cumsum'] = c_long['ret'].cumsum()
        c_short['ret_cumsum'] = c_short['ret'].cumsum()


        sharpe = c['ret'].to_frame().reset_index()
        sharpe['date'] = sharpe.dt.apply(lambda x: x.date())
        sharpedailyreturn = sharpe.groupby('date')['ret'].sum().to_frame()
        sharpe_ratio = round(
            sharpedailyreturn['ret'].mean() / sharpedailyreturn['ret'].std() * np.sqrt(242), 3)

        long_sharpe = c_long['ret'].to_frame().reset_index()
        long_sharpe['date'] = long_sharpe.dt.apply(lambda x: x.date())
        long_sharpedailyreturn = long_sharpe.groupby('date')['ret'].sum().to_frame()
        long_sharpe_ratio = round(
            long_sharpedailyreturn['ret'].mean() / long_sharpedailyreturn['ret'].std() * np.sqrt(242), 3)

        short_sharpe = c_short['ret'].to_frame().reset_index()
        short_sharpe['date'] = short_sharpe.dt.apply(lambda x: x.date())
        short_sharpedailyreturn = short_sharpe.groupby('date')['ret'].sum().to_frame()
        short_sharpe_ratio = round(
            short_sharpedailyreturn['ret'].mean() / short_sharpedailyreturn['ret'].std() * np.sqrt(242), 3)

        long_short_mdd, long_short_mdd_startdate, long_short_mdd_enddate = self.get_max_drawdone(sharpedailyreturn)

        if len(long_sharpedailyreturn) > 0:
            long_mdd, _, _ = self.get_max_drawdone(long_sharpedailyreturn)
        else:
            long_mdd = np.nan
        if len(short_sharpedailyreturn) > 0:
            short_mdd, _, _ = self.get_max_drawdone(short_sharpedailyreturn)
        else:
            short_mdd = np.nan

        sig_reshape = self.signal_reshaper(ps_raw)
        stats = self.signal_stats(sig_reshape)
        if self.factor_kind == 'overnight':
            win_ratio, winloss_ret_ratio = self.get_win_ratio_overnight(sig_reshape, ps_return)
        else:
            win_ratio, winloss_ret_ratio = self.get_win_ratio(sig_reshape, ps_return)

        stats['win_ratio'] = round(win_ratio, 4)
        stats['winloss_ret_ratio'] = round(winloss_ret_ratio, 4)

        long_deal_num = stats['long_deal_num']
        short_deal_num = stats['short_deal_num']
        ret_long = c_long.iloc[-1]['ret_cumsum'] if len(c_long) > 0 else np.nan
        ret_short = c_short.iloc[-1]['ret_cumsum'] if len(c_short) > 0 else np.nan

        # 累计盈利点数，与扣费后盈利点数
        ret_long_short = round(c.iloc[-1]['ret_cumsum'], 6)

        if self.factor_kind == 'overnight':
            ret_per_deal_long = round(ret_long / stats['long_num'], 6)
            ret_per_deal_short = round(ret_short / stats['short_num'], 6)
            ret_per_deal = round(ret_long_short / (stats['long_num'] + stats['short_num']), 6)
        else:
            ret_per_deal_long = round(ret_long / long_deal_num, 6)
            ret_per_deal_short = round(ret_short / short_deal_num, 6)
            ret_per_deal = round(ret_long_short / (long_deal_num + short_deal_num), 6)

        stats['ret_long_short'] = round(ret_long_short, 3)
        stats['ret_long'] = round(ret_long, 3)
        stats['ret_short'] = round(ret_short, 3)
        stats['ret_per_deal'] = ret_per_deal
        stats['ret_per_deal_long'] = ret_per_deal_long
        stats['ret_per_deal_short'] = ret_per_deal_short
        stats['IC-1min'] = IC
        stats['self_corr-shift(5)'] = self_corr
        stats['sharpe_Q' + str(maxQ) + '-Q0'] = sharpe_ratio
        stats['long_sharpe'] = long_sharpe_ratio
        stats['short_sharpe'] = short_sharpe_ratio
        stats['long_short_mdd'] = round(long_short_mdd, 4)
        stats['long_short_mdd_startdate'] = long_short_mdd_startdate
        stats['long_short_mdd_enddate'] = long_short_mdd_enddate
        stats['long_mdd'] = round(long_mdd, 4)
        stats['short_mdd'] = round(short_mdd, 4)

        fig = plt.figure(figsize=(14, 30))

        ax1 = fig.add_subplot(6, 1, 1)
        ax1.spines['top'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)

        plt.text(0.2, 1.2, self.factor_name + ' factor report', fontsize=28)
        timelist = self.df.dropna(subset = ['raw']).index.tolist()
        datelist = [x.date() for x in timelist]
        datenum = len(set(datelist))
        plt.text(0.2, 1.1, 'longshort threshold: ' + str(self.threshold), fontsize=14)
        plt.text(0.2, 1.0,
                 'time period: ' + str(timelist[0].date()).replace('-', '') + ' - ' + str(timelist[-1].date()).replace(
                     '-', '') + '    total ' + str(datenum) + ' days', fontsize=14)
        plt.text(0.2, 0.9, 'IC-1min: ' + str(IC), fontsize=14)
        plt.text(0.2, 0.8, 'self_corr-shift(5): ' + str(self_corr), fontsize=14)
        plt.text(0.2, 0.7, 'sharpe_Q' + str(maxQ) + '-Q0: ' + str(sharpe_ratio), fontsize=14)
        plt.text(0.2, 0.6, 'win_ratio: ' + str(round(win_ratio,3)), fontsize=14)
        plt.text(0.2, 0.5, 'win/loss: ' + str(round(winloss_ret_ratio,3)), fontsize=14)


        if self.factor_kind == '1min':
            plt.text(0.2, 0.3, 'avg_long_bars: ' + str(round(stats['avg_long_bars'], 2)) + ' mins', fontsize=14)
            plt.text(0.2, 0.2, 'avg_short_bars: ' + str(round(stats['avg_short_bars'], 2)) + ' mins', fontsize=14)
        elif self.factor_kind == '5s':
            plt.text(0.2, 0.3, 'avg_long_bars: ' + str(round(stats['avg_long_bars'] * 5 / 60, 2)) + ' mins',
                     fontsize=14)
            plt.text(0.2, 0.2, 'avg_short_bars: ' + str(round(stats['avg_short_bars'] * 5 / 60, 2)) + 'mins',
                     fontsize=14)
        elif self.factor_kind == 'open_to_open':
            plt.text(0.2, 0.3, 'avg_long_bars: ' + str(round(stats['avg_long_bars'], 2)) + ' days', fontsize=14)
            plt.text(0.2, 0.2, 'avg_short_bars: ' + str(round(stats['avg_short_bars'], 2)) + ' days', fontsize=14)

        if self.factor_kind in ['overnight']:
            plt.text(0.2, 0.3, 'avg_long_bars: ' + str(round(stats['avg_long_bars'], 2)) + ' nights', fontsize=14)
            plt.text(0.2, 0.2, 'avg_short_bars: ' + str(round(stats['avg_short_bars'], 2)) + ' nights', fontsize=14)
            plt.text(0.2, 0.1, 'long_num: ' + str(stats['long_num']), fontsize=14)
            plt.text(0.2, 0, 'short_num: ' + str(stats['short_num']), fontsize=14)
            dealnum_per_day = (stats['long_num'] + stats['short_num']) / datenum
        else:
            plt.text(0.2, 0.1, 'long_deal_num: ' + str(stats['long_deal_num']), fontsize=14)
            plt.text(0.2, 0, 'short_deal_num: ' + str(stats['short_deal_num']), fontsize=14)
            dealnum_per_day = (stats['long_deal_num'] + stats['short_deal_num']) / datenum

        plt.text(0.2, 0.4, 'dealnum_per_day: ' + str(round(dealnum_per_day, 1)), fontsize=14)


        stats['dealnum_per_day'] = round(dealnum_per_day, 1)

        plt.text(0.6, 0.9, 'skew: ' + str(round(self.df['raw'].skew(), 3)), fontsize=14)
        plt.text(0.6, 0.8, 'kurt: ' + str(round(self.df['raw'].kurt(), 3)), fontsize=14)

        # plt.text(0.6, 0.7, 'ret/mdd: ' + str(round(ret_mdd_ratio, 3)), fontsize=14)
        plt.text(0.6, 0.6, 'Ret_before_fee: ' + str(format(ret_long_short, '.1%')), fontsize=14)
        # if self.fee > 0:
        #     plt.text(0.6, 0.5, 'profit_after_fee: ' + str(after_fee_cumualtive_long_short_point), fontsize=14)

        plt.text(0.6, 0.5, 'ret_per_deal: ' + str(format(ret_per_deal, '.3%')), fontsize=14)
        plt.text(0.6, 0.4, 'ret_per_deal_long: ' + str(format(ret_per_deal_long, '.3%')), fontsize=14)
        plt.text(0.6, 0.3, 'ret_per_deal_short: ' + str(format(ret_per_deal_short, '.3%')), fontsize=14)
        plt.text(0.6, 0.2, 'long_short_mdd: ' + str(format(long_short_mdd, '.2%')), fontsize=14)
        plt.text(0.6, 0.1, 'mdd_startdate: ' + str(long_short_mdd_startdate), fontsize=14)
        plt.text(0.6, 0.0, 'mdd_enddate: ' + str(long_short_mdd_enddate), fontsize=14)

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
        ax2.plot(c_long['ret_cumsum'])
        plt.title(self.factor_name + ' Long Cumulative Ret', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Ret', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：空仓收益曲线
        ax2 = fig.add_subplot(6, 2, 8)
        ax2.plot(c_short['ret_cumsum'] * -1)
        plt.title(self.factor_name + ' Short Cumulative Ret', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Ret', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图：多空收益曲线
        ax2 = fig.add_subplot(6, 1, 5)
        ax2.plot(c['ret_cumsum'])
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

# 检查因子是否符合入库条件
def check_factor_into_lib(factor, ticker = 'IC.CFE',return_price_kind='vwap',
                          future_kind = 'contract_00',
                          start_time = 20170101, end_time = 20200101,
                          avg_bars_t = 5,
                          ret_per_deal_t = 0.00015,
                          long_short_mdd_t = -0.1,
                          IC_t = 0.01,
                          self_corr_t = 0.75,
                          sharpe_insample_t = 2,
                          corr_t = 0.7,
                          avg_corr_t = 100,
                          is_inoutsample_test = True,
                          is_check_corr = True,
                          factor_lib_name = 'IC_stage',
                          factor_lib_rootpath = '/data/user/015626/data/share/alpha/CHINA_FUTURES/MINUTE/'):
    """
    ！！！！！！！！！！！！切换ticker时记得修改因子库名称及路径！！！！！！！！！
    :param factor: 因子dataframe,  列为因子值。如果批量测试的话，可以先将returnpoints设置为第二列。
    :param ticker: 因子对应品种
    :param future_kind: 期货数据种类，'contract_00'表示近月连续, 'contract_main'表示主力连续,
    :param start_time: 测试开始时间
    :param end_time: 测试结束时间
    :param outsample_start_time: 测试开始时间
    :param outsample_end_time: 测试结束时间
    :param avg_bars_t: 平均持仓时间阈值
    :param rp_per_deal_t: 单笔收益阈值
    :param IC_t: IC阈值
    :param self_corr_t: 自相关性阈值
    :param sharpe_outsample_t: 样本外夏普率阈值
    :param sharpe_insample_t: 样本内夏普率阈值
    :param corr_t: 与因子库内因子最高相关性阈值
    :param is_inoutsample_test: 是否要做样本内外测试
    :param is_check_corr: 是否要测试相关性
    :param factor_lib_name: 因子库名字
    :param factor_lib_rootpath: 因子库路径
    :return: True为可以入库， False为不符合入库标准。
    """
    assert is_check_corr or is_inoutsample_test

    if isinstance(factor.index, pd.MultiIndex):
        assert len(factor.index.get_level_values(1).unique().tolist()) == 1, 'ticker must be unique'
        factor = factor.reset_index(level = 1, drop = True)
    factor_name = factor.columns.tolist()[0]
    raw_factor = factor[factor_name].to_frame()

    if is_inoutsample_test:
        if len(factor.columns.tolist()) == 1:
            data_root_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/'
            if future_kind == 'contract_main':
                dataname = 'MD_SIF_TICK_TO_MINUTE_MAIN.h5'
            elif future_kind == 'contract_00':
                dataname = 'MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5'
            origindata = IO.read_data([start_time, end_time], columns=[return_price_kind], alt=os.path.join(data_root_path, dataname))
            origindata = origindata.xs(ticker, level=1)
            origindata['ret'] = origindata[return_price_kind].shift(-2) / origindata[return_price_kind].shift(-1) - 1
            origindata = origindata[['ret']]
            df = factor.join(origindata, how='inner')
            # raw_factor = factor.copy()/
        else:
            df = factor.copy()

         # test insample
        df_full_history = df.copy()
        sif_full = SIF_Factor_Test(df_full_history, factor_name=factor_name, layers=4, save_image=False, show_image=False, starttime = start_time, endtime=end_time)
        stats_full = sif_full.draw_result()
        stats_full['avg_bars'] = np.nanmean([stats_full['avg_long_bars'] , stats_full['avg_short_bars']])

        t_dict = {'avg_bars': avg_bars_t, 'ret_per_deal': ret_per_deal_t, 'IC-1min': IC_t,
                  'self_corr-shift(5)': self_corr_t, 'sharpe_Q3-Q0': sharpe_insample_t, 'long_short_mdd': long_short_mdd_t}
        wrong_dict = {}
        for key in t_dict.keys():
            if stats_full[key] < t_dict[key]:
                wrong_dict[key] = stats_full[key]
        if len(wrong_dict) > 0:
            print('insample test results are not satisfiable')
            for key in wrong_dict.keys():
                print(key, ': ', stats_full[key], '   threshold: ', t_dict[key])
            return False

    # test corr with factorlib
    if is_check_corr:
        highcorrlist = []
        fullcorrlist = []
        factor_lib_path = os.path.join(factor_lib_rootpath, factor_lib_name)
        for x in tqdm(os.listdir(factor_lib_path)):
            if not x.endswith('h5'):
                continue
            # f = IO.read_data([start_time, end_time], alt = os.path.join(factor_lib_path, x)).xs(ticker, level = 1)
            f = pd.read_hdf(os.path.join(factor_lib_path, x)).loc[pd.to_datetime(str(start_time)):pd.to_datetime(str(end_time))]
            newf = raw_factor.join(f, how = 'inner')
            corr = abs(newf[x[:-3]].corr(newf[factor_name]))
            fullcorrlist.append(corr)
            if corr > corr_t:
                highcorrlist.append((x[:-3], round(corr,3)))
        avg_corr = round(np.mean(fullcorrlist),3)
        if len(highcorrlist) > 0:
            print('factor is very relevant to those factors: ', highcorrlist)
            if avg_corr > avg_corr_t:
                print('avg corr: ', avg_corr, '   threshold: ', avg_corr_t)
            return False
        if avg_corr > avg_corr_t:
            print('avg corr: ', avg_corr, '   threshold: ', avg_corr_t)
            return False

    return True