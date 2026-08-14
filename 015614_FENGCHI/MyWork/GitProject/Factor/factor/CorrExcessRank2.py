from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class CorrExcessRank2(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.open_minute', 'FactorData.Basic_factor.close_minute',
                    'FactorData.Basic_factor.citics_indcode1']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 1
    minute_lag=1
    # fix_times = ["1300"]
    # reform_window = 5

    
    def calc_single(self, database):

        citicsX_industry_code = database.depend_data['FactorData.Basic_factor.citics_indcode1']
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y%m%d'
        datelist = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = datelist[-1]
        pre_date = datelist[-2]
        c = MinuteClose.loc[compute_date]
        o = MinuteOpen.loc[compute_date]
        r = (c-o)/o
        # re = c.pct_change(1)
        re = c.diff()/c.shift()
        indus_unique = citicsX_industry_code.loc[pre_date].unique()
        for indus in indus_unique:
            ind = np.where(citicsX_industry_code.loc[pre_date]==indus)[0]
            re.iloc[:,ind] = re.iloc[:,ind].sub(re.iloc[:,ind].mean(axis=1).values,axis=0)
            r.iloc[:,ind] = r.iloc[:,ind].sub(r.iloc[:,ind].mean(axis=1).values,axis=0)
        re.iloc[0] = 0
        re = pd.DataFrame(1+re.values, index=re.index, columns=re.columns)
        c_excess = re.cumprod(axis=0)
        c_excess = c_excess* self.S2D(c.iloc[0], c)
        CorrExcess = Util.array_coef(r.abs().rank(axis=0), c_excess.rank(axis=0))
        return -CorrExcess

    def S2D(self, S, D):
        return pd.DataFrame(np.tile(S.values,(D.shape[0],1)),index=D.index,columns=D.columns)