from dataApi.tradeDate import get_date_range, get_pre_trade_date
from tqdm import tqdm
import pandas as pd
import numpy as np


class DataPrepare(object):

    def __init__(self, idx_address='/data/group/800319/junkBigFactor/'):

        self._idx_address = idx_address
        self._idx_date = np.load('%s/idx_date.npy' % idx_address).tolist()
        self._idx_time = np.load('%s/idx_time.npy' % idx_address).tolist()
        self._idx_code = np.load('%s/idx_code.npy' % idx_address).tolist()
        self._idx_len = len(self._idx_date)

    def set_date_range(self, start_date, end_date):

        date_range = get_date_range(start_date, end_date)
        start_date = date_range[0]
        end_date = get_pre_trade_date(date_range[-1], -1)
        self.start_idx = self._idx_date.index(start_date)
        self.end_idx = len(self._idx_date) if end_date > self._idx_date[
            -1] else self._idx_date.index(end_date)
        self.length = self.end_idx - self.start_idx
        self.idx_date = self._idx_date[self.start_idx: self.end_idx]
        self.idx_time = self._idx_time[self.start_idx: self.end_idx]
        self.idx_code = self._idx_code[self.start_idx: self.end_idx]

    def load_data(self, factor_list, return_df=True, factor_address=None):

        factor_address = factor_address if factor_address else self._idx_address
        factor_num = len(factor_list)
        arr = np.empty((len(factor_list), self.length), dtype=np.float32)

        for idx in tqdm(range(factor_num)):
            try:
                fp = np.memmap('%s/%s.npy' % (factor_address, factor_list[idx]),
                               dtype='float32', mode='r', shape=self._idx_len, offset=128)
                arr[idx] = fp[self.start_idx: self.end_idx]
                del fp
            except:
                print(factor_list[idx])

        if return_df:
            arr = pd.DataFrame(arr.T, index=[self.idx_date, self.idx_time, self.idx_code],
                               columns=factor_list)
            arr.index.names = ['date', 'time', 'code']

        return arr

import time

if __name__ == '__main__':
    dp = DataPrepare()

    e = time.time()
    dp.set_date_range(20150105,20151113)
    data = dp.load_data([str(x).zfill(4) for x in range(101,169)]+[str(x).zfill(4) for x in range(9101,9115)])
    use_time = time.time() - e
    print(use_time)