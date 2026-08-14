import numpy as np
import bottleneck


def rmse(_y, y):

    return np.nanmean((_y - y) ** 2) ** 0.5

def top_ret(_y, y):

    if len(np.unique(_y)) / np.isfinite(y).sum() < 0.75:
        ret = 1.
    else:
        ret = - np.nanmean((y - np.nanmean(y))[bottleneck.nanrankdata(_y) / np.isfinite(_y).sum() > 0.9])
    return ret