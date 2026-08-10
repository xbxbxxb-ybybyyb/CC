# 新增功能： 支持IM 只能测试zz1000指数,return_price_kind='close'或者twap
import matplotlib
matplotlib.use('Agg')

import pandas as pd
pd.set_option('max_columns', 200)
import pandas as pd
import numpy as np
import os, datetime
import matplotlib.pyplot as plt
from tqdm import tqdm
from multifactor.IO import IO
import multifactor.utility.dt as udt
from matplotlib.ticker import FuncFormatter

import warnings
warnings.filterwarnings('ignore')


def factor_to_signal(_factor, in_t = 0.8, out_t = 0.5):
    if isinstance(_factor, pd.Series):
        df = _factor.to_frame()
    else:
        df = _factor.copy()
    factorname = df.columns[0]

    condition1 = df[factorname] >= in_t
    condition2 = df[factorname].shift(1) < in_t
    df.loc[condition1 & condition2, 'signal_long'] = 1

    condition1 = df[factorname] < out_t
    condition2 = df[factorname].shift(1) >= out_t
    df.loc[condition1 & condition2, 'signal_long'] = 0

    condition1 = df[factorname] <= (-1 * in_t)
    condition2 = df[factorname].shift(1) > (-1 * in_t)
    df.loc[condition1 & condition2, 'signal_short'] = -1

    condition1 = df[factorname] > (-1 * out_t)
    condition2 = df[factorname].shift(1) <= (-1 * out_t)
    df.loc[condition1 & condition2, 'signal_short'] = 0

    df['signal'] = df[['signal_long', 'signal_short']].sum(axis = 1, min_count = 1, skipna = True)
    temp = df[df['signal'].notnull()][['signal']]
    temp = temp[temp['signal'] != temp['signal'].shift(1)]

    df['signal'] = temp['signal']
    df['signal'] = df['signal'].fillna(method = 'ffill')
    df['signal'] = df['signal'].fillna(value = 0)

    return df['signal']

class SIF_Factor_Test:
    def __init__(self, _df,in_t = None, out_t = None, factor_name=None, future_kind='contract_00', factor_kind='1min', layers=4,
                 return_price_kind='vwap', ticker='IC.CFE', direction = None,
                 signal_lims=(-1, 1), time_range=[935, 1450], overnight_time_period = [1450, 930],
                 save_image=True, show_image=True, starttime=20170101, endtime=20210101,
                 savepath='/data/user/015626/data/share/factor/factor_test/'):
        """
        :param df:因子单列，当factor_kind为overnight 或者open_to_open 也可双列但是第一列需为因子值，第二列为return，这样此程序就不会再读取return数据，可以节省时间
                  当factor_kind为1min或者5s时，也可以3列，需严格遵守第一列为因子值，第二列为ret，第三列为计算1-10分钟ret的price，计算IC_duration所用
        :param in_t, out_t: 把因子转变为in_t进out_t出
        :param factor_name: 因子名称，为None时默认为第一列的列名
        :param future_kind: 期货数据种类，'contract_00'表示近月连续, 'contract_main'表示主力连续
        :param factor_kind: 因子品种，1min、5s、overnight, 5s时futurekind只能是'conntract_main',
                        overnight表示隔夜收益因子，open_to_open表示open_to_open因子，此时futurekind随便设置，不会使用到
        :param layers: 分层
        :param fee: 手续费
        :param return_price_kind: 使用哪一列计算return，比如说'vwap'，或者'twap'，默认为'vwap'
                                future_kind为'overnight'时return_price_kind必须 in ['10minstickvwap', '10minsvwap', '10minsindexret', 'basisret','basisretminusbonus']
                                future_kind为'open_to_open'时，return_price_kind用不到, 使用每日早上10分钟LastPx的均值计算ret
        :param ticker: 测试的品种
        :param direction：需要测试的方向，当为None时多空都测，当为long时只测做多，当为short时只测做空
        :param signal_lims: 因子值范围，需要以0左右对称
        :param time_range: 筛选哪个时间段进行测试，最多可支持2个用来筛选的时间段，如[[935,1100],[1330,1450]]
        :param overnight_time_period: 测试哪个隔夜时间段的收益，[1450, 930]表示14:50-14:59的tick twap到第二日9:30-9:39的tick twap
        :param save_image: 是否需要保存图片
        :param show_image: 是否需要展示图片
        :param starttime: 读取数据开始时间
        :param endtime: 读取数据结束时间
        :param savepath: 图片保存路径
        """
        df = _df.copy()
        if isinstance(df, pd.Series):
            df = df.to_frame()
        if in_t is not None:
            assert out_t is not None
            df[df.columns[0]] = factor_to_signal(df[df.columns[0]].copy(), in_t, out_t)
        try:
            if len(df.columns.tolist()) == 1:
                df.columns = [str(df.columns[0])]
        except:
            pass
        if factor_kind in ['overnight']:
            assert overnight_time_period[0] in [1430, 1440, 1450]
            assert overnight_time_period[1] in [930, 940, 950]
        if factor_kind == 'overnight':
            assert return_price_kind in ['10minstickvwap', '10minsvwap', '10minsindexret','basisret','basisretminusbonus']
            if overnight_time_period != [1450, 930]:
                assert return_price_kind in ['10minstickvwap','10minsindexret','basisret','basisretminusbonus']
        else:
            assert return_price_kind in ['twap', 'vwap', 'close', 'open', 'high', 'low', 'close']
        

        assert (-1 * min(signal_lims)) == max(signal_lims), 'signal_lims must be central symmetry'
        assert factor_kind in ['1min', '5s', 'overnight', 'open_to_open'], 'factor_kind must be in [1min, 5s, overnight, open_to_open]'
        try:
            col0name = df.columns[0]
        except:
            col0name = df[0].columns[0]
        if factor_name == None:
            factor_name = col0name

        self.factor_kind = factor_kind
        self.future_kind = future_kind
        self.ticker = ticker 
        h5path = '/arch1/group/800466/warehouse/prod/MD/CHINA_COMMODITY/MINUTE/TEMP2/OUTSAMPLE/'
        if type(df) ==  pd.DataFrame:
            if len(df.columns.tolist()) == 1:
                
                datapath = h5path

                origindata_full = pd.read_pickle(datapath + self.ticker + '.pkl')
                origindata = ((origindata_full[return_price_kind])[origindata_full['main_mask']]).mean(axis = 1).to_frame()


                for i in range(1,11):
                    origindata['ret%s'%i] = ((origindata_full[return_price_kind].shift(-i - 1) / origindata_full[return_price_kind].shift(-1) - 1)[origindata_full['main_mask']]).mean(axis = 1)
                origindata['ret'] = origindata['ret1']
                origindata = origindata[['ret'] + ['ret%s'%i for i in range(1,11)]].loc[str(starttime) : str(endtime)]
                df = df.join(origindata, how='inner')
            elif len(df.columns.tolist()) == 3:
                df.columns = ['raw','ret','price']
                for i in range(1,11):
                    df['ret%s'%i] = df['price'].shift(-i - 1) / df['price'].shift(-1) - 1
                df = df.drop(['price'], axis = 1)
        else:

            price_temp = df[1]
            main_mask = df[2]
            origindata = (price_temp[main_mask]).mean(axis = 1).to_frame()


            for i in range(1,11):
                origindata['ret%s'%i] = ((price_temp.shift(-i - 1) / price_temp.shift(-1) - 1)[main_mask]).mean(axis = 1)
            origindata['ret'] = origindata['ret1']
            origindata = origindata[['ret'] + ['ret%s'%i for i in range(1,11)]].loc[str(starttime) : str(endtime)]
            df = df[0].copy()
            df = df.join(origindata, how='inner')


        df.columns = ['raw', 'ret'] if len(df.columns) == 2 else ['raw', 'ret'] + ['ret%s'%i for i in range(1,11)]
        if direction == 'long':
            df.loc[df.raw < 0, 'raw'] = 0
        elif direction == 'short':
            df.loc[df.raw > 0, 'raw'] = 0

        if factor_kind in ['overnight', 'open_to_open']:
            self.df = df
        else:
            self.df = self.slice_by_minute(df, time_range)

        self.df.index.name = 'dt'
        self.df = self.df.sort_index()

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
            #range_a.sort()
            #range_b.sort()
            finaltime1 = range_b[-1]
            finaltime2 = range_b[-1]
            slice_mask = [(i <= range_a[-1] and i >= range_a[0]) or (i <= range_b[-1] and i >= range_b[0]) for i in
                          hour_minute_list]
            dat_slice = dat[slice_mask].sort_index()
            
            finalhour2 = finaltime2 // 100
            finalminute2 = finaltime2 % 100

            finalhour1 = finaltime1 // 100
            finalminute1 = finaltime1 % 100

            idx = dat_slice.index
            dat_slice.loc[(idx.hour == finalhour1) & (idx.minute == finalminute1), 'raw'] = 0
            dat_slice.loc[(idx.hour == finalhour2) & (idx.minute == finalminute2), 'raw'] = 0
            dat_slice = dat_slice.sort_index()


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
        if self.factor_kind in ['1min', '5s']:
            IC_daily = self.df['raw'].rolling(1200,min_periods = 600).corr(self.df['ret'])
            # IC_daily = self.df['raw'].groupby(self.df.index.date).corr(self.df['ret']).rolling(10,min_periods = 5).mean()
        
        # 计算5分钟收益以及10分钟收益
        _df = self.df.copy()
        self.df = self.df[['raw','ret']]
       
        # 计算IC duration 
        IC5, IC10 = np.nan, np.nan
        if self.factor_kind in ['1min','5s']:       
            IC_duration_list = []
            for i in range(1,11):
                _df = _df.between_time(datetime.time(9,30), datetime.time(14, 56 - i - 1))
                IC_duration_list.append(round(_df['raw'].corr(_df['ret%s'%i]), 5))
            IC5 = IC_duration_list[4]
            IC10 = IC_duration_list[9]

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
            sharpedailyreturn['ret'].mean() / sharpedailyreturn['ret'].std() * np.sqrt(242), 5)

        long_sharpe = c_long['ret'].to_frame().reset_index()
        long_sharpe['date'] = long_sharpe.dt.apply(lambda x: x.date())
        long_sharpedailyreturn = long_sharpe.groupby('date')['ret'].sum().to_frame()
        long_sharpe_ratio = round(
            long_sharpedailyreturn['ret'].mean() / long_sharpedailyreturn['ret'].std() * np.sqrt(242), 5)

        short_sharpe = c_short['ret'].to_frame().reset_index()
        short_sharpe['date'] = short_sharpe.dt.apply(lambda x: x.date())
        short_sharpedailyreturn = short_sharpe.groupby('date')['ret'].sum().to_frame()
        short_sharpe_ratio = round(
            short_sharpedailyreturn['ret'].mean() / short_sharpedailyreturn['ret'].std() * np.sqrt(242), 5)

        if len(sharpedailyreturn) > 0:
            long_short_mdd, long_short_mdd_startdate, long_short_mdd_enddate = self.get_max_drawdone(sharpedailyreturn)
        else:
            long_short_mdd, long_short_mdd_startdate, long_short_mdd_enddate = np.nan, np.nan, np.nan

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

        stats['win_ratio'] = round(win_ratio, 6)
        stats['winloss_ret_ratio'] = round(winloss_ret_ratio, 6)

        long_deal_num = stats['long_deal_num']
        short_deal_num = stats['short_deal_num']
        ret_long = c_long.iloc[-1]['ret_cumsum'] if len(c_long) > 0 else np.nan
        ret_short = c_short.iloc[-1]['ret_cumsum'] if len(c_short) > 0 else np.nan

        # 累计盈利点数，与扣费后盈利点数
        ret_long_short = round(c.iloc[-1]['ret_cumsum'], 6) if len(c) > 0 else np.nan

        if self.factor_kind == 'overnight':
            ret_per_deal_long = round(ret_long / stats['long_num'], 6)
            ret_per_deal_short = round(ret_short / stats['short_num'], 6)
            ret_per_deal = round(ret_long_short / (stats['long_num'] + stats['short_num']), 6)
        else:
            ret_per_deal_long = round(ret_long / long_deal_num, 6)
            ret_per_deal_short = round(ret_short / short_deal_num, 6)
            ret_per_deal = round(ret_long_short / (long_deal_num + short_deal_num), 6)

        stats['ret_long_short'] = round(ret_long_short, 6)
        stats['ret_long'] = round(ret_long, 6)
        stats['ret_short'] = round(ret_short, 6)
        stats['ret_per_deal'] = ret_per_deal
        stats['ret_per_deal_long'] = ret_per_deal_long
        stats['ret_per_deal_short'] = ret_per_deal_short
        stats['IC-1min'] = IC
        if IC5 == IC5:
            stats['IC-5min'] = IC5
            stats['IC-10min'] = IC10
        stats['self_corr-shift(5)'] = self_corr
        stats['sharpe_Q' + str(maxQ) + '-Q0'] = sharpe_ratio
        stats['long_sharpe'] = long_sharpe_ratio
        stats['short_sharpe'] = short_sharpe_ratio
        stats['long_short_mdd'] = round(long_short_mdd, 6)
        stats['long_short_mdd_startdate'] = long_short_mdd_startdate
        stats['long_short_mdd_enddate'] = long_short_mdd_enddate
        stats['long_mdd'] = round(long_mdd, 6)
        stats['short_mdd'] = round(short_mdd, 6)
        stats['skew'] = round(self.df['raw'].skew(), 3)
        stats['kurt'] = round(self.df['raw'].kurt(), 3)
        if self.factor_kind not in ['overnight', 'open_to_open']:
            stats['IC_duration'] = IC_duration_list


        
        '''
        # 图：30分组收益
        ax30 = fig.add_subplot(fig_rows, 2, 5)
        xlist = pd_res30.index.tolist()
        ylist = (pd_res30['ret']*100).tolist()
        ax30.bar(np.arange(len(xlist)), ylist, color='dodgerblue')
        ax30.set_xticks(np.arange(len(xlist)))
        ax30.set_xticklabels(xlist)
        plt.xlabel('Segment', fontsize='medium')
        plt.ylabel('Return %', fontsize='medium')
        plt.title(self.factor_name + ' Segment_30 Return', fontsize='large')
        plt.subplots_adjust(top=0.95, hspace=0.3)
        '''

        return c, stats, pd_res30
