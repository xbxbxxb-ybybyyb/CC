from multifactor.IO import IO
import pandas as pd

pd.set_option('max_columns',200)

import pandas as pd
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime
from multifactor.IO import IO



class SIF_Factor_Test:
    def __init__(self, df, factor_name, layers = 4, threshold = 0.75, ticker = 'IC.CFE', starttime = 20160101, endtime = 20220101, savepath = '/data/user/015626/data/share/factor/factor_test/'):
        if len(df.columns.tolist()) == 1:
            origindata = IO.read_data([starttime, endtime], columns = ['close'], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/MINUTE/MAIN/MD_CHINA_FUTURES_MINUTE_MAIN.h5')
            origindata = origindata.xs(ticker, level = 1)
            origindata['return_points'] = origindata['close'].shift(-2) - origindata['close'].shift(-1)
            origindata = origindata[['return_points']]
            df = df.join(origindata)
        df.columns = ['raw','return_points']
        idx = df.index
        t1 = df.loc[(idx.hour == 9) & (idx.minute >= 35)]
        t2 = df.loc[(idx.hour >= 10) & (idx.hour <=13)]
        t3 = df.loc[(idx.hour == 14) & (idx.minute <= 50)]
        t = t1.append(t2).append(t3)
        t = t.sort_index()
        
        self.df = t
        self.factor_name = factor_name
        self.layers = layers
        self.threshold = threshold
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


    def ts_segment_test(self, ps_raw, ps_return, layer_lims=None, normalize=False, return_segment_time_series=False, **kwargs):
       
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
        _magic = pd.DataFrame(ps_bin).merge(pd.DataFrame(ps_return), how='left', left_index=True, right_index=True).dropna()
        if not return_segment_time_series:
            pd_res = _magic.groupby('bins').mean()
            pd_res.index = ['Q'+str(int(col)) for col in pd_res.index]
            return pd_res, _magic
        else:
            segment_dict = dict()
            for nbin, group in _magic.groupby('bins'):
                _ = group[ps_return.name]
                _.name = 'Q' + str(nbin)
                segment_dict[_.name] = _
            return segment_dict, _magic

    def signal_reshaper(self, signals, signal_lims=(-1, 1), print_stats=True):
        assert isinstance(signals, pd.Series)
        assert isinstance(signal_lims, tuple)
        assert 0 < self.threshold < 1
        signals = signals.copy()
        signals.index.name = 'dt'
        signals.name = 'signals'
        signal_mean = np.mean(signal_lims)
        signal_amp = (max(signal_lims) - min(signal_lims)) / 2
        signals = (signals - signal_mean) / signal_amp
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
        flag =  sig * sig.shift(-1)
        sig.name = 'sig'
        flag.name=  'flag'
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
        IC = round(self.df['raw'].corr(self.df['return_points']),3)
        self_corr = round(self.df['raw'].corr(self.df['raw'].shift(5)),3)
        
        df_copy = self.df.copy()
        ps_raw = df_copy['raw']
        ps_return = df_copy['return_points']
        
        pd_res, magic = self.ts_segment_test(ps_raw, ps_return)
        #print(pd_res)
        
        c = magic[(magic.bins == 0) | (magic.bins == 3)]
        c.loc[c.bins == 0, 'return_points'] *= -1
        
        sharpe = c['return_points'].to_frame().reset_index()
        sharpe['date'] = sharpe.dt.apply(lambda x:x.date())
        sharpedailyreturn = sharpe.groupby('date')['return_points'].sum().to_frame()
        sharpe_ratio = round(sharpedailyreturn['return_points'].mean()/sharpedailyreturn['return_points'].std()*np.sqrt(252),3)


        stats = self.signal_stats(self.signal_reshaper(ps_raw))
        
        fig = plt.figure(figsize=(9, 20))

        ax1 = fig.add_subplot(4, 1, 1)   
        ax1.spines['top'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)

        plt.text(0.2,1.1,self.factor_name + ' factor report',fontsize=28)
        timelist = self.df.index.tolist()
        plt.text(0.2,1.0, 'time period: '+ str(timelist[0].date()).replace('-','') + ' - ' + str(timelist[-1].date()).replace('-',''), fontsize=14)
        plt.text(0.2,0.9,'IC: '+str(IC),fontsize=14)
        plt.text(0.2,0.8,'self_corr: '+str(self_corr),fontsize=14)
        plt.text(0.2,0.7,'sharpe_Q4-Q1: ' + str(sharpe_ratio),fontsize=14)
        plt.text(0.2,0.6,'avg_long_bars: ' + str(round(stats['avg_long_bars'], 2)),fontsize=14)
        plt.text(0.2,0.5,'avg_short_bars: ' + str(round(stats['avg_short_bars'], 2)),fontsize=14)
        plt.text(0.2,0.4,'invalid_deal_num: ' + str(stats['invalid_deal_num']),fontsize=14)
        plt.text(0.2,0.3,'long_deal_num: ' + str(stats['long_deal_num']),fontsize=14)
        plt.text(0.2,0.2,'long_num: ' + str(stats['long_num']),fontsize=14)
        plt.text(0.2,0.1,'short_deal_num: ' + str(stats['short_deal_num']),fontsize=14)
        plt.text(0.2,0,'short_num: ' + str(stats['short_num']),fontsize=14)

        plt.xticks([])  #去掉x轴
        plt.yticks([])  #去掉y轴

        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图一
        ax1 = fig.add_subplot(4, 1, 2)    
        xlist = pd_res.index.tolist()
        ylist = pd_res['return_points'].tolist()
        ax1.bar(np.arange(len(xlist)), ylist, color='dodgerblue')
        ax1.set_xticks(np.arange(len(xlist)))
        ax1.set_xticklabels(xlist)
        plt.xlabel('Segment', fontsize='medium')
        plt.ylabel('Return', fontsize='medium')
        plt.title(self.factor_name + ' Segment Return', fontsize='large')
        plt.subplots_adjust(top=0.95, hspace=0.3)

        # 图二：多空收益曲线
        ax2 = fig.add_subplot(4, 1, 3)
        ax2.plot(c['return_points'].cumsum())
        plt.title(self.factor_name + ' Long-Short Points', fontsize='large')
        plt.xlabel('Date', fontsize='medium')
        plt.ylabel('Cumulative Points', fontsize='medium')
        plt.subplots_adjust(top=0.95, hspace=0.3)
   
        # 图三：分布图
        ax4 = fig.add_subplot(4, 1, 4)
        ax4.hist(ps_raw.dropna(), bins = 100)
        plt.title(self.factor_name + ' hist', fontsize='large')
        plt.xlabel('Factor value', fontsize='medium')
        plt.ylabel('Num', fontsize='medium')
        plt.subplots_adjust(hspace=0.3)
        #plt.savefig(os.path.join(self.savepath, self.factor_name + '.png'), format = 'png')  # 存储图片
        plt.show()
        plt.close()