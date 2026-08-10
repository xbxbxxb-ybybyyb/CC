from multiprocessing.pool import Pool
import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import os
import numpy as np
from overnight.naming_config import *
from overnight.utility import *
import re

class HistoryData:
    def __init__(self, date, hisdays=30):
        self.collector = dict()
        self.date = date
        self.hisdays = hisdays
        self.start_date = udt.get_trading_day_offset(date, -1 * hisdays)[0].strftime('%Y%m%d')

    def update_collector(self, data):
        assert isinstance(data, dict)
        assert len(set(data.keys()) & set(self.collector.keys())) == 0
        self.collector.update(data)

    def get_mask_for_future_data(self, start_date, end_date):
        contract = get_trade_contract(start_date, end_date, prod_id='IC.CFE')
        contract.loc[contract.index[-1] + pd.Timedelta('1D')] = np.nan
        trading_dates = udt.get_trading_date_range(contract.index[0], contract.index[-1])
        contract = contract.resample('1Min').ffill()
        contract['date'] = pd.to_datetime(contract.index.date)
        contract = contract.loc[contract.date.isin(trading_dates)]
        contract = pd.concat([contract.between_time(futures_data_morning_begin, futures_data_morning_end),
                              contract.between_time(futures_data_afternoon_begin, futures_data_afternoon_end)], axis=0).sort_index()
        contract['Flag'] = True
        mask = contract.reset_index().set_index(['dt', 'contract'])['Flag'].unstack().fillna(False)
        return mask

    def get_future_hisdata(self):
        mask = self.get_mask_for_future_data(self.start_date, self.date)
        collist = ['open', 'close', 'high', 'low', 'amount', 'volume', 'vwap', 'position']
        futures_data = IO.read_data([self.start_date, str(self.date)+'235959'], columns=collist, alt=futures_data_path)
        futures_data = futures_data.reset_index()
        futures_data['contract'] = futures_data.Ticker.apply(lambda x: re.sub("\D", "", x))
        futures_data['Ticker'] = futures_data.Ticker.apply(lambda x: ''.join(re.findall(r'\D+', x)))
        futures_data = futures_data.set_index(['dt', 'contract', 'Ticker'])
        df = futures_data.unstack(level = 1)
        target_data = {}
        for x in df.index.get_level_values(1).unique():
            d = df.xs(x, level = 1)
            for c in d.columns.get_level_values(0).unique():
                target_data['%s_%s' % (c, x)] = d[c].reindex(mask.index)
        maskclist = mask.columns.tolist()
        allclist = target_data[list(target_data.keys())[0]].columns.tolist()
        reslist = list(set(allclist) - set(maskclist))
        for c in reslist:
            mask[c] = False
        mask = mask.sort_index(axis = 1)
        target_data['recent_month_mask'] = mask
        return target_data

    def get_spot_hisdata(self):
        spotdaily_start_date = udt.get_trading_day_offset(self.date, -1 * 200)[0].strftime('%Y%m%d')
        target_data = {}
        for x in spot_list:
            spot = pd.read_pickle(os.path.join(spot_data_path, 'indexMinute_%s.pkl' % x.split('.')[0]), compression='gzip')
            spot = spot.loc[int(spotdaily_start_date): self.date].reset_index()
            spot['dt'] = spot['dt'] * 1E6 + spot['minute'] * 100
            spot['dt'] = pd.to_datetime(spot['dt'].astype('int64'), format='%Y%m%d%H%M%S')
            spot_daily = spot.rename(columns = {'amt':'amount'}).set_index('dt').drop(['Ticker','minute'], axis = 1)
            spot_minute = spot_daily.loc[self.start_date: str(self.date)]
            for key in spot_minute.columns:
                target_data['%s_%s' % (key, x)] = spot_minute[key]
            spot_daily  = spot_daily.between_time(minute_to_daily_start_time, minute_to_daily_stop_time)
            idx_date_list = pd.to_datetime(spot_daily.index.date)
            spot_daily = spot_daily.groupby(idx_date_list).agg(minute_to_daily_rule)
            for key in spot_daily.columns:
                target_data['%s_%s_daily_%s' % (key, x, minute_to_daily_tag)] = spot_daily[key]
        return target_data

    def get_kzz_and_stock_hisdata(self):
        target_data = IO.read_data([self.start_date, self.date], alt = )
        return target_data



    def get_all(self):
        self.update_collector(self.get_alla_daily_hisdata())
        self.update_collector(self.get_future_hisdata())
        self.update_collector(self.get_gc_hisdata())
        self.update_collector(self.get_spot_hisdata())
        self.update_collector(self.get_stock_hisdata())
        self.update_collector(self.get_weight_daily_hisdata())
        self.update_collector(self.get_raw_factor_hisdata())
        for k in ['weight_zz500_daily', 'weight_hs300_daily', 'weight_sh50_daily']:
            self.collector[k.replace('_daily', '')] = self.collector[k].reindex(self.collector['close_alla'].index, method = 'pad')


class HotData:
    def __init__(self, ref_date=None, mode = 'realtime'):
        assert mode in ['realtime', 'history']
        if ref_date is None:
            ref_date = pd.Timestamp.now().date()
        self.ref_date = IO.str_date_parser(ref_date)
        self.collector = dict()
        if mode == 'realtime':
            self.hotdir = 'hot'
        elif mode == 'history':
            self.hotdir = 'hot_proof'

    def get_weight_daily_hotdata(self):
        last_tday = int(udt.get_trading_day_offset(self.ref_date, -1)[0].strftime('%Y%m%d'))
        iw = IO.read_data(last_tday, ftype=FType.INDEXWEIGHT, dsource=DSource.CSI)
        target_data = {}
        for k in iw.columns:
            weight_daily = iw[iw[k] > 0][[k]].unstack()[k]
            weight_daily.index = [self.ref_date]
            weight_daily.index.names = ['dt']
            target_data['_'.join(k.split('_')[1:] + ['daily'])] = weight_daily
        return target_data

    def get_all(self):
        a = pd.read_hdf(os.path.join(trade_root, self.hotdir, self.ref_date.strftime('%Y%m%d'),
                       'alla_kline_1min_%s_%s.h5' % (trade_start_time.strftime('%H%M%S'), trade_mid_time.strftime('%H%M%S'))))
        b = pd.read_hdf(os.path.join(trade_root, self.hotdir, self.ref_date.strftime('%Y%m%d'),
                       'alla_kline_1min_%s_%s.h5' % (trade_mid_time.strftime('%H%M%S'), trade_stop_time.strftime('%H%M%S'))))
        final_kline = pd.concat([a, b], axis=0, sort=False)
        suspension = final_kline[['volume']].unstack()['volume'].sum()
        suspension_stk_list = suspension[suspension <= 0].index.tolist()
        final_kline.loc[(slice(None),suspension_stk_list),:] = np.nan
        edb = pd.read_hdf(os.path.join(trade_root, self.hotdir, self.ref_date.strftime('%Y%m%d'), 'edb.h5'))
        mdconstant = pd.read_hdf(os.path.join(trade_root, self.hotdir, self.ref_date.strftime('%Y%m%d'), 'mdconstant.h5'))
        misc_minute = pd.read_hdf(os.path.join(trade_root, self.hotdir, self.ref_date.strftime('%Y%m%d'), 'misc_minute_%s.h5' % trade_stop_time.strftime('%H%M'))).sort_index()
        # format data
        target_data = self.get_weight_daily_hotdata()
        for col in edb.columns:
            target_data[col] = edb[col].dropna()

        misc_minute['PROD_ID'] = [''.join(re.findall(r'\D+', x)) for x in misc_minute.index.get_level_values(1).tolist()]
        futures_list = [x for x in misc_minute.PROD_ID.unique().tolist() if x.split('.')[-1] in ['CFE']]
        futures_minute = misc_minute[misc_minute.PROD_ID.isin(futures_list)].reset_index()
        futures_minute['Ticker'] = futures_minute.Ticker.apply(lambda x:re.sub("\D", "", x))
        futures_minute = futures_minute.set_index(['dt','PROD_ID','Ticker']).unstack(level=[1,2])
        for x in futures_minute.columns.get_level_values(0).unique().tolist():
            for y in futures_minute.columns.get_level_values(1).unique().tolist():
                target_data['%s_%s' % (x, y)] = futures_minute[x][y]
        non_futures_minute = misc_minute[~misc_minute.PROD_ID.isin(futures_list)].drop(['vwap', 'position', 'PROD_ID'], axis = 1)
        for ticker in non_futures_minute.index.get_level_values(1).unique():
            temp = non_futures_minute.xs(ticker, level = 1)
            temp_minute = temp.add_suffix('_%s' % ticker)
            for col in temp_minute.columns:
                target_data[col] = temp_minute[col]
            if ticker in spot_list:
                temp_daily = temp.between_time(minute_to_daily_start_time, minute_to_daily_stop_time)
                idx_date_list = pd.to_datetime(temp_daily.index.date)
                temp_daily = temp_daily.groupby(idx_date_list).agg(minute_to_daily_rule)
                for key in temp_daily.columns:
                    target_data['%s_%s_daily_%s' % (key, ticker, minute_to_daily_tag)] = temp_daily[key]
        recent_month_contract = get_current_futures_contract('IC.CFE', trade_date=self.ref_date.strftime('%Y%m%d'))
        recent_month_contract = re.sub("\D", "", recent_month_contract)
        mask = target_data['close_IC.CFE']
        mask = pd.DataFrame(False, index = mask.index, columns = mask.columns)
        mask[recent_month_contract] = True
        target_data['recent_month_mask'] = mask

        mdconstant.index.names = ['Ticker']
        mdconstant['dt'] = self.ref_date
        mdconstant = mdconstant.reset_index().set_index(['dt','Ticker'])
        collist = mdconstant.columns
        temp = mdconstant.unstack()
        for col in collist:
            target_data['%s_alla_daily' % col] = temp[col]
        idx_date_list = pd.to_datetime(final_kline['open'].unstack().index.date)
        final_kline_unstacked = final_kline.unstack()
        target_data['open_alla_daily'] = final_kline_unstacked['open'].fillna(method = 'bfill').groupby(idx_date_list).first()
        target_data['high_alla_daily'] = final_kline_unstacked['high'].groupby(idx_date_list).max()
        target_data['low_alla_daily'] = final_kline_unstacked['low'].groupby(idx_date_list).min()
        target_data['close_alla_daily'] = final_kline_unstacked['close'].fillna(method = 'ffill').groupby(idx_date_list).last()
        target_data['volume_alla_daily'] = final_kline_unstacked['volume'].groupby(idx_date_list).sum()
        target_data['amount_alla_daily'] = final_kline_unstacked['amount'].groupby(idx_date_list).sum()
        for key in final_kline.columns:
            target_data[key + '_alla'] = final_kline_unstacked[key]
        for k in ['weight_zz500_daily', 'weight_hs300_daily', 'weight_sh50_daily']:
            target_data[k.replace('_daily', '')] = target_data[k].reindex(target_data['close_alla'].index, method = 'pad')
        self.collector = target_data

