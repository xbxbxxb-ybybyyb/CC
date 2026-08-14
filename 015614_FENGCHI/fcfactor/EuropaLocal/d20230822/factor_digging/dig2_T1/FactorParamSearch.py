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
import numpy as np
s = FactorData()

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
            factor_df = run_factor(self.calc_factor, factor_name, 'T-1_factor',
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

        high_corr_s = res_dict['factor_corr'].query('factor_corr >= 0.7')
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
    def calc_factor(start_date, end_date, IO, param_tuple, return_fillna_dic=False):
        factor_name = str(param_tuple)
        param1, param2 = param_tuple

        if return_fillna_dic:
            return {factor_name: 0, 'data': ['AShareMoneyFlow']}
        # -------------------------------------------------------------------------------------------------------------------
        start_date_ = int(s.tradingday(str(start_date), -130)[0])
        md_data = IO.read_data([start_date_, end_date], columns=[param1], alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5')

        factor_df = pd.DataFrame()
        factor_df[factor_name] = md_data[param1].unstack().diff().rolling(param2, min_periods=1).std().stack()

        return factor_df


if __name__ == '__main__':
    note = '20230824测试'
    fps = FactorParamSearch(note=note)
    param_list = [['BUY_VALUE_EXLARGE_ORDER', 'SELL_VALUE_EXLARGE_ORDER',
                   'BUY_VALUE_LARGE_ORDER', 'SELL_VALUE_LARGE_ORDER',
                   'BUY_VALUE_MED_ORDER', 'SELL_VALUE_MED_ORDER', 'BUY_VALUE_SMALL_ORDER',
                   'SELL_VALUE_SMALL_ORDER', 'BUY_VOLUME_EXLARGE_ORDER',
                   'SELL_VOLUME_EXLARGE_ORDER', 'BUY_VOLUME_LARGE_ORDER',
                   'SELL_VOLUME_LARGE_ORDER', 'BUY_VOLUME_MED_ORDER',
                   'SELL_VOLUME_MED_ORDER', 'BUY_VOLUME_SMALL_ORDER',
                   'SELL_VOLUME_SMALL_ORDER', 'TRADES_COUNT', 'BUY_TRADES_EXLARGE_ORDER',
                   'SELL_TRADES_EXLARGE_ORDER', 'BUY_TRADES_LARGE_ORDER',
                   'SELL_TRADES_LARGE_ORDER', 'BUY_TRADES_MED_ORDER',
                   'SELL_TRADES_MED_ORDER', 'BUY_TRADES_SMALL_ORDER',
                   'SELL_TRADES_SMALL_ORDER', 'VOLUME_DIFF_SMALL_TRADER',
                   'VOLUME_DIFF_SMALL_TRADER_ACT', 'VOLUME_DIFF_MED_TRADER',
                   'VOLUME_DIFF_MED_TRADER_ACT', 'VOLUME_DIFF_LARGE_TRADER',
                   'VOLUME_DIFF_LARGE_TRADER_ACT', 'VOLUME_DIFF_INSTITUTE',
                   'VOLUME_DIFF_INSTITUTE_ACT', 'VALUE_DIFF_SMALL_TRADER',
                   'VALUE_DIFF_SMALL_TRADER_ACT', 'VALUE_DIFF_MED_TRADER',
                   'VALUE_DIFF_MED_TRADER_ACT', 'VALUE_DIFF_LARGE_TRADER',
                   'VALUE_DIFF_LARGE_TRADER_ACT', 'VALUE_DIFF_INSTITUTE',
                   'VALUE_DIFF_INSTITUTE_ACT', 'S_MFD_INFLOWVOLUME',
                   'NET_INFLOW_RATE_VOLUME', 'S_MFD_INFLOW_OPENVOLUME',
                   'OPEN_NET_INFLOW_RATE_VOLUME', 'S_MFD_INFLOW_CLOSEVOLUME',
                   'CLOSE_NET_INFLOW_RATE_VOLUME', 'S_MFD_INFLOW', 'NET_INFLOW_RATE_VALUE',
                   'S_MFD_INFLOW_OPEN', 'OPEN_NET_INFLOW_RATE_VALUE', 'S_MFD_INFLOW_CLOSE',
                   'CLOSE_NET_INFLOW_RATE_VALUE', 'TOT_VOLUME_BID', 'TOT_VOLUME_ASK',
                   'MONEYFLOW_PCT_VOLUME', 'OPEN_MONEYFLOW_PCT_VOLUME',
                   'CLOSE_MONEYFLOW_PCT_VOLUME', 'MONEYFLOW_PCT_VALUE',
                   'OPEN_MONEYFLOW_PCT_VALUE', 'CLOSE_MONEYFLOW_PCT_VALUE',
                   'S_MFD_INFLOWVOLUME_LARGE_ORDER', 'NET_INFLOW_RATE_VOLUME_L',
                   'S_MFD_INFLOW_LARGE_ORDER', 'NET_INFLOW_RATE_VALUE_L',
                   'MONEYFLOW_PCT_VOLUME_L', 'MONEYFLOW_PCT_VALUE_L',
                   'S_MFD_INFLOW_OPENVOLUME_L', 'OPEN_NET_INFLOW_RATE_VOLUME_L',
                   'S_MFD_INFLOW_OPEN_LARGE_ORDER', 'OPEN_NET_INFLOW_RATE_VALUE_L',
                   'OPEN_MONEYFLOW_PCT_VOLUME_L', 'OPEN_MONEYFLOW_PCT_VALUE_L',
                   'S_MFD_INFLOW_CLOSEVOLUME_L', 'CLOSE_NET_INFLOW_RATE_VOLUME_L',
                   'S_MFD_INFLOW_CLOSE_LARGE_ORDER', 'CLOSE_NET_INFLOW_RATE_VALU_L',
                   'CLOSE_MONEYFLOW_PCT_VOLUME_L', 'CLOSE_MONEYFLOW_PCT_VALUE_L',
                   'BUY_VALUE_EXLARGE_ORDER_ACT', 'SELL_VALUE_EXLARGE_ORDER_ACT',
                   'BUY_VALUE_LARGE_ORDER_ACT', 'SELL_VALUE_LARGE_ORDER_ACT',
                   'BUY_VALUE_MED_ORDER_ACT', 'SELL_VALUE_MED_ORDER_ACT',
                   'BUY_VALUE_SMALL_ORDER_ACT', 'SELL_VALUE_SMALL_ORDER_ACT',
                   'BUY_VOLUME_EXLARGE_ORDER_ACT', 'SELL_VOLUME_EXLARGE_ORDER_ACT',
                   'BUY_VOLUME_LARGE_ORDER_ACT', 'SELL_VOLUME_LARGE_ORDER_ACT',
                   'BUY_VOLUME_MED_ORDER_ACT', 'SELL_VOLUME_MED_ORDER_ACT',
                   'BUY_VOLUME_SMALL_ORDER_ACT', 'SELL_VOLUME_SMALL_ORDER_ACT'],
                  [6, 20, 40, 60, 90, 120],]
    param_list = list(product(*param_list))
    multiprocess(20, fps.wrapper, param_list)
    # multiprocess(1, fps.wrapper, param_list[0])
    # fps.wrapper([('CLOSE_NET_INFLOW_RATE_VALUE', 5)]) # 用于调试