# coding: utf-8
# Author：fengchi863
# Date ：2022/7/2 18:48

import pickle
import os
import pandas as pd


class FileUtil:
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
    def save_df2csv(data: pd.DataFrame, path=None, filename=None, verbose=True):
        os.makedirs(path, exist_ok=True)
        data.to_csv(path + filename)
        if verbose:
            print(f'{filename} has been saved in {path + filename}')


FileUtil = FileUtil()
