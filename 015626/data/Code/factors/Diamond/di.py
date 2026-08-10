# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:11:55 2021

@author: appadmin
"""

import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *

class CC_33_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        
        required_columns=['close_000905.SH', 'volume_000905.SH']

        super(CC_33_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

        
    def on_bar(self, data):
        minute = futures_data_afternoon_end.minute
        hour = futures_data_afternoon_end.hour

        if minute < 1:
            minute = 60 + minute - 1
            hour = hour - 1
        else:
            minute = minute - 1

        high = data['close_000905.SH'].between_time(futures_data_morning_begin, datetime.time(hour, minute))

        close = data['volume_000905.SH'].between_time(futures_data_morning_begin, datetime.time(hour, minute))
        
        s = high.rolling(90, min_periods=10).std()
        f = close.rolling(90, min_periods=10).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(90, min_periods=10).cov(close) / (s * f)

        t_pcor2[abs(t_pcor2) > 1e8] = 0
        dd1 = t_pcor2.between_time(futures_data_morning_begin, trade_stop_time)
        dd1 = dd1.groupby(dd1.index.date).mean().to_frame()
        dd1.index.name = 'dt'

        dd1.columns = [self.__class__.__name__]
        dd1.index = pd.to_datetime(dd1.index)
        return -dd1
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc17_overnight_cfg(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_alla_preadj', 'amount_alla']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 计算当下时间价格上涨股票的成交额  
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_close = data_dict['close_alla_preadj'][zz500_stk_list]
        stk_amount = data_dict['amount_alla'][zz500_stk_list]
        stk_close = stk_close.between_time(futures_data_morning_begin, futures_data_afternoon_end)
        stk_amount = stk_amount.between_time(futures_data_morning_begin, futures_data_afternoon_end)

        price_diff = ts_delta(stk_close, 360)
        stk_amount_sum = ts_sum(stk_amount, 360)
        up_amount = stk_amount_sum[price_diff>=0].sum(axis=1)
        
        factor = -up_amount.iloc[up_amount.index.indexer_at_time(trade_stop_time)].to_frame()
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'


        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:26:50 2021

@author: appadmin
"""

from overnight.utility import *
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class IFIC4_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH']
        super(IFIC4_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=0, **kwargs)

    def on_bar(self, df):
        #columnname = self.__class__.__name__
        close = df['close_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        temp = close.rolling(60, min_periods = 15).mean() - close.shift(20).rolling(40, min_periods = 7).mean()
        factor = temp.to_frame()

        factor = np.abs(factor)
        factor = ts_rank(factor, 1200)
        t = factor.at_time(trade_stop_time)
        t.index = pd.to_datetime(t.index.date)
        t.index.name = 'dt'
        t.columns = [self.__class__.__name__]
        return t
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:10:22 2021

@author: appadmin
"""

from overnight.utility import *
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CC_7_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):

        required_columns =['high_IC.CFE','low_IC.CFE','recent_month_mask']
 
        super(CC_7_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)
    def on_bar(self, data):
        minute = trade_stop_time.minute
        hour = trade_stop_time.hour

        if minute < 49:
            minute = 60 + minute - 49
            hour = hour - 1
        else:
            minute = minute - 49

        temp_high = (data['high_IC.CFE'][data['recent_month_mask']]).between_time(datetime.time(hour, minute), trade_stop_time)
        temp_high = temp_high.groupby(temp_high.index.date)
        temp_low = (data['low_IC.CFE'][data['recent_month_mask']]).between_time(datetime.time(hour, minute), trade_stop_time)
        temp_low = temp_low.groupby(temp_low.index.date)
        a2 = ((temp_high.max()-temp_low.min())/replace_zero(temp_low.min())).mean(axis = 1).to_frame()
        
        a2.index = pd.to_datetime(a2.index)
        a2.index.name = 'dt'
        a2.columns = [self.__class__.__name__]
        return a2
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_39_rule(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'low_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        '''盘中一度达到跌停的股票比例'''
        '''中枢不稳定'''
        low_alla_daily_trun = data_dict['low_alla_daily_' + minute_to_daily_tag]
        stopping_alla_daily = data_dict['stopping_alla_daily']

        limit_judgement1 = (low_alla_daily_trun == stopping_alla_daily)  # 判断股票是否一度达到跌停
        
        factor = limit_judgement1.sum(axis=1) / stopping_alla_daily.count(axis=1)
        factor[factor<0.02] = 0
        factor[factor>0] = 1
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc28_overnight_cfg(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'low_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 当天涨幅一度小于7%，但尾盘还是大于7%的股票数量，反转因子(注意ts_rank的方向)
        # 分母用open效果不好，改成前一天的close以后好很多，可能是因为把前一天隔夜的信息包含进去了
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_close = data_dict['close_alla_daily_' + minute_to_daily_tag][zz500_stk_list]
        stk_low = data_dict['low_alla_daily_' + minute_to_daily_tag][zz500_stk_list]

        stk_ret = stk_close / stk_close.shift(1) - 1
        stk_ret_min = stk_low / stk_close.shift(1) - 1
        stk_ret_up_limit = stk_ret.gt(0.07)
        stk_ret_min_limit = stk_ret_min.gt(0.07)
        
        factor = stk_ret_min_limit.sum(axis=1) - stk_ret_up_limit.sum(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_22(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天开盘平均收益率
        close_alla_daily = data_dict['close_alla_daily']
        open_alla_daily_0930 = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1<1] = np.nan
        stk_ret = open_alla_daily_0930 / preclose_alla_daily - 1


        factor = -(limit_judgement1.shift(1) * stk_ret).mean(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc11_overnight_future(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_IC.CFE', 'volume_IC.CFE', 'position_IC.CFE', 'recent_month_mask']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 长江金工：经持仓量调整的价量相关性
        future_close = data_dict['close_IC.CFE']
        future_position = data_dict['position_IC.CFE']
        future_volume = data_dict['volume_IC.CFE']
        future_mask = data_dict['recent_month_mask']

        position_1 = future_position[future_mask].sum(axis=1).between_time(futures_data_morning_begin, trade_stop_time)
        volume_1 = future_volume[future_mask].sum(axis=1).between_time(futures_data_morning_begin, trade_stop_time)
        close_1 = future_close[future_mask].sum(axis=1).between_time(futures_data_morning_begin, trade_stop_time)

        volume_weight = volume_1.groupby(volume_1.index.date).apply(lambda x: x / x.sum())
        position_daily = position_1.groupby(position_1.index.date).last() - position_1.groupby(position_1.index.date).first()
        position_T_1 = volume_weight.groupby(volume_weight.index.date).apply(lambda x: x * position_daily[x.index.date[0]])
        position_T_0 = position_T_1 - position_1.groupby(position_1.index.date).apply(lambda x: x.diff())

        position_modify = (position_T_0 + position_T_1).groupby(position_T_0.index.date).apply(lambda x: x.cumsum()\
                                                                + position_1[(x.index.date[0]).strftime("%Y%m%d")].iloc[0])

        factor = pd.concat([close_1, position_modify], axis=1)
        factor = factor.groupby(factor.index.date).apply(lambda x: (x.diff().iloc[:,0]).corr(x.diff().iloc[:,1]))
        factor.index = pd.to_datetime(factor.index)
        factor.index.name = 'dt'
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:25:56 2021

@author: appadmin
"""

from overnight.utility import *
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class ICIF4_CC_IF(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH']
        super(ICIF4_CC_IF, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=0, **kwargs)

    def on_bar(self, df):
        #columnname = self.__class__.__name__
        close = df['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        temp = close.rolling(60, min_periods = 15).mean() - close.shift(20).rolling(40, min_periods = 7).mean()
        factor = temp.to_frame()
        
        factor = np.abs(factor)

        factor = ts_rank(factor, 1200)
        
        t = factor.at_time(trade_stop_time)
        t.index = pd.to_datetime(t.index.date)
        t.index.name = 'dt'
        t.columns = [self.__class__.__name__]
        return t
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:23:11 2021

@author: appadmin
"""

from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class GC001_Adiff_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['amount_204001.SH']
        super(GC001_Adiff_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=25, **kwargs)

    def on_bar(self, df):
        #columnname = self.__class__.__name__

        t = df['amount_204001.SH'].between_time(futures_data_morning_begin, futures_data_morning_end)
        t2 = df['amount_204001.SH'].between_time(futures_data_afternoon_begin, trade_stop_time)
        t = t.groupby(t.index.date).mean() - t2.groupby(t2.index.date).mean()
 
        t128 = t.to_frame()
        t128.index = pd.to_datetime(t128.index)
        t128.columns = [self.__class__.__name__]
        return t128
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_7(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'high_alla_daily_' + minute_to_daily_tag
        name2 = 'low_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'limit_alla_daily', 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 每个交易日一度跌停的股票比例减去一度涨停的股票比例
        high_alla_daily_trun = data_dict['high_alla_daily_' + minute_to_daily_tag]
        low_alla_daily_trun = data_dict['low_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']

        limit_judgement1 = (high_alla_daily_trun == limit_alla_daily)  # 判断股票是否一度涨停
        limit_judgement2 = (low_alla_daily_trun == stopping_alla_daily)  # 判断股票是否一度跌停
        
        
        factor = (limit_judgement2.sum(axis=1) - limit_judgement1.sum(axis=1)) / high_alla_daily_trun.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_if_2hour_return_nr_as_cfg(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_alla', 'amount_alla']
        super(wyc_if_2hour_return_nr_as_cfg, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=0, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        zz500_stock_list = self.get_mdconstant('zz500_stock_list')
        cif = df['close_alla'][zz500_stock_list].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif / cif.shift(1) - 1
        factor = ts_mean(ifreturn, 200)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount_alla'][zz500_stock_list].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 50)
        factor = ts_mean(factor, 40)
        factor = ts_rank(factor, 5 * 242)

        factor = factor.at_time(trade_stop_time)
        factor.index = pd.to_datetime(factor.index.date)
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:04:57 2021

@author: appadmin
"""
from overnight.utility import *
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CloseVoltoMean_ICIF_CC_IF(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH']
        super(CloseVoltoMean_ICIF_CC_IF, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=0, **kwargs)

    def on_bar(self, data):
        close = data['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        
        prstd3_r = close.rolling(30, min_periods =10).std()/close.rolling(30, min_periods =15).mean()
        prstd3_r[abs(prstd3_r)>100000] = np.nan
        prstd3_r = prstd3_r.rolling(15, min_periods = 2).mean()
        factor = prstd3_r.to_frame()

        factor.columns =  [self.__class__.__name__]
        factor = ts_rank(factor, 1200)
        factor[factor>1] = 0
        factor = factor.iloc[factor.index.indexer_at_time(trade_stop_time)]
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'
        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_1(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'amount_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'float_share_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, data_dict):
        # 中证800换手率
        zz800_stk_list = self.get_mdconstant('zz800_stock_list')
        close_zz800_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag][zz800_stk_list]
        amount_zz800_daily_1449 = data_dict['amount_alla_daily_' + minute_to_daily_tag][zz800_stk_list]
        float_share_zz800_daily = data_dict['float_share_alla_daily'][zz800_stk_list]
        daily_market_value = (float_share_zz800_daily * close_zz800_daily_1449).sum(axis=1)
        daily_amount = amount_zz800_daily_1449.sum(axis=1)

        factor = daily_amount / replace_zero(daily_market_value)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_41_rule(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天平均收益率(包含隔夜收益)
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']
        close_alla_daily_trun = close_alla_daily_trun.reindex(limit_alla_daily.index)

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1<1] = np.nan
        stk_ret = close_alla_daily_trun / preclose_alla_daily - 1


        factor = (limit_judgement1.shift(1) * stk_ret).mean(axis=1)
        factor[factor<0.008] = 1
        factor[factor<1] = 0
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:11:55 2021

@author: appadmin
"""

import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *

class CC_27_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        
        required_columns = ['close_IC.CFE','recent_month_mask']

        super(CC_27_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

        
    def on_bar(self, data):
        columnname = self.__class__.__name__
        temp = data['close_IC.CFE'][data['recent_month_mask']].mean(axis = 1)
        temp = temp.between_time(futures_data_morning_begin, trade_stop_time)
        temp = temp.groupby(temp.index.date)
        factor = (temp.max() - temp.min()).to_frame()

        factor.index.name = 'dt'

        factor.columns = [columnname]
        factor.index = pd.to_datetime(factor.index)
        return factor
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc18_overnight_cfg(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_alla_preadj', 'amount_alla']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 下午开盘至尾盘的Arms技术指标，用来显示成交额是否跟随价格上涨或者价格下跌
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_close = data_dict['close_alla_preadj'][zz500_stk_list]
        stk_amount = data_dict['amount_alla'][zz500_stk_list]
        stk_close = stk_close.between_time(futures_data_morning_begin, futures_data_afternoon_end)
        stk_amount = stk_amount.between_time(futures_data_morning_begin, futures_data_afternoon_end)

        price_diff = ts_delta(stk_close, 110)
        price_diff1 = ts_delta(stk_close, 360)
        stk_amount_sum = ts_sum(stk_amount, 110)

        up_num = (price_diff >= 0).sum(axis=1)
        down_num = (price_diff < 0).sum(axis=1)
        up_amount = stk_amount_sum[price_diff1 >= 0].sum(axis=1)
        down_amount = stk_amount_sum[price_diff1 < 0].sum(axis=1)
        
        factor = (up_num / down_num) / (up_amount / down_amount)
        factor = factor.iloc[factor.index.indexer_at_time(trade_stop_time)].to_frame()
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'


        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_15(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['high_000905.SH', 'low_000905.SH', 'close_000905.SH', 'volume_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=80, **kwargs)

    def on_bar(self, data_dict):
        # mfi技术指标
        close_spot = data_dict['close_000905.SH']
        high_spot = data_dict['high_000905.SH']
        low_spot = data_dict['low_000905.SH']
        volume_spot = data_dict['volume_000905.SH']

        n = 300
        typical_price = (high_spot + low_spot + close_spot) / 3
        mf = typical_price * volume_spot
        mf_pos = mf.copy()
        mf_pos[ts_delta(typical_price, 1) < 0] = 0
        mf_neg = mf.copy()
        mf_neg[ts_delta(typical_price, 1) > 0] = 0
        mf_pos = ts_sum(mf_pos, n)
        mf_neg = ts_sum(mf_neg, n)
        mfi = 100 - 100 / (1 + mf_pos / mf_neg)
        mfi = get_single_minute_data(mfi, trade_stop_time)
        factor = -mfi.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc25_overnight_cfg(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'high_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 当天涨幅到达过8%但在尾盘时回落至8%以下的股票数量，动量因子(注意ts_rank的方向)
        # 分母用open效果不好，改成前一天的close以后好很多，可能是因为把前一天隔夜的信息包含进去了
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_close = data_dict['close_alla_daily_' + minute_to_daily_tag][zz500_stk_list]
        stk_high = data_dict['high_alla_daily_' + minute_to_daily_tag][zz500_stk_list]

        stk_ret = stk_close / stk_close.shift(1) - 1
        stk_ret_max = stk_high / stk_close.shift(1) - 1
        stk_ret_up_limit = stk_ret.gt(0.08)
        stk_ret_max_limit = stk_ret_max.gt(0.08)
        
        factor = stk_ret_up_limit.sum(axis=1) - stk_ret_max_limit.sum(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc41_overnight_index_rule(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH', 'close_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 沪深300相比中证500当天收益率的超额
        index_close_ic = data_dict['close_000905.SH']
        index_close_if = data_dict['close_000300.SH']
        
        index_close_ic_1449 = get_single_minute_data(index_close_ic, trade_stop_time)
        index_close_if_1449 = get_single_minute_data(index_close_if, trade_stop_time)
        index_ret_ic_1449 = ts_pct_change(index_close_ic_1449, 1)
        index_ret_if_1449 = ts_pct_change(index_close_if_1449, 1)
        factor = (index_ret_ic_1449 < (index_ret_if_1449 - .005)) + 0.
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:20:00 2021

@author: appadmin
"""

from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CC_4_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['volume_IC.CFE', 'recent_month_mask']
        super(CC_4_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, df):

        suffix = '_IC.CFE'
        cif = df['volume' + suffix].between_time(futures_data_morning_begin, trade_stop_time)
        temp_volume = (cif[df['recent_month_mask'].between_time(futures_data_morning_begin, trade_stop_time)])
        temp_volume = temp_volume.groupby(temp_volume.index.date)
        temp1 = temp_volume.std().dropna(how = 'all').mean(axis = 1).to_frame()
        #ts_rank window: 60
        #a2 = ts_rank(temp1.to_frame(), 60)
        temp1.index = pd.to_datetime(temp1.index)
        temp1.columns = [self.__class__.__name__]
        return temp1
##########
import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_27(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'preclose_alla_daily', 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天开盘平均收益率减去前一个交易日跌停的股票当天开盘平均收益率
        close_alla_daily = data_dict['close_alla_daily']
        open_alla_daily_0930 = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1 < 1] = np.nan
        limit_judgement2 = (close_alla_daily == stopping_alla_daily)  # 判断当天股票是否跌停
        limit_judgement2[limit_judgement2 < 1] = np.nan
        stk_ret = open_alla_daily_0930 / preclose_alla_daily - 1


        factor = (limit_judgement2.shift(1) * stk_ret).mean(axis=1) - (limit_judgement1.shift(1) * stk_ret).mean(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_13(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'high_000905.SH_daily_' + minute_to_daily_tag
        name2 = 'low_000905.SH_daily_' + minute_to_daily_tag
        name3 = 'volume_000905.SH_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, name3]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, data_dict):
        # EMV技术指标，在500上用500数据好，300上500和1000差不多，50上1000数据好
        high_spot_daily_1449 = data_dict['high_000905.SH_daily_' + minute_to_daily_tag]
        low_spot_daily_1449 = data_dict['low_000905.SH_daily_' + minute_to_daily_tag]
        volume_spot_daily_1449 = data_dict['volume_000905.SH_daily_' + minute_to_daily_tag]

        mid_pt_move = ts_delta(high_spot_daily_1449 + low_spot_daily_1449, 1) / 2
        box_ratio = volume_spot_daily_1449 / (high_spot_daily_1449 - low_spot_daily_1449)
        emv = mid_pt_move / box_ratio
        factor = -emv.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:11:33 2021

@author: appadmin
"""

from overnight.utility import *
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CC_2_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):

        required_columns =['vwap_IC.CFE', 'recent_month_mask']
 
        super(CC_2_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=90, **kwargs)
    def on_bar(self, data):
        temp = (data['vwap_IC.CFE'][data['recent_month_mask']]).between_time(futures_data_morning_begin, trade_stop_time)
        temp = temp.groupby(temp.index.date)
        temp1 = ((temp.last()-temp.min())/replace_zero(temp.min())).mean(axis = 1)
        a2 = temp1.to_frame()
        a2.index = pd.to_datetime(a2.index)
        a2.index.name = 'dt'
        a2.columns = [self.__class__.__name__]
        return a2
##########
import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_28(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'preclose_alla_daily', 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天开盘平均收益率加上前一个交易日跌停的股票当天开盘平均收益率
        close_alla_daily = data_dict['close_alla_daily']
        open_alla_daily_0930 = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1 < 1] = np.nan
        limit_judgement2 = (close_alla_daily == stopping_alla_daily)  # 判断当天股票是否跌停
        limit_judgement2[limit_judgement2 < 1] = np.nan
        stk_ret = open_alla_daily_0930 / preclose_alla_daily - 1


        factor = (limit_judgement2.shift(1) * stk_ret).mean(axis=1) + (limit_judgement1.shift(1) * stk_ret).mean(axis=1)
        factor = factor.to_frame() * (-1)
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_5(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=80, **kwargs)

    def on_bar(self, data_dict):
        '''沪深300收益率截面离散度'''
        hs300_stk_list = self.get_mdconstant('hs300_stock_list')
        close_hs300_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag][hs300_stk_list]
        
        factor = ts_pct_change(close_hs300_daily_trun, 5).std(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_20_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=50, **kwargs)

    def on_bar(self, data_dict):
        # 尾盘收益率的反转指标
        close_spot_if = data_dict['close_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n = 50
        nvi_inc = ts_pct_change(close_spot_if, 1)
        nvi = ts_sum(nvi_inc, n)
        nvi = get_single_minute_data(nvi, trade_stop_time)
        factor = -nvi.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor




##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc40_overnight_cfg(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'low_alla_daily_' + minute_to_daily_tag
        name3 = 'high_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, name3]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 当天振幅超过8%的股票数量减去盘中最大跌幅在8%以上的股票数量
        # 分母用open效果不好，改成前一天的close以后好很多，可能是因为把前一天隔夜的信息包含进去了
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        stk_close = data_dict['close_alla_daily_' + minute_to_daily_tag][zz500_stk_list]
        stk_low = data_dict['low_alla_daily_' + minute_to_daily_tag][zz500_stk_list]
        stk_high = data_dict['high_alla_daily_' + minute_to_daily_tag][zz500_stk_list]

        stk_ret = stk_low / stk_close.shift(1) - 1
        stk_ret_max = stk_high / stk_low - 1
        stk_ret_up_limit = stk_ret.lt(-0.08)
        stk_ret_max_limit = stk_ret_max.gt(0.08)
        
        factor_raw = stk_ret_up_limit.sum(axis=1) - stk_ret_max_limit.sum(axis=1)
        factor = factor_raw.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_35(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'stopping_alla_daily', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天收益率之和（包含隔夜收益）与前一个交易日跌停的股票当天收益率之和（包含隔夜收益）相加
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']
        close_alla_daily_trun = close_alla_daily_trun.reindex(limit_alla_daily.index)

        limit_judgement1 = (close_alla_daily == limit_alla_daily) + 0.  # 判断股票当天是否涨停
        limit_judgement2 = (close_alla_daily == stopping_alla_daily) + 0.  # 判断当天股票是否跌停
        # limit_judgement1[limit_judgement1<1] = np.nan  # FALSE那部分不置为nan不会影响求和结果
        stk_ret = close_alla_daily_trun / preclose_alla_daily - 1  # 股票当天收益率（包含隔夜收益）


        factor = -((limit_judgement1 + limit_judgement2).shift(1) * stk_ret).sum(axis=1) / stopping_alla_daily.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *

class wsc16_overnight_cfg_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_alla_preadj', 'weight_hs300']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # abi技术指标，值越大表示市场越活跃，活动和变化频繁，反之意味着市场缺乏变化
        hs300_stk_list = self.get_mdconstant('hs300_stock_list')
        stk_close = data_dict['close_alla_preadj'][hs300_stk_list]
        stk_weight = data_dict['weight_hs300'][hs300_stk_list]
        stk_close = stk_close.between_time(futures_data_morning_begin, futures_data_afternoon_end)
        stk_weight = stk_weight.between_time(futures_data_morning_begin, futures_data_afternoon_end)

        price_diff = ts_delta(stk_close, 230)
        price_diff[price_diff >= 0] = 1
        price_diff[price_diff < 0] = -1

        factor = abs((price_diff*stk_weight).sum(axis=1))
        factor = factor.iloc[factor.index.indexer_at_time(trade_stop_time)].to_frame()
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_30(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'preclose_alla_daily', 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天平均收益率(包含隔夜收益)加上前一个交易日跌停的股票当天平均收益率(包含隔夜收益)
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']
        close_alla_daily_1449 = close_alla_daily_1449.reindex(limit_alla_daily.index)

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1 < 1] = np.nan
        limit_judgement2 = (close_alla_daily == stopping_alla_daily)  # 判断当天股票是否跌停
        limit_judgement2[limit_judgement2 < 1] = np.nan
        stk_ret = close_alla_daily_1449 / preclose_alla_daily - 1


        factor = (limit_judgement2.shift(1) * stk_ret).mean(axis=1) + (limit_judgement1.shift(1) * stk_ret).mean(axis=1)
        factor = factor.to_frame() * (-1)
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_15(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'close_alla_daily', 'limit_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票，第二天开盘涨停的股票比例减去尾盘涨停的股票比例
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag]
        open_alla_daily_0930 = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        close_alla_daily_1449 = close_alla_daily_1449.reindex(limit_alla_daily.index)

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement2 = (close_alla_daily_1449 == limit_alla_daily)  # 判断截止到1449，股票是否涨停
        limit_judgement3 = (open_alla_daily_0930 == limit_alla_daily)  # 判断当天0930，股票是否涨停
        limit_judgement4 = limit_judgement1.shift(1) * limit_judgement2  # 前一天涨停的股票今天尾盘是否继续涨停
        limit_judgement5 = limit_judgement1.shift(1) * limit_judgement3  # 前一天涨停的股票今天早盘是否继续涨停

        
        factor = (limit_judgement5.sum(axis=1) - limit_judgement4.sum(axis=1)) / close_alla_daily.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor

    
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_2(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 中证500过去120天成分股新高的数量
        zz500_stk_list = self.get_mdconstant('zz500_stock_list')
        close_zz500_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag][zz500_stk_list]
        factor = (close_zz500_daily_1449 >= ts_max(close_zz500_daily_1449, 120)).sum(axis=1)

        factor = factor.to_frame() * (-1)
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_21_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH', 'high_000300.SH', 'low_000300.SH', 'volume_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        # 20分钟vwap和close之差，类似于结算指标
        close_spot_if = data_dict['close_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        high_spot_if = data_dict['high_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        low_spot_if = data_dict['low_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        volume_spot_if = data_dict['volume_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n = 20
        typical = (high_spot_if + low_spot_if + close_spot_if) / 3
        mf = volume_spot_if * typical
        volume_sum = ts_sum(volume_spot_if, n)
        mf_sum = ts_sum(mf, n)
        vwap = mf_sum / volume_sum
        factor_raw = vwap - close_spot_if
        factor_raw = get_single_minute_data(factor_raw, trade_stop_time)
        factor = factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor




##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_4(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        name2 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'limit_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, data_dict):
        # 每个交易日尾盘和开盘涨停的股票比例之差
        open_alla_daily_trun = data_dict['open_alla_daily_' + minute_to_daily_tag]
        close_alla_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        close_alla_daily_trun = close_alla_daily_trun.reindex(limit_alla_daily.index)

        limit_judgement1 = (open_alla_daily_trun == limit_alla_daily)  # 判断股票开盘是否涨停
        limit_judgement2 = (close_alla_daily_trun == limit_alla_daily)  # 判断股票尾盘是否涨停
        
        factor = (limit_judgement1.sum(axis=1) - limit_judgement2.sum(axis=1)) / open_alla_daily_trun.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:27:15 2021

@author: appadmin
"""

from overnight.utility import *
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class MALS_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_IC.CFE', 'recent_month_mask']
        super(MALS_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=0, **kwargs)

    def on_bar(self, df):
        #columnname = self.__class__.__name__
        close = df['close_IC.CFE'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        mask = df['recent_month_mask'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        temp = close.rolling(60, min_periods = 15).mean() - close.shift(20).rolling(40, min_periods = 7).mean()
        temp = (temp[mask]).mean(axis = 1)
        factor = temp.rolling(3, min_periods = 1).mean().to_frame()
       
        factor = np.abs(factor)
        factor = rolling_norm(factor, 2420)
        factor = ts_rank(factor, 1200)
        
        t = factor.at_time(trade_stop_time)
        t.index = pd.to_datetime(t.index.date)
        t.index.name = 'dt'
        t.columns = [self.__class__.__name__]
        return t
##########
import scipy.stats
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import warnings
from overnight.utility import *


class wsc_pv_9(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_000300.SH', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        '''沪深300_日alla_Univ分位数'''
        close_000300 = data_dict['close_000300.SH']
        close_alla_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag]
        preclose_alla_daily = data_dict['preclose_alla_daily']

        close_000300_daily_1449 = close_000300.iloc[close_000300.index.indexer_at_time(trade_stop_time)]
        close_000300_daily_1500 = close_000300.iloc[close_000300.index.indexer_at_time('15:00')]
        close_000300_daily_1449.index = pd.to_datetime(close_000300_daily_1449.index.date)
        close_000300_daily_1500.index = pd.to_datetime(close_000300_daily_1500.index.date)
        close_000300_daily_1500 = close_000300_daily_1500.reindex(close_000300_daily_1449.index)
        spot_ret = close_000300_daily_1449 / close_000300_daily_1500.shift(1) - 1
        spot_ret.index.name = 'dt'
        stk_ret = close_alla_daily_1449 / preclose_alla_daily - 1

        i_date = stk_ret.index[-1]
        factor = pd.DataFrame(index=[i_date], columns=[self.__class__.__name__])
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', FutureWarning)
            factor.loc[i_date] = scipy.stats.percentileofscore(stk_ret.loc[i_date].dropna(), spot_ret.loc[i_date])
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:11:55 2021

@author: appadmin
"""
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CC_12_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['high_000905.SH', 'close_000905.SH']

        super(CC_12_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

            
    def on_bar(self, data):
        high = data['high_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        close = data['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        
        t_pcor2 = high.rolling(60, min_periods=30).corr(close)
        
        t_pcor2[abs(t_pcor2) > 1] = np.nan
        dd1 = t_pcor2.between_time(futures_data_afternoon_begin, trade_stop_time)
        dd1 = dd1.groupby(dd1.index.date).mean().to_frame()
        
        dd1.index = pd.to_datetime(dd1.index)
        dd1.index.name = 'dt'
        dd1.columns = [self.__class__.__name__]
        return dd1
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_18(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH', 'amount_000905.SH', 'open_000905.SH', 'high_000905.SH', 'low_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=120, **kwargs)

    def on_bar(self, data_dict):
        # wvad技术指标_短参数，用分钟内的价格变化给成交额加权，变化越大则权重越低，但是注意后面加了负号
        close_spot = data_dict['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        open_spot = data_dict['open_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        high_spot = data_dict['high_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        low_spot = data_dict['low_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        amount_spot = data_dict['amount_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n = 41
        wvad = ts_sum((close_spot - open_spot) / (high_spot - low_spot) * amount_spot, n)
        wvad = get_single_minute_data(wvad, trade_stop_time)
        factor = -wvad.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor




##########
import pandas as pd
import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_24(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'close_alla_daily', 'limit_alla_daily', 'close_000906.SH', 'open_000906.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天平均超额收益（不包含隔夜收益）
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag]
        open_alla_daily_0930 = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        close_000906 = data_dict['close_000906.SH']
        open_000906 = data_dict['open_000906.SH']
        close_alla_daily_1449 = close_alla_daily_1449.reindex(limit_alla_daily.index)

        open_000906_0930 = open_000906.iloc[open_000906.index.indexer_at_time(futures_data_morning_begin)]
        open_000906_0930.index = pd.to_datetime(open_000906_0930.index.date)
        close_000906_1449 = close_000906.iloc[close_000906.index.indexer_at_time(trade_stop_time)]
        close_000906_1449.index = pd.to_datetime(close_000906_1449.index.date)
        index_ret = close_000906_1449 / open_000906_0930 - 1
        index_ret.index.name = 'dt'


        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1<1] = np.nan
        stk_ret = close_alla_daily_1449 / open_alla_daily_0930 - 1


        factor = (limit_judgement1.shift(1) * stk_ret).mean(axis=1) - index_ret
        factor = factor.to_frame() * (-1)
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_36(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'stopping_alla_daily', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=15, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天收益率之和（包含隔夜收益）与前一个交易日跌停的股票当天收益率之和（包含隔夜收益）相减
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_trun = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']
        close_alla_daily_trun = close_alla_daily_trun.reindex(limit_alla_daily.index)

        limit_judgement1 = (close_alla_daily == limit_alla_daily) + 0.  # 判断股票当天是否涨停
        limit_judgement2 = (close_alla_daily == stopping_alla_daily) + 0.  # 判断当天股票是否跌停
        # limit_judgement1[limit_judgement1<1] = np.nan  # FALSE那部分不置为nan不会影响求和结果
        stk_ret = close_alla_daily_trun / preclose_alla_daily - 1  # 股票当天收益率（包含隔夜收益）

        factor = -((limit_judgement1 - limit_judgement2).shift(1) * stk_ret).sum(axis=1) / stopping_alla_daily.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_13(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票今天尾盘继续涨停的占昨天涨停股票的比例
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        close_alla_daily_1449 = close_alla_daily_1449.reindex(limit_alla_daily.index)

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement2 = (close_alla_daily_1449 == limit_alla_daily)  # 判断截止到1449，股票是否涨停
        limit_judgement3 = limit_judgement1.shift(1) * limit_judgement2
        
        
        factor = -limit_judgement3.sum(axis=1) / limit_judgement1.shift(1).sum(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_search3_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['high_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 算法搜索
        high_000905 = data_dict['high_000905.SH'].to_frame()

        factor_raw = ts_std(high_000905, 75)
        factor = ts_rank(factor_raw, 1200)
        factor = get_single_minute_data(factor, trade_stop_time)
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:11:55 2021

@author: appadmin
"""

import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *

class CC_31_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        
        required_columns=['close_IF.CFE', 'volume_IF.CFE', 'recent_month_mask']

        super(CC_31_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

        
    def on_bar(self, data):
        
        temp1 = data['close_IF.CFE'].diff()
        temp2 = np.abs(data['volume_IF.CFE'] * temp1)
        temp2 = temp2[data['recent_month_mask']].mean(axis = 1).to_frame()
        hdl_ind_r = temp2.rolling(30, min_periods = 10).mean()
        a1 = hdl_ind_r

        minute = trade_stop_time.minute
        hour = trade_stop_time.hour

        if minute < 4:
            minute = 60 + minute - 4
            hour = hour - 1
        else:
            minute = minute - 4

        temp = a1.between_time(datetime.time(hour, minute), trade_stop_time)
        temp = temp.groupby(temp.index.date).mean()
        temp.index.name = 'dt'
        temp.columns = [self.__class__.__name__]
        temp.index = pd.to_datetime(temp.index)
        return temp
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc10_overnight_future(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_IC.CFE']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 近远月价差的日内变化
        future_close = data_dict['close_IC.CFE']

        recent_month_close = future_close.stack().groupby('dt').first()  # 获取近月合约的close序列
        far_month_close = future_close.stack().groupby('dt').nth(1)  # 获取次近月合约的close序列
        price_spread = recent_month_close - far_month_close
        price_spread_1449 = price_spread.iloc[price_spread.index.indexer_at_time(trade_stop_time)]
        price_spread_1449.index = pd.to_datetime(price_spread_1449.index.date)
        price_spread_0930 = price_spread.iloc[price_spread.index.indexer_at_time(futures_data_morning_begin)]
        price_spread_0930.index = pd.to_datetime(price_spread_0930.index.date)

        factor = (price_spread_0930 - price_spread_1449).to_frame()
        factor.index.name = 'dt'
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc13_overnight_future(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_IC.CFE']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # 近月合约和次近月合约尾盘收益率之差
        future_close = data_dict['close_IC.CFE']

        future_ret = ts_pct_change(future_close.stack().groupby('dt').nth(1), 30)
        future_ret = future_ret.iloc[future_ret.index.indexer_at_time(trade_stop_time)]
        future_ret.index = pd.to_datetime(future_ret.index.date)

        future_ret1 = ts_pct_change(future_close.stack().groupby('dt').nth(0), 30)
        future_ret1 = future_ret1.iloc[future_ret1.index.indexer_at_time(trade_stop_time)]
        future_ret1.index = pd.to_datetime(future_ret1.index.date)

        factor = (future_ret - future_ret1).to_frame()
        factor.index.name = 'dt'
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_factor_settlement(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_IC.CFE', 'recent_month_mask', 'amount_IC.CFE', 'volume_IC.CFE']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 股指期货结算价/收盘价，＞0.15%置为1，其余为0，反应了期指尾盘下跌情况。
        future_close = data_dict['close_IC.CFE']
        future_mask = data_dict['recent_month_mask']
        future_amount = data_dict['amount_IC.CFE']
        future_volume = data_dict['volume_IC.CFE']
        
        amount_sum = ts_sum(future_amount, 60)
        volume_sum = ts_sum(future_volume, 60)
        vwap_60 = (amount_sum / volume_sum)[future_mask].sum(axis=1)
        vwap_60 = vwap_60.iloc[vwap_60.index.indexer_at_time(trade_stop_time)].to_frame()
        vwap_60.index = pd.to_datetime(vwap_60.index.date)
        vwap_60.index.name = 'dt'

        close_stop_time = future_close[future_mask].sum(axis=1)
        close_stop_time = close_stop_time.iloc[close_stop_time.index.indexer_at_time(trade_stop_time)].to_frame()
        close_stop_time.index = pd.to_datetime(close_stop_time.index.date)
        close_stop_time.index.name = 'dt'

        factor = replace_zero((vwap_60/200) / close_stop_time)
        factor[factor<1.0015] = 0
        factor[factor>0] = 1


        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:21:38 2021

@author: appadmin
"""


from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class GC001_6_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_204001.SH', 'open_204001.SH']
        super(GC001_6_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=25, **kwargs)

    def on_bar(self, df):
        #columnname = self.__class__.__name__
        open1 = df['open_204001.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        close = df['close_204001.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        a = close - open1
        a[a>0] = 1
        a[a<0] = -1

        t = (a).groupby(a.index.date).sum()
        t114 = t.to_frame()
        t114.index = pd.to_datetime(t114.index)
        t114.columns = [self.__class__.__name__]
        return t114
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc21_overnight_index_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # rsj技术指标：（上行波动率-下行波动率）/（上行波动率+下行波动率）
        index_close = data_dict['close_000300.SH']
        index_close = index_close.between_time(futures_data_morning_begin, futures_data_afternoon_end)  # 新版指数数据有14:58-15:00的数据，为了与之前的因子值保持一致，做此截断处理
        # index_close.to_excel('/data/user/017024/index_close_29210513.xlsx')

        index_ret_up = ts_pct_change(index_close, 1)
        index_ret_up[index_ret_up < 0] = 0
        index_ret_down = ts_pct_change(index_close, 1)
        index_ret_down[index_ret_down > 0] = 0
        vol_up = ts_sum(index_ret_up**2, 350)
        vol_down = ts_sum(index_ret_down**2, 350)
        rsj = (vol_up-vol_down) / replace_zero(vol_up+vol_down)

        factor = -rsj.iloc[rsj.index.indexer_at_time(trade_stop_time)].to_frame()
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc42_overnight_index_rule(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 中证500当天收益率绝对值是否＞1.5%
        index_close_ic = data_dict['close_000905.SH']
        
        index_close_ic_1449 = get_single_minute_data(index_close_ic, trade_stop_time)
        index_ret_ic_1449 = ts_pct_change(index_close_ic_1449, 1)
        index_ret_ic_1449[abs(index_ret_ic_1449)>0.015] = 1
        index_ret_ic_1449[index_ret_ic_1449<1] = 0
        factor = index_ret_ic_1449.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import scipy.stats
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import warnings
from overnight.utility import *


class wsc_pv_7(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        '''中证500_日zz800_Univ分位数'''
        zz800_stk_list = self.get_mdconstant('zz800_stock_list')
        close_000905 = data_dict['close_000905.SH']
        close_zz800_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag][zz800_stk_list]

        close_000905_daily_1449 = close_000905[close_000905.index.indexer_at_time(trade_stop_time)]
        close_000905_daily_1449.index = pd.to_datetime(close_000905_daily_1449.index.date)
        close_000905_daily_1449.index.name = 'dt'
        spot_ret = ts_pct_change(close_000905_daily_1449, 1)
        stk_ret = ts_pct_change(close_zz800_daily_1449, 1)

        i_date = stk_ret.index[-1]
        factor = pd.DataFrame(index=[i_date], columns=[self.__class__.__name__])
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', FutureWarning)
            factor.loc[i_date] = -scipy.stats.percentileofscore(stk_ret.loc[i_date].dropna(), spot_ret.loc[i_date])
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 13:39:03 2021

@author: appadmin
"""

from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class GC001_corr_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_204001.SH', 'close_IH.CFE', 'recent_month_mask']
        super(GC001_corr_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=15, **kwargs)

    def on_bar(self, df):
        #columnname = self.__class__.__name__
        GC_close =  df['close_204001.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        close_ih = df['close_IH.CFE'][df['recent_month_mask']].mean(axis = 1).between_time(futures_data_morning_begin, trade_stop_time)
        t = (close_ih.rolling(150, min_periods = 60).corr(GC_close))
        t = -t.between_time(futures_data_afternoon_begin, trade_stop_time)
        t = t.groupby(t.index.date).mean().to_frame()
        t.index.name = 'dt'
        t.index = pd.to_datetime(t.index)
        t.columns = [self.__class__.__name__]
        return t
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *
  
class wyc_on31_DownBarNumPm_spot(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH','open_000905.SH','high_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=10, **kwargs)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        
        close_spot = df['close_000905.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        open_spot = df['open_000905.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        high_spot = df['high_000905.SH'].between_time(futures_data_morning_begin, trade_stop_time)

        down1 = close_spot < open_spot
        down2 = high_spot < open_spot.shift(1)
        down = down1 & down2

        down = down.groupby(down.index.date).sum()

        factor = down.to_frame()

        factor.index.name = 'dt'
        factor.index = pd.to_datetime(factor.index)
        factor.columns = [columnname]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:09:50 2021

@author: appadmin
"""

from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CC_12_if_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['high_000300.SH', 'close_000300.SH']

        super(CC_12_if_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

            
    def on_bar(self, data):
        high = data['high_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        close = data['close_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        
        t_pcor2 = high.rolling(60, min_periods=30).corr(close)
        
        t_pcor2[abs(t_pcor2) > 1] = np.nan
        dd1 = t_pcor2.between_time(futures_data_afternoon_begin, trade_stop_time)
        dd1 = dd1.groupby(dd1.index.date).mean().to_frame()
        
        dd1.index = pd.to_datetime(dd1.index)
        dd1.index.name = 'dt'
        dd1.columns = [self.__class__.__name__]
        return dd1
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_return_comparison(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH', 'close_000300.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 比较hs300指数和zz500指数过去三分钟收益率大小
        close_000905 = data_dict['close_000905.SH']
        close_000300 = data_dict['close_000300.SH']
        close_000300 = close_000300.between_time(futures_data_morning_begin, futures_data_afternoon_end)
        close_000905 = close_000905.between_time(futures_data_morning_begin, futures_data_afternoon_end)

        ret_000905 = ts_pct_change(close_000905, 3)
        ret_000300 = ts_pct_change(close_000300, 3)
        ret_diff = ret_000905 - ret_000300
        ret_diff[ret_diff > 0] = 1
        ret_diff[ret_diff <= 0] = 0
        temp = ts_sum(ret_diff, 180)
        factor_raw = ts_sum(ret_diff, 30) / replace_zero(temp)
        factor_mean = ts_mean(factor_raw, 10).to_frame()
        factor = ts_rank(factor_mean, 1200)
        factor = factor.iloc[factor.index.indexer_at_time(trade_stop_time)]
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_23(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=120, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天平均收益率(包含隔夜收益)
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']
        close_alla_daily_1449 = close_alla_daily_1449.reindex(limit_alla_daily.index)

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1<1] = np.nan
        stk_ret = close_alla_daily_1449 / preclose_alla_daily - 1


        factor = -(limit_judgement1.shift(1) * stk_ret).mean(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *

class wsc35_overnight_index_if(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH_daily_' + minute_to_daily_tag]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

    def on_bar(self, data_dict):
        # pos技术指标，反转因子
        index_close_daily = data_dict['close_000300.SH_daily_' + minute_to_daily_tag]

        n = 75
        price1 = ts_delta(index_close_daily, n) / ts_delay(index_close_daily, n)
        pos1 = (price1 - ts_min(price1, n)) / (ts_max(price1, n) - ts_min(price1, n))
        factor = -pos1.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        
        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_32(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'stopping_alla_daily', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日跌停的股票当天开盘收益率之和
        open_alla_daily_trun = data_dict['open_alla_daily_' + minute_to_daily_tag]
        close_alla_daily = data_dict['close_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']

        limit_judgement1 = (close_alla_daily == stopping_alla_daily)  # 判断当天股票是否跌停
        # limit_judgement1[limit_judgement1<1] = np.nan  # FALSE那部分不置为nan不会影响求和结果
        stk_ret = open_alla_daily_trun / preclose_alla_daily - 1  # 股票开盘收益率


        factor = -(limit_judgement1.shift(1) * stk_ret).sum(axis=1) / stopping_alla_daily.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_6(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        name2 = 'low_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 每个交易日跌停后又开板的股票比例
        close_alla_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag]
        low_alla_daily_1449 = data_dict['low_alla_daily_' + minute_to_daily_tag]
        stopping_alla_daily = data_dict['stopping_alla_daily']
        close_alla_daily_1449 = close_alla_daily_1449.reindex(stopping_alla_daily.index)

        limit_judgement1 = (low_alla_daily_1449 == stopping_alla_daily)  # 判断截止到1449，股票是否曾经触及跌停
        limit_judgement2 = (close_alla_daily_1449 == stopping_alla_daily)  # 判断截止到1449，股票是否跌停
        
        
        factor = (limit_judgement1.sum(axis=1) - limit_judgement2.sum(axis=1)) / close_alla_daily_1449.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_31(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=10, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天开盘收益率之和
        close_alla_daily = data_dict['close_alla_daily']
        open_alla_daily_trun = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        # limit_judgement1[limit_judgement1<1] = np.nan  # FALSE那部分不置为nan不会影响求和结果
        stk_ret = open_alla_daily_trun / preclose_alla_daily - 1  # 股票开盘收益率


        factor = -(limit_judgement1.shift(1) * stk_ret).sum(axis=1) / limit_alla_daily.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_5(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        name2 = 'low_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        # 每个交易日一度达到跌停的股票比例减去开盘即跌停的股票比例
        open_alla_daily_trun = data_dict['open_alla_daily_' + minute_to_daily_tag]
        low_alla_daily_trun = data_dict['low_alla_daily_' + minute_to_daily_tag]
        stopping_alla_daily = data_dict['stopping_alla_daily']

        limit_judgement1 = (low_alla_daily_trun == stopping_alla_daily)  # 判断截止到1449，股票是否曾经触及跌停
        limit_judgement2 = (open_alla_daily_trun == stopping_alla_daily)  # 判断截止到1449，股票是否跌停
        
        
        factor = (limit_judgement1.sum(axis=1) - limit_judgement2.sum(axis=1)) / open_alla_daily_trun.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_6(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_000300.SH_daily_' + minute_to_daily_tag
        name2 = 'close_000905.SH_daily_' + minute_to_daily_tag
        required_columns=[name1, name2]
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

    def on_bar(self, data_dict):
        '''沪深300与中证500日收益率之差'''
        close_000300_daily_trun = data_dict['close_000300.SH_daily_' + minute_to_daily_tag]
        close_000905_daily_trun = data_dict['close_000905.SH_daily_' + minute_to_daily_tag]
        
        spot_ret_if = ts_pct_change(close_000300_daily_trun, 1)
        spot_ret_ic = ts_pct_change(close_000905_daily_trun, 1)
        factor = spot_ret_if - spot_ret_ic
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_40_rule(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=1, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天开盘平均收益率
        close_alla_daily = data_dict['close_alla_daily']
        open_alla_daily_trun = data_dict['open_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1<1] = np.nan
        stk_ret = open_alla_daily_trun / preclose_alla_daily - 1

        factor = (limit_judgement1.shift(1) * stk_ret).mean(axis=1)
        factor[factor<0.015] = 1
        factor[factor<1] = 0
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import numpy as np
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_29(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'preclose_alla_daily', 'stopping_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天平均收益率(包含隔夜收益)减去前一个交易日跌停的股票当天平均收益率(包含隔夜收益)
        close_alla_daily = data_dict['close_alla_daily']
        close_alla_daily_1449 = data_dict['close_alla_daily_' + minute_to_daily_tag]
        limit_alla_daily = data_dict['limit_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']
        close_alla_daily_1449 = close_alla_daily_1449.reindex(stopping_alla_daily.index)

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement1[limit_judgement1 < 1] = np.nan
        limit_judgement2 = (close_alla_daily == stopping_alla_daily)  # 判断当天股票是否跌停
        limit_judgement2[limit_judgement2 < 1] = np.nan
        stk_ret = close_alla_daily_1449 / preclose_alla_daily - 1


        factor = (limit_judgement2.shift(1) * stk_ret).mean(axis=1) - (limit_judgement1.shift(1) * stk_ret).mean(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc43_overnight_index(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=120, **kwargs)

    def on_bar(self, data_dict):
        # 中证500当天收益率绝对值
        index_close_ic = data_dict['close_000905.SH']
        
        index_close_ic_1449 = get_single_minute_data(index_close_ic, trade_stop_time)
        index_ret_ic_1449 = ts_pct_change(index_close_ic_1449, 1)
        
        factor = abs(index_ret_ic_1449).to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_9(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'low_alla_daily_' + minute_to_daily_tag
        name2 = 'high_alla_daily_' + minute_to_daily_tag
        name3 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, name2, name3, 'stopping_alla_daily', 'limit_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=80, **kwargs)

    def on_bar(self, data_dict):
        # as follows
        low_alla_daily_1449 = data_dict['low_alla_daily_' + minute_to_daily_tag]
        high_alla_daily_1449 = data_dict['high_alla_daily_' + minute_to_daily_tag]
        open_alla_daily_0930 = data_dict['open_alla_daily_' + minute_to_daily_tag]
        stopping_alla_daily = data_dict['stopping_alla_daily']
        limit_alla_daily = data_dict['limit_alla_daily']

        limit_judgement1 = (low_alla_daily_1449 == stopping_alla_daily)  # 判断截止到1449，股票是否曾经触及跌停
        limit_judgement2 = (high_alla_daily_1449 == limit_alla_daily)  # 判断截止到1449，股票是否曾经触及涨停
        limit_judgement3 = (open_alla_daily_0930 == limit_alla_daily)  # 判断股票早盘是否涨停
        limit_judgement4 = (open_alla_daily_0930 == stopping_alla_daily)  # 判断股票早盘是否涨停
        
        
        factor = (limit_judgement1.sum(axis=1) - limit_judgement2.sum(axis=1) + limit_judgement3.sum(axis=1) - limit_judgement4.sum(axis=1)) / low_alla_daily_1449.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_pv_19(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH', 'volume_000905.SH']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # pvt技术指标
        close_spot = data_dict['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        volume_spot = data_dict['volume_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)

        n1 = 110
        n2 = 500
        pvt = ts_pct_change(close_spot, 1) * volume_spot
        pvt_ma1 = ts_mean(pvt, n1)
        pvt_ma2 = ts_mean(pvt, n2)
        factor_raw = pvt_ma1 - pvt_ma2
        factor_raw = get_single_minute_data(factor_raw, trade_stop_time)
        factor = factor_raw.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor




##########
