# @Time : 2021/12/3 9:45
# @Author : Zhichen Lu
# @File : SignalDistrAnalysis.py
import pandas as pd
import numpy as np
from StrongStockModel.conf.path_config import root_path
import bottleneck


def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)

def calc_recent_ratio(signal,window):
    signal_arr = signal.values.reshape(signal.shape[0], 7, signal.shape[-1])
    idx_arr = np.empty(signal_arr.shape)
    for idx in range(7):
        idx_arr[:, idx, :] = np.ones((idx_arr.shape[0], idx_arr.shape[-1])) * idx + 1
    idx_arr[~signal_arr] = np.nan
    first_signal = np.nanmin(idx_arr, axis=1)[:, None, :]
    is_triggered_first = np.isclose(first_signal, idx_arr)
    recent_20d_s_count = bottleneck.move_sum(np.where(is_triggered_first,1,0),axis=0,window=window)
    recent_20d_s_count = delay(recent_20d_s_count,2)
    recent_20d_s_count = pd.DataFrame(recent_20d_s_count.reshape(signal.shape),index=signal.index,columns=signal.columns)
    barly_recent_20d_s_count = recent_20d_s_count.sum(axis=1).unstack()
    barly_recent_20d_ratio = (barly_recent_20d_s_count.T/barly_recent_20d_s_count.sum(axis=1)).T
    return barly_recent_20d_ratio


def count_freq(signal_array,pool_array,index):
    daily_barly_count = np.nansum(signal_array&pool_array, axis=2)
    daily_pool_count = np.nansum(pool_array, axis=2)
    bar_ratio = daily_barly_count/daily_pool_count
    bar_ratio_df = pd.DataFrame({'ratio':bar_ratio.reshape(bar_ratio.shape[0]*7).tolist(),'year':index.map(lambda x:x[0]//10000)},index=index)
    bar_yearly_ratio = bar_ratio_df.reset_index().groupby(['year','time']).mean()['ratio']
    all_ratio = bar_ratio_df['ratio'].groupby(level=1).mean()
    all_ratio.index = pd.MultiIndex.from_tuples([('全时段',x) for x in all_ratio.index])
    bar_yearly_ratio = bar_yearly_ratio.append(all_ratio)
    return bar_yearly_ratio

def main():
    signal, pred_ret = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGBMonthlyV4_Cat_LightWithoutMax5_0.05.pkl')
    stock_pool = pd.read_pickle(root_path + 'stock_pool_without_limit_up_down.pkl').shift(1)
    signal = signal.reindex(stock_pool.columns, axis=1).fillna(False)
    stock_pool = stock_pool.loc[signal.index.levels[0]].fillna(False)

    pool_arr = stock_pool.values[:, None, :]
    signal_arr = signal.values.reshape(pool_arr.shape[0], 7, pool_arr.shape[-1])
    idx_arr = np.empty(signal_arr.shape)
    for idx in range(7):
        idx_arr[:, idx, :] = np.ones((idx_arr.shape[0], idx_arr.shape[-1])) * idx + 1
    idx_arr[~signal_arr] = np.nan
    first_signal = np.nanmin(idx_arr, axis=1)[:, None, :]
    is_triggered_first = np.isclose(first_signal, idx_arr)
    # signal_first_only = pd.DataFrame(is_triggered_first.reshape(signal.shape), index=signal.index, columns=signal.columns)

    pool_first_signal_arr = is_triggered_first & pool_arr
    index = signal.index

    bar_yearly_ratio_pool = count_freq(pool_first_signal_arr,pool_arr,signal.index)
    bar_yearly_ratio_first_all_mkt = count_freq(is_triggered_first,pool_arr,signal.index)
    out_file = './各个时点信号量占全市场股票数量比例统计_首次触发.xlsx'
    first_ratio_stack_all_mkt = bar_yearly_ratio_first_all_mkt.unstack()
    first_ratio_stack_pool = bar_yearly_ratio_pool.unstack()
    with pd.ExcelWriter(out_file) as writer:
        (first_ratio_stack_all_mkt.T/first_ratio_stack_all_mkt.sum(axis=1)).T.to_excel(writer,sheet_name='全市场首次触发数量占全天首次触发数量比')
        first_ratio_stack_all_mkt.to_excel(writer,sheet_name='首次触发数量占全市场股票数量')

        (first_ratio_stack_pool.T / first_ratio_stack_pool.sum(axis=1)).T.to_excel(writer, sheet_name='股票池首次触发数量占全天首次触发数量比')
        first_ratio_stack_pool.to_excel(writer,sheet_name='股票池首次触发数量占股票池股数量')
    from dataApi.sendInfo import send_file

    send_file(['015664'],out_file)






main()


# signal['year'] = signal.index.map(lambda x : x[0]//10000)
# signal = signal.reset_index().set_index(['year','date','time'])
# stat = signal.stack().groupby
# signal =
