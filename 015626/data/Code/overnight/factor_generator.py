from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from overnight.data_center import HistoryData, HotData
from overnight.naming_config import *
from overnight.utility import *
import pandas as pd
import numpy as np
import os
import datetime
import warnings
import bottleneck as bk

class FactorGenerator:
    __data__ = None
    __trade_date__ = None

    def __init__(self, factor_name='test', required_columns=None, ts_norm_method='ts_rank', ts_norm_bars=20, savepath = '/data/user/015626/data/share/factor/overnight/test/'):
        self.factor_name = factor_name
        self.required_columns = required_columns
        assert ts_norm_method in ['ts_rank', 'rolling_norm']
        assert isinstance(ts_norm_bars, int)
        self.ts_norm_method = ts_norm_method
        self.ts_norm_bars = ts_norm_bars
        self.savepath = savepath

    @classmethod
    def prepare_hist_data(inst, trade_date=None, hisdays=30):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        inst.__trade_date__ = trade_date
        ref_date = int(udt.get_trading_day_offset(inst.__trade_date__, -1)[0].strftime('%Y%m%d'))
        hd = HistoryData(ref_date, hisdays)
        hd.get_all()
        inst.checker(hd.collector)
        inst.__data__ = hd.collector

    @classmethod
    def dump_hist_data(inst):
        save_path = os.path.join(trade_root, 'history', inst.__trade_date__.strftime('%Y%m%d'))
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        diller(os.path.join(save_path, 'history.pkl'), (inst.__trade_date__, inst.__data__))

    @classmethod
    def load_hist_data(inst, trade_date=None):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        save_path = os.path.join(trade_root, 'history', trade_date.strftime('%Y%m%d'))
        _trade_date, _data = diller(os.path.join(save_path, 'history.pkl'))
        assert _trade_date == trade_date
        inst.__trade_date__ = _trade_date
        inst.__data__ = _data

    @classmethod
    def merge_hot_data(inst, trade_date=None):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)

        inst.load_hist_data(trade_date=trade_date)
        hist_data = inst.__data__
        hd = HotData(trade_date)
        hd.get_all()

        # assert set(hd.collector.keys()) == set(inst.__data__.keys())
        hot_data = hd.collector
        
        inst.checker(hot_data, date = trade_date)
        
        prod_data = {}

        # preadj
        for n in ['zz500','hs300','zz800']:
            collist = list(set(hist_data['close_%s' % n].columns) & set(hot_data['close_%s' % n].columns))
            collist.sort()
            hisadj = hist_data['adjfactor_alla_daily'][collist].fillna(method = 'ffill')
            hisadj = hisadj.reindex(hist_data['close_%s' % n].index, method = 'pad')
            hotadj = hot_data['adjfactor_alla_daily'][collist]
            adj = pd.DataFrame(hisadj.values / np.tile(hotadj.values,(len(hisadj),1)), index=hisadj.index, columns=hisadj.columns) 

            for m in ['open', 'high', 'low', 'close']:
                hist_data['%s_%s_preadj' % (m, n)] = hist_data['%s_%s' % (m, n)] * adj
                hot_data['%s_%s_preadj' % (m, n)] = hot_data['%s_%s' % (m, n)]
            for m in ['volume']:
                hist_data['%s_%s_preadj' % (m, n)] = hist_data['%s_%s' % (m, n)] / adj
                hot_data['%s_%s_preadj' % (m, n)] = hot_data['%s_%s' % (m, n)]            

        t = minute_to_daily_start_time.strftime('%H%M') + minute_to_daily_stop_time.strftime('%H%M')
        for k, v in hot_data.items():

            if k in ['AUDJPY', 'SHIBOR']:
                prod_data[k] = v
            elif k.endswith('.SH') or k.endswith('.CFE') or k.endswith('zz800_daily') or (k.split('_')[-1] in ['zz500','hs300','zz800','preadj']):
                prod_data[k] = pd.concat([hist_data[k], v], axis=0, sort=True)
            elif k.endswith('_mask'):
                prod_data[k] = pd.concat([hist_data[k], v], axis=0, sort=True).fillna(False).astype('bool')
            elif k.endswith('_daily'):
                collist = list(set(hist_data[k].columns) & set(hot_data[k].columns))
                collist.sort()
                prod_data[k] = pd.concat([hist_data[k][collist], v[collist]], axis=0)
            elif k.endswith('_alla'):
                collist = list(set(hist_data[k].columns) & set(hot_data[k].columns))
                collist.sort()
                minute_to_daily = pd.concat([hist_data[k][collist], v[collist]], axis=0)
                prod_data[k] = minute_to_daily
                minute_to_daily = minute_to_daily.between_time(minute_to_daily_start_time, minute_to_daily_stop_time).sort_index()
                if k.startswith('open'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.fillna(method = 'bfill').resample('D').first()
                elif k.startswith('high'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.resample('D').max()
                elif k.startswith('low'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.resample('D').min()
                elif k.startswith('close'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.fillna(method = 'ffill').resample('D').last()
                elif k.startswith('volume'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.resample('D').sum()
                elif k.startswith('amount'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.resample('D').sum()

        float_share_zz800_daily = hist_data['float_share_zz800_daily']
        float_share_zz800_daily.loc[trade_date] = np.nan
        prod_data['float_share_zz800_daily'] = float_share_zz800_daily.fillna(method = 'ffill')

        alla_ticker_list = list(set(prod_data['close_alla'].columns) & set(prod_data['close_alla_daily'].columns))
        for k in prod_data.keys():
            if '_alla' in k:
                prod_data[k] = prod_data[k][alla_ticker_list]

        # pct_change_alla = prod_data['close_alla'].pct_change()
        # preclose_alla_daily = prod_data['preclose_alla_daily']
        # close_alla_925 = prod_data['close_alla'].at_time(datetime.time(9,25))
        # preclose_alla_daily.index = close_alla_925.index
        # pct_change_925 = close_alla_925 / preclose_alla_daily - 1
        # pct_change_alla.loc[pct_change_925.index] = pct_change_925
        # pct_change_alla = pct_change_alla.fillna(0)

        # last_tday = int(udt.get_trading_day_offset(inst.__trade_date__, -1)[0].strftime('%Y%m%d'))
        # zz500_stock_list, hs300_stock_list, zz800_stock_list, _ = get_constituent_stock_list(last_tday)
        # prod_data['pct_change_alla'] = pct_change_alla
        # prod_data['pct_change_zz800'] = pct_change_alla[zz800_stock_list]
        # prod_data['pct_change_zz500'] = pct_change_alla[zz500_stock_list]
        # prod_data['pct_change_hs300'] = pct_change_alla[hs300_stock_list]

        inst.__data__ = prod_data

    def slicer(self):
        return {col: self.__data__[col].copy() for col in self.required_columns}

    @staticmethod
    def checker(data, date = None):
        assert len(data) > 0
        assert data['recent_month_mask'].sum(axis = 1).sum() == len(data['recent_month_mask']), 'recent_month_mask is wrong'
        for k, v in data.items():
            if date is not None:
                assert len(v.loc[date:].dropna(axis = 0, how = 'all')) > 0, '%s has no data' % str(date)
            if k.endswith('.CFE') or k.endswith('.SH'):
                if k.endswith('.CFE'):
                    if date is None:
                        assert data[k].shape == data['recent_month_mask'].shape , '%s has different shape with mask' % k
                    df = data[k][data['recent_month_mask']].sum(axis = 1)
                else:
                    df = data[k]
                richness = len(df[df > 0]) / len(df)
            else:
                df = data[k]
                richness = len(df.dropna(axis = 0, how = 'all')) / len(df)

                su = k.split('_')[-1]
                if su in ['zz800', 'zz500', 'hs300']:
                    if df.shape[1] != int(su[2:]):
                        warnings.warn('%s has %f stocks' % (k, int(su[2:])))

            assert richness > min_data_richness_threshold, '%s richness is %f' % (k, richness)
            if richness < data_richness_threshold:
                warnings.warn('%s richness is %f' % (k, richness))


    def __callback__(self):
        data = self.slicer()
        
        raw_path = os.path.join(self.savepath, 'raw')
        norm_path = os.path.join(self.savepath, 'norm')
        if not os.path.exists(raw_path):
            os.makedirs(raw_path)
        if not os.path.exists(norm_path):
            os.makedirs(norm_path)

        factor_raw = self.on_bar(data)
        if self.ts_norm_bars in [0, 1]:
            factor_norm = factor_raw
        else:
            if self.ts_norm_method == 'ts_rank':
                factor_norm = self.ts_rank(factor_raw, self.ts_norm_bars)
            elif self.ts_norm_method == 'rolling_norm':
                factor_norm = self.rolling_norm(factor_raw, self.ts_norm_bars)

        pd_writer(factor_raw, raw_path)
        pd_writer(factor_norm, norm_path)

    def get_avaliable_columns(self):
        return list(self.__data__.keys())

    def get_data(self):
        return self.__data__
    
    def rolling_norm(self, sig, window=1200, method='max_min'):
        assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
        if window == 0:
            return sig
        else:
            if isinstance(sig, pd.DataFrame):
                colnames = sig.columns
            elif isinstance(sig, pd.Series):
                colnames = sig.name
            sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                index=sig.index, name=colnames)
            sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                index=sig.index, name=colnames)
            temp = sig_max - sig_min
            temp[abs(temp) < 1e-8] = np.nan
            signal = (sig - sig_min) / temp
            return 2 * signal - 1
  

    def ts_rank(self, df1, d=4800):
        # moving time-series rank for the past d periods
        assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
        if d == 1:
            output = df1
        else:
            if isinstance(df1, pd.DataFrame):
                output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                      index=df1.index, columns=df1.columns)
            elif isinstance(df1, pd.Series):
                output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                   index=df1.index, name=df1.name)
        return output