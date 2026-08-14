# -*- coding: utf-8 -*-

"""

*因子名 : MinuteAmtRetCor5d
*因子功能描述 : 5分钟级成交额与收益率的相关性, 5日均值

*因子参数 : Minute_Status,MinuteClose, MinuteTurnover, is_valid_raw 
*作者 : 刘正
*因子创建日期 : 2018.01.02
*函数修改日期 : 尚未修改
*修改人 ：尚未修改
*修改原因 :  尚未修改


"""
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinuteAmtRetCor5d(BaseFactor):
    
    factor_type = "DAY"
    s_close_min = 'FactorData.Basic_factor.close_minute'
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    depend_data = [s_close_min, s_amt_min]
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        close_min = database.depend_data[self.s_close_min]
        amt_min = database.depend_data[self.s_amt_min]
        factor = self.minute(amt_min, close_min)
        return factor
    
    def reform(self, temp_result):
        return -temp_result.rolling(self.reform_window, 1).mean()

    # def definition(self, Minute_Status,MinuteClose, MinuteTurnover, is_valid_raw ):
        
    #     factor = self.minute_help(self.minute, 'MinuteAmtRetCor5dHelp', MinuteTurnover, MinuteClose)
    #     factor[(is_valid_raw == 0)|(Minute_Status == 1)|(Minute_Status == 2)|(Minute_Status == 5)] = np.nan
    #     factor = -factor.rolling(5,1).mean()
    #     return factor
    
    def minute(self, MinuteTurnover, MinuteClose):
        # date_list = np.unique(MinuteTurnover.index.strftime('%Y%m%d'))
        timestamp = MinuteTurnover.index[-1]
        MinuteTurnover =MinuteTurnover.groupby(pd.Grouper(freq='5min')).sum().dropna(how='all')
        MinuteClose =MinuteClose.asfreq(freq ='5min').dropna(how='all')

        MinuteTurnoverDay = MinuteTurnover
        MinuteCloseDay = MinuteClose
        MinuteCloseDayGrowth = MinuteCloseDay.pct_change(1)
        MinuteTurnoverDayGrowth = MinuteTurnoverDay.pct_change(1)
        df_corr = pd.concat((MinuteCloseDayGrowth, MinuteTurnoverDayGrowth), axis = 1)

        f = Util.array_coef(df_corr.iloc[:, :len(MinuteCloseDayGrowth.columns)], df_corr.iloc[:, -len(MinuteTurnoverDayGrowth.columns):])
        # f = MinuteCloseDayGrowth.corrwith(MinuteTurnoverDayGrowth)
        f.name = timestamp
        # AmtRetCor.append(f)
            
        # MinuteAmtRetCor = pd.DataFrame(AmtRetCor)
        # MinuteAmtRetCor.index = pd.to_datetime(MinuteAmtRetCor.index)
        return f
    

    