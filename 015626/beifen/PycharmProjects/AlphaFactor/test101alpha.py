from multifactor.IO import IO
import pandas as pd
from Alpha101 import Alphas

df = IO.read_data([20140101,20150101],columns = ['open','high','low','close','pct_chg','amt','volume'],
                       alt = 'A:/zhangf/data/md/CHINA_STOCK/B8/WIND/MD_CHINA_STOCK_B8_WIND.h5')

Alpha101 = Alphas(df)
df['Alpha001'] = Alpha101.alpha001()

print(df)