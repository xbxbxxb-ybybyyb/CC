import numpy as np
from dataApi.tradeDate import get_date_range

def load_m5(start_date=20140801, end_date=20140901, m5_factors=None, m30_factors=None, code_list=None,
                  return_idx=True,
                  m5_path='/arch1/group/800442/800319/HFfactor/DTC2021/data/'):
    time_map_idx = [52, 58, 64, 70, 76, 82, 88,93]
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data//idx_date.npy' )
    idx_code = np.load('/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data//idx_code.npy' )
    idx_time = np.array([1030, 1100, 1300, 1330, 1400, 1430,1455, 1000, 1030, 1100, 1300, 1330,1400, 1430,1455])#np.load('%s/idx_time.npy' % m30_path)

    idx_date1 = np.load('%s/idx_date.npy' % m5_path)
    idx_code1 = np.load('%s/idx_code.npy' % m5_path)
    idx_time1 = np.load('%s/idx_time.npy' % m5_path)
    time_len = idx_time1.shape[0]
    starts = (idx_date1 < date_list[0]).sum()
    shape = (idx_date1 <= date_list[-1]).sum() - starts
    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date1), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date1
    if code_list:
        code_list.sort()
        # TODO: idx_code not sorted
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code1), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code1
        choose &= choose1

    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(m5_factors):
        fp = np.memmap(f'{m5_path}/{f}.npy', dtype='float32', mode='r',
                       shape=(shape, time_len), offset=starts * time_len * 4 + 128)
        X[len(m30_factors) + j] = fp[choose, time_map_idx]
        del fp

    if return_idx:
        return X, y, nolimit, idx_date, idx_code, idx_time
    else:
        return X, y, nolimit

def load_mix_data(start_date=20140801, end_date=20140901, m5_factors=None, m30_factors=None, code_list=None,
                  return_idx=True,
                  m5_path='/arch1/group/800442/800319/HFfactor/DTC2021/data/',
                  m30_path='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/'):
    time_map_idx = [52, 58, 64, 70, 76, 82, 88]
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % m30_path)
    idx_code = np.load('%s/idx_code.npy' % m30_path)
    idx_time = np.load('%s/idx_time.npy' % m30_path)
    time_len = idx_time.shape[0]
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date
    if code_list:
        code_list.sort()
        # TODO: idx_code not sorted
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code
        choose &= choose1
    if return_idx:
        idx_date = idx_date[choose, None].repeat(7, axis=1)
        idx_code = idx_code[choose, None].repeat(7, axis=1)
        idx_time = idx_time[None, -7:].repeat(choose.sum(), axis=0)

    fp = np.memmap(f'{m30_path}/future.npy', dtype='float32', mode='r', offset=128)
    real_y_shape = fp.shape[0] // 7 - starts
    del fp
    real_y_shape = 0 if real_y_shape < 0 else (real_y_shape if real_y_shape < shape else shape)
    real_y_choose = (
            np.arange(choose[:starts + real_y_shape].shape[0])[choose[:starts + real_y_shape]] - starts).tolist()
    real_y_choose = slice(None) if len(real_y_choose) == real_y_shape else real_y_choose

    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    X = np.empty((len(m30_factors) + len(m5_factors), len(choose), 7), dtype=np.float32)
    y = np.empty((len(choose), 7), dtype=np.float32)
    nolimit = np.empty((len(choose), 7), dtype=np.bool)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(m30_factors):
        fp = np.memmap(f'{m30_path}/{f}.npy', dtype='float32', mode='r',
                       shape=(shape, time_len), offset=starts * time_len * 4 + 128)
        X[j] = fp[choose, -7:]
        del fp

    if not real_y_shape:
        y[:] = np.nan
        nolimit[:] = False
    else:
        fp = np.memmap(f'{m30_path}/future.npy', dtype='float32', mode='r',
                       shape=(real_y_shape, 7), offset=starts * 7 * 4 + 128)
        y[:real_y_shape] = fp[real_y_choose, :]
        y[real_y_shape:] = np.nan

        fp = np.memmap(f'{m30_path}/nolimit.npy', dtype='bool', mode='r',
                       shape=(real_y_shape, 7), offset=starts * 7 + 128)
        nolimit[:real_y_shape] = fp[real_y_choose, :]
        nolimit[real_y_shape:] = False

    idx_date1 = np.load('%s/idx_date.npy' % m5_path)
    idx_code1 = np.load('%s/idx_code.npy' % m5_path)
    idx_time1 = np.load('%s/idx_time.npy' % m5_path)
    time_len = idx_time1.shape[0]
    starts = (idx_date1 < date_list[0]).sum()
    shape = (idx_date1 <= date_list[-1]).sum() - starts
    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date1), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date1
    if code_list:
        code_list.sort()
        # TODO: idx_code not sorted
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code1), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code1
        choose &= choose1

    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(m5_factors):
        fp = np.memmap(f'{m5_path}/{f}.npy', dtype='float32', mode='r',
                       shape=(shape, time_len), offset=starts * time_len * 4 + 128)
        X[len(m30_factors) + j] = fp[choose, time_map_idx]
        del fp

    if return_idx:
        return X, y, nolimit, idx_date, idx_code, idx_time
    else:
        return X, y, nolimit
"""

m5_path = '/arch1/group/800442/800319/HFfactor/DTC2021/data/'
m30_path = '/data/group/800319/HFfactor/RealTimeFixRollRobust/data/'
m5_factors = [20201207174832884,
              20201203163535149,
              20201207130708188,
              20201207124000156,
              20201203162921570]
m30_factors = ['WR2d_13h', 'GTJA2', 'sistdwfiavg_re', 'WRMean5d_13h', 'SwingPriceCorr']

X, y, nolimit, idx_date, idx_code, idx_time = load_mix_data(
    start_date=20140801, end_date=20140901, m5_factors=m5_factors, m30_factors=m30_factors,
    code_list=None, return_idx=True,
    m5_path=m5_path,
    m30_path=m30_path)

"""