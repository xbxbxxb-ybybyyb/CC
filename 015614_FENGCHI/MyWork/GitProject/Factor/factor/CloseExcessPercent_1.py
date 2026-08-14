from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time
from copy import deepcopy
from collections import Counter


class CloseExcessPercent_1(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.citics_indcode1', 'FactorData.Basic_factor.close_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 2
    minute_lag=1
    # fix_times = ["1300"]
    # reform_window = 20

    
    def calc_single(self, database):

        citicsX_industry_code = database.depend_data['FactorData.Basic_factor.citics_indcode1']
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y%m%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        # print(date_list)
        # print(citicsX_industry_code.index)
        compute_date = date_list[-1]
        pre_date = date_list[-2]
        close = MinuteClose.loc[compute_date]

        # r = close.pct_change(1)
        r = close.diff()/close.shift()
        indus_unique = citicsX_industry_code.loc[pre_date].unique()
        r_excess = deepcopy(r)
        for indus in indus_unique:
            ind = np.where(citicsX_industry_code.loc[pre_date]==indus)[0]
            r_excess.iloc[:,ind] = r_excess.iloc[:,ind].sub(r.iloc[:,ind].mean(axis=1).values,axis=0)
        r_excess.iloc[0,:] = 0
        c_excess = pd.DataFrame(1+r_excess.values, index=r_excess.index, columns=r_excess.columns).cumprod(axis=0)*close
        close_arr = c_excess.values
        result = np.array([np.nan]*close.shape[1])
        for j in range(close.shape[1]):
            mylist = close_arr[:,j]
            if ~np.isnan(close_arr[-1,j]) and Counter(np.isnan(mylist))[0]>=close_arr.shape[0]*0.8:
                ind = np.where(~np.isnan(mylist))[0]
                sort = np.sort((mylist)[ind])
                if close_arr[-1,j]<sort[0]:
                    result[j] = (close_arr[-1,j]-sort[0])/abs(sort[0])
                elif close_arr[-1,j]>=sort[-1]:
                    result[j]=1+(close_arr[-1,j]-sort[-1])/abs(sort[-1])
                else:
                    bigger_this_data = np.where(sort>=close_arr[-1,j])[0]
                    result[j] = (bigger_this_data[0]+1)/(len(sort)+1)
        CloseExcessPercent = pd.Series(result,index=close.columns)
        return -CloseExcessPercent
