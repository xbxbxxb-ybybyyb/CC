# coding: utf-8
# Author：fengchi863
# Date ：2022/3/24 13:44

from SimiStock.config.path_config import barra_path2
import numpy as np
import pandas as pd


class BarraFactor:
    def __init__(self):
        date_list = np.load(barra_path2 + 'date_list.npy')
        code_list = np.load(barra_path2 + 'code_list.npy')

        self.date_list = list(date_list)
        self.code_list = list(code_list)

    def get_1factor(self, factor=None, trade_date=None):
        trade_date_idx = self.date_list.index(trade_date)
        ret = np.load(barra_path2 + f'{factor}.npy')[trade_date_idx, 0, :]
        return ret

    def get_factors(self, factor_list: list, trade_date: int):
        ret = list()
        for factor in factor_list:
            ret.append(self.get_1factor(factor, trade_date)[:, None])
        ret = np.concatenate(ret, axis=1).T
        ret = pd.DataFrame(ret)
        ret.columns = self.code_list
        ret.index = factor_list
        return ret


if __name__ == '__main__':
    bf = BarraFactor()
    df = bf.get_factors(['LNCAP', 'MIDCAP'], trade_date=20210104)
    print(df)

