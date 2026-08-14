from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class MinuteGroupReBias5d(BaseFactor):  # 派生一个因子类
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.close_badj']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 1
    minute_lag=0
    # fix_times = ["1500"]
    reform_window = 5
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series

    def calc_single(self, database):


    # def definition(self, Minute_Status, MinuteClose, close_adj, is_valid_raw ):
        
        # re = close_adj/close_adj.shift(1) -1
        # status = (is_valid_raw == 0)|(Minute_Status == 1)|(Minute_Status == 2)|(Minute_Status == 3)|(Minute_Status == 5)
        # factor = self.minute_help(self.minute, 'MinuteGroupReBias5dHelp', MinuteClose, re, status)
        
        # factor[(is_valid_raw == 0)|(Minute_Status == 1)|(Minute_Status == 2)|(Minute_Status == 3)| (Minute_Status == 5)] = np.nan
        # factor = -factor.abs().rolling(5,1).mean()
        # return factor
    
    # def minute(self, MinuteClose, re, status):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']

        GroupReBias5d  = []
        # invalid_stock = status.columns[status.loc[pd.to_datetime(date_list)].sum()> 0]      

        re_today = ((close_adj-close_adj.shift(1)) / close_adj.shift(1)).iloc[-1,:]
        
        # t1=time.time()
        # re_cur_valid = MinuteClose.pct_change(1)

        re_cur_valid = (MinuteClose-MinuteClose.shift(1)) / MinuteClose.shift(1)
        # print('cost',time.time()-t1) 
        # re_cur_valid[invalid_stock] = np.nan
        # print(np.cov(re_cur_valid.values.T))
        # X = pd.DataFrame(np.corrcoef(re_cur_valid.values.T), index=re_cur_valid.columns, columns=re_cur_valid.columns)
        x1 = re_cur_valid.fillna(re_cur_valid.mean())
        X = pd.DataFrame(np.corrcoef(x1.values.T), index=re_cur_valid.columns, columns=re_cur_valid.columns)
        # print(X)
        # print('cost1',time.time()-t1)

        X = X.rank(axis =1,pct=True)
        # print('cost2',time.time()-t1)
        # print(X)
        # group = (X!=1)&(X>=0.95)
        group = pd.DataFrame((X.values!=1)*(X.values>=0.95), index=X.index, columns=X.columns)
        # print('cost3',time.time()-t1)
        # print(group.shape)
        # print(close_adj.shape)
        # print(group.sum())
        
        Y = group.apply(lambda x : (re_today.loc[group.columns[x]]).mean(), axis = 1)
        # print('cost4',time.time()-t1)
        # print(Y.notnull().sum())
        # print(Y.sum())
        f = re_today - Y
        # print(f.size)
        # f.name = date
        # f[invalid_stock] = np.nan
        # GroupReBias5d.append(f)

        # MinuteGroupReBias5d = pd.DataFrame(GroupReBias5d)
        # MinuteGroupReBias5d.index = pd.to_datetime(MinuteGroupReBias5d.index)
        # print(MinuteGroupReBias5d)
        
        return f


    def  reform(self, temp_result):
        A = temp_result.abs().rolling(5,1).mean()
        # A = pd.DataFrame(-1.*A.values, index=A.index, columns=A.columns,)
        return -A