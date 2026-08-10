from multifactor.IO import IO
import pandas as pd
import os
from pandas import Series
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import time

def layer_chopper(ps_raw, layers, rank=True):
    if isinstance(layers, int):
        _labels = range(layers)
    else:
        _labels = range(len(layers) - 1)
    if rank:
        return pd.cut(ps_raw.rank(), layers, retbins=False, labels=_labels)
    else:
        return pd.cut(ps_raw, layers, retbins=False, labels=_labels)

def spread_agg(pd_sorter, pd_data, layers):
    if type(pd_sorter) not in [pd.DataFrame, pd.Series]:
        raise AssertionError
    if type(pd_data) not in [pd.DataFrame, pd.Series]:
        raise AssertionError
    if isinstance(pd_sorter, pd.Series):
        pd_sorter = pd_sorter.unstack().dropna(how='all')
    else:
        pd_sorter = pd_sorter.dropna(how='all')
    pd_bins = pd_sorter.rank(axis=1).apply(layer_chopper, axis=1, layers=layers, rank=False)
    _sorter = pd_bins.stack()
    _sorter.name = 'bins'
    _data = pd_data.stack() if isinstance(pd_data, pd.DataFrame) else pd_data
    _data.name = 'data'
    _magic = pd.DataFrame(_sorter).merge(pd.DataFrame(_data), how='left', left_index=True, right_index=True).dropna()
    res = []
    for date, grouped in _magic.groupby(level=0):
        sliced_res = grouped.groupby('bins').mean()['data']
        sliced_res.name = date
        res.append(sliced_res)
    pd_res = pd.concat(res, axis=1).T
    pd_res.columns = ['Q'+str(int(col)) for col in pd_res.columns]
    return pd_res

def segment_test(start_date, end_date, factor_path, fig_save_path):
    print('read ' + factor_name + ' data')
    alp = IO.read_data([start_date,end_date],alt = factor_path)
    alp_ret = pd.concat([alp, vwap_ret_skip_overnight],axis=1)
    print('calculate Segment Return')
    Q = spread_agg(alp[alp.columns[0]].unstack(),vwap_ret_skip_overnight['vwap_ret_skip_overnight'].unstack(),layers=20)

    fig = plt.figure(figsize=[18, 5], dpi=200)
    # 图一：分组收益
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.bar(Q.mean().index.tolist(), Q.mean().tolist(), color='dodgerblue')
    plt.xlabel('Segment', fontsize='medium')
    plt.ylabel('Return', fontsize='medium')
    plt.title(factor_name + ' Segment Return', fontsize='large')
    # plt.xticks(ic_df.index[range(0,len(ic_df),6*holding_period)], rotation=45,fontsize='medium')
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图二：多空收益曲线
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot((Q['Q19'] - Q['Q0']).cumsum())
    ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.xticks(Q.index[range(0, len(Q), 20 * 8)], rotation=45, fontsize='medium')
    # plt.legend(group_nav.columns,ncol=2,fontsize='small')
    plt.title(factor_name + ' Long-Short Return', fontsize='large')
    plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Cumulative Return', fontsize='medium')
    plt.subplots_adjust(hspace=0.3)
    plt.savefig(os.path.join(fig_save_path, factor_name + '.png'))  # 存储图片
    plt.show()

    IC = alp_ret.corr().iloc[1, 0]
    seg_ret = Q.mean()

    seg_ret = seg_ret.append(Series({'IC': IC}))
    seg_ret = seg_ret.to_frame()
    seg_ret['alphaname'] = factor_name
    seg_ret = seg_ret.reset_index()
    seg_ret = seg_ret.rename(columns={'index': 'Segment', 0: 'return'})
    seg_ret = seg_ret.set_index(['alphaname', 'Segment'])

    return seg_ret

if __name__ == "__main__":
    start_date = 20140101
    end_date = 20170101

    data = IO.read_data([start_date, end_date],
                        alt=r'A:\zhangf\data\md\CHINA_STOCK\B8\WIND\MD_CHINA_STOCK_B8_filter.h5')
    data['vwap_adj'] = data['vwap'] * data['adjfactor']
    vwap_adj_df = data['vwap_adj'].unstack()
    vwap_ret_df = (vwap_adj_df.shift(-1) / vwap_adj_df - 1)
    idx = vwap_ret_df.index
    vwap_ret_skip_overnight_df = vwap_ret_df[~((idx.hour == 14) & (idx.minute == 30))]
    vwap_ret_skip_overnight = pd.DataFrame(vwap_ret_skip_overnight_df.shift(-1).stack(),
                                           columns=['vwap_ret_skip_overnight'])

    xwj_path = r'A:\xiangwj\h5_fac30'
    wyc_path = r'A:\weiyc\factor\factor101\new101'
    fig_save_path = r'A:\weiyc\factor\factor101_test_results'
    path_list = [xwj_path,wyc_path]

    total_seg_ret = pd.DataFrame()
    for path in path_list:
        factor_list = os.listdir(path)
        for factor in factor_list:
            factor_name = factor.split('_')[0] if 'fac' in factor else 'fac' + str(int(factor[-6:-3]))
            print(factor_name)
            start_time = time.time()
            seg_ret = segment_test(start_date, end_date, os.path.join(path, factor), fig_save_path)
            print(seg_ret)
            print(factor_name + ' time taken: ' ,time.time() - start_time)
            total_seg_ret = total_seg_ret.append(seg_ret)

    total_seg_ret.to_csv(os.path.join(fig_save_path,'IC_seg_ret.csv'))

