from IO import IO
import pandas as pd
import os


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

data = IO.read_data([start_date,end_date],alt = r'A:\zhangf\data\md\CHINA_STOCK\B8\WIND\MD_CHINA_STOCK_B8_filter.h5')
data['vwap_adj']=data['vwap']*data['adjfactor']
vwap_adj_df = data['vwap_adj'].unstack()
vwap_ret_df = (vwap_adj_df.shift(-1)/vwap_adj_df-1)
idx = vwap_ret_df.index
vwap_ret_skip_overnight_df=vwap_ret_df[~((idx.hour==14)&(idx.minute==30))]
vwap_ret_skip_overnight=pd.DataFrame(vwap_ret_skip_overnight_df.shift(-1).stack(),columns=['vwap_ret_skip_overnight'])

alp = IO.read_data(alt = ...)
alp_ret = pd.concat([alp, vwap_ret_skip_overnight],axis=1)
Q = spread_agg(alp[alp.columns[0]].unstack(),vwap_ret_skip_overnight['vwap_ret_skip_overnight'].unstack(),layers=20)

# 图
Q.mean().plot(kind='bar')
(Q[19]-Q[0]).cumsum().plot()

# data to excel
IC = alp_ret.corr().iloc[1,0]
seg_ret = Q.mean()