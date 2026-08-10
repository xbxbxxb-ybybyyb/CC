from multiprocessing.pool import Pool
import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import os
import numpy as np
from arrow.naming_config import *
from arrow.utility import *
# from arrow.get_rule_blacklist_df import get_final_data_lastday
import re

class HistoryData:
    def __init__(self, date, hisdays=0):
        self.date = date
        self.hisdays = hisdays
        self.start_date = udt.get_trading_day_offset(date, -1 * hisdays)[0].strftime('%Y%m%d')
        self.tdays_list = [x.strftime('%Y%m%d') for x in udt.get_trading_date_range(self.start_date, self.date)]
        self.next_tdate = udt.get_trading_day_offset(date, 1)[0].strftime('%Y%m%d')
        # self.raw_model_start_date = udt.get_trading_day_offset(date, -1 * factor_raw_histdays)[0].strftime('%Y%m%d')

        univ = pd.read_pickle(universe_path).reset_index()
        self.date_list = [x.strftime('%Y%m%d') for x in sorted(list(set(univ.dt.tolist())))]
        self.universe = univ[univ['dt'] == self.next_tdate].Ticker.tolist()
        self.collector = {'universe':self.universe}

        eod = IO.read_data([self.start_date, self.date], columns = ['S_DQ_LIMIT', 'S_DQ_STOPPING'], alt = eod_path)
        eod = eod.replace(0, np.nan)
        eod = eod.loc[(slice(None), self.universe),:]
        eod = eod.reset_index()
        eod['dt'] = eod['dt'].apply(lambda x:x.strftime('%Y%m%d'))
        eod = eod.set_index(['dt', 'Ticker'])
        self.limit_price = eod['S_DQ_LIMIT'].dropna().to_dict()
        self.stop_price = eod['S_DQ_STOPPING'].dropna().to_dict()

    def update_collector(self, data):
        assert isinstance(data, dict)
        assert len(set(data.keys()) & set(self.collector.keys())) == 0
        self.collector.update(data)

    def get_stock_hisdata(self):
        all_data_dict = {}
        for k,v in name_dict.items():
            data_dict = {}
            for stk in self.universe:
                data_complete = True
                stk_path = os.path.join(data_root, v, stk)
                csv_list = []
                for date in self.tdays_list:
                    csv_path = os.path.join(stk_path, f'{date}.parquet')
                    if not os.path.exists(csv_path):
                        csv_list.append(pd.DataFrame())
                        print(f'{csv_path} not exists')
                        data_complete = False
                        break
                    else:
                        try:
                            csv_df = pd.read_parquet(csv_path)
                        except:
                            csv_list.append(pd.DataFrame())
                            print(f'{csv_path} read with problem')
                            data_complete = False
                            break
                        if len(csv_df) > 0:
                            if k in ['order', 'order_raw']:
                                csv_df = csv_df[(csv_df['OrderType'].isin([1,2,3,10])) & csv_df['OrderBSFlag'].isin([1,2])]
                                if len(csv_df) < 100:
                                    data_complete = False
                                    continue
                                if (str(date), stk) in self.limit_price.keys():
                                    limit_px = self.limit_price[(str(date), stk)]
                                    csv_df.loc[(csv_df.OrderPrice > limit_px) & (csv_df.OrderType.isin([2, 10])) & (csv_df.OrderPrice != 0), 'OrderPrice'] = limit_px
                                if (str(date), stk) in self.stop_price.keys():
                                    stop_px = self.stop_price[(str(date), stk)]
                                    csv_df.loc[(csv_df.OrderPrice < stop_px) & (csv_df.OrderType.isin([2, 10])) & (csv_df.OrderPrice != 0), 'OrderPrice'] = stop_px
                                csv_df.loc[csv_df['OrderType'].isin([1,3]),'OrderPrice'] = np.nan
                                csv_df = csv_df[csv_df.OrderPrice != 0]
                                if len(csv_df) < 100:
                                    data_complete = False
                                    continue
                                csv_df['temp_col'] = round(csv_df['OrderPrice'].rolling(10,min_periods = 5).mean(),2)
                                csv_df['OrderPrice'] = csv_df['OrderPrice'].fillna(csv_df['temp_col']).fillna(method = 'ffill')
                                csv_df = csv_df.drop(['temp_col'], axis = 1)
                            csv_list.append(csv_df)
                        else:
                            data_complete = False
                            break 
                if data_complete:
                    stk_data = pd.concat(csv_list)
                    stk_data['dt'] = pd.to_datetime(stk_data['dt'])
                    stk_data = stk_data.set_index('dt').between_time(auction_start_time, data_end_time).sort_index().reset_index()
                    if k == 'transaction':
                        stk_data.loc[stk_data.TradeBuyNo > stk_data.TradeSellNo, 'TradeBSFlag'] = 1
                        stk_data.loc[stk_data.TradeBuyNo < stk_data.TradeSellNo, 'TradeBSFlag'] = 2
                    data_dict[stk] = stk_data
            all_data_dict[k] = data_dict
        return all_data_dict

    def get_hist_factor(self):
        start_date_ago = udt.get_trading_day_offset(self.date, -1 * (histfactor_days - 1))[0].strftime('%Y%m%d')
        histfactor = IO.read_data([start_date_ago, self.date], alt = histfactor_path)
        return {'histfactor' : histfactor}

    def get_hist_daily_data(self):
        start_date_ago = udt.get_trading_day_offset(self.date, -60)[0].strftime('%Y%m%d')
        daily_data = IO.read_data([start_date_ago, self.date], alt = eod_path)
        return {'daily_data' : daily_data}

    # def get_mad_startdate(self):
    #     d_dict = {}
    #     for x in mad_periods:
    #         d_dict[x] = self.date_list[max(self.date_list.index(self.next_tdate) - (x - 1), 0)]
    #     return {'mad_startdate':d_dict}

    def get_dummy(self):
        from xquant.factordata import FactorData
        s = FactorData()

        univ = pd.read_pickle(universe_path).loc[self.next_tdate].reset_index()
        dt = univ.dt[0].strftime('%Y%m%d')
        trading_days = [pd.Timestamp(x) for x in s.tradingday(dt, (pd.Timestamp(dt) + datetime.timedelta(days = 60)).strftime('%Y%m%d'))]
        next_day_gap = np.array([(trading_days[x+1] - trading_days[x]).days for x in range(len(trading_days) - 1)])

        long_vacation_dates = np.array(trading_days[:-1])[(next_day_gap >= 4) & (next_day_gap <= 5)]
        long_vacation_deltas = np.array([[x.days for x in y - long_vacation_dates] for y in trading_days])
        long_vacation = np.array(trading_days)[((long_vacation_deltas <= 0) & (long_vacation_deltas >= -13)).any(axis = 1)]
        univ['long_vacation_3'] = [1 * (x in long_vacation) for x in univ.dt]

        long_vacation_dates = np.array(trading_days[:-1])[(next_day_gap >= 6) & (next_day_gap <= 7)]
        long_vacation_deltas = np.array([[x.days for x in y - long_vacation_dates] for y in trading_days])
        long_vacation = np.array(trading_days)[((long_vacation_deltas <= 0) & (long_vacation_deltas >= -13)).any(axis = 1)]
        univ['long_vacation_5'] = [1 * (x in long_vacation) for x in univ.dt]

        long_vacation_dates = np.array(trading_days[:-1])[(next_day_gap >= 8) & (next_day_gap <= 100)]
        long_vacation_deltas = np.array([[x.days for x in y - long_vacation_dates] for y in trading_days])
        long_vacation = np.array(trading_days)[((long_vacation_deltas <= 0) & (long_vacation_deltas >= -13)).any(axis = 1)]
        univ['long_vacation_7'] = [1 * (x in long_vacation) for x in univ.dt]

        result = pd.get_dummies(univ.set_index(['dt', 'Ticker'])[['long_vacation_3', 'long_vacation_5', 'long_vacation_7']])
        
        return {'dummy':result}

    # def get_factor_scope(self):
    #     start_date_ago = udt.get_trading_day_offset(self.date, -1 * (factor_clip_scope_days - 1))[0].strftime('%Y%m%d')
    #     factor = IO.read_data([start_date_ago, self.date], alt = rawfactor_path)
    #     up_base = factor.quantile(0.995)
    #     down_base = factor.quantile(0.005)
    #     up_adjust = factor[right_95_list].quantile(0.95)
    #     down_adjust = factor[left_5_list].quantile(0.05)
    #     up_base.update(up_adjust)
    #     down_base.update(down_adjust)
    #     up_base = up_base.append(pd.Series([10000] * 3, index = ['factor_openPct', 'factor_s1_high_to_limit', 'factor_s2_high_to_limit']))
    #     down_base = down_base.append(pd.Series([-10000] * 3, index = ['factor_openPct', 'factor_s1_high_to_limit', 'factor_s2_high_to_limit']))
    #     return {'factor_clip_scope' : {'up':up_base, 'down':down_base}}

    def get_rule_balcklist_df(self):
        return {'rule_blacklist_df':get_final_data_lastday(self.next_tdate)}

    def get_raw_model(self):
        pass

    def get_model_file(self):
        pass
        
    def get_all(self, data_kind = 'all'):
        if data_kind == 'all':
            self.update_collector(self.get_stock_hisdata())
            self.update_collector(self.get_hist_daily_data())
            self.update_collector(self.get_hist_factor())
            self.update_collector(self.get_dummy())
            # self.update_collector(self.get_factor_scope())
            # self.update_collector(self.get_mad_startdate())
            self.update_collector(self.get_rule_balcklist_df())
        elif data_kind == 'data':
            self.update_collector(self.get_stock_hisdata())
            self.update_collector(self.get_hist_daily_data())
        elif data_kind == 'factor':
            self.update_collector(self.get_hist_factor())
            self.update_collector(self.get_dummy())
            # self.update_collector(self.get_factor_scope())
            # self.update_collector(self.get_mad_startdate())
            self.update_collector(self.get_rule_balcklist_df())
     
class HotData:
    def __init__(self, ref_date=None):
        if ref_date is None:
            ref_date = pd.Timestamp.now().date()
        self.ref_date = IO.str_date_parser(ref_date).strftime('%Y%m%d')

    # 记得处理transaction中的bsflag
    def get_all(self, kind = 'history'):
        if kind == 'history':
            return pd.read_pickle(os.path.join(hot_root, self.ref_date, 'hot.pkl'))
        elif kind == 'today':
            return pd.read_pickle(os.path.join(hot_today_root, self.ref_date, 'hot.pkl'))