from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform



class HF_OverBuySell_13h(BaseFactor):
    """
    *因子名 : HF_OverBuySell_13h
    *因子功能描述 : 收盘价超越2倍标准差的相对幅度
    *因子参数 : MinuteClose-分钟收盘价
    *作者 : hezq
    *因子创建日期 : 2019.6.21

    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 0
    

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]

        close = MinuteClose.loc[date_list].sort_index(ascending=True)
        mean_close = close.rolling(window=10,min_periods=1).mean()
        std_close = close.rolling(window=10,min_periods=1).std()
        boll_down = mean_close-std_close-std_close
        down_range = boll_down-close
        boll_up = mean_close+std_close+std_close
        up_range = close-boll_up
        arr = down_range.values>0
        arr_df = pd.DataFrame(arr,index=down_range.index,columns=down_range.columns)

        arr = up_range.values>0
        arr_up_df = pd.DataFrame(arr,index=up_range.index,columns=up_range.columns)

        downrange_pct = (down_range[arr_df]/boll_down)
        uprange_pct = (up_range[arr_up_df]/boll_up)      
        df = downrange_pct.sum(axis=0)+uprange_pct.sum(axis=0)        
        
        df[np.isinf(df)] = np.nan
        return -df

