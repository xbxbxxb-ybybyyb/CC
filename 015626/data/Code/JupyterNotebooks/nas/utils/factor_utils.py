import numpy as np
import pandas as pd

def link_collector(pair_lst):
    set_lst = []
    for pair in pair_lst:
        if len(set_lst) == 0:
            set_lst.append(set(pair))
        else:
            assigned = False
            for _set in set_lst:
                if np.any([i in _set for i in pair]):
                    _set.update(pair)
                    assigned = True
                    break
            if not assigned:
                set_lst.append(set(pair))
    return set_lst

# 用来筛选相关性低的因子，将相关性高的因子合并起来
def deep_link(score_mtx, threshold, score_vec=None, max_workers=None):
    # Given distance matrix, return list of sets of nearest neighbors
    # Elements are judged as neighbors with propagation: A~B, B~C -> A~C
    # Given score_vec, return discard list instead (keeping higher score)
    pair_lst = np.argwhere(score_mtx>=threshold)
    if max_workers is not None:
        max_workers = int(max_workers)
        _len = len(pair_lst)
        with Pool(processes=max_workers) as pool:
            res = pool.map(link_collector, chunks(pair_lst, int(_len/max_workers) + 1))
        set_lst = flatten_nested_lst(res)
    else:
        set_lst = link_collector(pair_lst)
    # Deep link
    merged_set_lst = []
    while len(set_lst) != 0:
        c_set = set_lst.pop()
        is_merged = False
        for _set in set_lst:
            if len(c_set.intersection(_set)) != 0:
                _set.update(c_set)
                is_merged = True
        if not is_merged:
            if len(merged_set_lst) == 0:
                merged_set_lst.append(c_set)
            else:
                for _set in merged_set_lst:
                    if len(c_set.intersection(_set)) != 0:
                        _set.update(c_set)
                        is_merged = True
                if not is_merged:
                    merged_set_lst.append(c_set)
    if score_vec is None:
        return merged_set_lst
    else:
        discard_set = set()
        _min = min(score_vec)
        assert len(score_vec) == score_mtx.shape[0]
        for _set in merged_set_lst:
            pos = None
            _max = _min
            for item in _set:
                if score_vec[item] >= _max:
                    pos = item
                    _max = score_vec[item]
            _set.remove(pos)
            discard_set.update(_set)
        return list(discard_set)

# fac_corr = df[faclist].corr().abs()
# x = deep_link(fac_corr.values, 0.7, score_vec=None, max_workers=None)

# clist = fac_corr.columns.tolist()

# factor_ic2 = factor_ic['corr5_abs']

# ylist = []
# for y in x:
#     klist = []
#     for k in y:
#         klist.append(clist[k])
#     if len(klist) == 1:
#         ylist.append(klist[0])
#     else:
#         ylist.append(abs(factor_ic2.loc[klist]).idxmax())



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

# 分层收益
def ts_segment_test(ps_raw, ps_return, layers,layer_lims=None, normalize=False, return_segment_time_series=False,
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