from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np
# up volatility/ down volatility ratio
class  UpDownVolatility(BaseFactor):

    factor_type = "DAY"

    s_pct_chg = 'FactorData.Basic_factor.pct_chg'
    depend_data = [s_pct_chg]
    
    n = 20
    lag = n - 1
    def calc_single(self, database):
        re = database.depend_data[self.s_pct_chg] 
        re_u = re[pd.DataFrame(re.values > 0, columns = re.columns, index = re.index)]
        re_d = re[pd.DataFrame(re.values <= 0, columns = re.columns, index = re.index)]
        uper = re_u.std() * re_u.count()
        downer = re_d.std() * re_d.count()
        return uper / downer

    def reform(self, temp_result):
        return -temp_result #反转因子符号

    # def definition(self, close_adj):
        
    #     re = close_adj/close_adj.shift(1)-1
    #     n = 20
    #     re_u = re[re>0]
    #     re_d = re[re<=0]
    #     uper =  re_u.rolling(window = n, min_periods=5).std()*re_u.rolling(n).count()
    #     downer =  re_d.rolling(window = n, min_periods=5).std()*re_d.rolling(n).count()
    #     result = uper/downer
    #     return result