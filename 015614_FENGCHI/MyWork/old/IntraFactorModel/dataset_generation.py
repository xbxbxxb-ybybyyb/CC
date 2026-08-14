# @Time : 2020/5/6 10:46
# @Author : Zhichen Lu
# @File : dataset_generation.py

'''
定义数据集的sampling methodology & labeling methodology
'''
import os
import random

import gc

from conf.path_config import *
from dataApi.getData import get_minute_1factor, get_daily_1factor
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_recent_trade_date, get_pre_trade_date, get_date_range, trade_minutes
from dataApi.usefulTools import *


class FactorDataSet:

    def __init__(self, root_path='/data/group/800319/junkData/IntraFactorModel/FactorByStock/', start=20170101,
                 end=20191231):
        print(root_path)
        self.pool = clean_stock_list('ALL', no_limit_down=True, no_limit_up=True).loc[start:end]
        isin_judge = self.pool.sum()
        self.pool = self.pool[isin_judge[isin_judge != 0].index]
        pool_all = clean_stock_list(no_ST=False, least_live_days=1, least_recover_days=1, no_limit_up=True,
                                    no_limit_down=True)
        self.pool = pool_all[self.pool.columns].loc[start:end]
        self.factor_root_path = root_path
        self.date_list = get_date_range(start, end)
        self.time_list = trade_minutes
        # pool_arr = self.pool.values
        # self.pool_arr = np.array([pool_arr for i in range(242)])
        self.stk_list = self.pool.columns.tolist()

    def shift_back(self, arr, n):
        arr_shift = arr.copy()
        arr_shift[:-n] = arr_shift[n:]
        arr_shift[-n:] = np.nan
        return arr_shift

    def load_factor(self, stk_id, start, end):
        if start is None:
            start = self.date_list[0]
        if end is None:
            end = self.date_list[-1]
        start_idx = self.date_list.index(start) * 242
        end_idx = self.date_list.index(end) * 242 + 242
        # factor = pd.read_pickle(
        #     self.factor_root_path + str(stk_id) + '.pkl')
        if os.path.exists(self.factor_root_path + str(stk_id) + '.h5'):
            factor = pd.read_hdf(self.factor_root_path + str(stk_id) + '.h5', str(stk_id), start=start_idx, stop=end_idx)
        elif os.path.exists(self.factor_root_path + str(stk_id) + '.pkl'):
            factor = pd.read_pickle(self.factor_root_path + str(stk_id) + '.pkl')
        else:
            raise Exception('No such file', self.factor_root_path + str(stk_id))
        return factor.loc[(start, 925):(end, 1500)]

    def get_label_rise_down(self, stk_id, start_date=None, end_date=None, lag=5):
        if start_date is None:
            start_date = self.date_list[0]
        if end_date is None:
            end_date = self.date_list[-1]
        start_datetime = start_date * 10000 + 925
        end_datetime = end_date * 10000 + 1500
        minute_price = get_minute_1factor('close', start_datetime, end_datetime, code_list=[stk_id])
        index, columns = minute_price.index.tolist(), minute_price.columns.tolist()
        minute_price = frame2arr(minute_price)
        minute_pct = self.shift_back(minute_price, lag) / minute_price - 1
        label = 1 * (minute_pct > 0)
        label[np.isnan(minute_pct)] = np.nan
        label_df = arr2frame(label, index=index, columns=columns)
        return label_df[stk_id]

    def get_label_intraday_pct(self, stk_id, start_date=None, end_date=None, threshold=0.2, lag=5):
        if start_date is None:
            start_date = self.date_list[0]
        if end_date is None:
            end_date = self.date_list[-1]
        start_datetime = start_date * 10000 + 925
        end_datetime = end_date * 10000 + 1500
        minute_price = get_minute_1factor('close', start_datetime, end_datetime, code_list=[stk_id])
        index, columns = minute_price.index.tolist(), minute_price.columns.tolist()
        minute_price = frame2arr(minute_price)
        minute_pct = self.shift_back(minute_price, lag) / minute_price - 1
        up_threshold, down_threshold = np.nanquantile(minute_pct, 0.8, axis=0), np.nanquantile(minute_pct, 0.2, axis=0)
        label = (minute_pct > up_threshold) * 1. - 1. * (minute_pct < down_threshold)
        label[np.isnan(minute_pct)] = np.nan
        label_df = arr2frame(label, index=index, columns=columns)
        return label_df[stk_id]

    def get_label_rise_down_zero(self, stk_id, start_date=None, end_date=None, lag=5,
                                 path=labels_path):
        if start_date is None:
            start_date = self.date_list[0]
        if end_date is None:
            end_date = self.date_list[-1]
        path = path + 'rise_down_zero_%dmin/' % lag
        if os.path.exists(path + '%d.pkl' % stk_id):
            label_df = pd.read_pickle(path + '%d.pkl' % stk_id)
            return label_df.loc[(start_date, 925):(end_date, 1500)]
        start_datetime = self.date_list[0] * 10000 + 925
        end_datetime = self.date_list[-1] * 10000 + 1500
        minute_price = get_minute_1factor('close', start_datetime, end_datetime, code_list=[stk_id])
        index, columns = minute_price.index.tolist(), minute_price.columns.tolist()
        minute_price = frame2arr(minute_price)
        minute_pct = self.shift_back(minute_price, lag) / minute_price - 1
        label = (minute_pct > 0) * 1. - 1. * (minute_pct < 0)
        label[np.isnan(minute_pct)] = np.nan
        isin_pool = self.pool[[stk_id]].values.reshape(len(self.pool))
        isin_pool = np.array([np.array([isin_pool for i in range(242)])]).transpose(1, 2, 0)
        label[~isin_pool] = np.nan
        label_df = arr2frame(label, index=index, columns=columns)
        pd.to_pickle(label_df[stk_id], path + '%d.pkl' % stk_id)
        print('save labels in %s' % (path + '%d.pkl' % stk_id))
        del minute_price, minute_pct
        gc.collect()
        return label_df[stk_id].loc[(start_date, 925):(end_date, 1500)]

    def get_label_twap(self, stk_id, start_date=None, end_date=None,
                       path=labels_path + 'twap/'):
        if start_date is None:
            start_date = self.date_list[0]
        if end_date is None:
            end_date = self.date_list[-1]
        if os.path.exists(path + '%d.pkl' % stk_id):
            label_df = pd.read_pickle(path + '%d.pkl' % stk_id)
            return label_df.loc[(start_date, 925):(end_date, 1500)]
        start_datetime = self.date_list[0] * 10000 + 925
        end_datetime = self.date_list[-1] * 10000 + 1500
        minute_price = get_minute_1factor('close', start_datetime, end_datetime, code_list=[stk_id])
        daily_twap = get_daily_1factor('twap', date_list=self.date_list, code_list=[stk_id])
        index, columns = minute_price.index.tolist(), minute_price.columns.tolist()
        minute_price = frame2arr(minute_price)
        minute_pct = daily_twap.values / minute_price - 1
        label = (minute_pct > 0) * 1. - 1. * (minute_pct < 0)
        label[np.isnan(minute_pct)] = np.nan
        isin_pool = self.pool[[stk_id]].values.reshape(len(self.pool))
        isin_pool = np.array([np.array([isin_pool for i in range(242)])]).transpose(1, 2, 0)
        label[~isin_pool] = np.nan
        label_df = arr2frame(label, index=index, columns=columns)
        pd.to_pickle(label_df[stk_id], path + '%d.pkl' % stk_id)
        return label_df[stk_id].loc[(start_date, 925):(end_date, 1500)]

    def get_label_tick_twap(self, stk_id, start_date=None, end_date=None,
                            path=labels_path + 'tick_twap/'):
        if start_date is None:
            start_date = self.date_list[0]
        if end_date is None:
            end_date = self.date_list[-1]
        if os.path.exists(path + '%d.pkl' % stk_id):
            # print(stk_id,'exist')
            label_df = pd.read_pickle(path + '%d.pkl' % stk_id)
            return label_df.loc[(start_date, 925):(end_date, 1500)]
        future_tick_info = pd.read_pickle(
            '/data/group/800319/junkData/IntraFactorModel/MinutelyTickByStock/%d.pkl' % stk_id)
        future_tick_info = future_tick_info.loc[(start_date, 925):(end_date, 1500)]
        daily_twap = get_daily_1factor('twap', date_list=self.date_list, code_list=[stk_id])
        order_1_arr = frame2arr(future_tick_info[['Buy1Price', 'Sell1Price']])
        order_1_arr = self.shift_back(order_1_arr, 1)
        daily_twap_arr = daily_twap.values
        # twap低于下一个盘口的买1价为 -1  twap高于下一盘口的卖1价为 +1, 中间为0
        label = (order_1_arr[:, :, 1:] < daily_twap_arr) * 1. - (order_1_arr[:, :, 0:1] > daily_twap_arr) * 1.
        label_df = arr2frame(label, index=future_tick_info.index, columns=[stk_id])
        pd.to_pickle(label_df[stk_id], path + '%d.pkl' % stk_id)
        # minutely_broadcast_twap = arr2frame(np.array([daily_twap_arr for i in range(242)]), index=future_tick_info.index, columns=['twap'])
        # check_twap_profit = daily_twap_arr / order_1_arr
        # check_twap_profit = arr2frame(check_twap_profit, index=future_tick_info.index, columns=['Buy_rela', 'Sell_rela'])
        # check = pd.concat([arr2frame(order_1_arr,index=label_df.index,columns=['Buy1Price','Sell1Price']),
        #                    minutely_broadcast_twap,label_df,check_twap_profit],axis=1).reindex([5,
        #                 'Buy1Price','twap','Sell1Price','Buy_rela','Sell_rela'],axis=1)
        # check['Buy_val'] = check['twap']/check['Buy1Price']
        # check['Sell_val'] = check['twap']/check['Sell1Price']
        # label_df.groupby(stk_id).size()
        return label_df[stk_id].loc[(start_date, 925):(end_date, 1500)]

    def get_dataset(self, stk_id, start_date, end_date, label_method='rise_down_zero_5min'):
        if start_date is None:
            start_date = self.date_list[0]
        else:
            start_date = get_pre_trade_date(get_recent_trade_date(start_date - 1), -1)
        if end_date is None:
            end_date = self.date_list[0]
        else:
            end_date = get_recent_trade_date(end_date)
        if label_method == 'rise_down_zero_5min':
            label = self.get_label_rise_down_zero(stk_id, start_date=start_date, end_date=end_date, lag=5)
        elif label_method == 'rise_down_zero_1min':
            label = self.get_label_rise_down_zero(stk_id, start_date=start_date, end_date=end_date, lag=1)
        elif label_method == 'twap':
            label = self.get_label_twap(stk_id, start_date=start_date, end_date=end_date)
        elif label_method == 'tick_twap':
            label = self.get_label_tick_twap(stk_id, start_date=start_date, end_date=end_date)
        elif label_method == 'rise_down':
            label = self.get_label_rise_down(stk_id, start_date=start_date, end_date=end_date)
        elif label_method == 'pct_intraday':
            label = self.get_label_intraday_pct(stk_id, start_date=start_date, end_date=end_date)
        else:
            raise Exception('Unknown label method')
        factor = self.load_factor(stk_id, start_date, end_date)
        # print(factor.index[0], factor.index[-1])
        return factor, label  # .loc[(start_date, 925):(end_date, 1500)]

    def dataset_resample_dataset(self, label):
        count = pd.DataFrame(label).groupby(0).size()
        times = (count.max() / count).apply(round)
        target_label = times[times == 1].index[0]
        idx_list = np.where(label == target_label)[0].tolist()
        res_sample_idx_list = []
        for temp_label in times.index:
            if temp_label == target_label:
                continue
            res_sample_idx_list = res_sample_idx_list + np.where(label == temp_label)[0].tolist()
        random.shuffle(idx_list)
        subsets_idx = []
        for i in range(times.max()):
            temp_part_idx = idx_list[int(len(idx_list) * i / times.max()):int(len(idx_list) * (i + 1) / times.max())]
            temp_part_idx = temp_part_idx + res_sample_idx_list
            random.shuffle(temp_part_idx)
            subsets_idx.append(temp_part_idx)
        return subsets_idx


# fds = FactorDataSet()
# check = fds.get_dataset(5, 20170103, 20191231, 'rise_down_zero_1min')
# print(1)

# check1 = fds.get_dataset(5, 20170103, 20191231, 'tick_twap')
# check2 = fds.get_dataset(5, 20170103, 20191231, 'twap')


# def wraper_rise_down_zeros(stk):
#     if os.path.exists(labels_path + 'rise_down_zero_%dmin/%d.pkl' % (1, stk)):
#         print(stk, 'exist')
#         return 0
#     try:
#         # label = fds.get_label_rise_down_zero(stk)
#         label = fds.get_label_rise_down_zero(stk, start_date=20170101, end_date=20191231, lag=1)
#         del label
#         gc.collect()
#         print(stk,'done')
#     except:
#         pd.to_pickle(labels_path + 'rise_down_zero_%dmin/' % 1 + 'Wrong_%d.pkl' % stk)
#         print('Wrong',stk)
#
# def wraper_tick_twap(stk):
#     try:
#         # label = fds.get_label_rise_down_zero(stk)
#         label = fds.get_label_tick_twap(stk)
#         print(stk,'done')
#     except:
#         pd.to_pickle('/data/group/800319/junkData/IntraFactorModel/tick_twap/Wrong_%d.pkl'%stk)
#         print('Wrong',stk)


# wraper_rise_down_zeros(2)
# if __name__ == "__main__":

# import gc
# def wraper_rise_down_zeros(stk):
#     try:
#         label = fds.get_label_rise_down_zero(stk, lag=1)
#         del label
#         gc.collect()
#         print(stk,'done')
#     except:
#         pd.to_pickle('/data/group/800319/junkData/IntraFactorModel/labels/rise_down_zero_1min/Wrong_%d.pkl'%stk)
#         print('Wrong',stk)
# #
# fds = FactorDataSet()
# from multiprocessing import Pool
#
# pool = Pool(10)
# para_list = fds.stk_list
# # para_list = para_list[::-1]
# pool.map(wraper_rise_down_zeros, para_list)
# pool.close()
# pool.join()
