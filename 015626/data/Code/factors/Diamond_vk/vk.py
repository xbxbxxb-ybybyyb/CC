from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k1_cvcorr_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','volume']
        super(wyc_k1_cvcorr_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]
        close = df['close'].loc[tday:]
        volume = df['volume'].loc[tday:]

        factor = close.corrwith(volume).to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB2_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume', 'volume_stk']
        super(CB2_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        f1 = df['volume_stk'].between_time(data_morning_begin, trade_stop_time)[-215:]
        f2 = df['volume'].between_time(data_morning_begin, trade_stop_time)[-215:]

        f = f1.rolling(210, min_periods = 30).corr(f2)
        factor = f[-5:].mean().to_frame()

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB1_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['amount']
        super(CB1_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = df['amount'][-250:].between_time(data_morning_begin, trade_stop_time)
        factor = factor.groupby(factor.index.date).skew() * -1

        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB29_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(CB29_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'][-242*6:].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        factor = abs(close.pct_change(5)*ts_std(close.pct_change(),5))

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k26_ast_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['amount']
        super(wyc_k26_ast_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        a = df['amount'].between_time(data_morning_begin, trade_stop_time)
        factor = a.groupby(a.index.date).std()
        factor.index = pd.to_datetime(factor.index)
   
        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB5_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','high']
        super(CB5_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        f1 = df['close'][-5:]
        f2 = df['high'][-5:]

        f = f1/f2
        factor = f.mean().to_frame() * -1
        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k10_onret_y(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['kzz_onret']
        super(wyc_k10_onret_y, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        
        factor = ts_sum(df['kzz_onret'], 10)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB32_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(CB32_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):

        hclose1 = df['close'].between_time(data_morning_begin, data_afternoon_end)
        hclose2 = df['close'].between_time(data_morning_begin, trade_stop_time)

        f1 = (hclose1.groupby(hclose1.index.date).last()/hclose1.groupby(hclose1.index.date).first()-1).shift(1)
        f1 = ts_sum(f1, 10)

        f2 = (hclose2.groupby(hclose2.index.date).last()/hclose2.groupby(hclose2.index.date).first()-1)
        factor = abs(f1+f2)

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB33_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(CB33_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        # hclose = df['close'].pct_change(30).between_time(datetime.time(10,0), trade_stop_time)

        # temp = hclose.groupby(hclose.index.date).std()

        # f = ts_mean(temp, 10).rank(axis = 1, pct = True)*2-1

        hclose = df['close'].pct_change(30).between_time('1000', '1449')

        temp = hclose.groupby(hclose.index.date).std()

        f = temp.rolling(10, min_periods = 2).mean().rank(axis = 1, pct = True)*2-1
        factor = abs(f)

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB13_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','open','close_stk','open_stk']
        super(CB13_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):        
        high = df['close'][-500:] / df['open'][-500:]
        close = df['close_stk'][-500:] / df['open_stk'][-500:]
        s = ts_std(high, 120)
        f = ts_std(close, 120)
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(120, min_periods=30).cov(close) / (s * f)

        factor = t_pcor2.between_time(datetime.time(13, 0), trade_stop_time)
        factor = factor.groupby(factor.index.date).mean()
        factor = factor.replace([-np.inf, np.inf], np.nan)
        factor.index = pd.to_datetime(factor.index)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k15_yue_kzzrdf(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','B_INFO_OUTSTANDINGBALANCE']
        super(wyc_k15_yue_kzzrdf, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tickerlist = df['close'].columns.tolist()
        cbondamount = df['B_INFO_OUTSTANDINGBALANCE']
        cbondamount = cbondamount[list(set(cbondamount.columns.tolist()) & set(tickerlist))]
        factor = -1 * cbondamount
        factor = factor.replace([np.inf, -np.inf, 0], np.nan)
        factor.index = pd.to_datetime(factor.index)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB15_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume']
        super(CB15_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['volume'].index.date[-1]
        f1 = df['volume'].loc[tday:].between_time(datetime.time(14,0), trade_stop_time)
        factor = f1.skew().to_frame() * -1

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB23_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','open']
        super(CB23_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)
        opendf = df['open'].between_time(data_morning_begin, trade_stop_time)
        opendf = opendf.groupby(opendf.index.date).first()
        opendf.index = pd.to_datetime(opendf.index)

        factor = abs(ts_mean(close/opendf - 1, 8))

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB24_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['amount']
        super(CB24_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        f1 = rolling_norm(df['amount'], 1200).between_time(data_morning_begin, trade_stop_time)
        f = f1.groupby(f1.index.date).sum()

        factor = abs(ts_reg_beta(f, 30))

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k154_TYP_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','high','low','volume']
        super(wyc_k154_TYP_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):

        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)
        high = df['high'].between_time(data_morning_begin, trade_stop_time)
        high = high.groupby(high.index.date).max()
        high.index = pd.to_datetime(high.index)
        low = df['low'].between_time(data_morning_begin, trade_stop_time)
        low = low.groupby(low.index.date).min()
        low.index = pd.to_datetime(low.index)
        volume = df['volume'].between_time(data_morning_begin, trade_stop_time)
        volume = volume.groupby(volume.index.date).sum()
        volume.index = pd.to_datetime(volume.index)

        N = 20
        TYP = (high + low + close) / 3
        a = pd.DataFrame(columns = close.columns, index = close.index)
        a[TYP > ts_delay(TYP, 1)] = TYP * volume
        a[TYP <= ts_delay(TYP, 1)] = 0
        b = pd.DataFrame(columns = close.columns, index = close.index)
        b[TYP < ts_delay(TYP, 1)] = TYP * volume
        b[TYP >= ts_delay(TYP, 1)] = 0
        V1 = ts_sum(a, N) / ts_sum(b, N)
        factor = 100 - (100 / (1 + V1))
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class kzz_crssuper(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(kzz_crssuper, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        c = df['close'][-3000:].pct_change(5)
        c = ts_std(c, 2400)
        f = c.between_time(data_morning_begin, trade_stop_time)
        tday = df['close'].index.date[-1]
        factor = f.loc[tday:].mean().to_frame()

        factor = factor.replace([np.inf, -np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB28_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','high']
        super(CB28_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'][-240:].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)
        high = df['high'][-240:].between_time(data_morning_begin, trade_stop_time)
        high = high.groupby(high.index.date).max()
        high.index = pd.to_datetime(high.index)

        factor = high/close

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k43_DC_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','high','low']
        super(wyc_k43_DC_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):

        h = df['high'][-200:].between_time(data_afternoon_begin, trade_stop_time)
        lo = df['low'][-200:].between_time(data_afternoon_begin, trade_stop_time)
        h = h.groupby(h.index.date).max()
        lo = lo.groupby(lo.index.date).min()
        h.index = pd.to_datetime(h.index)
        lo.index = pd.to_datetime(lo.index)

        close = df['close'][-200:].between_time(data_afternoon_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        UPPER = h
        LOWER = lo
        MIDDLE = (UPPER+LOWER)/2
        factor = (close - MIDDLE) / MIDDLE * -1

        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k16_vturnoverrate_kzzrdf(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume','B_INFO_OUTSTANDINGBALANCE']
        super(wyc_k16_vturnoverrate_kzzrdf, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        
        volume = df['volume'].between_time(data_morning_begin, trade_stop_time)
        volume = volume.groupby(volume.index.date).sum()
        volume.index = pd.to_datetime(volume.index)
        cbondamount = df['B_INFO_OUTSTANDINGBALANCE']
        tickerlist = list(set(cbondamount.columns.tolist()) & set(volume.columns.tolist()))
        cbondamount = cbondamount[tickerlist]
        volume = volume[tickerlist]

        factor = volume / (cbondamount / 100)
        factor = factor.replace([np.inf, -np.inf, 0], np.nan)
        factor = factor.rank(axis = 1, pct = True)
        factor.index = pd.to_datetime(factor.index)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k161_obv_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','volume']
        super(wyc_k161_obv_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)
        volume = df['volume'].between_time(data_morning_begin, trade_stop_time)
        volume = volume.groupby(volume.index.date).sum()
        volume.index = pd.to_datetime(volume.index)

        con1 = close > ts_delay(close, 1)
        OBV = pd.DataFrame(columns=close.columns, index = close.index)
        OBV[con1] = volume
        con2 = close < ts_delay(close, 1)
        OBV[~con1 & con2] = -1 * volume
        OBV[~con1 & ~con2] = 0
        factor = ts_sum(OBV, 20)

        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB12_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(CB12_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        ret = df['close'].pct_change()
        temp_rsi = (ret>=0)
        temp_rsi2 = (ret<=0)

        upvol = ts_std(temp_rsi*ret, 220)
        downvol = ts_std(temp_rsi2*ret, 220) * -1
        realvol = ts_std(ret, 220)
        vwtc_r = (upvol-downvol)/realvol

        factor = vwtc_r[-10:].mean().to_frame() * -1

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k4_maxpct_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(wyc_k4_maxpct_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        data = df['close'][-242:].between_time(data_morning_begin,trade_stop_time)
        p = data.groupby(data.index.date)
        factor = p.last() / p.min() - 1
        factor.index = pd.to_datetime(factor.index)

        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k192_stdv_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume']
        super(wyc_k192_stdv_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        # （成交价上涨部分对应的成交额-下跌部分对应的成交额）/总成交额
        volume = df['volume'].between_time(data_morning_begin, trade_stop_time)
        volume = volume.groupby(volume.index.date).sum()
        volume.index = pd.to_datetime(volume.index)

        factor = ts_std(volume, 10)
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB10_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume', 'close']
        super(CB10_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        temp1 = df['close'][-50:].pct_change()
        temp2 = np.abs(df['volume'][-50:] * temp1)
        hdl_ind_r = ts_mean(temp2, 30)
        factor = hdl_ind_r[-10:].mean().to_frame()

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB17_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(CB17_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        temp = df['close'][-500:].between_time(data_morning_begin, trade_stop_time)
      
        temp = temp.groupby(temp.index.date)

        factor = abs(temp.last()/temp.first().shift(1)-1)
        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB25_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','open','close_stk','open_stk']
        super(CB25_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):        
        f1 = ts_mean(df['close'][-90:],10)
        f1 = ts_reg_beta(f1, 60)[-20:]
        factor = abs(f1.mean()).to_frame()
        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k31_arc_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','amount']
        super(wyc_k31_arc_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        #收益率与成交额的相关性
        c = df['close'].between_time(data_morning_begin, trade_stop_time)
        a = df['amount'].between_time(data_morning_begin, trade_stop_time)
        g = c.groupby(c.index.date)
        r = g.last() / g.first() - 1
        r = r.replace([np.inf, -np.inf], np.nan)

        a = a.groupby(a.index.date).sum()
        N = 10
        factor = a[-1*N:].corrwith(r[-1*N:]).to_frame()
        factor = factor.replace([np.inf, -np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB22_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close', 'high', 'low']
        super(CB22_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)
        high = df['high'].between_time(data_morning_begin, trade_stop_time)
        high = high.groupby(high.index.date).max()
        high.index = pd.to_datetime(high.index)
        low = df['low'].between_time(data_morning_begin, trade_stop_time)
        low = low.groupby(low.index.date).min()
        low.index = pd.to_datetime(low.index)

        factor = (ts_max(high, 10)/close) - (ts_min(low, 10)/close)

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k12_convvalue_kzzrdf(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','close_stk','CB_ANAL_CONVPRICE']
        super(wyc_k12_convvalue_kzzrdf, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        conv = df['CB_ANAL_CONVPRICE'] # 转股价
        kzz_close = df['close']
        clist = list(set(kzz_close.columns) & set(conv.columns))
        clist.sort()
        conv = conv[clist]
        kzz_close = kzz_close[clist]
        stk_close = df['close_stk'][clist]
        conv_minute = conv.reindex(kzz_close.index, method='pad') # 转股价reindex到分钟

        conv_minute = conv_minute.replace(0, np.nan)
        conv_value = 100 * stk_close / conv_minute # 转股价值

        factor = conv_value.between_time(data_morning_begin, trade_stop_time)
        factor = factor.groupby(factor.index.date).last()
        factor.index = pd.to_datetime(factor.index) # 14点49分的转股溢价
        factor = factor.replace([np.inf, -np.inf], np.nan)
      
        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB35_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','open','close_stk','open_stk']
        super(CB35_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):        
        hclose = df['close'].between_time(data_morning_begin, trade_stop_time)
        hopen = df['open'].between_time(data_morning_begin, trade_stop_time)

        diff = hclose.groupby(hclose.index.date).last()- hopen.groupby(hopen.index.date).first()

        factor = abs(ts_reg_beta(diff, 15))

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB36_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['high','low']
        super(CB36_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        high = df['high'].between_time(data_morning_begin, trade_stop_time)
        low = df['low'].between_time(data_morning_begin, trade_stop_time)

        diff = high.groupby(high.index.date).max()- low.groupby(low.index.date).min()

        factor = abs(ts_reg_beta(diff, 20))

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k198_stda_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['amount']
        super(wyc_k198_stda_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        #收益率与成交额的相关性
        amount = df['amount'].between_time(data_morning_begin, trade_stop_time)
        amount = amount.groupby(amount.index.date).sum()
        amount.index = pd.to_datetime(amount.index)

        factor = ts_std(amount, 10)

        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k110_BR_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','high','low']
        super(wyc_k110_BR_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)
        high = df['high'].between_time(data_morning_begin, trade_stop_time)
        high = high.groupby(high.index.date).max()
        high.index = pd.to_datetime(high.index)
        low = df['low'].between_time(data_morning_begin, trade_stop_time)
        low = low.groupby(low.index.date).min()
        low.index = pd.to_datetime(low.index)

        M=20
        factor = ts_sum(MAX(0,high-ts_delay(close,1)),M)/ts_sum(MAX(0,ts_delay(close,1)-low),M)
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k28_cm_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(wyc_k28_cm_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_afternoon_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        factor = abs(close / ts_mean(close, 20) - 1)
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB14_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','volume']
        super(CB14_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]

        hc = df['close'][-400:].pct_change()
        hcv = df['volume'][-400:].pct_change()
        upclose = hc > 0
        upvolume = hcv > 0

        aa = upclose*upvolume
        vwtc_r = ts_sum(aa, 220)
        vwtc_r = vwtc_r.loc[tday:].between_time(datetime.time(14,0), trade_stop_time)
        factor = vwtc_r.mean().to_frame()
        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB27_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(CB27_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        hclose = df['close'].between_time(datetime.time(14, 0), trade_stop_time)
        hclose = hclose.groupby(hclose.index.date)
        factor = ts_mean(hclose.last()/hclose.first()-1, 15) * -1

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB31_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(CB31_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]

        close = df['close'][-200:]
        cm = ts_mean(close, 60)
        cs = ts_std(close, 60)

        bb = cm+2*cs

        f = (close/bb).loc[tday:].between_time(datetime.time(14,0), trade_stop_time)
        factor = f.mean().to_frame() * -1

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB4_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','volume']
        super(CB4_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        f1 = df['close'][-190:]
        f2 = df['volume'][-190:]

        f = f1.rolling(180, min_periods = 30).corr(f2)
        f = f[-10:]
        factor = f.mean().to_frame()

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k2_retdiffstd_ks(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','close_stk','CB_ANAL_CONVPRICE']
        super(wyc_k2_retdiffstd_ks, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        ret_diff = df['close_stk'].pct_change() - df['close'].pct_change()
        factor = ts_std(ret_diff, 230)
      
        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k29_cstd_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(wyc_k29_cstd_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_afternoon_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        factor = abs(close / ts_mean(close, 20) - 1)
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
        # 因子开发时保存因子错误，保存成k28了
        # close = df['close'].between_time(data_morning_begin, trade_stop_time)
        # close = close.groupby(close.index.date).last()
        # close.index = pd.to_datetime(close.index)

        # N = 30
        # factor = ts_std(close, N)
        # factor = factor.replace([np.inf, -np.inf], np.nan)

        # factor = factor.iloc[-1].to_frame()
        # columnname = self.__class__.__name__
        # factor.columns = [columnname]
        # return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k107_AD_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','high','low','volume']
        super(wyc_k107_AD_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)
        high = df['high'].between_time(data_morning_begin, trade_stop_time)
        high = high.groupby(high.index.date).max()
        high.index = pd.to_datetime(high.index)
        low = df['low'].between_time(data_morning_begin, trade_stop_time)
        low = low.groupby(low.index.date).min()
        low.index = pd.to_datetime(low.index)
        volume = df['volume'].between_time(data_morning_begin, trade_stop_time)
        volume = volume.groupby(volume.index.date).sum()
        volume.index = pd.to_datetime(volume.index)

        factor = -1 * ts_sum(((close-low)-(high-close))/(high-low)*volume,30)
        factor = factor.replace([np.inf, -np.inf], np.nan)
      
        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB16_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','open','high']
        super(CB16_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'][-240:].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)
        high = df['high'][-240:].between_time(data_morning_begin, trade_stop_time)
        high = high.groupby(high.index.date).max()
        high.index = pd.to_datetime(high.index)
        opendf = df['open'][-240:].between_time(data_morning_begin, trade_stop_time)
        opendf = opendf.groupby(opendf.index.date).first()
        opendf.index = pd.to_datetime(opendf.index)

        temp = pd.DataFrame(np.where(close>opendf, close, opendf),index = close.index,columns=close.columns)

        factor = high / temp
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB8_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['high', 'low']
        super(CB8_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['high'].index.date[-1]

        temp_high = df['high'].loc[tday:].between_time(datetime.time(14,0), trade_stop_time).max()
        temp_low = df['low'].loc[tday:].between_time(datetime.time(14,0), trade_stop_time).min()

        factor = ((temp_high-temp_low)/temp_low).to_frame()

        factor = factor.replace([-np.inf, np.inf], np.nan)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class kzz_cssuper(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(kzz_cssuper, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        
        c = df['close'].between_time(data_morning_begin, trade_stop_time)
        factor = c.groupby(c.index.date).std()
        factor.index = pd.to_datetime(factor.index)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k11_doublelow_kzzrdf(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close', 'close_stk', 'CB_ANAL_CONVPRICE']
        super(wyc_k11_doublelow_kzzrdf, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        # 双低策略因子
        conv = df['CB_ANAL_CONVPRICE'] # 转股价
        kzz_close = df['close']
        clist = list(set(kzz_close.columns) & set(conv.columns))
        clist.sort()
        conv = conv[clist]
        kzz_close = kzz_close[clist]
        stk_close = df['close_stk'][clist]
        conv_minute = conv.reindex(kzz_close.index, method='pad') # 转股价reindex到分钟

        conv_minute = conv_minute.replace(0, np.nan)
        conv_value = 100 * stk_close / conv_minute # 转股价值
        conv_premium = kzz_close - conv_value # 转股溢价
        conv_premium_ratio = conv_premium / conv_value # 转股溢价率

        conv_premium_ratio_1449 = conv_premium_ratio.between_time(data_morning_begin, trade_stop_time)
        conv_premium_ratio_1449 = conv_premium_ratio_1449.groupby(conv_premium_ratio_1449.index.date).last()
        conv_premium_ratio_1449.index = pd.to_datetime(conv_premium_ratio_1449.index) # 14点49分的转股溢价率

        close_1449 = df['close'][clist].between_time(data_morning_begin, trade_stop_time)
        close_1449 = close_1449.groupby(close_1449.index.date).last()
        close_1449.index = pd.to_datetime(close_1449.index)

        factor = close_1449 + conv_premium_ratio_1449 * 100
        factor = factor.rank(axis = 1, pct = True)
        factor = abs(factor - 0.5)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class kzz_assuper(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['amount']
        super(kzz_assuper, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = df['amount'][-250:].between_time(data_morning_begin,trade_stop_time)
        factor = factor.groupby(factor.index.date).sum()
        factor.index = pd.to_datetime(factor.index)
      
        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k41_ADXpdm_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['high','low','close']
        super(wyc_k41_ADXpdm_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)
        high = df['high'].between_time(data_morning_begin, trade_stop_time)
        high = high.groupby(high.index.date).max()
        high.index = pd.to_datetime(high.index)
        low = df['low'].between_time(data_morning_begin, trade_stop_time)
        low = low.groupby(low.index.date).min()
        low.index = pd.to_datetime(low.index)

        N = 40
        max_high = MAX(high - ts_delay(high,1), 0)
        max_low = MAX(ts_delay(low, 1) - low, 0)
        xpdm = pd.DataFrame(0,columns = max_high.columns, index = max_high.index)
        xpdm[max_high > max_low] = high - ts_delay(high, 1)
        pdm = ts_sum(xpdm, N)
        tr = MAX(abs(high - low), abs(high - close))
        tr = MAX(tr, abs(low - close))
        tr = ts_sum(tr, N)
        factor = (pdm) / tr
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k22_vs_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['volume']
        super(wyc_k22_vs_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        a = df['volume'].between_time(data_morning_begin, trade_stop_time)
        factor = a.groupby(a.index.date).sum()
        factor.index = pd.to_datetime(factor.index)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB26_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['open','low']
        super(CB26_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        low = df['low'][-240:].between_time(data_afternoon_begin, trade_stop_time)
        low = low.groupby(low.index.date).min()
        low.index = pd.to_datetime(low.index)
        opendf = df['open'][-240:].between_time(data_afternoon_begin, trade_stop_time)
        opendf = opendf.groupby(opendf.index.date).first()
        opendf.index = pd.to_datetime(opendf.index)

        factor = (low / opendf) * -1

        factor.index = pd.to_datetime(factor.index)
        factor = factor.replace([-np.inf, np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k177_ADOWN_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close']
        super(wyc_k177_ADOWN_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        N = 20
        DOWN = pd.DataFrame(columns = close.columns, index = close.index, dtype = 'float')
        DOWN[close <= ts_delay(close, 1)] = ts_std(close, N)
        DOWN[close > ts_delay(close, 1)] = 0
        factor = ts_mean(DOWN, N)
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k44_MTM_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','amount']
        super(wyc_k44_MTM_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_afternoon_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        factor = close.pct_change(30)
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k30_neta_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','amount']
        super(wyc_k30_neta_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        # （成交价上涨部分对应的成交额-下跌部分对应的成交额）/总成交额
        c = np.sign(df['close'].pct_change().between_time(data_morning_begin, trade_stop_time))
        a = df['amount'].between_time(data_morning_begin, trade_stop_time)

        f = a * c
        factor = f.groupby(f.index.date).sum() / a.groupby(a.index.date).sum()
        factor = abs(factor) * -1
        factor.index = pd.to_datetime(factor.index)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k183_sqret_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','volume']
        super(wyc_k183_sqret_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        n = 6
        r = close / ts_max(close, 10) -1
        factor = np.sqrt(ts_mean(ts_sum(r ** 2, n), n))
        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k129_Chande_kzz(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close','high','low']
        super(wyc_k129_Chande_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        close = df['close'].between_time(data_morning_begin, trade_stop_time)
        close = close.groupby(close.index.date).last()
        close.index = pd.to_datetime(close.index)

        N = 20
        con1 = close - ts_delay(close, 1) > 0
        CZ1 = pd.DataFrame(columns = close.columns, index = close.index)
        CZ1[con1] = close - ts_delay(close, 1)
        CZ1[~con1] = 0
        factor = ts_sum(CZ1, N)

        factor = factor.replace([np.inf, -np.inf], np.nan)

        factor = factor.iloc[-1].to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
