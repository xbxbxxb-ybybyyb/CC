# coding: utf-8
# Author：fengchi863
# Date ：2022/3/9 14:14

import pickle
import os
import pandas as pd
from multiprocessing import Pool
from SimiStock.config.path_config import *
import traceback


class Util:
    @staticmethod
    def save_list2pkl(data: list, path=None, filename=None, verbose=True):
        os.makedirs(path, exist_ok=True)
        writer = open(path + filename, 'wb')
        pickle.dump(data, writer)
        if verbose:
            print(f'{filename} has been saved in {path + filename}')

    @staticmethod
    def read_list(path=None, filename=None):
        writer = open(path + filename, 'rb')
        return pickle.load(writer)

    @staticmethod
    def read_pkl(path=None, filename=None):
        writer = open(path + filename, 'rb')
        return pickle.load(writer)

    @staticmethod
    def save_df2xls(data: pd.DataFrame, path=None, filename=None, verbose=True):
        os.makedirs(path, exist_ok=True)
        data.to_excel(path + filename)
        if verbose:
            print(f'{filename} has been saved in {path + filename}')

    @staticmethod
    def read_df4xls(path=None, filename=None):
        ret = pd.read_excel(path + filename)
        return ret

    @staticmethod
    def save_dict2xls(data: dict, path=None, filename=None, verbose=True):
        os.makedirs(path, exist_ok=True)
        with pd.ExcelWriter(path + filename) as writer:
            for each in data:
                data[each].to_excel(writer, each)
        if verbose:
            print(f'{filename} has been saved in {path + filename}')

    @staticmethod
    def save_df2pkl(data: pd.DataFrame, path=None, filename=None, verbose=True):
        os.makedirs(path, exist_ok=True)
        data.to_pickle(path + filename)
        if verbose:
            print(f'{filename} has been saved in {path + filename}')

    @staticmethod
    def save_dict2pkl(data: dict, path=None, filename=None, verbose=True):
        os.makedirs(path, exist_ok=True)
        writer = open(path + filename, 'wb')
        pickle.dump(data, writer)
        if verbose:
            print(f'{filename} has been saved in {path + filename}')

    @staticmethod
    def multiprocess(kernal_num, func, iterable, *args):
        def error_callback(e):
            print('error_callback()', e)
            traceback.print_exception(type(e), e, e.__tradeback__)
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
            pool_apply_async[j] = pool.apply_async(func, (sub_iter,) + args, error_callback=error_callback)
            iter_start = iter_end
        pool.close()
        pool.join()
        print('多进程结束')
        return pool_apply_async

    @staticmethod
    def stats_hedge_list(hedge_list, output_name='hedge_result.xlsx'):
        """stk_id, date, discount, hedge_weight, hedge_list, hedge_value"""
        ret_list = list()
        for idx, hedge in enumerate(hedge_list):
            ret_list.append([hedge['stk_id'], hedge['date'], hedge['discount'], len(hedge['hedge_list'])])

        df = pd.DataFrame(ret_list, columns=['stk_id', 'date', 'discount', '对冲标的可选数量'])

        # 先使用简单的聚类方式，按年
        df['年份'] = df['date'] // 10000
        tmp = df.groupby(['stk_id', '年份'])['date'].count()
        tmp = tmp.reset_index()
        yearly_ret_df = tmp.groupby(['年份'])['stk_id'].count()
        yearly_ret_df = pd.DataFrame(yearly_ret_df)

        df3 = pd.Series()
        df3['对冲标的均值'] = df['对冲标的可选数量'].mean()
        for i in [1, 3, 5, 8]:
            df3[f'大于{i}的项目数量'] = (df['对冲标的可选数量'] >= i).sum()
            df3[f'大于{i}的项目百分比'] = (df['对冲标的可选数量'] >= i).sum() / len(df)
        df3 = pd.DataFrame(df3)

        save_dict = {
            '明细': df,
            '年份汇总': yearly_ret_df,
            '汇总': df3
        }
        util.save_dict2xls(save_dict, other_stats_path, output_name)


util = Util()
