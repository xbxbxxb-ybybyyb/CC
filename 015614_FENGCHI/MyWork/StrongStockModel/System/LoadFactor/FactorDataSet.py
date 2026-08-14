# coding: utf-8
# Author：fengchi863
# Date ：2020/7/17 14:11

import os
from itertools import product

import numpy as np
import pandas as pd

from StrongStockModel.conf.path_config import intraday_factor_path, fix_factor_by_date_path, \
    intraday_factor_by_date_path, root_path, fix_factor_by_date_h5_path, fix_factor_strong_by_date_path
from StrongStockModel.dataApi.getData import get_date_range
from StrongStockModel.dataApi.tradeDate import fix_minutes, trade_minutes


class FactorDataSet:

    def __init__(self, start_date=20140101, end_date=20191231, intraday_factor_path=intraday_factor_path,
                 fix_factor_path=fix_factor_by_date_path, interday_factor_path=None):
        # self.stk_dict = #pd.read_pickle(root_path + 'factor/stk_dict/stk_dict.pkl')
        # self.fix_factor_dict = pd.read_pickle(root_path + 'factor/fix_factor_dict/fix_factor_dict.pkl')
        # self.intraday_factor_dict = pd.read_pickle(root_path + 'factor/intraday_factor_dict/intraday_factor_dict.pkl')
        self.intraday_factor_path = intraday_factor_path
        self.fix_factor_path = fix_factor_path
        self.interday_factor_path = interday_factor_path
        self.date_list = get_date_range(start_date, end_date)
        self.fix_minutes_list = fix_minutes
        self.trade_minutes_list = trade_minutes
        self.stk_list = pd.read_pickle(root_path + 'stock_pool.pkl').columns.tolist()  # list(self.stk_dict.keys())
        self.stk_list.sort()

    def load_fix_factor(self, stk_list, factor_list, date, factor_address=fix_factor_by_date_path):
        if len(stk_list) == 0:
            return np.array([[] for i in factor_list]).T, [], factor_list
        stk_list_idx = list(self.stk_dict[stk_id] for stk_id in stk_list)
        factor_list_idx = list(self.fix_factor_dict[fix_factor_name] for fix_factor_name in factor_list)
        factor = np.load(factor_address + '%d.npy' % date)
        if len(stk_list) == 0:
            return np.array([[] for i in factor_list]).T, [], factor_list
        factor = factor[:, np.array(stk_list_idx)[:, None], np.array(factor_list_idx)[None, :]]
        factor = factor.reshape(-1, len(factor_list))
        index = product([date], self.fix_minutes_list, stk_list)
        return factor, index, factor_list

    def load_stk_date(self, stk, date, factor_list, factor_address=fix_factor_by_date_h5_path):
        start = self.stk_list.index(stk) * 7
        end = start + 7
        stk_date_df = pd.read_hdf(factor_address + '%d.h5' % date, str(date), start=start, stop=end)
        return stk_date_df[factor_list]

    def load_fix_factor_h5(self, stk_list, factor_list, date, factor_address=fix_factor_by_date_h5_path):
        df_list = []
        for stk in stk_list:
            temp_df = self.load_stk_date(stk, date, factor_list, factor_address)
            df_list.append(temp_df)
        factor = pd.concat(df_list)
        return factor

    def load_strong_stk_date(self, date, factor_list, factor_address=fix_factor_strong_by_date_path):
        if os.path.exists(factor_address + '%d.pkl' % date):
            stk_date_df = pd.read_pickle(factor_address + '%d.pkl' % date)
        elif os.path.exists(factor_address + '%d.h5' % date):
            stk_date_df = pd.read_hdf(factor_address + '%d.h5' % date, str(date))
        else:
            stk_date_df = pd.DataFrame(columns=factor_list)
        # print(factor_address)
        return stk_date_df[factor_list]
    # def load_interday_factor(self, factor_list, start_date, end_date, factor_address=interday_factor_path):
    #     date_list = get_date_range(start_date, end_date)
    #     factor_df = pd.DataFrame()
    #     for date in date_list:
    #         file_name = factor_address + 'mddate=' + str(date) + '/'
    #         df = pd.read_parquet('%s/mddate=%s/%s' % (factor_address, date, file_name), columns=['stock'] + factor_list)
    #         df.set_index('stock', inplace=True)
    #         df.index = df.index.map(trans_windcode2int)

    def load_intraday_factor(self, stk_list, factor_list, date,
                             factor_address=intraday_factor_by_date_path):
        stk_list_idx = list(self.stk_dict[stk_id] for stk_id in stk_list)
        factor_list_idx = list(self.intraday_factor_dict[fix_factor_name] for fix_factor_name in factor_list)
        factor = np.load(factor_address + '%d.npy' % date)
        factor = factor[:, np.array(stk_list_idx)[:, None], np.array(factor_list_idx)[None, :]]
        factor = factor.reshape(-1, len(factor_list))
        index = product([date], self.trade_minutes_list, stk_list)
        return factor, index, factor_list


if __name__ == '__main__':
    fds = FactorDataSet()
    # e = time.time()
    # res = fds.load_intraday_factor(intraday_factor_list, 20170103, 20170110)
    # print(time.time()-e)
    # fix_factor_list = fetch_factor_list()
    # res = fds.load_fix_factor([1, 2, 4], ['GTJA2', 'GTJA1_6'], 20170103)
    res = fds.load_intraday_factor([1, 2, 4], ['alpha1', 'alpha10'], 20191231)
    pass
