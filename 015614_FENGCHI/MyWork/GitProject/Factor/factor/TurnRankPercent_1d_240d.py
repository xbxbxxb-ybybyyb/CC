from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
from collections import Counter



class TurnRankPercent_1d_240d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.turn"]

    lag = 240


    def calc_single(self,database):
        turn = database.depend_data['FactorData.Basic_factor.turn']
        turn_rank =  turn.rank(axis=1)
        TurnRankPercent = self.get_percentile(turn_rank,1,self.lag,int(self.lag*0.8))
        return -TurnRankPercent.iloc[-1]
        

    def get_percentile(self,df,n,window,min_periods):

        result = np.array([[np.nan]*df.shape[1]]*df.shape[0])
        df_arr = df.values
        if n>1:
            df_mean_arr = df.rolling(window=n,min_periods=int(0.8*n)).mean().values
        else:
            df_mean_arr = df_arr
        for t in range(window,df.shape[0]):
            for j in range(df.shape[1]):
                mylist = df_arr[t-window:t-n,j]
                if ~np.isnan(df_mean_arr[t,j]) and Counter(np.isnan(mylist))[0]>=min_periods:
                    ind = np.where(~np.isnan(mylist))[0]
                    sort = np.sort((mylist)[ind])
                    if df_mean_arr[t,j]<sort[0]:
                        result[t,j] = (df_mean_arr[t,j]-sort[0])/abs(sort[0])
                    elif df_mean_arr[t,j]>=sort[-1]:
                        result[t,j]=1+(df_mean_arr[t,j]-sort[-1])/abs(sort[-1])
                    else:
                        bigger_this_data = np.where(sort>=df_mean_arr[t,j])[0]
                        result[t,j] = bigger_this_data[0]/(len(sort)+1)
                        
        return pd.DataFrame(result,index=df.index,columns=df.columns)