from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class Min_UpRange(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # fix_times = ["1500"]
    # reform_window = 5
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series


    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']


        # for date in date_list:
        #     dt = pd.Timestamp(date)
        #     Volume = MinuteVolume.loc[date]
        #     Turnover = MinuteTurover.loc[date]
        #     vwap = Turnover/Volume
        #     mean_vwap = vwap.rolling(window=10,min_periods=1).mean()
        #     std_vwap = vwap.rolling(window=10,min_periods=1).std()
        #     boll_up = mean_vwap+2*std_vwap
        #     up_range = vwap-boll_up
        #     uprange_pct = (up_range[up_range>0]/boll_up)
        #     res[dt] = uprange_pct.sum(axis=0)[uprange_pct.mean(axis=0).notnull()]
        # res = pd.DataFrame(res).T
        # res[np.isinf(res)]= np.nan

        vwap = amt / volume
        mean_vwap = vwap.rolling(window=10,min_periods=1).mean()
        std_vwap = vwap.rolling(window=10,min_periods=1).std()
        # boll_up = mean_vwap+2*std_vwap
        boll_up = pd.DataFrame(mean_vwap.values+2*std_vwap.values, index=amt.index,columns=amt.columns)

        up_range = vwap-boll_up
        # t1=time.time()
        # uprange_pct = (up_range[up_range>0]/boll_up)
        u = up_range.values
        b = boll_up.values
        uprange_pct = pd.DataFrame(u*(u>0)/b, index=amt.index,columns=amt.columns)
        # print('cost:',time.time()-t1)
        res = uprange_pct.sum(axis=0)[uprange_pct.mean(axis=0).notnull()]
        res[np.isinf(res.values)]= np.nan
        
        return -res