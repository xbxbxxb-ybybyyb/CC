from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 更优波动率的均值
class factor_717_9(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns = ['open', 'high', 'low', 'close', 'amount']
        super(factor_717_9, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]
        opendf = df['open'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        close = df['close'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        high = df['high'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        low = df['low'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        amount = df['amount'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        
        factor = {}
        for stk in close.columns.tolist():
            dfmin = pd.concat([opendf[stk], high[stk], low[stk], close[stk], amount[stk]], axis = 1)
            dfmin.columns = ['open', 'high', 'low', 'close', 'amount']
            if dfmin['amount'].sum() == 0:
                continue
            
            price_data = dfmin[['open', 'high', 'low', 'close']].values.reshape(-1)
            dfmin['std20'] = pd.Series(price_data).rolling(window=20).std().values[3::4]
            dfmin['mean20'] = pd.Series(price_data).rolling(window=20).mean().values[3::4]
            dfmin['super_std'] = (dfmin['std20'] / dfmin['mean20']) ** 2
            
            dfmin['ret'] = dfmin['close'].pct_change()
            dfmin['ret_std'] = dfmin['ret'] / dfmin['super_std']
            
            # 更优波动率
            super_std = dfmin['super_std'].mean()*1e6
            # 收益波动比与更优波动率的比值
            ret_std = dfmin['ret_std'].mean()
            # 收益率与更优波动率的协方差
            sr_cov = dfmin['ret_std'].cov(dfmin['super_std']) * 1e5
            # 更优波动率的波动率
            super_ss = dfmin['super_std'].std()*1e6
            # 当日更优波动率异常高的分钟数
            dfmin['standard'] = dfmin['super_std'].mean() + dfmin['super_std'].std()
            temp = dfmin[dfmin['super_std'] > dfmin['standard']]
            high_ss_num = len(temp)
            # 当日更优波动率异常高的分钟数的收益波动比均值
            high_rs = temp['ret_std'].mean()
            # 当日更优波动率异常高的时段的收益波动比与更优波动率的协方差
            high_cov = temp['ret_std'].cov(temp['super_std'])
            # 当日更优波动率异常高的分钟数成交额占比
            high_amount_ratio = temp['amount'].sum() / dfmin['amount'].sum()
            # 当日更优波动率异常高的分钟数的收益率之和
            high_ret_sum = temp['ret'].sum()
                        
            factor[stk] = [super_std, ret_std, sr_cov, super_ss, high_ss_num, high_rs, high_cov, high_amount_ratio, high_ret_sum]
            
        factor = pd.DataFrame(factor, index = [f'factor_{i}' for i in range(717, 726)]).T
        return factor