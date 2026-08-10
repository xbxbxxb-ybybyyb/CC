import numpy as np
import bottleneck as bk


def section_rank_np(data, pct=False):
    # 基于numpy的截面排序，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis=1)
    data_argsort[np.isnan(data)] = np.nan  # bottleneck rankdata会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort