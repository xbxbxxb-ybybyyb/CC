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
        self.date = date # 生成日期
        self.hisdays = hisdays # 历史数据天数
        self.start_date = udt.get_trading_day_offset(date, -1 * hisdays)[0].strftime('%Y%m%d') #开始日期

    def update_collector(self, data):
        assert isinstance(data, dict)
        assert len(set(data.keys()) & set(self.collector.keys())) == 0
        self.collector.update(data)

    def get_mask_for_future_data(self, start_date, end_date):
        u = get_trade_contract(start_date, end_date, prod_id='IC.CFE')
        u = u.reset_index().rename(columns = {'dt':'date'})[['date','contract']].set_index('date')

        t_days_list = udt.get_trading_date_range(str(u.index[0].date()).replace('-',''),str(u.index[-1].date()).replace('-',''))
        t_days_list = [str(i)[:10] for i in t_days_list]
        t_mins_list = pd.date_range(futures_data_morning_begin, futures_data_morning_end, freq='min').to_list() + \
                      pd.date_range(futures_data_afternoon_begin, futures_data_afternoon_end, freq='min').to_list()
        t_mins_list = [str(i)[-8:] for i in t_mins_list]
        index_list = []
        for d in t_days_list:
            for m in t_mins_list:
                index_list.append(d + ' ' + m)
        index_df = pd.DataFrame({'dt':index_list})
        index_df['dt'] = pd.to_datetime(index_df['dt'])
        index_df['date'] = index_df.dt.apply(lambda x:x.date())
        index_df = index_df.set_index('date')
        udf = index_df.join(u).reset_index().set_index(['dt', 'contract']).sort_index()
        udf['date'] = True
        udf = udf.unstack().droplevel(0, axis = 1)
        mask = udf == True
        return mask

    def get_future_hisdata(self):
        mask = self.get_mask_for_future_data(self.start_date, self.date)

        collist = ['open', 'close', 'high', 'low', 'amount', 'volume', 'vwap', 'position']
        futures_data = IO.read_data([self.start_date, str(self.date)+'235959'],columns = collist, alt=future_data_path)
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
        target_data = {}
        for x in ['000300.SH','000905.SH','000016.SH']:
            spot = pd.read_pickle(os.path.join(spot_data_path, 'indexMinute_%s.pkl' % x[:-3]), compression='gzip')
            spot = spot.loc[int(self.start_date): self.date].reset_index()
            spot['dt'] = spot['dt'] * 1E6 + spot['minute'] * 100
            spot['dt'] = pd.to_datetime(spot['dt'].astype('int64'), format='%Y%m%d%H%M%S')
            spot = spot.rename(columns = {'amt':'amount'}).set_index('dt').drop(['Ticker','minute'], axis = 1)
            for key in spot.columns:
                target_data['%s_%s' % (key, x)] = spot[key]
        return target_data

    def get_gc_hisdata(self):
        gcticker_list = ['204001.SH']
        gc_data = IO.read_data([self.start_date, str(self.date)+'235959'], columns=['open','high','low','close', 'volume', 'amount'], alt= gc_hispath)
        target_data = {}
        for gcticker in gcticker_list:
            data = gc_data.xs(gcticker, level = 1).add_suffix('_%s' % gcticker)
            for key in data.columns:
                target_data[key] = data[key]
        return target_data

    def get_stock_hisdata(self):
        zz500_stock_list, hs300_stock_list, zz800_stock_list, _ = get_constituent_stock_list(self.date)
        datelist = [x.strftime('%Y%m%d') for x in udt.get_trading_date_range(self.start_date, self.date)]
        stkdf_list = []
        for tday in datelist:
            stkdf = pd.read_pickle(os.path.join(stock_minute_per_date_path, tday + '.pkl'), compression='gzip')
            stkdf_list.append(stkdf)
        stk_full_mins_data = pd.concat(stkdf_list, axis = 0).reset_index()
        stk_full_mins_data['Ticker'] = stk_full_mins_data.Ticker.map(ticker_match)
        stk_full_mins_data['dt'] = stk_full_mins_data['dt'] * 1E6 + stk_full_mins_data['minute'] * 100
        stk_full_mins_data['dt'] = pd.to_datetime(stk_full_mins_data['dt'].astype('int64'), format='%Y%m%d%H%M%S')
        stk_full_mins_data = stk_full_mins_data.drop(['minute'], axis = 1)
        stk_full_mins_data = stk_full_mins_data.rename(columns = {'amt':'amount'}).set_index(['dt','Ticker']).sort_index()
        zz800df = stk_full_mins_data.loc[(slice(None),zz800_stock_list),:]
        zz500df = zz800df.loc[(slice(None),zz500_stock_list),:].add_suffix('_zz500')
        hs300df = zz800df.loc[(slice(None),hs300_stock_list),:].add_suffix('_hs300')
        zz800df = zz800df.add_suffix('_zz800')
        stk_full_mins_data = stk_full_mins_data.add_suffix('_alla')
        target_data = {}
        for df in [zz500df, hs300df, zz800df, stk_full_mins_data]:
            columns = df.columns
            df = df.unstack()
            for key in columns:
                target_data[key] = df[key]
        return target_data

    def get_alla_zz800_daily_hisdata(self):
        eod = IO.read_data([self.start_date, self.date],columns=['S_DQ_PRECLOSE','S_DQ_OPEN','S_DQ_HIGH','S_DQ_LOW','S_DQ_CLOSE','S_DQ_AMOUNT','S_DQ_VOLUME','S_DQ_LIMIT','S_DQ_STOPPING'], alt =alla_eod_path)
        md = IO.read_data([self.start_date, self.date], columns = ['adjfactor'])
        eod = eod.join(md, how = 'left')
        eod = eod.rename(columns = {x:str.lower(x.split('_')[-1]) + '_alla_daily' for x in eod.columns})
        clist = eod.columns.tolist()
        target_data = {}
        eod = eod.unstack()
        for key in clist:
            if 'volume' in key:
                target_data[key] = eod[key] * 100
            elif 'amount' in key:
                target_data[key] = eod[key] * 1000
            else:
                target_data[key] = eod[key]
        # 以上是全A的daily数据，以下是zz800的daily数据
        zz500_stock_list, hs300_stock_list, zz800_stock_list, _ = get_constituent_stock_list(self.date)
        datelist = udt.get_trading_date_range(self.start_date, self.date)
        df = pd.DataFrame(np.zeros((len(datelist),len(zz800_stock_list))),index=datelist,columns=zz800_stock_list)
        df.index.names = ['dt']
        df.columns.names = ['Ticker']
        df = df.stack().to_frame()
        df.columns = ['num']
        df = df.swaplevel().sort_index()
        ashare = IO.read_data([20080710, 21000101],columns = ['CHANGE_DT', 'FLOAT_A_SHR'],  dtable=DTable.AShareCapitalization)
        ashare = ashare.reset_index()
        ashare['CHANGE_DT'] = ashare['CHANGE_DT'].astype('int').astype('str')
        ashare['dt'] = pd.to_datetime(ashare['CHANGE_DT'])
        ashare = ashare[ashare.Ticker.isin(zz800_stock_list)]
        ashare = ashare.set_index(['Ticker','dt']).drop(['CHANGE_DT'], axis = 1).sort_index()
        ashare = ashare.loc[~ashare.index.duplicated()]
        temp = ashare.join(df, how = 'outer')
        temp = temp[['FLOAT_A_SHR']].unstack(level = 0).fillna(method = 'ffill')
        temp = temp.loc[datelist].stack()
        temp.columns = ['float_share_zz800_daily']
        target_data['float_share_zz800_daily'] = temp.unstack(level = 1)['float_share_zz800_daily'][zz800_stock_list]
        target_data['preclose_zz800_daily'] = target_data['preclose_alla_daily'][zz800_stock_list]
        return target_data

    def get_weight_daily_hisdata(self):
        iw_start_date = udt.get_trading_day_offset(self.date, -1 * (self.hisdays + 1))[0].strftime('%Y%m%d') #开始日期
        iw = IO.read_data([iw_start_date, self.date], ftype=FType.INDEXWEIGHT, dsource=DSource.CSI)    
        iw = iw.unstack().shift(1).stack()
        target_data = {}
        for k in iw.columns:
            weight_daily = iw[iw[k] > 0][[k]].unstack()[k]
            target_data['_'.join(k.split('_')[1:] + ['daily'])] = weight_daily
            # weight_zz500 = weight_zz500_daily.reindex(a['close_zz500'].index, method='pad')
        return target_data

    def get_all(self):
        self.update_collector(self.get_alla_zz800_daily_hisdata())
        self.update_collector(self.get_future_hisdata())
        self.update_collector(self.get_gc_hisdata())
        self.update_collector(self.get_spot_hisdata())
        self.update_collector(self.get_stock_hisdata())
        self.update_collector(self.get_weight_daily_hisdata())

        for k in ['weight_zz500_daily', 'weight_hs300_daily', 'weight_sh50_daily']:
            self.collector[k.replace('_daily', '')] = self.collector[k].reindex(self.collector['close_zz800'].index, method = 'pad')



class HotData:
    def __init__(self, ref_date=None):
        if ref_date is None:
            ref_date = pd.Timestamp.now().date()
        self.ref_date = IO.str_date_parser(ref_date)
        self.collector = dict()

    def get_weight_daily_hotdata(self):
        last_tday = int(udt.get_trading_day_offset(self.ref_date,-1)[0].strftime('%Y%m%d'))
        iw = IO.read_data(last_tday, ftype=FType.INDEXWEIGHT, dsource=DSource.CSI) 
        target_data = {}
        for k in iw.columns:
            weight_daily = iw[iw[k] > 0][[k]].unstack()[k]
            weight_daily.index = [self.ref_date]
            weight_daily.index.names = ['dt']
            target_data['_'.join(k.split('_')[1:] + ['daily'])] = weight_daily
        return target_data

    def get_all(self):
        a = pd.read_hdf(os.path.join(trade_root, 'hot', self.ref_date.strftime('%Y%m%d'),
                       'alla_kline_1min_%s_%s.h5' % (trade_start_time.strftime('%H%M%S'), trade_mid_time.strftime('%H%M%S'))))
        b = pd.read_hdf(os.path.join(trade_root, 'hot', self.ref_date.strftime('%Y%m%d'),
                       'alla_kline_1min_%s_%s.h5' % (trade_mid_time.strftime('%H%M%S'), trade_stop_time.strftime('%H%M%S'))))
        final_kline = pd.concat([a, b], axis=0, sort=False)
        edb = pd.read_hdf(os.path.join(trade_root, 'hot', self.ref_date.strftime('%Y%m%d'), 'edb.h5'))
        mdconstant = pd.read_hdf(os.path.join(trade_root, 'hot', self.ref_date.strftime('%Y%m%d'), 'mdconstant.h5'))
        misc_minute = pd.read_hdf(os.path.join(trade_root, 'hot', self.ref_date.strftime('%Y%m%d'), 'misc_minute.h5'))
        # format data
        target_data = self.get_weight_daily_hotdata()
        for col in edb.columns:
            target_data[col] = edb[col].dropna()

        mask_ticker_list = [x for x in misc_minute.index.get_level_values(1).unique() if x.endswith('CFE')]
        mask_ticker = {re.sub("\D", "", ticker) for ticker in mask_ticker_list}
        assert len(mask_ticker) == 1
        indexlist = misc_minute.loc[(slice(None), mask_ticker_list),:].index.get_level_values(0).unique()
        mask = pd.DataFrame(data=[True for x in indexlist],index=indexlist, columns = list(mask_ticker))
        target_data['recent_month_mask'] = mask.sort_index()

        for ticker in misc_minute.index.get_level_values(1).unique():
            if ticker.split('.')[-1] in ['CFE']:
                contract = re.sub("\D", "", ticker)
                kind = ''.join(re.findall(r'\D+', ticker))
                temp = misc_minute.xs(ticker, level = 1).add_suffix('_%s' % kind)
                for col in temp.columns:
                    coldf = temp[[col]]
                    coldf.columns = [contract]
                    target_data[col] = coldf.reindex(mask.index)
            else:
                temp = misc_minute.xs(ticker, level = 1).add_suffix('_%s' % ticker)
                for col in temp.columns:
                    if col.split('_')[0] in ['position', 'vwap']:
                        continue
                    target_data[col] = temp[col]

        mdconstant.index.names = ['Ticker']
        mdconstant['dt'] = self.ref_date
        mdconstant = mdconstant.reset_index().set_index(['dt','Ticker'])
        collist = mdconstant.columns
        temp = mdconstant.unstack()
        for col in collist:
            target_data['%s_alla_daily' % col] = temp[col]

        last_tday = int(udt.get_trading_day_offset(self.ref_date,-1)[0].strftime('%Y%m%d'))
        zz500_stock_list, hs300_stock_list, zz800_stock_list, _ = get_constituent_stock_list(last_tday)

        target_data['preclose_zz800_daily'] = target_data['preclose_alla_daily'][zz800_stock_list]

        target_data['open_alla_daily'] = final_kline[['open']].unstack()['open'].fillna(method = 'bfill').resample('D').first()
        target_data['high_alla_daily'] = final_kline[['high']].unstack()['high'].resample('D').max()
        target_data['low_alla_daily'] = final_kline[['low']].unstack()['low'].resample('D').min()
        target_data['close_alla_daily'] = final_kline[['close']].unstack()['close'].fillna(method = 'ffill').resample('D').last()
        target_data['volume_alla_daily'] = final_kline[['volume']].unstack()['volume'].resample('D').sum()
        target_data['amount_alla_daily'] = final_kline[['amount']].unstack()['amount'].resample('D').sum()

        zz800df = final_kline.loc[(slice(None),zz800_stock_list),:]
        zz500df = zz800df.loc[(slice(None),zz500_stock_list),:].add_suffix('_zz500')
        hs300df = zz800df.loc[(slice(None),hs300_stock_list),:].add_suffix('_hs300')
        zz800df = zz800df.add_suffix('_zz800')
        final_kline = final_kline.add_suffix('_alla')
        for df in [zz500df, hs300df, zz800df, final_kline]:
            columns = df.columns
            df = df.unstack()
            for key in columns:
                target_data[key] = df[key]

        for k in ['weight_zz500_daily', 'weight_hs300_daily', 'weight_sh50_daily']:
            target_data[k.replace('_daily', '')] = target_data[k].reindex(target_data['close_zz800'].index, method = 'pad')

        self.collector = target_data