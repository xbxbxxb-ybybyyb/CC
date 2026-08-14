# @Time : 2021/10/12 20:16
# @Author : Zhichen Lu
# @File : MonthlyFactorEvaluation.py
import sys
sys.path.extend(['/data/user/015614/MyWork', '/data/user/015614/MyWork/StrongStockModel', '/data/user/015614/MyWork/StrongStockModel/System', '/data/user/015614/MyWork/LimitUpPredStrategy', '/data/user/015614/MyWork/FaaMonitor', '/data/user/015614/MyWork/R2D2', '/data/user/015614/MyWork/CrossFT', '/data/user/015614/MyWork/CrossFT/basic', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件', '/data/user/015614/MyWork/SimiStock', '/data/user/015614/MyWork/GitProject/Factor', '/data/user/015614/MyWork/GitProject', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib/riskfolio', '/data/user/015614/MyWork/SimiStock/dataApi', '/data/user/015614/MyWork/ensemblemonitor-strategy-python', '/data/user/015614/MyWork/MillenniumFalcon', '/data/user/015614/MyWork'])
import numpy as np
from dataApi.tradeDate import get_sub_date_index
import bottleneck
import pandas as pd
import os,gc
from tqdm import tqdm
from dataApi.tradeDate import get_pre_trade_date

def stats_range(date_index, date_list):
    date_list = np.asanyarray(date_list)
    date_index = np.asanyarray(date_index + [len(date_list)])
    start = date_list[date_index[:-1]]
    end = date_list[date_index[1:] - 1]
    return start, end

def calc_corr(x, y, x2, y2, xy, n):
    corr = (xy - x * y / n) / ((x2 - x ** 2 / n) * (y2 - y ** 2 / n)) ** 0.5
    corr = np.where(np.isfinite(corr), corr, 0)
    corr = np.where(n >= 4, corr, np.nan)
    corr = corr if corr.size > 1 else corr.item()
    return corr

def test_factor(factor,future2,test_date_list,freq,test_drop_days=0, standardize_days=0, move_window=12):
    # factor = factor.values[:,None,:]
    # future2 = label.values[:,None,:]
    # test_date_list = label.index.tolist()
    # freq = 1

    factor_finite = np.isfinite(factor)
    future_finite = np.isfinite(future2)
    if standardize_days:
        factor[~ factor_finite] = 0
        factor2 = factor ** 2

        d_cf = factor.sum(axis=1)
        d_cf2 = factor2.sum(axis=1)
        d_cn = factor_finite.sum(axis=1)

        rd_cf = np.lib.stride_tricks.as_strided(d_cf, shape=(
            d_cf.shape[0] - standardize_days + 1, standardize_days, d_cf.shape[1]), strides=(
            d_cf.strides[0], d_cf.strides[0], d_cf.strides[1])).sum(axis=1)

        rd_cf2 = np.lib.stride_tricks.as_strided(d_cf2, shape=(
            d_cf2.shape[0] - standardize_days + 1, standardize_days, d_cf2.shape[1]), strides=(
            d_cf2.strides[0], d_cf2.strides[0], d_cf2.strides[1])).sum(axis=1)

        rd_cn = np.lib.stride_tricks.as_strided(d_cn, shape=(
            d_cn.shape[0] - standardize_days + 1, standardize_days, d_cn.shape[1]), strides=(
            d_cn.strides[0], d_cn.strides[0], d_cn.strides[1])).sum(axis=1).astype(float)

        rd_cn[rd_cn < standardize_days * freq / 2] = np.nan
        factor[~ factor_finite] = np.nan

        rd_mean = (rd_cf / rd_cn)[test_drop_days - standardize_days: -1]
        rd_std = (((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5)[test_drop_days - standardize_days: -1]
        rd_std[rd_std == 0] = np.nan

        factor = (factor[test_drop_days:] - rd_mean[:, None]) / rd_std[:, None]
        factor = factor.clip(-6, 6)
        factor_finite = np.isfinite(factor)
        factor[~ factor_finite] = 0
        del d_cf, d_cf2, rd_cf, rd_cf2, rd_cn

    else:
        factor[~ factor_finite] = 0
        future2[~future_finite] = 0
        factor = factor[test_drop_days:]
        factor_finite = factor_finite[test_drop_days:]
        factor[~ factor_finite] = 0

    factor2 = factor.copy()
    month_split = get_sub_date_index(test_date_list, 'M')
    start_dates, end_dates = stats_range(month_split, test_date_list)

    def reduce_sum(arr, axis=0, keep_axis=()):

        keep_axis = (keep_axis,) if isinstance(keep_axis, int) else keep_axis
        left_axis = tuple(sorted(list(set(range(arr.ndim)) - {axis} - set(keep_axis))))
        if left_axis:
            arr = arr.sum(axis=left_axis)
        axis = np.searchsorted(keep_axis, axis)
        arr1 = np.add.reduceat(arr, month_split, axis=axis)
        return arr1

    def roll_sum(arr, axis=0, keep_axis=()):

        arr1 = reduce_sum(arr, axis=axis, keep_axis=keep_axis)
        keep_axis = (keep_axis,) if isinstance(keep_axis, int) else keep_axis
        axis = np.searchsorted(keep_axis, axis)
        arr1 = bottleneck.move_sum(arr1, window=move_window, axis=axis)
        return arr1

    def reduce_mean(arr, axis=0, keep_axis=()):

        finite = np.isfinite(arr)
        arr[~ finite] = 0
        arr1 = reduce_sum(arr, axis=axis, keep_axis=keep_axis)
        finite1 = reduce_sum(finite, axis=axis, keep_axis=keep_axis)
        mean = arr1 / finite1
        mean[~ np.isfinite(arr1)] = np.nan
        return mean

    def roll_mean(arr, axis=0, keep_axis=()):

        finite = np.isfinite(arr)
        arr[~ finite] = 0
        arr1 = roll_sum(arr, axis=axis, keep_axis=keep_axis)
        finite1 = roll_sum(finite, axis=axis, keep_axis=keep_axis)
        mean = arr1 / finite1
        mean[~ np.isfinite(arr1)] = np.nan
        return mean

    factor_complete = roll_sum(factor_finite & future_finite) / roll_sum(future_finite)

    x = factor2
    y = future2
    n = future_finite
    x[~ n] = 0
    x2 = x ** 2
    y2 = y ** 2
    xy = x * y

    c2x = x.sum(axis=2)
    c2y = y.sum(axis=2)
    c2x2 = x2.sum(axis=2)
    c2y2 = y2.sum(axis=2)
    c2xy = xy.sum(axis=2)
    c2n = n.sum(axis=2)

    ic_c = roll_mean(calc_corr(c2x, c2y, c2x2, c2y2, c2xy, c2n))

    ic_dc = np.nanmean(calc_corr(roll_sum(c2x, keep_axis=1), roll_sum(c2y, keep_axis=1),
                                 roll_sum(c2x2, keep_axis=1), roll_sum(c2y2, keep_axis=1),
                                 roll_sum(c2xy, keep_axis=1), roll_sum(c2n, keep_axis=1)), axis=1)

    ic_d = np.nanmean(calc_corr(roll_sum(x, keep_axis=(1, 2)), roll_sum(y, keep_axis=(1, 2)),
                                roll_sum(x2, keep_axis=(1, 2)), roll_sum(y2, keep_axis=(1, 2)),
                                roll_sum(xy, keep_axis=(1, 2)), roll_sum(n, keep_axis=(1, 2))), axis=(1, 2))

    ic_direction = 2 * (ic_d > 0) - 1

    ic_dc *= ic_direction
    ic_d *= ic_direction
    ic_c *= ic_direction

    result_ic = dict(
        start_dates=start_dates[move_window - 1:],
        end_dates=end_dates[move_window - 1:],
        factor_complete=factor_complete[move_window - 1:],
        ic_direction=ic_direction[move_window - 1:],
        ic_dc=ic_dc[move_window - 1:],
        ic_d=ic_d[move_window - 1:],
        ic_c=ic_c[move_window - 1:],
    )
    return result_ic

def one_wave_evaluation(label_type, factor_type, base_path):
    factor_path = f'{base_path}{factor_type}/'
    label_path = f'{base_path}label/'

    eval_res_path = f'{base_path}eval_res/{factor_type}_{label_type}/'
    out_path = f'{base_path}eval_res_integration/{factor_type}_{label_type}/'
    if not os.path.exists(eval_res_path):
        os.makedirs(eval_res_path)
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    factor_list = list(map(lambda x : x.replace('.pkl',''),os.listdir(factor_path)))
    label = pd.read_pickle(f'{label_path}{label_type}.pkl')
    for factor_name in tqdm(factor_list):
        raw_factor = pd.read_pickle(f'{factor_path}{factor_name}.pkl')
        res = test_factor(raw_factor.values[:,None,:],label.values[:,None,:],raw_factor.index.tolist(),1)
        pd.to_pickle(res,f'{eval_res_path}{factor_name}.pkl')
        del raw_factor
        gc.collect()

    factor_list = os.listdir(eval_res_path)
    res = {}
    for factor_name in tqdm(factor_list):
        temp_res = pd.read_pickle(f'{eval_res_path}{factor_name}')
        temp_res = pd.DataFrame(temp_res).set_index('end_dates')
        temp_res.index = temp_res.index.map(lambda x : get_pre_trade_date(x,-3))
        res[factor_name] = temp_res.stack().swaplevel(0,1)

    res = pd.DataFrame(res)

    res = res.loc[[ 'ic_dc', 'ic_d','ic_c']]
    items = [  'ic_dc', 'ic_d','ic_c']
    for each in items:
        temp = res.loc[each]
        temp[temp>=1] = 0
        temp[temp<=-1] = 0
        pd.to_pickle(temp,f'{out_path}{each}.pkl')

if __name__ == '__main__':

    # l_type = 'lable_group_stk_future_rise_pct_1'

    b_path = '/data/group/800442/800319/HFfactor/DailySW2PreNormalized/'
    type_list = list(map(lambda x : x.replace('.pkl',''),os.listdir(f'{b_path}label/')))
    from xquant.compute.aimr import AIMR

    i = int(AIMR.getParam())
    f_type = 'mean'
    l_type = type_list[i]
    one_wave_evaluation(l_type, f_type, b_path)

    # for f_type in ['zscore','mean']:
    #     for l_type in ['lable_group_stk_future_rise_pct_1','lable_group_stk_future_avg_1']:
    #         one_wave_evaluation(l_type, f_type, b_path)

