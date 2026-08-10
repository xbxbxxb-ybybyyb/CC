from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from overnight.data_center import HistoryData, HotData
from overnight.naming_config import *
from overnight.utility import *
from overnight.signal_dealer import signal_dealer
import pandas as pd
import numpy as np
import importlib
import os
import datetime
import warnings
import bottleneck as bk
from multiprocessing import Pool
from xquant.xqutils.helper import link
lm = link.LinkMessage()

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
    def prepare_hist_data(inst, trade_date=None, hisdays=15):
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
        diller(os.path.join(save_path, 'history_%s.pkl' % minute_to_daily_tag), (inst.__trade_date__, inst.__data__, inst.__mdconstant__))

    @classmethod
    def load_hist_data(inst, trade_date=None):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        save_path = os.path.join(trade_root, 'history', trade_date.strftime('%Y%m%d'))
        _trade_date, _data, _mdconstant = diller(os.path.join(save_path, 'history_%s.pkl' % minute_to_daily_tag))
        assert _trade_date == trade_date
        inst.__trade_date__ = _trade_date
        inst.__data__ = _data
        inst.__mdconstant__ = _mdconstant

    @classmethod
    def merge_hot_data(inst, trade_date=None, mode='realtime'):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        # load history data
        inst.load_hist_data(trade_date=trade_date)
        hist_data = inst.__data__
        # retrieve hot data
        hd = HotData(trade_date, mode = mode)
        hd.get_all()
        hot_data = hd.collector
        inst.checker(hot_data, date = trade_date)
        # combine history and hot
        prod_data = {}
        # preadj
        alla_ticker_list = sorted(list(set(hot_data['adjfactor_alla_daily'].columns) & \
                                       set(hist_data['close_alla'].columns) & \
                                       set(hot_data['close_alla'].columns) & \
                                       set(hist_data['close_alla_daily'].columns) & \
                                       set(hot_data['close_alla_daily'].columns)))
        # handle weight stock list
        for k, v in inst.__mdconstant__.items():
            inst.__mdconstant__[k] = sorted(list(set(v) & set(alla_ticker_list)))

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
            elif k.endswith('.SH') or k.endswith('.CFE') or k.endswith('_daily') or \
                 k.endswith('_daily_%s' % minute_to_daily_tag) or (k.split('_')[-1] in ['zz500','hs300','sh50','preadj']):
                prod_data[k] = pd.concat([hist_data[k], v], axis=0, sort=False)
            elif k.endswith('_mask'):
                prod_data[k] = pd.concat([hist_data[k], v], axis=0, sort=False).fillna(False).astype('bool')
            elif k.endswith('_alla'):
                minute_to_daily = pd.concat([hist_data[k], v], axis=0, sort=False)
                prod_data[k] = minute_to_daily
                minute_to_daily = minute_to_daily.between_time(minute_to_daily_start_time, minute_to_daily_stop_time).sort_index()
                idx_date_list = pd.to_datetime(minute_to_daily.index.date)
                if k.startswith('open'):
                    minute_to_daily = minute_to_daily.groupby(idx_date_list).fillna(method = 'bfill')
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).first()
                elif k.startswith('high'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).max()
                elif k.startswith('low'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).min()
                elif k.startswith('close'):
                    minute_to_daily = minute_to_daily.groupby(idx_date_list).fillna(method='ffill')
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).last()
                elif k.startswith('volume'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).sum()
                elif k.startswith('amount'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).sum()
        float_share_alla_daily = hist_data['float_share_alla_daily']
        float_share_alla_daily.loc[trade_date] = np.nan
        prod_data['float_share_alla_daily'] = float_share_alla_daily.fillna(method='ffill')
        prod_data['raw_factors'] = hist_data['raw_factors']
        for k in prod_data.keys():
            if '_alla' in k:
                prod_data[k] = prod_data[k][alla_ticker_list]

        # sort futures data columns
        futures_column_list = sorted(prod_data['recent_month_mask'].columns.tolist())
        for k in prod_data.keys():
            if k.endswith('.CFE') or ('mask' in k):
                prod_data[k] = prod_data[k][futures_column_list]

        inst.__data__ = prod_data

    def slicer(self):
        return {col: self.__data__[col].copy() for col in self.required_columns}

    @staticmethod
    def checker(data, date = None):
        assert len(data) > 0
        assert data['recent_month_mask'].sum(axis = 1).sum() == len(data['recent_month_mask']), 'recent_month_mask is wrong'
        for k, v in data.items():
            if k in ['raw_factors']:
                continue
            if date is not None:
                assert len(v.loc[date:].dropna(axis = 0, how = 'all')) > 0, '%s %s has no data' % (str(date), k)
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
        try:
            factor_raw = self.on_bar(data).loc[self.__trade_date__:].astype('float64')
        except:
            factor_raw = pd.DataFrame(np.nan,index=[self.__trade_date__],columns=['factor_name'])
        assert factor_raw.shape[1] == 1
        if self.ts_norm_bars in [0, 1]:
            factor_norm = factor_raw
        else:
            factor_raw_whole = pd.concat([self.__data__['raw_factors'][factor_name].astype('float64'), factor_raw], axis=0)
            if self.ts_norm_method == 'ts_rank':
                factor_norm = ts_rank(factor_raw_whole, self.ts_norm_bars)
            elif self.ts_norm_method == 'rolling_norm':
                factor_norm = rolling_norm(factor_raw_whole, self.ts_norm_bars)
        raw_score = factor_raw.loc[self.__trade_date__, factor_name]
        norm_score = factor_norm.loc[self.__trade_date__, factor_name]
        if np.isnan(raw_score) or np.isnan(norm_score):
            warnings.warn(f'{factor_name} returned nan!')
        return {'name': factor_name, 'raw': raw_score, 'norm': norm_score}

    def get_avaliable_columns(self):
        return list(self.__data__.keys())

    def get_data(self):
        return self.__data__

    def get_mdconstant(self, k):
        return self.__mdconstant__.get(k, None)

    def get_available_mdconstants(self):
        return list(self.__mdconstant__.keys())

    def get_spot_close_dict(self):
        target_spot_close_list = ['000905.SH', '000300.SH', '000016.SH']
        return {k:self.__data__['close_%s' % k].iloc[-1] for k in target_spot_close_list}


def prepare_history(trade_date=None, hisdays=15):
    inst = FactorGenerator()
    inst.prepare_hist_data(trade_date=trade_date, hisdays=hisdays)
    inst.dump_hist_data()


def get_factors(subcls):
        print('calculating: ', subcls.__name__)
        return subcls().__callback__()


def executor(trade_date=None, max_workers=12, mode = 'realtime'):
    # load factors
    for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'factors')):
        if f.endswith('.py'):
            importlib.import_module('overnight.factors.%s' % f.split('.')[0])
    subclass_list = FactorGenerator.__subclasses__()
    print('total factor num: %d' % len(subclass_list))
    # merge hot data
    inst = FactorGenerator()
    inst.merge_hot_data(trade_date=trade_date, mode = mode)
    score_list = list()
    if max_workers == 1:
        for x in subclass_list:
            score_list.append(get_factors(x))
    else:
        with Pool(processes=max_workers) as pool:
            score_list = pool.map(get_factors, subclass_list)
    factor_score = pd.DataFrame(score_list).set_index('name')
    if mode == 'history':
        return factor_score
    # call model here
    spot_close_dict = inst.get_spot_close_dict()
    recent_contract = re.sub("\D", "", get_current_futures_contract('IC.CFE',trade_date, mode = 'recent'))
    season_contract = re.sub("\D", "", get_current_futures_contract('IC.CFE',trade_date, mode = 'season'))

    volume_limit_dict = {}
    tdays = [x.strftime('%Y%m%d') for x in udt.get_trading_day_offset(inst.__trade_date__, list(range(-1 * calculate_volume_histdays, 0)))]
    for key in ['IC.CFE', 'IF.CFE', 'IH.CFE']:
        future_kind = key.split('.')[0]
        recent_month_df = inst.__data__['volume_%s' % key][inst.__data__['recent_month_mask']].mean(axis = 1).loc[tdays[0]:tdays[-1]]
        recent_month_df = recent_month_df.between_time(calculate_volume_start_time,calculate_volume_stop_time)
        volume_limit_dict['%s%s' % (future_kind, recent_contract)] = recent_month_df.groupby(recent_month_df.index.date).sum().mean() * calculate_volume_ratio
        season_df = inst.__data__['volume_%s' % key][season_contract].loc[tdays[0]:tdays[-1]]
        season_df = season_df.between_time(calculate_volume_start_time,calculate_volume_stop_time)
        volume_limit_dict['%s%s' % (future_kind, season_contract)] = season_df.groupby(season_df.index.date).sum().mean() * calculate_volume_ratio

    settlement_ratio_dict = {}
    for key in ['IC.CFE', 'IF.CFE', 'IH.CFE']:
        future_close = inst.__data__['close_%s' % key]
        future_mask = inst.__data__['recent_month_mask']
        future_amount = inst.__data__['amount_%s' % key]
        future_volume = inst.__data__['volume_%s' % key]
        amount_sum = ts_sum(future_amount, 60)
        volume_sum = ts_sum(future_volume, 60)
        vwap_60 = (amount_sum / volume_sum)[future_mask].sum(axis=1)
        vwap_60 = vwap_60.iloc[vwap_60.index.indexer_at_time(trade_stop_time)].values[-1]
        close_stop_time = future_close[future_mask].sum(axis=1)
        close_stop_time = close_stop_time.iloc[close_stop_time.index.indexer_at_time(trade_stop_time)].values[-1]
        settlement_ratio_dict[key] = round(vwap_60 / price_per_point[key] / close_stop_time, 5)

    trading_plan_1_0, trading_plan_2_0 = signal_dealer(factor_score['norm'], spot_close_dict, recent_contract, season_contract, volume_limit_dict, settlement_ratio_dict)
    print('-' * 60)
    print('Diamond 1.0:')
    print(trading_plan_1_0)
    # lm.sendMessage('Diamond 1.0:\n' + str(trading_plan_1_0))
    print('-' * 60)
    print('Diamond 2.0:')
    print(trading_plan_2_0)
    lm.sendMessage('Diamond 2.0:\n' + str(trading_plan_2_0))
    # lm.sendMessage('Diamond 1.0:\n' + str(trading_plan_1_0[['Contract', 'Contract_Num','Seconds_Interval']]))
    lm.sendMessage('Diamond 2.0:\n' + str(trading_plan_2_0[['Contract', 'Contract_Num','Seconds_Interval']]))
    print('-' * 60)
    # dump factor
    trade_date = inst.__trade_date__.strftime('%Y%m%d')
    factor_savepath = os.path.join(inst.savepath, '%s' % trade_date)
    if not os.path.exists(factor_savepath):
        os.makedirs(factor_savepath)
    factor_score.to_csv(os.path.join(factor_savepath, '%s.csv' % trade_date))
    # dump trading plan
    trading_plan_savepath = os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')))
    if not os.path.exists(trading_plan_savepath):
        os.makedirs(trading_plan_savepath)
    trading_plan_1_0.to_csv(os.path.join(trading_plan_savepath, '%s_%s_1_0.csv' % (trade_date, trade_stop_time.strftime('%H%M'))))
    trading_plan_2_0.to_csv(os.path.join(trading_plan_savepath, '%s_%s_2_0.csv' % (trade_date, trade_stop_time.strftime('%H%M'))))


