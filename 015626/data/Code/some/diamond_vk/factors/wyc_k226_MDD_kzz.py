from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

def get_mdd(sharpedailyreturn):
    sharpedailyreturn = pd.DataFrame(sharpedailyreturn)
    sharpedailyreturn.columns = ['equity_curve']
    sharpedailyreturn['max2here'] = sharpedailyreturn['equity_curve'].expanding().max()
    # 计算到历史最高值到当日的跌幅，drowdwon
    sharpedailyreturn['dd2here'] = sharpedailyreturn['equity_curve'] - sharpedailyreturn['max2here']
    # 计算最大回撤
    max_draw_down = sharpedailyreturn['dd2here'].min()
    return max_draw_down

class wyc_k226_MDD_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_daily']
        super(wyc_k226_MDD_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        temp = df['close_daily']

        ret = temp.pct_change().cumsum() + 1
        mdd = ret.rolling(30).apply(lambda x:get_mdd(x))
        factor = mdd.copy() * -1
        factor = factor.replace([np.inf,-np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor