# coding: utf-8
# Author：fengchi863
# Date ：2021/9/15 15:14

from BombStockStrategy.conf.path_conf import samples_path, index_path, factor_path, label_path
import pandas as pd
import numpy as np
from multiprocessing import Pool
from ShortTermTrading.Util.tools import save_pickle


class SampleConcat:
    def __init__(self, start_date=20140701, end_date=20210701):
        self.factor = ['Close', 'HighDownPct', 'LenZtMin', 'UpperShadowPct', 'OpenVsClose']
        self.start_date = start_date
        self.end_date = end_date
        self.code_list = pd.read_pickle(index_path + 'code_list.pkl')
        self.date_list = pd.read_pickle(index_path + 'date_list.pkl')
        self.samples = pd.read_pickle(samples_path + 'samples_tuple_list.pkl')

    def start_concat(self, kernel=12):
        pool = Pool(kernel)
        res_dict = dict()
        for idx, (date, stk_id) in enumerate(self.samples):
            date_idx = self.date_list.index(date)
            code_idx = self.code_list.index(stk_id)
            res_dict[idx] = pool.apply_async(self.wrapper, (date_idx, code_idx))
        print('全部加入队列')
        pool.close()
        pool.join()

        data_queque = dict()
        for idx in res_dict:
            data_queque[idx] = res_dict[idx].get()
        samples = pd.DataFrame([data_queque[x] for x in data_queque])
        # 整理成dataframe
        col_name = ['date', 'stk_id'] + self.factor + ['label']
        samples.columns = col_name
        samples = samples.set_index(['date', 'stk_id'])
        return samples

    def wrapper(self, date_idx, code_idx):
        ret = [self.date_list[date_idx], self.code_list[code_idx]]
        for factor in self.factor:
            factor_npy = np.load(factor_path + f'daily/20140701_20210531/{factor}.npy')
            factor = factor_npy[date_idx, 0, code_idx]
            ret.append(factor)
        # add labels
        label = np.load(label_path + f'daily/20140701_20210531/Lable2.npy')
        ret.append(label[date_idx, 0, code_idx])
        return ret


if __name__ == '__main__':
    sc = SampleConcat()
    concat_samples = sc.start_concat()
    print(len(concat_samples))
    ret = concat_samples.iloc[:-57, :]  # 去掉最后两天的label为0的情况，因为Labels1的计算问题
    save_pickle(ret, samples_path, 'samples_Label2_20211105.pkl')
