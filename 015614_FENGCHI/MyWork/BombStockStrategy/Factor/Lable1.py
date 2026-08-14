# coding: utf-8
# Author：fengchi863
# Date ：2021/9/15 13:52

from BombStockStrategy.Factor.basic.crossFactor import crossFactor
from CrossFT.basic.crossUtils import *
from CrossFT.basic.operators import *
from BombStockStrategy.conf.path_conf import label_path


def _fill(arr, l, axis=0):
    if arr.ndim == 2:
        return np.pad(arr, ((l, 0), (0, 0)), mode='constant', constant_values=np.nan)

    elif arr.ndim == 3:
        if axis:
            return np.pad(arr, ((0, 0), (l, 0), (0, 0)), mode='constant', constant_values=np.nan)
        else:
            return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)

    else:
        raise ValueError


class Lable1(crossFactor):
    extend_days = 10
    author = 'fc'
    start = 20140701
    # start = 20210401
    end = 20210531
    logic = '相对于昨日开盘vwap的收益率'
    article = ''
    freq = 'daily'
    basic_datas = {'daily': [], '1min': ['amt', 'vol']}
    save_loc = label_path

    def st_factor(self):
        amt = self.database['1min']['amt']
        vol = self.database['1min']['vol']
        return amt, vol

    def cal_factor(self):
        amt, vol = self.st_factor()
        open_vwap = np.nansum(amt[:, :31, :], axis=1) / np.nansum(vol[:, :31, :], axis=1)
        close_vwap = np.nansum(amt[:, 212:242, :], axis=1) / np.nansum(vol[:, 212:242, :], axis=1)
        ret = close_vwap[2:] / open_vwap[1: -1] - 1
        ret = np.pad(ret[:, None], ((0, 2), (0, 0), (0, 0)), mode='constant', constant_values=0)
        return arr_match_index(ret, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_factor()


if __name__ == '__main__':
    f = Lable1()
    f.check_factor(f.result())
    f.save_result()
