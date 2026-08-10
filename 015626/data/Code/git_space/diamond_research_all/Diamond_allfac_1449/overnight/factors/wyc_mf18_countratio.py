from overnight.factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import datetime
        
class wyc_mf18_countratio(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        required_columns=['volume_500','BuyUniqueOrderNum_500','SellUniqueOrderNum_500']
        
        super(wyc_mf18_countratio, self).__init__(*args, required_columns=required_columns,
                                   ts_norm_bars=5, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        # 尾盘50分钟每笔成交量 占全天每笔成交量的比值
        volume_500 = df['volume_500']
        volume_500_noon = volume_500.loc[(volume_500.index.time >= datetime.time(14,0))&(volume_500.index.time <= datetime.time(14,49))]
        volume_500 = volume_500.loc[volume_500.index.time <= datetime.time(14,49)]

        BuyUniqueOrderNum_500 = df['BuyUniqueOrderNum_500']
        BuyUniqueOrderNum_500_noon = BuyUniqueOrderNum_500.loc[(BuyUniqueOrderNum_500.index.time >= datetime.time(14,0))&(BuyUniqueOrderNum_500.index.time <= datetime.time(14,49))]
        BuyUniqueOrderNum_500 = BuyUniqueOrderNum_500.loc[BuyUniqueOrderNum_500.index.time <= datetime.time(14,49)]
        SellUniqueOrderNum_500 = df['SellUniqueOrderNum_500']
        SellUniqueOrderNum_500_noon = SellUniqueOrderNum_500.loc[(SellUniqueOrderNum_500.index.time >= datetime.time(14,0))&(SellUniqueOrderNum_500.index.time <= datetime.time(14,49))]
        SellUniqueOrderNum_500 = SellUniqueOrderNum_500.loc[SellUniqueOrderNum_500.index.time <= datetime.time(14,49)]

        ordernum = BuyUniqueOrderNum_500 + SellUniqueOrderNum_500

        pvol = volume_500 / ordernum
        pvol = pvol.replace([np.inf,-np.inf], np.nan)
        pvol = pvol.groupby(pvol.index.date).sum().sum(axis = 1)

        ordernum_noon = BuyUniqueOrderNum_500_noon + SellUniqueOrderNum_500_noon
        pvol_noon = volume_500_noon / ordernum_noon
        pvol_noon = pvol_noon.replace([np.inf,-np.inf], np.nan)
        pvol_noon = pvol_noon.groupby(pvol_noon.index.date).sum().sum(axis = 1)

        factor = pvol_noon / pvol
        factor = factor.replace([np.inf,-np.inf], np.nan)
        factor = ts_mean(factor, 3)
        # factor = ts_rank(factor, 5)
        
        factor.index.names = ['dt']
        factor.index = pd.to_datetime(factor.index)

        factor.columns = [columnname]
        return factor