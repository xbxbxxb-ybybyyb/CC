from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from overnight.data_center import HistoryData, HotData
from overnight.naming_config import *
from overnight.factors import *
from overnight.utility import *
import pandas as pd
import numpy as np
import os
import datetime
import warnings
import bottleneck as bk
from multiprocessing import Pool


class FactorGenerator:
    __data__ = None
    __mdconstant__ = dict()
    __trade_date__ = None

    def __init__(self, required_columns=None, ts_norm_method='ts_rank', ts_norm_bars=20, savepath=hisfactor_path):
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
        zz500_stock_list, hs300_stock_list, zz800_stock_list, sh50_stock_list = get_constituent_stock_list(ref_date)
        index_components = {'zz500_stock_list': zz500_stock_list,
                            'hs300_stock_list': hs300_stock_list,
                            'zz800_stock_list': zz800_stock_list,
                            'sh50_stock_list' : sh50_stock_list}
        inst.__mdconstant__.update(index_components)
        hd = HistoryData(ref_date, hisdays)
        hd.get_all()
        inst.checker(hd.collector)
        inst.__data__ = hd.collector

    @classmethod
    def dump_hist_data(inst):
        save_path = os.path.join(trade_root, 'history', inst.__trade_date__.strftime('%Y%m%d'))
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        diller(os.path.join(save_path, 'history.pkl'), (inst.__trade_date__, inst.__data__, inst.__mdconstant__))

    @classmethod
    def load_hist_data(inst, trade_date=None):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        save_path = os.path.join(trade_root, 'history', trade_date.strftime('%Y%m%d'))
        _trade_date, _data, _mdconstant = diller(os.path.join(save_path, 'history.pkl'))
        assert _trade_date == trade_date
        inst.__trade_date__ = _trade_date
        inst.__data__ = _data
        inst.__mdconstant__ = _mdconstant

    @classmethod
    def merge_hot_data(inst, trade_date=None):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        # load history data
        inst.load_hist_data(trade_date=trade_date)
        hist_data = inst.__data__
        # retrieve hot data
        hd = HotData(trade_date)
        hd.get_all()
        hot_data = hd.collector
        inst.checker(hot_data, date = trade_date)
        # combine history and hot
        prod_data = {}

        # preadj
        alla_ticker_list = sorted(list(set(hist_data['close_alla'].columns) & \
                                       set(hot_data['close_alla'].columns) & \
                                       set(hist_data['close_alla_daily'].columns) & \
                                       set(hot_data['close_alla_daily'].columns)))
        hisadj = hist_data['adjfactor_alla_daily'][alla_ticker_list].fillna(method='ffill')
        hisadj = hisadj.reindex(hist_data['close_alla'].index, method='pad')
        hotadj = hot_data['adjfactor_alla_daily'][alla_ticker_list]
        adj = pd.DataFrame(hisadj.values / np.tile(hotadj.values, (len(hisadj), 1)), index=hisadj.index, columns=hisadj.columns)
        for m in ['open', 'high', 'low', 'close']:
            hist_data['%s_alla_preadj' % m] = hist_data['%s_alla' % m][alla_ticker_list] * adj
            hot_data['%s_alla_preadj' % m] = hot_data['%s_alla' % m][alla_ticker_list]
        for m in ['volume']:
            hist_data['%s_alla_preadj' % m] = hist_data['%s_alla' % m][alla_ticker_list] / adj
            hot_data['%s_alla_preadj' % m] = hot_data['%s_alla' % m][alla_ticker_list]
        t = minute_to_daily_tag
        for k, v in hot_data.items():
            if k in ['AUDJPY', 'SHIBOR']:
                prod_data[k] = v
            elif k.endswith('.SH') or k.endswith('.CFE') or (k.split('_')[-1] in ['zz500','hs300','sh50','preadj']): #weight_zz500, weight_hs300, weight_sh50
                prod_data[k] = pd.concat([hist_data[k], v], axis=0, sort=True)
            elif k.endswith('_mask'):
                prod_data[k] = pd.concat([hist_data[k], v], axis=0, sort=True).fillna(False).astype('bool')
            elif k.endswith('_daily'):
                prod_data[k] = pd.concat([hist_data[k], v], axis=0, sort=True)
            elif k.endswith('_alla'):
                minute_to_daily = pd.concat([hist_data[k], v], axis=0, sort=True)
                prod_data[k] = minute_to_daily
                minute_to_daily = minute_to_daily.between_time(minute_to_daily_start_time, minute_to_daily_stop_time).sort_index()
                idx_date_list = pd.to_datetime(minute_to_daily.index.date)
                if k.startswith('open'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.fillna(method = 'bfill').groupby(idx_date_list).first()
                elif k.startswith('high'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).max()
                elif k.startswith('low'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).min()
                elif k.startswith('close'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.fillna(method = 'ffill').groupby(idx_date_list).last()
                elif k.startswith('volume'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).sum()
                elif k.startswith('amount'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).sum()
        float_share_alla_daily = hist_data['float_share_alla_daily']
        float_share_alla_daily.loc[trade_date] = np.nan
        prod_data['float_share_alla_daily'] = float_share_alla_daily.fillna(method = 'ffill')
        prod_data['raw_factors'] = hist_data['raw_factors']
        for k in prod_data.keys():
            if '_alla' in k:
                prod_data[k] = prod_data[k][alla_ticker_list]
        inst.__data__ = prod_data

    def slicer(self):
        return {col: self.__data__[col].copy() for col in self.required_columns}

    @staticmethod
    def checker(data, date = None):
        assert len(data) > 0
        assert data['recent_month_mask'].sum(axis = 1).sum() == len(data['recent_month_mask']), 'recent_month_mask is wrong'
        for k, v in data.items():
            if k == 'raw_factors':
                continue
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
                if su in ['hs300', 'zz500', 'sh50']:
                    if int(df.shape[1]) != int(re.sub("\D", "", su)):
                        warnings.warn('%s has %f stocks' % (k, int(df.shape[1])))
            assert richness > min_data_richness_threshold, '%s richness is %f' % (k, richness)
            if richness < data_richness_threshold:
                warnings.warn('%s richness is %f' % (k, richness))

    def __callback__(self):
        data = self.slicer()
        factor_name = self.__class__.__name__
        factor_raw = self.on_bar(data).loc[self.__trade_date__:]
        assert factor_raw.shape[1] == 1
        if self.ts_norm_bars in [0, 1]:
            factor_norm = factor_raw
        else:
            factor_raw_whole = pd.concat([self.__data__['raw_factors'][factor_name], factor_raw], axis=0)
            if self.ts_norm_method == 'ts_rank':
                factor_norm = ts_rank(factor_raw_whole, self.ts_norm_bars)
            elif self.ts_norm_method == 'rolling_norm':
                factor_norm = rolling_norm(factor_raw_whole, self.ts_norm_bars)
        if len(factor_raw) == 0:
            warnings.warn(f'{factor_name} returned no data')
            raw_score = np.nan
            norm_score = np.nan
        else:
            raw_score = factor_raw.loc[self.__trade_date__, factor_name]
            norm_score = factor_norm.loc[self.__trade_date__, factor_name]
        return {'name': factor_name, 'raw': raw_score, 'norm': norm_score}

    def get_avaliable_columns(self):
        return list(self.__data__.keys())

    def get_data(self):
        return self.__data__

    def get_mdconstant(self, k):
        return self.__mdconstant__.get(k, None)

    def get_available_mdconstants(self):
        return list(self.__mdconstant__.keys())


def prepare_history(trade_date=None, hisdays=30):
    inst = FactorGenerator()
    inst.prepare_hist_data(trade_date=trade_date, hisdays=hisdays)
    inst.dump_hist_data()


def prepare_hot_dummy(trade_date):
    pass


def executor(trade_date=None, max_workers=1):
    subclass_list = FactorGenerator.__subclasses__()
    print('total factor num: %d' % len(subclass_list_cfg))
    # merge hot data
    inst = FactorGenerator()
    inst.merge_hot_data(trade_date=trade_date)

    def get_factors(subcls):
        print('calculating: ', subcls.__name__)
        return subcls().__callback__()

    score_list = list()
    if max_workers == 1:
        for x in subclass_list_cfg:
            score_list.append(get_factors(x))
    else:
        with Pool(processes=max_workers) as pool:
            score_list = pool.map(get_factors, subclass_list)
    factor_score = pd.DataFrame(score_list)
    factor_score = factor_score.set_index('name')
    # call model here

    # dump data
    trade_date = inst.__trade_date__.strftime('%Y%m%d')
    factor_savepath = os.path.join(inst.savepath, trade_date)
    if not os.path.exists(factor_savepath):
        os.makedirs(factor_savepath)
    csvpath = os.path.join(factor_savepath, '%s.csv' % trade_date)
    factor_score.to_csv(csvpath)


