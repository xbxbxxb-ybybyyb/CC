# coding: utf-8
# Author：fengchi863
# Date ：2021/4/23 16:10

import pandas as pd, numpy as np
import sys
import os

class DataUtil:
    def save_pickle(self, file, file_path, verbose=True):
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file.to_pickle(file_path)
        if verbose:
            print('已保存至%s' % file_path)

    def read_pickle(self, file_path, verbose=True):
        if verbose:
            print('已读取%s' % file_path)
        return pd.read_pickle(file_path)

DataUtil = DataUtil()