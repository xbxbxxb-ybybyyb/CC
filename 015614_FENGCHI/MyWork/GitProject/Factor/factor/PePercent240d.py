from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
from collections import Counter



class PePercent240d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.pe_ttm"]

    lag = 240

    def calc_single(self,database): 
        pe_ttm = database.depend_data['FactorData.Basic_factor.pe_ttm']
        PePercent240d = self.get_percentile(pe_ttm,self.lag,int(self.lag*0.8))

        return -PePercent240d.iloc[-1]



    # 一致预期估值分位点
    def get_percentile(self,df,window,min_periods):
        result = np.array([[np.nan]*df.shape[1]]*df.shape[0])
        df_arr = df.values
        for t in range(window,df.shape[0]):
            for j in range(df.shape[1]):
                mylist = df_arr[t-window:t,j]
                if ~np.isnan(df_arr[t,j]) and Counter(np.isnan(mylist))[0]>=min_periods:
                    ind = np.where(~np.isnan(mylist))[0]
                    sort = np.sort((mylist)[ind])
                    if df_arr[t,j]<sort[0]:
                        result[t,j] = (df_arr[t,j]-sort[0])/abs(sort[0])
                    elif df_arr[t,j]>=sort[-1]:
                        result[t,j]=1+(df_arr[t,j]-sort[-1])/abs(sort[-1])
                    else:
                        bigger_this_data = np.where(sort>=df_arr[t,j])[0]
                        result[t,j] = bigger_this_data[0]/(len(sort)+1)
                        
        return pd.DataFrame(result,index=df.index,columns=df.columns)