from overnight.factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf15_amtdiffstd(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        required_columns=['amount_500','BuyUniqueOrderNum_500','SellUniqueOrderNum_500']
        
        super(wyc_mf15_amtdiffstd, self).__init__(*args, required_columns=required_columns,
                                   ts_norm_bars=20, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        # 计算平均最后50分钟平均每笔成交额差分的标准差，来自于长江证券研报高频因子（九）
        amount_500 = df['amount_500']
        amount_500 = amount_500.loc[(amount_500.index.time <= datetime.time(14,49))]

        BuyUniqueOrderNum_500 = df['BuyUniqueOrderNum_500']
        BuyUniqueOrderNum_500 = BuyUniqueOrderNum_500.loc[(BuyUniqueOrderNum_500.index.time <= datetime.time(14,49))]

        SellUniqueOrderNum_500 = df['SellUniqueOrderNum_500']
        SellUniqueOrderNum_500 = SellUniqueOrderNum_500.loc[(SellUniqueOrderNum_500.index.time <= datetime.time(14,49))]

        allmoney = amount_500.sum(axis = 1)
        allordernum = BuyUniqueOrderNum_500.sum(axis = 1) + SellUniqueOrderNum_500.sum(axis = 1)

        mmean = allmoney / allordernum

        mmean = mmean - mmean.shift(1)

        factor =  mmean.groupby(mmean.index.date).std().to_frame() * -1
        # factor = ts_rank(factor, 20)
        
        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor