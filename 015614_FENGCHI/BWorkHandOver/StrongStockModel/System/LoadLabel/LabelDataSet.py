# coding: utf-8
# Author：fengchi863
# Date ：2020/7/17 14:09

import numpy as np
import pandas as pd
from StrongStockModel.dataApi.getData import get_minute_1factor, get_daily_1factor
from StrongStockModel.dataApi.stockList import clean_stock_list
from StrongStockModel.dataApi.tradeDate import get_date_range, trade_minutes, get_pre_trade_date
from StrongStockModel.dataApi.usefulTools import frame2arr, arr2frame
from StrongStockModel.conf.path_config import label_path
from StrongStockModel.dataApi.tradeDate import get_pre_trade_date, get_recent_trade_date


class LabelDataSet:
    def __init__(self, start_date=20140101, end_date=20201031):
        pool = clean_stock_list(no_ST=False, least_live_days=1, least_recover_days=1, no_limit_up=True,
                                no_limit_down=True)
        self.pool = pool[pool.columns].loc[start_date:end_date]
        self.date_list = get_date_range(start_date, end_date)
        self.minute_list = trade_minutes
        self.stk_list = self.pool.columns.tolist()
        self.base_date_list = get_date_range(20140101, 20201031)

    def calc_pctchg_N(self, stk_list=None, start_date=None, end_date=None, lag=242, kind='reg', threshold=0, address=label_path, load_local=True):
        if stk_list is None:
            stk_list = self.stk_list
        if start_date is None:
            start_date = self.date_list[0]
        if end_date is None:
            end_date = self.date_list[-1]

        if (lag == 242) and (not address is None) and load_local:
            start_date = get_pre_trade_date(get_recent_trade_date(start_date - 1), offset=-1)
            end_date = get_recent_trade_date(end_date)
            start = self.base_date_list.index(start_date) * 7
            end = self.base_date_list.index(end_date) * 7 + 7
            pct_change = pd.read_hdf(address + 'pct_240m.h5', 'pct_240m', start=start, stop=end)
            pct_change = pct_change[stk_list]
            if kind == 'reg':
                return pct_change
            elif kind == 'clf':
                label = (pct_change > threshold) - 1 * (pct_change <= threshold)
                label[pct_change.isnull()] = np.nan
                return label
        day_lag = lag // 242 + 1
        start_datetime = start_date * 10000 + 925
        end_datetime = get_pre_trade_date(end_date, offset=-day_lag) * 10000 + 1500
        minute_close_price = get_minute_1factor('close_badj', start_datetime, end_datetime, code_list=stk_list)
        minute_close_price_shift = minute_close_price.shift(-lag)
        index, columns = minute_close_price.index.tolist(), minute_close_price.columns.tolist()
        minute_close_price = frame2arr(minute_close_price)
        minute_close_price_shift = frame2arr(minute_close_price_shift)
        minute_pct = minute_close_price_shift / minute_close_price - 1
        if kind == 'reg':
            pct_change = minute_pct
            pct_change[np.isnan(minute_pct)] = np.nan
            label_df = arr2frame(pct_change, index=index, columns=columns)
        elif kind == 'clf':
            pct_change = (minute_pct > threshold) * 1. - 1. * (minute_pct <= threshold)
            pct_change[np.isnan(minute_pct)] = np.nan
            label_df = arr2frame(pct_change, index=index, columns=columns)
        else:
            raise Exception('no parameter kind of %s' % kind)
        date_list = get_date_range(start_date, end_date)
        start_date, end_date = date_list[0], date_list[-1]
        return label_df.loc[(start_date, 925):(end_date, 1500)]

    def calc_pctchg_N_freq_5min(self, stk_list=None, start_date=None, end_date=None, lag=242, kind='reg', threshold=0, address=label_path, load_local=True):
        if stk_list is None:
            stk_list = self.stk_list
        if start_date is None:
            start_date = self.date_list[0]
        if end_date is None:
            end_date = self.date_list[-1]

        if (lag == 242) and (not address is None) and load_local:
            start_date = get_pre_trade_date(get_recent_trade_date(start_date - 1), offset=-1)
            end_date = get_recent_trade_date(end_date)
            start = self.base_date_list.index(start_date) * 48
            end = self.base_date_list.index(end_date) * 48 + 48
            pct_change = pd.read_hdf(address + 'pct_240m_freq_5min.h5', 'pct_240m_freq_5min', start=start, stop=end)
            pct_change = pct_change[stk_list]
            if kind == 'reg':
                return pct_change
            elif kind == 'clf':
                label = (pct_change > threshold) - 1 * (pct_change <= threshold)
                label[pct_change.isnull()] = np.nan
                return label
        else:
            raise Exception('Un-realized function')

    def calc_pctchg_next_N_close(self, stk_list=None, start_date=None, end_date=None, lag=1, kind='reg', threshold=0):
        if stk_list is None:
            stk_list = self.stk_list
        if start_date is None:
            start_date = self.date_list[0]
        if end_date is None:
            end_date = self.date_list[-1]
        start_datetime = start_date * 10000 + 925
        end_datetime = end_date * 10000 + 1500
        minute_close_price = get_minute_1factor('close_badj', start_datetime, end_datetime, code_list=stk_list)
        index, columns = minute_close_price.index.tolist(), minute_close_price.columns.tolist()
        start_date = get_pre_trade_date(self.date_list[0])
        end_date = get_pre_trade_date(self.date_list[-1], offset=-lag)
        date_list = get_date_range(start_date, end_date)
        day_close_price = get_daily_1factor('close_badj', date_list, code_list=stk_list).shift(-lag)
        minute_close_price_arr = frame2arr(minute_close_price)
        day_close_price_arr = day_close_price.values
        day_close_price_arr = np.expand_dims(day_close_price_arr, 0).repeat(242, axis=0)
        label_arr = day_close_price_arr / minute_close_price_arr - 1
        if kind == 'reg':
            label_df = arr2frame(label_arr, index=index, columns=columns)
        elif kind == 'clf':
            label = (label_arr > threshold) * 1. - 1. * (label_arr <= threshold)
            label[np.isnan(label)] = np.nan
            label_df = arr2frame(label, index=index, columns=columns)
        else:
            raise Exception('no parameter kind of %s' % kind)
        return label_df.loc[(start_date, 925):(end_date, 1500)]

# if __name__ == '__main__':
#     lds = LabelDataSet()
#     label_df = lds.calc_pctchg_N(kind='reg',address=None)
#     check = pd.read_hdf(label_path + 'pct_240m_old.h5', 'pct_240m')
#     validation = label_df.loc[check.index,check.columns] - check
#     check_1 = validation[1].sort_values()
# label_df = lds.calc_pctchg_next_N_close(kind='clf')
#     pass
