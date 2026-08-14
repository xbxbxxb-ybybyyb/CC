# coding: utf-8
# Author：fengchi863
# Date ：2023/4/6 15:09
import sys
sys.path.append('/data/user/015614/fcfactor')

import pandas as pd
from EuropaLocal.TestTool.test1_factor_demo import strongFactorTest
from EuropaLocal.TestTool.run_factor_demo import run_factor
import IO
from multiprocessing import Pool
from itertools import product
from xquant.factordata import FactorData
from datetime import datetime
import os
from tqdm import tqdm
import datetime as dt
import numpy as np
import decimal
s = FactorData()

def round_(x, n=0):
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

def fun_get_time(time1, sec_delta):
    # 计算给定时间戳time1在sec_delta秒后的时间戳
    tmp_time = dt.datetime.strptime(str(time1)[:-3], '%H%M%S')
    tmp_time2 = tmp_time + dt.timedelta(seconds=sec_delta)
    tmp_time2_str = tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
    if (int(tmp_time2_str) > 113000000) & (time1 <= 113000000):
        adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=1.5 * 3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str) < 130000000) & (time1 >= 130000000):
        adj_tmp_time2 = tmp_time2 - dt.timedelta(seconds=1.5 * 3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str) < 93000000) & (time1 >= 93000000):
        adj_tmp_time2_str = '92500000'
        return int(adj_tmp_time2_str)
    elif time1 < 93000000:
        adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=4 * 60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)

def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    cov = np.nanmean(d_x * d_y, axis=0)
    var = (np.nanvar(x, axis=0) * np.nanvar(y, axis=0)) ** 0.5
    return cov / var

def array_rcorr_np(x, y):
    rank_x = np.argsort(np.argsort(x, axis=0), axis=0)
    rank_y = np.argsort(np.argsort(y, axis=0), axis=0)
    d_x, d_y = rank_x - np.nanmean(rank_x, axis=0), rank_y - np.nanmean(rank_y, axis=0)
    cov = np.nanmean(d_x * d_y, axis=0)
    var = (np.nanvar(rank_x, axis=0) * np.nanvar(rank_y, axis=0)) ** 0.5
    return cov / var

def weight_mean(elements, weights=None):
    if not weights:
        weights = [i / len(elements) for i in range(1, len(elements) + 1)]
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.mean([x*y for x, y in zip(elements, weights)])

def multiprocess(kernal_num, func, iterable, *args):
    pool = Pool(kernal_num)
    print('多进程启动')
    pool_apply_async = {}
    parts = len(iterable) // kernal_num
    remainder = len(iterable) % kernal_num
    iter_start = 0
    for j in range(kernal_num):
        if remainder > 0:
            iter_end = iter_start + parts + 1
            remainder = remainder - 1
        else:
            iter_end = iter_start + parts
        sub_iter = iterable[iter_start: iter_end]
        pool_apply_async[j] = pool.apply_async(func, (sub_iter,) + args)
        iter_start = iter_end
    pool.close()
    pool.join()
    print('多进程结束')
    return pool_apply_async


class FactorParamSearch:
    def __init__(self, note=None):
        self.start_date = 20160101
        self.end_date = 20191231
        note = note
        self.basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_001.h5'

        cur_datetime = datetime.today().strftime('%Y%m%d%H%M%S')
        self.res_path = f'/data/user/015614/factor/factor_digging_{cur_datetime}_{note}/'
        os.makedirs(self.res_path)

    def wrapper(self, param_list):
        for param_tuple in tqdm(param_list):
            factor_name = str(param_tuple)
            # TODO: 第三个参数因子类型需要根据回测需求进行更改
            factor_df = run_factor(self.calc_factor, factor_name, 'TTickab',
                           self.start_date, self.end_date, self.basic_file_path, self.res_path, param_tuple=param_tuple, interval_res=False, multi=False)
            # factor_df = self.calc_factor(self.start_date, self.end_date, param_tuple) # 这个计算出来的因子有问题，比如没有填充、没有平移
            self.start_backtest(factor_df, param_tuple)

    def start_backtest(self, factor_df, param_tuple):
        bt_columns = ['nan_num', 'same_rate', 'value_diff_score', 'value_stability_score', 'mixed_diff_score',
                      'mixed_stability_score', 'score', 'corr_tot', 'mic_tot', 'high_corr_factor', 'high_corr_factor_corr']
        res_df = pd.DataFrame(columns=bt_columns)

        # filter_factor = pd.read_pickle('/data/group/800463/data/project1_public/factor_lib_v2/filter_quickrise.pkl')
        # sft = strongFactorTest(self.start_date, self.end_date, filter_factor=filter_factor, filter_name='quickrise')
        sft = strongFactorTest(self.start_date, self.end_date)  # 全样本下测试
        res_dict = sft.factor_test(factor_df, result_path=self.res_path, factor_corr_test=True, generate_pdf=True)

        nan_num = res_dict['factor_information'].loc['Nan|Inf Count', 'Factor Info']
        same_rate = res_dict['other_sta'].loc['', 'same_rate']
        value_diff_score = res_dict['check_score_res'].loc['score', 'value_diff_score']
        value_stability_score = res_dict['check_score_res'].loc['score', 'value_stability_score']
        mixed_diff_score = res_dict['check_score_res'].loc['score', 'mixed_diff_score']
        mixed_stability_score = res_dict['check_score_res'].loc['score', 'mixed_stability_score']
        score = res_dict['check_score_res'].loc['score', 'tot_score']
        corr_tot = res_dict['corr_sta'].loc['corr_tot', 'value']
        mic_tot = res_dict['corr_sta'].loc['mic_tot', 'value']

        high_corr_s = res_dict['factor_corr'].query('factor_corr >= 0.685')
        if len(high_corr_s) == 0:
            high_corr_s = res_dict['factor_corr'].iloc[:2]
        else:
            high_corr_s = res_dict['factor_corr'].iloc[:len(high_corr_s) + 2]

        high_corr_factor_list_str = '，'.join(high_corr_s.index.tolist())
        high_corr_factor_corr_list_str = '，'.join(high_corr_s['factor_corr'].map(lambda x: round(x, 4)).map(str).tolist())

        res_df.loc[str(param_tuple)] = [nan_num, same_rate, value_diff_score, value_stability_score,
                                   mixed_diff_score, mixed_stability_score, score, corr_tot, mic_tot, high_corr_factor_list_str, high_corr_factor_corr_list_str]
        print(str(param_tuple), ': ', score)
        res_df.to_excel(self.res_path + f'{str(param_tuple)}.xlsx')
        factor_df.to_pickle(self.res_path + f'{str(param_tuple)}.pkl')

    @staticmethod
    def calc_factor(df, param_tuple, return_fillna_dic=False):
        factor_name = str(param_tuple)
        param1, param2 = param_tuple

        if return_fillna_dic:
            return {factor_name: 0}
        # -------------------------------------------------------------------------------------------------------------------
        dt, Ticker = df.index[0]
        zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
        pre_close = df['pre_close'].iloc[0]
        zt_time = int(df.iloc[-1]['MDTime'])
        df = df[df['MDTime'] >= 93000000]

        df['ValueTrade'] = df['TotalValueTrade'] - df['TotalValueTrade'].shift(1).fillna(0)
        df['VolumeTrade'] = df['TotalVolumeTrade'] - df['TotalVolumeTrade'].shift(1).fillna(0)
        df = df[df['MDTime'] >= max(fun_get_time(zt_time, -param1), 93000000)]
        df = df.tail(int(len(df) / param2))
        df['vwap'] = df['ValueTrade'].cumsum() / df['VolumeTrade'].cumsum()
        mean = (df['vwap'] / df['LastPx']).mean()
        std = (df['vwap'] / df['LastPx']).std()
        cv = std / (mean + 0.000001)

        factor_dict = {factor_name: cv}
        # ---------------------------------------------------------------------------------------------------------------
        return pd.Series(factor_dict)

    """
    MDTime: 时间
    WeightedAvgOfferPx：本tick平均买入价
    WeightedAvgBidPx：本tick平均卖出价
    LastPx：最新价
    TotalOfferQty：卖出总量
    TotalBidQty：买入总量
    NumTrades：从开盘到现在成交笔数，切记是总成交，所以要diff()
    TotalVolumeTrade:
    TotalValueTrade:
    Buy1Price:
    Sell1Price:
    Buy1OrderQty:
    Sell1OrderQty:
    Buy1NumOrders:
    Sell1NumOrders:
    """


if __name__ == '__main__':
    note = 'cv'
    fps = FactorParamSearch(note=note)
    param_list = [[60, 300, 600, 1200, 6000, 12000, 24000],
                 [1, 2, 3, 4, 5]]
    param_list = list(product(*param_list))
    # param_list = list(filter(lambda x: x[1] < x[2], param_list))
    multiprocess(10, fps.wrapper, param_list)
    # multiprocess(1, fps.wrapper, param_list[0])
    # fps.wrapper([('WeightedAvgBidPx', 10, 15)]) # 用于调试