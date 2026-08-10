import sys
sys.path.insert(4,'/data/user/015626/JupyterNotebooks/utils/')
import json,datetime,os,glob
from multiprocessing.pool import Pool
import pandas as pd
from multifactor.IO import IO
import numpy as np
pd.set_option('max_columns', 200)
%matplotlib inline

def test_cb_factor(factor, y_ret = None, factor_name = 'test', savepath = None):

    if y_ret is None:
        origin_data = IO.read_data(columns = ['close'], alt = '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/CHINA_CONVERTIBLE_BOND_MINUTE.h5')
        origin_data = origin_data.unstack()['close']
        origin_data = origin_data.replace(0, np.nan)
        y_ret = origin_data.shift(-11) / origin_data.shift(-1) - 1
        y_ret = y_ret.between_time(datetime.time(9,35), datetime.time(14,49))
    
    columnslist = list(set(factor.columns) & set(y_ret.columns))
    columnslist.sort()

    tempy = y_ret.loc[factor.index[0]:factor.index[-1]]
    _factor = factor[columnslist].reindex(tempy.index)
    _y = tempy[columnslist]

    r = _factor.rolling(20*225, min_periods = 10*225).corr(_y)

    r[r>1] = np.nan
    r[r<-1] = np.nan

    corr_mean = r.mean(axis = 1)
    corr_25 = r.quantile(0.25, axis = 1)
    corr_75 = r.quantile(0.75, axis = 1)

    result = pd.concat([corr_mean, corr_25, corr_75], axis = 1)
    result.columns = ['corr_mean','corr_25','corr_75']
    
    resultdf = result.mean().to_frame().T
    resultdf.index = [factor_name]

    ax = result.plot(figsize = (20, 10), title = factor_name, fontsize=12)
    ax.axes.title.set_size(25)
    fig = ax.get_figure()
    
    if savepath is not None:
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        fig.savefig(os.path.join(savepath, factor_name + '.png'))
    
    # result为3条IC序列，resultdf为result每列均值
    return resultdf, result

fac = pd.read_pickle('/data/user/016700/Data/Factors/CB/VALUES/CDO_CC.pkl')
test_cb_factor(fac)