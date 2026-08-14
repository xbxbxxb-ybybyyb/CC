import sys
import os

sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/016385/test/digger_factor')
from dataApi.tradeDate import get_date_range, get_sub_date_index, get_pre_trade_date, trade_minutes
from dataApi.stockList import clean_stock_list
from dataApi.getData import get_minute_1factor
from basic.crossConfig import cross_loc, cross_range, cross_freqs
from basic.crossUtils import load_material, cross_resample
from basic.operators import  ArrReshape
import numpy as np
import gc
import warnings
import bottleneck

warnings.filterwarnings("ignore")


def dt_forward(x, m):
    ar = ArrReshape()
    return ar.to3d(np.pad(ar.to2d(x)[m:], ((0, m), (0, 0)), mode='constant', constant_values=np.nan))


def stats_range(date_index, date_list):
    date_list = np.asanyarray(date_list)
    date_index = np.asanyarray(date_index + [len(date_list)])
    start = date_list[date_index[:-1]]
    end = date_list[date_index[1:] - 1]
    return start, end


def calc_corr(x, y, x2, y2, xy, n):
    corr = (xy - x * y / n) / ((x2 - x ** 2 / n) * (y2 - y ** 2 / n)) ** 0.5
    corr = np.where(np.isfinite(corr), corr, 0)
    # corr = corr if corr.size > 1 else corr.item()
    return corr


def calc_raw_corr(x, y):
    cx2 = (x ** 2).sum()
    cy2 = (y ** 2).sum(axis=-1)
    cxy = (x * y).sum(axis=-1)
    cn = x.size
    cx = x.sum()
    cy = y.sum(axis=-1)
    corr = (cxy - cx * cy / cn) / ((cx2 - cx ** 2 / cn) * (cy2 - cy ** 2 / cn)) ** 0.5
    corr = np.where(np.isfinite(corr), corr, 0)
    # corr = corr if corr.size > 1 else corr.item()
    return corr


class cross_test(object):

    def get_stock_pool(self, date_list, code_list, address):
        name = 'stock_pool_{}_{}_{}.npy'.format(date_list[0], date_list[-1], len(code_list))
        if name in os.listdir(address):
            #print('loaded existed st pool')
            stock_pool = np.load(address + '/' + name)
        else:
            stock_pool = \
                clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240, no_pause=True, least_recover_days=1,
                                 no_pause_limit=0.5, no_pause_stats_days=120, no_limit_up=False, no_limit_down=False,
                                 other_limit=None, start_date=None, end_date=None, trade_mode=False,
                                 address='/data/group/800442/800319/junkData/daily').loc[
                    date_list, code_list].values.astype(np.float32)
            stock_pool = np.ascontiguousarray(stock_pool[:, None, :])
            np.save(address + '/' + name, stock_pool)
        return stock_pool

    def get_future(self, date_list, code_list, address, forcast_days, freq, forward_t=1, windows=5):

        name = 'future_{}_{}_{}_{}_{}.npy'.format(date_list[0], date_list[-1], len(code_list),
                                                  '&'.join(map(str, forcast_days)), freq)
        if name in os.listdir(address):
            #print('loaded existed future')
            future = np.load(address + '/' + name)
        else:
            d = {1: 'daily', 8: '30mins', 48: '5mins', 242: '1min'}
            if isinstance(forcast_days, int):
                f_end = get_pre_trade_date(date_list[-1], - forcast_days - 1)
                # TODO 因为读取的就是adj的数据，目前不考虑复权系数adj
                close = get_minute_1factor('close_badj', date_list[0], f_end, code_list=code_list).values
                idx = cross_resample(np.arange((len(date_list) + forcast_days) * 242).reshape((-1, 242, 1)) +
                                     (np.arange(windows) + forward_t)[None, None, :], d[freq],shift=True)
                idx = np.fmin(idx, ((np.arange(len(date_list) + forcast_days) + 1) * 242)[:, None, None])
                twap = np.nanmean(close[idx], axis=2)
                future = (twap[forcast_days:len(date_list) + forcast_days, :, :] / twap[:len(date_list), :, :] - 1)
            else:
                tfuture = 0
                for forcast_day in forcast_days:
                    f_end = get_pre_trade_date(date_list[-1], - forcast_day - 1)
                    close = get_minute_1factor('close_badj', date_list[0], f_end, code_list=code_list).values
                    idx = cross_resample(np.arange((len(date_list) + forcast_day) * 242).reshape((-1, 242, 1)) + \
                                         (np.arange(windows) + forward_t)[None, None, :], d[freq],shift=True)
                    idx = np.fmin(idx, ((np.arange(len(date_list) + forcast_day) + 1) * 242)[:, None, None])
                    twap = np.nanmean(close[idx], axis=2)
                    if isinstance(tfuture, int):
                        tfuture = (twap[forcast_day:len(date_list) + forcast_day, :, :] / twap[:len(date_list), :,
                                                                                          :] - 1)
                    else:
                        tfuture += (twap[forcast_day:len(date_list) + forcast_day, :, :] / twap[:len(date_list), :,
                                                                                           :] - 1)
                future = tfuture / len(forcast_days)
            future = np.ascontiguousarray(future.astype(np.float32))
            np.save(address + '/' + name, future)
        return future

    def get_limit_status(self, freq, date_list, code_list, address):

        name = 'limit_status_{}_{}_{}_{}.npy'.format(date_list[0], date_list[-1], len(code_list), freq)
        if name in os.listdir(address):
            #print('loaded existed limit status')
            limit_status = np.load(address + '/' + name)
        else:
            d = {1: 'daily', 8: '30mins', 48: '5mins', 242: '1min'}
            limit_status = load_material('limit_status', date_list[0], date_list[-1], d[freq],
                                         '/arch1/group/800442/800319/AAcross/basic/datas',
                                         code_list).reshape((-1, freq, len(code_list)))
            limit_status = np.ascontiguousarray(limit_status.astype(np.float32))
            np.save(address + '/' + name, limit_status)
        return limit_status

    def _get_ret(self, splits, sign, pos, ret, pool, methods, save_raw=False, cstd=False):
        for i, method in enumerate(methods):
            if i == len(methods) - 1 and cstd:
                std = ret

            if method[1] == 'sum':
                sign = sign.sum(axis=method[0])
                pos = pos.sum(axis=method[0])
                ret = ret.sum(axis=method[0])
                pool = pool.sum(axis=method[0])
            elif method[1] == 'mean':
                ret = ret.sum(axis=method[0]) / sign.sum(axis=method[0])
                sign = np.isfinite(ret)
                ret[~ sign] = 0
                sign = sign.astype('float32')
                pos = (ret > 0).astype('float32')
                pool = (pool.sum(axis=method[0]) > 0).astype('float32')

        signs, poss, rets, stds, sharps = [], [], [], [], []
        for split in splits:
            sign_split = np.add.reduceat(sign, split, axis=0)  # (num_year,);前top的个数
            pos_split = np.add.reduceat(pos, split, axis=0)  # (num_year,);前top中盈利个数
            ret_split = np.add.reduceat(ret, split, axis=0)  # (num_year,)；前top收益
            pool_split = np.add.reduceat(pool, split, axis=0) if isinstance(pool,
                                                                            np.ndarray) else None  # (num_year,)，总个数（非nan)

            signs.append(np.where(pool_split == 0, 0, sign_split / pool_split))  # (num_year,), top占比
            poss.append(np.where(sign_split == 0, 0, pos_split / sign_split))  # (num_year,)，收益为正的比例
            rets.append(np.where(sign_split == 0, 0, ret_split / sign_split))  # (num_year,)，平均收益

            if cstd:
                std_split = np.array(
                    [np.nanstd(std[start:end], axis=tuple([0] + [x for x in methods[-1][0]])) for start, end in
                     zip(split, split[1:] + [len(std)])])
                stds.append(std_split)
                sharps.append(np.where(std_split == 0, np.nan, rets[-1] / std_split))
        if len(splits):
            signs.append(sign_split.sum(axis=0) / pool_split.sum(axis=0))  # float
            poss.append(pos_split.sum(axis=0) / sign_split.sum(axis=0))  # float
            rets.append(ret_split.sum(axis=0) / sign_split.sum(axis=0))  # float

        if save_raw:
            rets.append(ret)
        if cstd:
            std = np.array([np.nanstd(std, axis=tuple([0] + [x for x in methods[-1][0]]))])
            stds.append(std)
            sharps.append(rets[-1] / std)
            return signs, poss, rets,stds, sharps
        return signs, poss, rets

    def get_ret_details(self, factor, top_tile, axis, splits):
        name = 'cross' if axis else 'timeseries'
        factor = factor.reshape(self._test_date_num * max(self.freq - 1, 1), self._code_num)  # (dt,code)
        if axis:
            sign_threshold = np.nanquantile(factor, top_tile, axis, keepdims=True)\
                            .reshape(self._test_date_num, max(self.freq - 1, 1), -1)  # 截面上的百分位数
        else:
            sign_threshold = np.nanquantile(factor, top_tile, axis)  # (code,),时序上的百分位数
        factor = factor.reshape(self._test_date_num, max(self.freq - 1, 1), self._code_num)
        splits_name = ['month' if x == 'M' else 'half' for x in splits]
        splits = [self.dsplits[x] for x in splits]
        sign = (factor >= sign_threshold) & self._future_finite  # 找到top_tile的日期时点,(d,t,c)
        future2 = self._future.copy()
        future2[~ sign] = 0
        positive = future2 > 0
        pool = self._future_finite

        # mix mode, d
        sign_ratio_mix, pos_ratio_mix, ret_ratio_mix, std_mix, sharp_mix = self._get_ret(splits, sign, positive, future2, pool,[((1,2),'sum')],cstd=True)

        # time mean then mix mode, dc
        sign_ratio_dc_mean, pos_ratio_dc_mean, ret_ratio_dc_mean = self._get_ret(splits,  sign, positive, future2, pool,[((1,),'mean'),((1,),'sum')])

        # time code mix mean then date mode
        sign_ratio_d_mean, pos_ratio_d_mean, ret_ratio_d_mean = self._get_ret(splits,  sign, positive, future2, pool,[((1,2),'mean')],True)

        # time mean then code mean then date mode
        _sign_ratio_d_mean, _pos_ratio_d_mean, _ret_ratio_d_mean = self._get_ret(splits,  sign, positive, future2, pool,[((1,),'mean'),((1,),'mean')],True)

        # date code mix then time
        sign_ratio_dt, pos_ratio_dt, ret_ratio_dt, std_dt, sharp_dt = self._get_ret(splits, sign, positive, future2, pool, [((2,), 'sum')],cstd=True)

        # date time mix then code
        sign_ratio_c, pos_ratio_c, ret_ratio_c, std_c, sharp_c = self._get_ret(splits, sign, positive, future2, pool, [((1,), 'sum')],cstd=True)

        # time mean then date mean then code
        _sign_ratio_c, _pos_ratio_c, _ret_ratio_c= self._get_ret(splits,  sign, positive, future2, pool,[((1,),'mean')])

        result = {'tc_d_ret_{}'.format(name): ret_ratio_d_mean[-1],
                  't_c_d_ret_{}'.format(name): _ret_ratio_d_mean[-1]}

        for i, t in enumerate(splits_name + ['all']):
            result.update({
                # dtc mode
                'dtc_sign_{}_{}'.format(t, name): sign_ratio_mix[i],
                'dtc_pos_{}_{}'.format(t, name): pos_ratio_mix[i],
                'dtc_ret_{}_{}'.format(t, name): ret_ratio_mix[i],
                'dtc_std_{}_{}'.format(t, name): std_mix[i],
                'dtc_sharp_{}_{}'.format(t, name): sharp_mix[i],

                # t_dc mode, time mean后再算
                't_dc_sign_{}_{}'.format(t, name): sign_ratio_dc_mean[i],
                't_dc_pos_{}_{}'.format(t, name): pos_ratio_dc_mean[i],
                't_dc_ret_{}_{}'.format(t, name): ret_ratio_dc_mean[i],

                # tc_d_mode，time code mean再算
                'tc_d_sign_{}_{}'.format(t, name): sign_ratio_d_mean[i],
                'tc_d_pos_{}_{}'.format(t, name): pos_ratio_d_mean[i],
                'tc_d_ret_{}_{}'.format(t, name): ret_ratio_d_mean[i],

                # t_c_d_mode， time mean code mean 再算
                't_c_d_pos_{}_{}'.format(t, name): _pos_ratio_d_mean[i],
                't_c_d_ret_{}_{}'.format(t, name): _ret_ratio_d_mean[i],

                # dc_t mode，date code mean再算
                'dc_t_sign_{}_{}'.format(t, name): sign_ratio_dt[i],
                'dc_t_pos_{}_{}'.format(t, name): pos_ratio_dt[i],
                'dc_t_ret_{}_{}'.format(t, name): ret_ratio_dt[i],
                'dc_t_std_{}_{}'.format(t, name): std_dt[i],
                'dc_t_sharp_{}_{}'.format(t, name): sharp_dt[i],

                # dt_c mode，date time mean再算
                'dt_c_sign_{}_{}'.format(t, name): sign_ratio_c[i],
                'dt_c_pos_{}_{}'.format(t, name): pos_ratio_c[i],
                'dt_c_ret_{}_{}'.format(t, name): ret_ratio_c[i],
                'dt_c_std_{}_{}'.format(t, name): std_c[i],
                'dt_c_sharp_{}_{}'.format(t, name): sharp_c[i],

                # t_d_c mode，time mean ,date mean 再算
                't_d_c_sign_{}_{}'.format(t, name): _sign_ratio_c[i],
                't_d_c_pos_{}_{}'.format(t, name): _pos_ratio_c[i],
                't_d_c_ret_{}_{}'.format(t, name): _ret_ratio_c[i],
            })
        return result

    def reduce_sum(self, arr, splits):
        arr_splits = []
        for split in splits:
            tarr = np.add.reduceat(arr, split, axis=0)
            arr_splits.append(tarr)
        arr_total = arr.sum(axis=0)
        return arr_splits, arr_total

    def reduce_mean_std(self, arr, splits):
        mean_splits = []
        std_splits = []
        mean_std_splits = []
        finite = np.isfinite(arr)
        arr[~ finite] = 0
        finite = finite.sum(axis=tuple(range(1, arr.ndim)))
        for split in splits:
            tfinite = np.add.reduceat(finite, split).astype('float32')
            tarr = arr.sum(axis=tuple(range(1, arr.ndim)))
            tarr = np.add.reduceat(tarr, split)
            tarr /= tfinite
            tarr[~ np.isfinite(tarr)] = np.nan
            mean_splits.append(tarr)
            tarr_std = np.array([np.nanstd(arr[start:end]) for start, end in zip(split, split[1:] + [len(tarr)])])
            std_splits.append(tarr_std)
            tarr_mean_std = tarr / tarr_std
            tarr_mean_std[~ np.isfinite(tarr_mean_std)] = np.nan
            mean_std_splits.append(tarr_mean_std)
        mean_total = arr.sum() / finite.sum()
        std_total = arr.std()
        mean_std_total = mean_total / std_total
        mean_splits.append(mean_total)
        std_splits.append(std_total)
        mean_std_splits.append(mean_std_total)
        return mean_splits, std_splits, mean_std_splits

    def _get_ic(self, basics, axiss, splits):
        x, y, x2, y2, xy, n = basics

        if 0 in axiss:
            axiss = tuple([x for x in axiss if x != 0])
            c2x = x.sum(axis=axiss)
            c2y = y.sum(axis=axiss)
            c2x2 = x2.sum(axis=axiss)
            c2y2 = y2.sum(axis=axiss)
            c2xy = xy.sum(axis=axiss)
            c2n = n.sum(axis=axiss)
            c2x_splits, c2x = self.reduce_sum(c2x, splits)
            c2y_splits, c2y = self.reduce_sum(c2y, splits)
            c2x2_splits, c2x2 = self.reduce_sum(c2x2, splits)
            c2y2_splits, c2y2 = self.reduce_sum(c2y2, splits)
            c2xy_splits, c2xy = self.reduce_sum(c2xy, splits)
            c2n_splits, c2n = self.reduce_sum(c2n, splits)
            ic_means, ic_stds, icirs = [], [], []
            for i in range(len(splits)):
                corr = calc_corr(c2x_splits[i], c2y_splits[i], c2x2_splits[i], c2y2_splits[i], c2xy_splits[i],
                                 c2n_splits[i])

                ic_mean = np.nanmean(corr, axis=tuple(range(1, corr.ndim)))
                ic_std = np.nanstd(corr, axis=tuple(range(1, corr.ndim)))
                icir = np.where(ic_std==0,np.nan,ic_mean / ic_std)
                ic_means.append(ic_mean)
                ic_stds.append(ic_std)
                icirs.append(icir)
            corr = calc_corr(c2x, c2y, c2x2, c2y2, c2xy, c2n)
            mean_total, std_total = np.nanmean(corr), np.nanstd(corr)
            ic_means.append(mean_total)
            ic_stds.append(std_total)
            if std_total:
                icirs.append(mean_total / std_total)
            else:
                icirs.append(np.nan)

        else:
            c2x = x.sum(axis=axiss)
            c2y = y.sum(axis=axiss)
            c2x2 = x2.sum(axis=axiss)
            c2y2 = y2.sum(axis=axiss)
            c2xy = xy.sum(axis=axiss)
            c2n = n.sum(axis=axiss)
            corr = calc_corr(c2x, c2y, c2x2, c2y2, c2xy, c2n)
            ic_means, ic_stds, icirs = self.reduce_mean_std(corr, splits)
        return ic_means, ic_stds, icirs

    def get_ic_details(self, factor, splits):
        x = factor
        y = self._future
        n = self._future_finite.astype('float32')
        x2 = x ** 2
        y2 = y ** 2
        xy = x * y
        factor_basic = (x, y, x2, y2, xy, n)
        splits1 = [self.dsplits[x] for x in splits]
        ic_t, ic_std_t, icir_t = self._get_ic(factor_basic, (1,), splits1)
        ic_d, ic_std_d, icir_d = self._get_ic(factor_basic, (0,), splits1)
        ic_c, ic_std_c, icir_c = self._get_ic(factor_basic, (2,), splits1)
        ic_tc, ic_std_tc, icir_tc = self._get_ic(factor_basic, (1, 2), splits1)
        ic_dc, ic_std_dc, icir_dc = self._get_ic(factor_basic, (0, 2), splits1)
        ic_dt, ic_std_dt, icir_dt = self._get_ic(factor_basic, (0, 1), splits1)
        ic_dtc, ic_std_dtc, icir_dtc = self._get_ic(factor_basic, (0, 1, 2), splits1)

        # 为了让正负因子进行比较
        ic_direction = 2 * (ic_dt[-1] > 0) - 1

        result = {'ic_direction': ic_direction}

        for i, type in enumerate(['month' if x == 'M' else 'half' for x in splits] + ['all']):
            d = {
                'ic_dtc_{}'.format(type): ic_dtc[i] * ic_direction,
                'ic_dt_{}'.format(type): ic_dt[i] * ic_direction,
                'ic_tc_{}'.format(type): ic_tc[i] * ic_direction,
                'ic_dc_{}'.format(type): ic_dc[i] * ic_direction,
                'ic_d_{}'.format(type): ic_d[i] * ic_direction,
                'ic_t_{}'.format(type): ic_t[i] * ic_direction,
                'ic_c_{}'.format(type): ic_c[i] * ic_direction,

                'ic_std_dtc_{}'.format(type): ic_std_dtc[i] * ic_direction,
                'ic_std_dt_{}'.format(type): ic_std_dt[i] * ic_direction,
                'ic_std_tc_{}'.format(type): ic_std_tc[i] * ic_direction,
                'ic_std_dc_{}'.format(type): ic_std_dc[i] * ic_direction,
                'ic_std_d_{}'.format(type): ic_std_d[i] * ic_direction,
                'ic_std_t_{}'.format(type): ic_std_t[i] * ic_direction,
                'ic_std_c_{}'.format(type): ic_std_c[i] * ic_direction,

                'icir_dtc_{}'.format(type): icir_dtc[i] * ic_direction,
                'icir_dt_{}'.format(type): icir_dt[i] * ic_direction,
                'icir_tc_{}'.format(type): icir_tc[i] * ic_direction,
                'icir_dc_{}'.format(type): icir_dc[i] * ic_direction,
                'icir_d_{}'.format(type): icir_d[i] * ic_direction,
                'icir_t_{}'.format(type): icir_t[i] * ic_direction,
                'icir_c_{}'.format(type): icir_c[i] * ic_direction
            }
            result.update(d)
        return result

    def __init__(self, test_start_date=20140701, end_date=20150830, test_drop_days=0, standardize_days=40,
                 seed=3251, freq=48, forcast_days=1, split= ['M', 'H'],address=cross_loc + '/basic/datas'):
        test_date_list = get_date_range(test_start_date, end_date)
        test_start_date = test_date_list[0]
        end_date = test_date_list[-1]
        calc_start_date = get_pre_trade_date(test_start_date, test_drop_days)
        calc_date_list = get_date_range(calc_start_date, end_date)
        test_date_num = len(test_date_list)
        calc_date_num = len(calc_date_list)
        code_list = np.load(cross_loc + '/basic/code_list.npy').tolist()
        stock_pool = self.get_stock_pool(test_date_list, code_list, address) > 0.5 #(d,c)

        if freq == 1:
            future = self.get_future(test_date_list, code_list, address, forcast_days, freq)[:, -1:]
            limit_status = self.get_limit_status(freq, test_date_list, code_list, address)[:, -1:] < 0.5
        else:
            future = self.get_future(test_date_list, code_list, address, forcast_days, freq)[:, : -1]
            limit_status = self.get_limit_status(freq, test_date_list, code_list, address)[:, : -1] < 0.5
        future_finite = np.isfinite(future) & limit_status & stock_pool

        future[~ future_finite] = 0
        valid_daily_code_num = stock_pool.sum(axis=1) #(d,)
        valid_daily_sign_num = future_finite.sum(axis=(1, 2))
        valid_sample = stock_pool.sum() * max(freq - 1, 1)
        code_num = len(code_list)

        random_state = np.random.RandomState(seed)
        sample = random_state.choice(valid_sample, 3000, replace=False)

        self._calc_start_date = calc_start_date
        self._end_date = end_date
        self._valid_daily_sign_num = valid_daily_sign_num
        self._valid_daily_code_num = valid_daily_code_num
        self._stock_pool = stock_pool
        self._calc_date_list = calc_date_list
        self._test_date_list = test_date_list
        self._calc_date_num = calc_date_num
        self._test_date_num = test_date_num
        self._standardize_days = standardize_days
        self._test_drop_days = test_drop_days
        self._future_finite = future_finite
        self._valid_sample = valid_sample
        self._code_list = code_list
        self._code_num = code_num
        self._future = future
        self._sample = sample
        self._top_tile = 0.05
        self.Material = {}
        self.freq = freq
        self.split = split
        self.dates_exempt = [20150710, 20150713, 20150714, 20160104, 20160105, 20160106, 20160107, 20160108, 20200203,
                             20200204]

    def test_factor(self, factor):
        #print('this is version2: include icir, sharp, std; freq:monthly, yearly, all')
        # ************************** 因子处理********************************
        factor[[self._test_date_list.index(x) for x in self.dates_exempt if x in self._test_date_list]] = np.nan
        factor_finite = np.isfinite(factor)

        if self._standardize_days:  # 时间序列上进行标准化
            factor[~ factor_finite] = 0
            factor2 = factor ** 2

            d_cf = factor.sum(axis=1)
            d_cf2 = factor2.sum(axis=1)
            d_cn = factor_finite.sum(axis=1)

            rd_cf = bottleneck.move_sum(d_cf, self._standardize_days, axis=0)
            rd_cf2 = bottleneck.move_sum(d_cf2, self._standardize_days, axis=0)
            rd_cn = bottleneck.move_sum(d_cn.astype('float32'), self._standardize_days, axis=0)
            rd_cn[rd_cn < self._standardize_days * self.freq / 2] = np.nan

            rd_mean = rd_cf / rd_cn
            rd_std = ((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5
            rd_std[rd_std == 0] = np.nan

            factor[~ factor_finite] = np.nan
            if self._test_drop_days:
                factor = (factor[self._test_drop_days:] - rd_mean[self._test_drop_days - 1: -1, None]
                          ) / rd_std[self._test_drop_days - 1: -1, None]
            else:
                factor = (factor - rd_mean[:, None]) / rd_std[:, None]
            del d_cf, d_cf2, rd_cf, rd_cf2, rd_cn, rd_mean, rd_std, factor2
            factor = factor.clip(-6, 6)  # 去除极端值
        else:
            #print('非标准化')
            factor = factor[self._test_drop_days:, :]
            factor = np.clip(factor, np.round(np.quantile(factor, 0.01, axis=(0, 1), keepdims=True), 4),
                             np.round(np.quantile(factor, 0.99, axis=(0, 1), keepdims=True), 4))  # 去除极端值
        if self.freq != 1:
            factor = factor[self._test_drop_days:, :-1]  # 这个目的是为了去除15:00的影响

        factor_finite = np.isfinite(factor)
        factor[~ factor_finite] = 0

        factor_sample = factor[self._stock_pool.repeat(max(self.freq - 1, 1), axis=1)][self._sample]
        factor[~ self._future_finite] = 0
        factor_complete = (factor_finite & self._future_finite).sum() \
                          / self._valid_daily_sign_num.sum()  # factor中非na的比例
        self.dsplits = {split: get_sub_date_index(self._test_date_list, split) for split in ['M', 'H']}
        start_dates, end_dates = stats_range(self.dsplits['H'], self._test_date_list)
        mstart_dates, mend_dates = stats_range(self.dsplits['M'], self._test_date_list)
        top_tile = self._top_tile if self._top_tile > 0.5 else 1 - self._top_tile
        # basic information 
        result = {
            'date_list': self._test_date_list,
            'date_num': self._test_date_num,
            'date_half_year_starts': start_dates,
            'date_half_year_ends': end_dates,
            'date_month_starts ': mstart_dates,
            'date_month_ends ': mend_dates,
            'date_standardize_days': self._standardize_days,

            'code_num': self._code_num,
            'future_top_tile': top_tile,
            'factor_complete': factor_complete,
            'factor_sample': factor_sample}
        # ************************** IC计算（d,t,c)********************************
        ic_result = self.get_ic_details(factor, self.split)
        result.update(ic_result)
        # ************************** ret计算（d,t,c)********************************
        factor *= ic_result['ic_direction']
        factor[~ (factor_finite & self._future_finite)] = np.nan

        ret_timeseries_res = self.get_ret_details(factor, top_tile, 0, self.split)
        ret_cross_res = self.get_ret_details(factor, top_tile, 1, self.split)

        result.update(ret_timeseries_res)
        result.update(ret_cross_res)

        return result


if __name__ == '__main__':
    f = 8
    ft = cross_test(freq=f, forcast_days=[1, 3, 5],split=['H'])
    res = ft.test_factor(np.random.random((288, f, 4512)))
    print(res)
    # for key in res.keys():
    #     if '_tc' in key:
    #         print(key, res[key])
