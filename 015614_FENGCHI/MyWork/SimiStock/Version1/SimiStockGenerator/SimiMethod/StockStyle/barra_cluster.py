# coding: utf-8
# Author：fengchi863
# Date ：2022/4/6 14:58

"""
根据barra聚类结果，返回每个样本对应的同一类别中的样本
"""

from sklearn.cluster import KMeans
from SimiStock.Version1.config.path_config import *
import pandas as pd
import numpy as np
from sklearn.preprocessing import Imputer, MinMaxScaler
from sklearn.impute import KNNImputer
from SimiStock.Version1.SimiStockGenerator.util import util
from tqdm import tqdm


class SimiCluster:
    def __init__(self, start_date=20180101, end_date=20200630, factor_list=None, cluster_name=None):
        code_list = np.load(barra_path + 'code_list.npy')
        date_list = np.load(barra_path + 'date_list.npy')
        block_data = pd.read_pickle(data_path + 'block_data.pkl')

        self.code_list = list(code_list)
        self.date_list = date_list
        self.factor_list = factor_list
        self.block_data = block_data.query(f'{start_date} <= 交易日期 <= {end_date}')

        self.cluster_name = cluster_name

    def get_x(self, trade_date):
        ret_list = list()
        for factor in self.factor_list:
            tmp = pd.DataFrame(np.load(barra_path + f'barras/{factor}.npy')[:, 0, :],
                               index=self.date_list, columns=self.code_list).loc[trade_date]
            ret_list.append(tmp)
        ret_df = pd.DataFrame(ret_list, columns=self.code_list, index=self.factor_list).T
        ret_df = ret_df.dropna(axis=0, how='all')
        ret_df = self.min_max_transfer(ret_df.T)
        ret_df = ret_df.T
        return ret_df

    def min_max_transfer(self, df: pd.DataFrame):
        tmp_df = df.copy()
        scaler = MinMaxScaler()
        im = Imputer(missing_values='NaN', strategy='median', axis=1)
        tmp_df = im.fit_transform(tmp_df)
        ret = scaler.fit_transform(tmp_df.T)
        ret = ret.T
        ret = pd.DataFrame(ret, columns=df.columns, index=df.index)
        return ret

    def calc_category(self, stk_id, trade_date):
        x_train = self.get_x(trade_date)

        estimator = KMeans(n_clusters=5, max_iter=500, precompute_distances='auto', random_state=2022)
        _ = estimator.fit_transform(x_train)
        label = estimator.labels_
        check = pd.Series(label, index=x_train.index)
        ret = check[check == check[stk_id]].index.tolist()
        return ret

    def calc_categories(self, stk_date_list):
        ret_dict = dict()
        pbar = tqdm(range(len(stk_date_list)))
        for idx in pbar:
            stk_id, trade_date = stk_date_list[idx]
            pbar.set_description('并行生成中|%s|%s' % (int(stk_id), int(trade_date)))
            ret_dict[(stk_id, trade_date)] = self.calc_category(stk_id, trade_date)
        return ret_dict

    def get_cluster_list(self, mode='serial', kernal_num=10, output_name=None):
        if not output_name:
            output_name = f'{self.cluster_name}.pkl'

        ret_dict = dict()
        if mode is 'serial':
            pbar = tqdm(range(len(self.block_data)))
            for idx in pbar:
                block = self.block_data.iloc[idx]
                stk_id = block['股票代码']
                trade_date = block['交易日期']
                pbar.set_description('串行生成中|%s|%s' % (int(stk_id), int(trade_date)))
                ret_dict[(stk_id, trade_date)] = self.calc_category(stk_id, trade_date)

        if mode is 'multi':
            stk_date_list = list(zip(self.block_data['股票代码'].tolist(), self.block_data['交易日期'].tolist()))
            multi_dict = util.multiprocess(kernal_num, self.calc_categories, stk_date_list)

            ret_result = dict()
            for k in multi_dict:
                try:
                    ret_result[k] = multi_dict[k].get()
                except:
                    print('多进程内部出错')
                    ret_result[k] = self.calc_categories(stk_date_list)

            for k in ret_result:
                ret_dict.update(ret_result[k])
        util.save_dict2pkl(ret_dict, clusters_path, output_name)
        return ret_dict


if __name__ == '__main__':
    sc = SimiCluster(start_date=20180101, end_date=20200625, factor_list=['LNCAP', 'DASTD'],
                     cluster_name='V1')
    ret_dict = sc.get_cluster_list(mode='multi')
