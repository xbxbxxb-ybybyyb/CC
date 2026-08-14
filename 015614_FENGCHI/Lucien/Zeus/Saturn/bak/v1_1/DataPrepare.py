# coding: utf-8
# Author：fengchi863
"""
本文件用于准备数据，包括获取数据等
"""

from Zeus.Saturn.v1_1.path_conf import saturn_data_fpath
import pandas as pd
from sklearn.model_selection import StratifiedKFold


class DataPrepare:
    def __init__(self, date_config):
        self.raw_data = None

        self.train_start_date = date_config['train_start_date']
        self.train_end_date = date_config['train_end_date']
        self.valid_start_date = date_config['valid_start_date']
        self.valid_end_date = date_config['valid_end_date']
        self.pred_start_date = date_config['pred_start_date']
        self.pred_end_date = date_config['pred_end_date']

    def get_raw_data(self):
        samples = pd.read_pickle(saturn_data_fpath)
        X = samples[filter(lambda x: x.find('label'), samples.columns.tolist())]

        nan_flag = X.isnull().any()
        has_nan_factor_list = nan_flag[nan_flag].index.tolist()

        # 这里做一个统计，以及输出有空值的因子
        print('原样本中包含空值的因子有:', ','.join(has_nan_factor_list))

        # 这里不去空，在后面再去空值
        # X = X.dropna(how='any', axis=0)     # 去掉包含nan的行
        # samples = samples.loc[X.index]
        self.raw_data = samples

    def get_train_data(self):
        samples = self.raw_data.copy()
        samples['trade_date'] = samples.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
        samples = samples.query(f'trade_date >= {self.train_start_date} & trade_date <= {self.train_end_date}')
        return samples

    def get_valid_data(self):
        samples = self.raw_data.copy()
        samples['trade_date'] = samples.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
        samples = samples.query(f'trade_date >= {self.train_start_date} & trade_date <= {self.train_end_date}')

