# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
    

class HF_UpReaturnRealStdZScore(BaseFactor):
    """
    *因子名 : HF_UpReaturnRealStdZScore_13h
    *因子功能描述 : high相对close收益率的波动率，并取其zscore；值越大，表示超买，收益越低
    *因子参数 :  MinuteHigh--分钟最高价,MinuteClose-分钟收盘价
    *作者 : hezq
    *因子创建日期 : 2019.7.2

    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.high_minute","FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 20

    # def definition(self,MinuteHigh,MinuteClose):
    #     rd = 20
    #     df = self.minute_help(self.minute, 'HF_UpReaturnRealStdZScore_13hHelp',MinuteHigh,MinuteClose)
    #     df = (df-df.rolling(window=rd,min_periods=1).mean())/df.rolling(window=rd,min_periods=1).std()
    #     df[np.isinf(df)] = np.nan
    #     return -df
    # def minute(self,MinuteHigh,MinuteClose): 
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
    #     # print(date_list)
    #     close = MinuteClose.sort_index(ascending=True)
    #     high = MinuteHigh.sort_index(ascending=True)
    #     re = ((high/close-1)*100)
    #     res = np.sqrt(np.power(re[re>=0],2).mean(axis=0))
    #     return res

    def calc_single(self, database):
        MinuteHigh = database.depend_data["FactorData.Basic_factor.high_minute"]
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        # print(date_list)
        close = MinuteClose.sort_index(ascending=True)
        high = MinuteHigh.sort_index(ascending=True)
        re = pd.DataFrame(((high/close).values-1)*100, index=close.index,columns=close.columns)
        res = np.sqrt(np.power(re[pd.DataFrame(re.values>=0,index=re.index,columns=re.columns)],2).mean(axis=0))
        return res

    def reform(self, df):
        rd = 20
        df = (df-df.rolling(window=rd,min_periods=1).mean())/df.rolling(window=rd,min_periods=1).std()
        df[np.isinf(df)] = np.nan
        return -df