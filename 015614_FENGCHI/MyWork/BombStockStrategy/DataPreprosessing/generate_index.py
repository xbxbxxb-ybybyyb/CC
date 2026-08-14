# coding: utf-8
# Author：fengchi863
# Date ：2021/9/14 9:45

from BombStockStrategy.Factor.basic.crossFactor import crossFactor
from BombStockStrategy.conf.path_conf import index_path
from ShortTermTrading.Util.tools import save_pickle


class IndexGen(crossFactor):
    start = 20140701
    end = 20210531

    def get_code_list(self):
        return self.code_list

    def get_date_list(self):
        return self.date_range


if __name__ == '__main__':
    ig = IndexGen()
    code_list = ig.get_code_list()
    date_list = ig.get_date_list()
    save_pickle(code_list, index_path, 'code_list.pkl')
    save_pickle(date_list, index_path, 'date_list.pkl')
