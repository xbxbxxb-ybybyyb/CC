import pandas as pd
import numpy as np

df = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUND/DAILY/MD_CHINA_ETF_DAILY.h5')

# 制作收益
y = df['close'].unstack()
y = y.shift(-2) / y.shift(-1) - 1
y = y.stack().reindex(df.index).replace([np.inf, -np.inf], np.nan)

# 读取universe
univ = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUND/UNIVERSE/CHINA_FUND_UNIVERSE.h5')
univ = univ[univ['univ'] == True]

# 只测试universe中标的的收益
y = y.reindex(univ.index)

def layer_chopper(ps_raw, layers, rank=True):
    # return pd.Series with categorical tags representing bins to which raw data has been assigned
    # use rank to ensure that each bin contains equal numbers of samples at best situation
    if isinstance(layers, int):
        _labels = range(layers)
    else:
        _labels = range(len(layers) - 1)
    if rank:
        return pd.cut(ps_raw.rank(), layers, retbins=False, labels=_labels)
    else:
        return pd.cut(ps_raw, layers, retbins=False, labels=_labels)
        
def ts_segment_test( ps_raw, ps_return, layers, layer_lims=None, normalize=False,
                        return_segment_time_series=False,
                        **kwargs):
    assert isinstance(ps_raw, pd.Series)
    assert isinstance(ps_return, pd.Series)
    if layer_lims is not None:
        _up, _down = max(layer_lims), min(layer_lims)
        bins = [i for i in np.arange(_down, _up, (_up - _down) / layers)]
        bins[0] = -np.inf
        bins.append(np.inf)
        ps_bin = layer_chopper(ps_raw, layers=bins, rank=False)
    else:
        ps_bin = layer_chopper(ps_raw, layers=layers, rank=False)
    ps_bin.name = 'bins'
    ps_return.name = ps_return.name if ps_return.name is not None else 'return'
    _magic = pd.DataFrame(ps_bin).merge(pd.DataFrame(ps_return), how='left', left_index=True,
                                        right_index=True).dropna()
    if not return_segment_time_series:
        pd_res = _magic.groupby('bins').mean()
        pd_res.index = ['Q' + str(int(col)) for col in pd_res.index]
        return pd_res, _magic
    else:
        segment_dict = dict()
        for nbin, group in _magic.groupby('bins'):
            _ = group[ps_return.name]
            _.name = 'Q' + str(nbin)
            segment_dict[_.name] = _
        return segment_dict
    
def test_factor(factor, up_quantile = 0.05, down_quantile = 0.95):
    ref_score = factor
    ref_score.index.names = ['dt','Ticker']
    seg = ts_segment_test(ref_score, y, 5, [ref_score.quantile(up_quantile), ref_score.quantile(down_quantile)], return_segment_time_series=True)

    seg = pd.DataFrame(seg)

    %matplotlib inline
    _ = seg.groupby(pd.Grouper(level=0))
    _.mean().cumsum().plot(figsize=(20, 5))
    count_per_group = _.count().mean().to_frame()
    count_per_group.columns = ['num']
    print(count_per_group)


# 因子示例
close = df['close'].unstack()
volume = df['volume'].unstack()
ca_corr = close.rolling(60).corr(volume)
factor = ca_corr.stack().reindex(df.index)

# 因子测试
test_factor(factor, up_quantile = 0.05, down_quantile = 0.95)