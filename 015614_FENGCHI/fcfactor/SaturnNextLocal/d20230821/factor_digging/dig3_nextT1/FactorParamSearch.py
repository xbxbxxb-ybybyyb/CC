# coding: utf-8
# Author：fengchi863
# Date ：2023/8/4 9:17

import sys
sys.path.append('/data/user/015614/fcfactor')

import pandas as pd
from SaturnNextLocal.TestTool.project_2_factor_test_origin import pj2FactorTest, send_message
from SaturnNextLocal.TestTool.run_factor_demo import run_factor
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
        self.basic_file_path = '/data/group/800463/data/project2_public/factor_lib_next/Basic_next_hf_finish_20160101_20191231.h5'

        cur_datetime = datetime.today().strftime('%Y%m%d%H%M%S')
        self.res_path = f'/data/user/015614/factor/factor_digging_{cur_datetime}_{note}/'
        os.makedirs(self.res_path)

    def wrapper(self, param_list):
        for param_tuple in tqdm(param_list):
            factor_name = str(param_tuple).replace('/', '%')
            # TODO: 第三个参数因子类型需要根据回测需求进行更改
            factor_df = run_factor(self.calc_factor, factor_name, 'Next_T-1_factor',
                           self.start_date, self.end_date, self.basic_file_path, self.res_path, param_tuple=param_tuple, interval_res=False, multi=False)
            # factor_df = self.calc_factor(self.start_date, self.end_date, param_tuple) # 这个计算出来的因子有问题，比如没有填充、没有平移
            self.start_backtest(factor_df, param_tuple)

    def start_backtest(self, factor_df, param_tuple):
        bt_columns = ['nan_num', 'same_rate', 'score', 'corr_tot', 'high_corr_factor', 'high_corr_factor_corr']
        res_df = pd.DataFrame(columns=bt_columns)

        # filter_factor = pd.read_pickle('/data/group/800463/data/project1_public/factor_lib_v2/filter_quickrise.pkl')
        # sft = strongFactorTest(self.start_date, self.end_date, filter_factor=filter_factor, filter_name='quickrise')
        sft = pj2FactorTest(self.start_date, self.end_date)  # 全样本下测试
        res_dict = sft.factor_test(factor_df, result_path=self.res_path, factor_corr_test=True, generate_pdf=True)

        nan_num = res_dict['factor_information'].loc['Nan|Inf Count', 'Factor Info']
        same_rate = res_dict['max_same_ratio'].loc['repeated_ratio', 'first']
        score = res_dict['check_score_res'].loc['score', 'tot_score']
        corr_tot = res_dict['corr_sta'].loc['corr_tot', 'value']

        high_corr_s = res_dict['factor_corr'].query('factor_corr >= 0.7')
        if len(high_corr_s) == 0:
            high_corr_s = res_dict['factor_corr'].iloc[:2]
        else:
            high_corr_s = res_dict['factor_corr'].iloc[:len(high_corr_s) + 2]

        high_corr_factor_list_str = '，'.join(high_corr_s.index.tolist())
        high_corr_factor_corr_list_str = '，'.join(high_corr_s['factor_corr'].map(lambda x: round(x, 4)).map(str).tolist())

        res_df.loc[str(param_tuple)] = [nan_num, same_rate, score, corr_tot, high_corr_factor_list_str, high_corr_factor_corr_list_str]
        # send_message(f'{str(param_tuple)}\n{nan_num}\n{same_rate}\n{score}\n{corr_tot}\n{high_corr_factor_list_str}\n{high_corr_factor_corr_list_str}')
        print(str(param_tuple), ': ', score)
        res_df.to_excel(self.res_path + f'{str(param_tuple).replace("/", "%")}.xlsx')
        factor_df.to_pickle(self.res_path + f'{str(param_tuple).replace("/", "%")}.pkl')

    @staticmethod
    def calc_factor(start_date, end_date, IO, param_tuple, return_fillna_dic=False):
        factor_name = str(param_tuple).replace('/', '%')
        param1, param2 = param_tuple

        if return_fillna_dic:
            return {factor_name: 0, 'data': ['minute5']}
        # -------------------------------------------------------------------------------------------------------------------
        start_date_ = int(s.tradingday(str(start_date), -35)[0])
        close = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/close.h5')
        amt = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
        vol = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/volume.h5')
        opn = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/open.h5')
        high = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/high.h5')
        low = IO.read_data([start_date_, end_date], alt='/data/group/800463/data/generalStrong/minute5/low.h5')
        vwap = amt / vol

        res = eval(param1).mean(axis=1)

        res_mean = pd.DataFrame(res.unstack().rolling(param2, 2).mean().stack())
        res_std = pd.DataFrame(res.unstack().rolling(param2, 2).std().stack())
        res_cv = res_std / res_mean
        res_cv.columns = [factor_name]
        factor_df = res_cv
        return factor_df


if __name__ == '__main__':
    """
    利用minute5表 遍历生成因子
    """
    note = '20230823测试'
    fps = FactorParamSearch(note=note)
    from SaturnNextLocal.d20230821.factor_digging.dig3_nextT1.formule import fomule_list
    param_list = [fomule_list,
                  [3, 4, 5, 6, 8, 10, 15, 20, 25, 30],]
    param_list = list(product(*param_list))
    multiprocess(10, fps.wrapper, param_list)
    # multiprocess(1, fps.wrapper, param_list[0])
    # fps.wrapper([(fomule_list[0], 5)]) # 用于调试

    # check1 = IO.read_data([20160101, 20181231], alt='/data/user/018107/share_file/for_fc/fc_stk_zz1000_r_5.h5')
    # check2 = IO.read_data([20160101, 20181231], alt='/data/user/015614/factor/factor_digging_20230424160441新框架下与市场相关性测试/(5, \'corr\').h5')
    # check3 = IO.read_data([20160101, 20181231], alt='/data/user/015614/factor/factor_digging_20230424204144第二次跑并行测试一致性/(5, \'corr\').h5')
    # cmp = pd.concat([check1, check2], axis=1)
    # check1.mean()
    # check2.mean()

"""
# minute5
open high low close amt vol
m925 m930 m935 ... m1130  m1300 m1305 ... m1430 m1435 ... m1455
表示的是这五分钟内的amt和vol，不是截至当前累积的
iloc[:, :25]就是上午
"""