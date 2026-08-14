import pandas as pd
import numpy as np
import bottleneck
from model.alphaDataPrepare import winsorize
from dataApi.tradeDate import get_date_range

def roll_nanmean(arr, window, tolerate=0.1):

    n = bottleneck.move_sum(np.isfinite(arr), window, axis=0)[window - 1:]
    n[n / window <= 1 - tolerate] = np.nan
    x = arr.copy()
    x[~ np.isfinite(arr)] = 0.
    cx = bottleneck.move_sum(x, window, axis=0)[window - 1:]
    cx /= n
    return cx

def roll_nanstd(arr, window, tolerate=0.1):

    n = bottleneck.move_sum(np.isfinite(arr), window, axis=0)[window - 1:]
    n[n / window <= 1 - tolerate] = np.nan
    x = arr.copy()
    x[~ np.isfinite(arr)] = 0.
    cx = bottleneck.move_sum(x, window, axis=0)[window - 1:]
    cx2 = bottleneck.move_sum(x ** 2, window, axis=0)[window - 1:]
    return np.sqrt((cx2 - cx ** 2 / n) / (n - 1))

def roll_nant(arr, window, tolerate=0.1):

    n = bottleneck.move_sum(np.isfinite(arr), window, axis=0)[window - 1:]
    n[n / window <= 1 - tolerate] = np.nan
    x = arr.copy()
    x[~ np.isfinite(arr)] = 0.
    cx = bottleneck.move_sum(x, window, axis=0)[window - 1:]
    cx2 = bottleneck.move_sum(x ** 2, window, axis=0)[window - 1:]
    return cx / np.sqrt((n * cx2 - cx ** 2) / (n - 1))

def roll_nanir(arr, window, tolerate=0.1):

    n = bottleneck.move_sum(np.isfinite(arr), window, axis=0)[window - 1:]
    n[n / window <= 1 - tolerate] = np.nan
    x = arr.copy()
    x[~ np.isfinite(arr)] = 0.
    cx = bottleneck.move_sum(x, window, axis=0)[window - 1:]
    cx2 = bottleneck.move_sum(x ** 2, window, axis=0)[window - 1:]
    return cx / np.sqrt((n * cx2 - cx ** 2) * n / (n - 1))

def roll_windows(a, window):
    """Creates rolling-window 'blocks' of length `window` from `a`.
    Note that the orientation of rows/columns follows that of pandas.
    Example
    -------
    import numpy as np
    onedim = np.arange(20)
    twodim = onedim.reshape((5,4))
    print(twodim)
    [[ 0  1  2  3]
     [ 4  5  6  7]
     [ 8  9 10 11]
     [12 13 14 15]
     [16 17 18 19]]
    print(rwindows(onedim, 3)[:5])
    [[0 1 2]
     [1 2 3]
     [2 3 4]
     [3 4 5]
     [4 5 6]]
    print(rwindows(twodim, 3)[:5])
    [[[ 0  1  2  3]
      [ 4  5  6  7]
      [ 8  9 10 11]]
     [[ 4  5  6  7]
      [ 8  9 10 11]
      [12 13 14 15]]
     [[ 8  9 10 11]
      [12 13 14 15]
      [16 17 18 19]]]
    """

    if window > a.shape[0]:
        raise ValueError(
            "Specified `window` length of {0} exceeds length of"
            " `a`, {1}.".format(window, a.shape[0])
        )
    if isinstance(a, (pd.Series, pd.DataFrame)):
        a = a.values
    if a.ndim == 1:
        a = a.reshape(-1, 1)
    shape = (a.shape[0] - window + 1, window) + a.shape[1:]
    strides = (a.strides[0],) + a.strides
    windows = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    if windows.ndim == 1:
        windows = np.atleast_2d(windows)
    return windows

class AlphaFactorSelect(object):


    def __init__(self, start_date, end_date, select_days, tolerate, middle_address, future_days=5, model_days=None):

        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        date_num = len(date_list)

        if isinstance(future_days, int):
            future_days = list(range(1, future_days + 1))
        elif not isinstance(future_days, list):
            raise TypeError('future_days must be int or list')

        model_days = select_days if model_days is None else model_days

        self.middle_address = middle_address
        self.start_date = start_date
        self.end_date = end_date
        self.date_list = date_list
        self.date_num = date_num
        self.select_days = select_days
        self.tolerate = tolerate
        self.future_days = future_days
        self.model_days = model_days

    def load_factor_pool(self, load_address=None):

        load_address = self.middle_address if load_address is None else load_address
        _factor_pool = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (load_address, 'factor_pool', x))
                                          for x in self.date_list)]
        self._factor_pool = _factor_pool

    def roll_factor_pool(self, select_days=None, model_days=None, tolerate=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days
        model_days = self.model_days if model_days is None else model_days
        _factor_pool = self._factor_pool

        if model_days == select_days:
            factor_pool = bottleneck.move_sum(self._factor_pool, model_days, axis=0)[model_days - 1:] == model_days
        else:
            factor_pool = ((bottleneck.move_sum(self._factor_pool, model_days, axis=0)[select_days - 1:] == model_days)
                           & (bottleneck.move_sum(self._factor_pool[:-model_days], select_days - model_days, axis=0)[
                              select_days - model_days - 1:] >= (select_days - model_days) * (1 - tolerate)))

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'factor_pool', factor_pool)
        self.factor_pool = factor_pool

    def roll_factor_corr(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days
        load_address = self.middle_address if load_address is None else load_address

        _factor_corr = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (load_address, 'factor_corr', x))
                                          for x in self.date_list)]
        _factor_corr[~ self._factor_pool] = np.nan
        _factor_corr.transpose(0, 2, 1)[~ self._factor_pool] = np.nan

        factor_corr = roll_nanmean(_factor_corr, select_days, tolerate=tolerate)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'factor_corr', factor_corr)
        self.factor_corr = factor_corr

    def roll_IC(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days

        if (load_address is None) & (hasattr(self, '_IC')):
            _IC = self._IC
        else:
            load_address = self.middle_address if load_address is None else load_address
            _IC = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (load_address, 'IC', x)) for x in self.date_list)]
            _IC.transpose(0, 2, 1)[~ self._factor_pool] = np.nan

        IC = roll_nanmean(_IC, select_days, tolerate=tolerate).transpose(1, 0, 2)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'IC', IC)
        self._IC = _IC
        self.IC = IC

    def roll_rank_IC(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days

        if (load_address is None) & (hasattr(self, '_rank_IC')):
            _rank_IC = self._rank_IC
        else:
            load_address = self.middle_address if load_address is None else load_address
            _rank_IC = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (load_address, 'rank_IC', x)) for x in self.date_list)]
            _rank_IC.transpose(0, 2, 1)[~ self._factor_pool] = np.nan

        rank_IC = roll_nanmean(_rank_IC, select_days, tolerate=tolerate).transpose(1, 0, 2)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'rank_IC', rank_IC)
        self._rank_IC = _rank_IC
        self.rank_IC = rank_IC

    def roll_group_IC(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days

        if (load_address is None) & (hasattr(self, '_group_IC')):
            _group_IC = self._group_IC
        else:
            load_address = self.middle_address if load_address is None else load_address
            _group_IC = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (load_address, 'group_IC', x)) for x in self.date_list)]
            _group_IC.transpose(0, 2, 1)[~ self._factor_pool] = np.nan

        group_IC = roll_nanmean(_group_IC, select_days, tolerate=tolerate).transpose(1, 0, 2)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'group_IC', group_IC)
        self._group_IC = _group_IC
        self.group_IC = group_IC

    def roll_ICIR(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days

        if (load_address is None) & (hasattr(self, '_IC')):
            _IC = self._IC
        else:
            load_address = self.middle_address if load_address is None else load_address
            _IC = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (load_address, 'IC', x)) for x in self.date_list)]
            _IC.transpose(0, 2, 1)[~ self._factor_pool] = np.nan

        ICIR = roll_nanir(_IC, select_days, tolerate=tolerate).transpose(1, 0, 2) * np.sqrt(244)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'ICIR', ICIR)
        self._IC = _IC
        self.ICIR = ICIR

    def roll_rank_ICIR(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days

        if (load_address is None) & (hasattr(self, '_rank_IC')):
            _rank_IC = self._rank_IC
        else:
            load_address = self.middle_address if load_address is None else load_address
            _rank_IC = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (load_address, 'rank_IC', x)) for x in self.date_list)]
            _rank_IC.transpose(0, 2, 1)[~ self._factor_pool] = np.nan

        rank_ICIR = roll_nanmean(_rank_IC, select_days, tolerate=tolerate).transpose(1, 0, 2) * np.sqrt(244)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'rank_ICIR', rank_ICIR)
        self._rank_IC = _rank_IC
        self.rank_ICIR = rank_ICIR

    def roll_MI(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days
        load_address = self.middle_address if load_address is None else load_address

        _MI = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (load_address, 'MI', x)) for x in self.date_list)]
        _MI.transpose(0, 2, 1)[~ self._factor_pool] = np.nan

        MI = roll_nanmean(_MI, select_days, tolerate=tolerate).transpose(1, 0, 2)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'MI', MI)
        self.MI = MI

    def roll_group_MI(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days
        load_address = self.middle_address if load_address is None else load_address

        _group_MI = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (load_address, 'group_MI', x)) for x in self.date_list)]
        _group_MI.transpose(0, 2, 1)[~ self._factor_pool] = np.nan

        group_MI = roll_nanmean(_group_MI, select_days, tolerate=tolerate).transpose(1, 0, 2)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'group_MI', group_MI)
        self.group_MI = group_MI

    def roll_half_IC(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days

        if (load_address is None) & (hasattr(self, '_IC')):
            _IC = self._IC
        else:
            load_address = self.middle_address if load_address is None else load_address
            _IC = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (load_address, 'IC', x)) for x in self.date_list)]
            _IC.transpose(0, 2, 1)[~ self._factor_pool] = np.nan

        IC_near = roll_nanmean(_IC[select_days - select_days // 2:], select_days // 2,
                               tolerate=tolerate).transpose(1, 0, 2)

        IC_far = roll_nanmean(_IC[:select_days // 2 - select_days], select_days // 2,
                              tolerate=tolerate).transpose(1, 0, 2)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'IC_near', IC_near)
        np.save(save_address + 'IC_far', IC_far)

        self._IC = _IC
        self.IC_near = IC_near
        self.IC_far = IC_far

    def roll_half_group_IC(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days

        if (load_address is None) & (hasattr(self, '_group_IC')):
            _group_IC = self._group_IC
        else:
            load_address = self.middle_address if load_address is None else load_address
            _group_IC = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (load_address, 'group_IC', x)) for x in self.date_list)]
            _group_IC.transpose(0, 2, 1)[~ self._factor_pool] = np.nan

        group_IC_near = roll_nanmean(_group_IC[select_days - select_days // 2:], select_days // 2,
                                     tolerate=tolerate).transpose(1, 0, 2)

        group_IC_far = roll_nanmean(_group_IC[:select_days // 2 - select_days], select_days // 2,
                                    tolerate=tolerate).transpose(1, 0, 2)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'group_IC_near', group_IC_near)
        np.save(save_address + 'group_IC_far', group_IC_far)

        self._group_IC = _group_IC
        self.group_IC_near = group_IC_near
        self.group_IC_far = group_IC_far

    def align_date_axis(self, *attributes):

        if len(attributes) == 1:
            attributes = attributes[0]

        arrays = tuple(getattr(self, x) if isinstance(x, str) else x for x in attributes)
        remain_days = min(arr.shape[-2] for arr in arrays)
        arrays = tuple(arr[(slice(None),) * (arr.ndim - 2) + (slice(-remain_days, None), slice(None))] for arr in arrays)
        return arrays

    def distinguish_factor_direction(self, save_address=None):

        evidence = ['ICIR', 'rank_ICIR', 'IC', 'rank_IC', 'group_IC',
                    'IC_near', 'IC_far', 'group_IC_near', 'group_IC_far']
        evidence = [x for x in evidence if hasattr(self, x)]

        if ('IC' in evidence) & ('ICIR' in evidence):
            evidence.remove('IC')
        if ('rank_IC' in evidence) & ('rank_ICIR' in evidence):
            evidence.remove('rank_IC')
        if len(evidence) < 2:
            raise AttributeError("evidence is not enough to distinguish factor direction")
        print(evidence, 'are evidence to distinguish factor direction')

        arrays = self.align_date_axis(evidence)

        factor_pos = np.r_['0,4', tuple(x > 0 for x in arrays)].all(axis=0)
        factor_neg = np.r_['0,4', tuple(x < 0 for x in arrays)].all(axis=0)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'factor_pos', factor_pos)
        np.save(save_address + 'factor_neg', factor_neg)

        self.factor_pos = factor_pos
        self.factor_neg = factor_neg

    def factor_direction_merge(self, arr, pos, neg):

        arr, pos, neg = self.align_date_axis(arr, pos, neg)

        if arr.ndim <= pos.ndim:
            if arr.shape[0] == 2:
                return np.ma.array(arr[0] * neg + arr[1] * pos, mask=~neg & ~pos, fill_value=np.nan).data
            else:
                return np.ma.array(arr * pos - arr * neg, mask=~neg & ~pos, fill_value=np.nan).data
        else:
            if arr.shape[0] == 2:
                data = arr[0] * neg + arr[1] * pos
                data[(slice(None), ) * (arr.ndim - pos.ndim - 1) + (~neg & ~pos, )] = np.nan
            else:
                data = arr * pos - arr * neg
                data[(slice(None), ) * (arr.ndim - pos.ndim) + (~neg & ~pos, )] = np.nan
            return data

    def roll_factor_turn(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days

        load_address = self.middle_address if load_address is None else load_address
        _factor_turn = np.load('%s%s.npy' % (load_address, '_factor_turn'))

        factor_turn = roll_nanmean(_factor_turn, select_days, tolerate=tolerate).transpose(1, 2, 0, 3)
        factor_turn = self.factor_direction_merge(factor_turn, self.factor_pos, self.factor_neg)
        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'factor_turn', factor_turn)

        self.factor_turn = factor_turn

    def load_group_active(self, load_address=None):

        load_address = self.middle_address if load_address is None else load_address
        _group_active = np.r_['0,4', tuple(np.load('%s%s %s.npy' % (load_address, 'group_active', x))
                                          for x in self.date_list)][:, :, :, [0, -1]]
        _group_active[~ self._factor_pool] = np.nan
        self._group_active = _group_active

    def roll_active_gross(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days

        if not hasattr(self, '_group_active'):
            self.load_group_active(load_address)

        active_gross = roll_nanmean(self._group_active, select_days, tolerate=tolerate).transpose(3, 2, 0, 1)
        active_gross = self.factor_direction_merge(active_gross, self.factor_pos, self.factor_neg)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'active_gross', active_gross)
        self.active_gross = active_gross

    def roll_active_net(self, fee, active_address=None, turn_address=None, save_address=None):

        gross = np.load('%s%s.npy' % (
            active_address, 'active_gross')) if active_address is not None else self.active_gross
        turn = np.load('%s%s.npy' % (turn_address, 'factor_turn')) if turn_address is not None else self.factor_turn
        gross, turn = self.align_date_axis(gross, turn)
        net = gross - fee * turn

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'active_net', net)

        self.fee = fee
        self.active_net = net

    def roll_mdd_gross(self, select_days=None, load_address=None, save_address=None):

        select_days = self.select_days if select_days is None else select_days

        if not hasattr(self, '_group_active'):
            self.load_group_active(load_address)

        arr = self._group_active.copy()
        arr[~ np.isfinite(arr)] = 0.
        np.cumsum(arr, axis=0, out=arr)
        arr = roll_windows(arr, select_days)
        arr -= np.maximum.accumulate(arr, axis=1)
        arr *= -1
        arr = arr.max(axis=1)
        arr[arr == 0.] = np.nan
        arr = arr.transpose(3, 2, 0, 1)
        arr = self.factor_direction_merge(arr, self.factor_pos, self.factor_neg)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'mdd_gross', arr)
        self.mdd_gross = arr

    def roll_mdd_net(self, fee=None, select_days=None, load_address=None, save_address=None):

        fee = self.fee if fee is None else fee
        select_days = self.select_days if select_days is None else select_days
        turn = np.load('%s%s.npy' % (load_address, 'factor_turn')) if load_address is not None else self.factor_turn
        arr = roll_windows(self._group_active, select_days).transpose(4, 1, 3, 0, 2)
        arr = self.factor_direction_merge(arr, self.factor_pos, self.factor_neg)
        arr, turn = self.align_date_axis(arr, turn)
        arr -= fee * turn
        arr[~ np.isfinite(arr)] = 0.
        np.cumsum(arr, axis=0, out=arr)
        arr -= np.maximum.accumulate(arr, axis=0)
        arr *= -1
        arr = arr.max(axis=0)
        arr[arr == 0.] = np.nan

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'mdd_net', arr)
        self.mdd_net = arr

    def roll_active_std(self, select_days=None, tolerate=None, load_address=None, save_address=None):

        tolerate = self.tolerate if tolerate is None else tolerate
        select_days = self.select_days if select_days is None else select_days

        if not hasattr(self, '_group_active'):
            self.load_group_active(load_address)

        active_std = roll_nanstd(self._group_active, select_days, tolerate=tolerate).transpose(3, 2, 0, 1)
        active_std = self.factor_direction_merge(active_std, self.factor_pos, self.factor_neg)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'active_std', active_std)
        self.active_std = active_std

    def roll_sp_net(self, active_address=None, std_address=None, save_address=None):

        active_net = np.load('%s%s.npy' % (
            active_address, 'active_net')) if active_address is not None else self.active_net
        active_std = np.load('%s%s.npy' % (std_address, 'active_std')) if std_address is not None else self.active_std
        active_net, active_std = self.align_date_axis(active_net, active_std)
        sp_net = active_net / active_std
        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'sp_net', sp_net)
        self.sp_net = sp_net

    def roll_sp_gross(self, active_address=None, std_address=None, save_address=None):

        active_gross = np.load('%s%s.npy' % (
            active_address, 'active_gross')) if active_address is not None else self.active_gross
        active_std = np.load('%s%s.npy' % (std_address, 'active_std')) if std_address is not None else self.active_std
        active_gross, active_std = self.align_date_axis(active_gross, active_std)
        sp_gross = active_gross / active_std
        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'sp_gross', sp_gross)
        self.sp_gross = sp_gross

    def roll_cm_net(self, active_address=None, mdd_address=None, save_address=None):

        active_net = np.load('%s%s.npy' % (
            active_address, 'active_net')) if active_address is not None else self.active_net
        mdd_net = np.load('%s%s.npy' % (mdd_address, 'mdd_net')) if mdd_address is not None else self.mdd_net
        active_net, mdd_net = self.align_date_axis(active_net, mdd_net)
        cm_net = active_net / mdd_net
        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'cm_net', cm_net)
        self.cm_net = cm_net

    def roll_cm_gross(self, active_address=None, mdd_address=None, save_address=None):

        active_gross = np.load('%s%s.npy' % (
            active_address, 'active_gross')) if active_address is not None else self.active_gross
        mdd_gross = np.load('%s%s.npy' % (mdd_address, 'mdd_gross')) if mdd_address is not None else self.mdd_gross
        active_gross, mdd_gross = self.align_date_axis(active_gross, mdd_gross)
        cm_gross = active_gross / mdd_gross
        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'cm_gross', cm_gross)
        self.cm_gross = cm_gross

    def select_factor_pool(self, active_evidence='active_net', pool_address=None,
                           direction_address=None, active_address=None, save_address=None):

        factor_pool = self.factor_pool if pool_address is None else np.load(
            '%s%s.npy' % (pool_address, 'factor_pool'))
        factor_pos = self.factor_pos if direction_address is None else np.load(
            '%s%s.npy' % (direction_address, 'factor_pos'))
        factor_neg = self.factor_neg if direction_address is None else np.load(
            '%s%s.npy' % (direction_address, 'factor_neg'))
        active = getattr(self, active_evidence) if active_address is None else np.load(
            '%s%s.npy' % (active_address, active_evidence))

        factor_pool, factor_pos, factor_neg, active = self.align_date_axis(factor_pool, factor_pos, factor_neg, active)
        factor_pool_select = factor_pool & (factor_pos | factor_neg) & (active > 0)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'factor_pool_select', factor_pool_select)
        self.factor_pool_select = factor_pool_select

    def grade_factor(self, metrics, weight, winsor=True, method='mad', alpha=0.01,
                     pool_address=None, metrics_address=None, save_address=None):

        factor_pool = self.factor_pool_select if pool_address is None else np.load(
            '%s%s.npy' % (pool_address, 'factor_pool_select'))
        arrays = [getattr(self, m).astype(float) if metrics_address is None
                  else np.load('%s%s.npy' % (metrics_address, m)) for m in metrics]
        _ = self.align_date_axis(arrays + [factor_pool])
        arrays, factor_pool = _[:-1], _[-1]

        ARR = tuple()
        weight = np.asanyarray(weight) / sum(weight)

        for m, arr in zip(metrics, arrays):
            arr[~factor_pool] = np.nan
            arr = arr.swapaxes(0, -1)
            if 'IC' in m:
                arr = np.abs(arr)
            arr_median = np.nanmedian(arr, axis=0)
            arr[factor_pool.swapaxes(0, -1) & ~np.isfinite(arr)] = np.expand_dims(arr_median, axis=0).repeat(
                arr.shape[0], axis=0)[factor_pool.swapaxes(0, -1) & ~np.isfinite(arr)]
            if winsor:
                arr = winsorize(arr, axis=0, method=method, out='raw_rank', alpha=alpha)
            arr_max = np.nanmax(arr, axis=0)
            arr_min = np.nanmin(arr, axis=0) - 1e-7
            arr = (arr - arr_min) / (arr_max - arr_min)
            arr[~factor_pool.swapaxes(0, -1)] = 0.
            ARR += (arr,)
        ARR = np.r_['0,%d' % (factor_pool.ndim + 1), ARR]
        ARR = ARR.transpose(tuple(range(1, ARR.ndim)) + (0,)).dot(weight).swapaxes(0, -1)
        ARR[~factor_pool] = np.nan

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'factor_metrics', ARR)
        self.factor_metrics = ARR

    def grade_multi_period_factor(self, future_days_weight, metrics_address=None,
                                  pool_address=None, direction_address=None, save_address=None):

        metrics = self.factor_metrics if metrics_address is None else np.load(
            '%s%s.npy' % (metrics_address, 'factor_metrics'))
        pos = self.factor_pos if direction_address is None else np.load(
            '%s%s.npy' % (direction_address, 'factor_pos'))
        neg = self.factor_neg if direction_address is None else np.load(
            '%s%s.npy' % (direction_address, 'factor_neg'))
        pool = self.factor_pool_select if pool_address is None else np.load(
            '%s%s.npy' % (pool_address, 'factor_pool_select'))
        metrics, pos, neg, pool = self.align_date_axis(metrics, pos, neg, pool)

        weight = np.asanyarray(future_days_weight) / sum(future_days_weight)
        valid_weight = ~ np.isclose(weight, 0)
        weight = weight[valid_weight]

        metrics = metrics[valid_weight].copy()
        pool = np.all(pool[valid_weight], axis=0)
        pos = np.all(pos[valid_weight], axis=0)
        neg = np.all(neg[valid_weight], axis=0)

        pool &= pos | neg
        metrics[~ np.isfinite(metrics)] = 0.
        metrics = metrics.transpose(tuple(range(1, metrics.ndim)) + (0,)).dot(weight)
        metrics[~pool] = np.nan

        weight = metrics.copy()
        weight[neg] *= -1

        future_days = np.asanyarray(self.future_days)
        future_days_max = max(future_days[valid_weight])

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'factor_weight', metrics)
        self.factor_weight = metrics
        self.future_days_max = future_days_max

    def corr_filter(self, corr_limit, corr_address=None, weight_address=None, save_address=None):

        corr = self.factor_corr if corr_address is None else np.load(
            '%s%s.npy' % (corr_address, 'factor_corr'))
        weight = self.factor_weight.copy() if weight_address is None else np.load(
            '%s%s.npy' % (weight_address, 'factor_weight'))
        corr, weight = self.align_date_axis(corr.swapaxes(0, 1), weight)
        corr = corr.swapaxes(0, 1)

        corr = np.abs(corr)
        corr[~ np.isfinite(corr)] = 1.

        pool = np.isfinite(weight)
        metrics = np.abs(weight)

        corr[~ pool] = 0.
        corr.swapaxes(1, 2)[~ pool] = 0.

        rank = (- metrics).argsort(axis=1)
        corr = corr[np.arange(corr.shape[0])[:, None, None], rank[:, :, None], rank[:, None, :]]
        corr_triu = np.tril_indices(corr.shape[1])
        corr[:, corr_triu[0], corr_triu[1]] = 0.

        corr_pool = np.full_like(pool, True)
        corr_pool[np.arange(corr_pool.shape[0])[:, None], rank] = corr.max(axis=2) < corr_limit
        corr_pool &= pool

        weight[~ corr_pool] = 0.
        weight = (weight.T / np.nansum(np.abs(weight), axis=1)).T

        metrics[~ corr_pool] = np.nan
        metrics = bottleneck.nanrankdata(- metrics, axis=1)

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'factor_weight_corr', weight)
        np.save(save_address + 'factor_rank_corr', metrics)
        self.factor_weight_corr = weight
        self.factor_rank_corr = metrics

    def double_select(self, factor_num_limit=np.inf, factor_proportion_limit=1., load_address=None, save_address=None):

        weight = self.factor_weight_corr.copy() if load_address is None else np.load(
            '%s%s.npy' % (load_address, 'factor_weight_corr'))
        rank = self.factor_rank_corr.copy() if load_address is None else np.load(
            '%s%s.npy' % (load_address, 'factor_rank_corr'))

        pool = np.isfinite(rank)
        valid_num = pool.sum(axis=1)

        double_select = ((rank.T <= factor_num_limit) & (rank.T <= valid_num * factor_proportion_limit)).T
        rank[~ double_select] = np.nan
        weight[~ double_select] = 0.
        weight = (weight.T / np.nansum(np.abs(weight), axis=1)).T

        save_address = self.middle_address if save_address is None else save_address
        np.save(save_address + 'factor_weight_double', weight)
        np.save(save_address + 'factor_rank_double', rank)
        self.factor_weight_double = weight
        self.factor_rank_double = rank

if __name__ == '__main__':

    start_date = 20140102
    end_date = 20181228
    select_days = 120
    tolerate = 0.8
    future_days = 5
    model_days = 60
    fee = 0.001
    metrics = ['active_net', 'sp_net']
    metrics_weight = [1, 1]
    future_days_weight = [0, 0, 0, 0, 1]
    corr_limit = 0.75
    factor_num_limit = np.inf
    factor_proportion_limit = 1.
    middle_address = '/data/user/015836/model/temp20200527/'
    middle_address2 = '/data/user/015836/model/temp20200609/'

    afs = AlphaFactorSelect(start_date, end_date, select_days, tolerate, middle_address2, future_days, model_days)
    afs.load_factor_pool(load_address=middle_address)
    afs.roll_factor_pool()
    afs.roll_factor_corr(load_address=middle_address) #407
    afs.roll_IC(load_address=middle_address) #4.8
    afs.roll_rank_IC(load_address=middle_address) #5.1
    afs.roll_group_IC(load_address=middle_address) #5
    afs.roll_ICIR(load_address=middle_address) #2.3
    afs.roll_rank_ICIR(load_address=middle_address) #1.9
    afs.roll_MI(load_address=middle_address) #4
    afs.roll_group_MI(load_address=middle_address) #5.8
    afs.roll_half_IC(load_address=middle_address) #4.5
    afs.roll_half_group_IC(load_address=middle_address) #4.5
    afs.distinguish_factor_direction() #0.2
    afs.roll_factor_turn(load_address=middle_address) #5.2
    afs.load_group_active(load_address=middle_address) #4.2
    afs.roll_active_gross() #3.6
    afs.roll_active_net(fee=fee) #0.2
    afs.roll_mdd_gross() #51
    afs.roll_mdd_net() #44
    afs.roll_active_std() #3.9
    afs.roll_sp_net() #0.1
    afs.roll_sp_gross() #0.1
    afs.roll_cm_net() #0.1
    afs.roll_cm_gross() #0.1
    afs.select_factor_pool() #0.1
    afs.grade_factor(metrics, metrics_weight) #2.7
    afs.grade_multi_period_factor(future_days_weight) #0.11
    afs.corr_filter(corr_limit=corr_limit) #29
    afs.double_select(factor_num_limit, factor_proportion_limit) #0.1
