# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class MinuteDownVolatilityRatio20d(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.is_valid_raw"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    reform_window = 20
    fix_times=["1500"]
 
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        is_valid_raw = database.depend_data['FactorData.Basic_factor.is_valid_raw']
        factor = self.minute_help(MinuteClose)
        factor[(is_valid_raw.iloc[-1,:] != 1)] = np.nan
        return factor
        
    def minute_help(self, MinuteClose):

        MinuteClose = MinuteClose.asfreq(freq='5min').dropna(how ='all')
        re = pd.DataFrame(MinuteClose.values/MinuteClose.shift(1).values-1,index=MinuteClose.index,columns=MinuteClose.columns)
        re_neg = re.copy()
        re_neg = pd.DataFrame(np.where(re.values>0,np.nan,re_neg.values),index=re_neg.index,columns=re_neg.columns)        
        factor_today = re_neg.std()/re.std()
            # result_df.loc[date] = factor_today

        return factor_today
    def reform(self,temp_result):
        factor = temp_result
        res =factor.rolling(20,1).mean()
        return res