from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime, math
import numpy as np
import bottleneck as bk
import pandas as pd
# 开源3 聪明钱因子
class factor_736_5(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction']
        super(factor_736_5, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['transaction'][stk]
            data = data[data.TradeType == 0].set_index('dt')

            dfmin = data.resample('1min').agg({'TradePrice':['first','max','min','last'], 'TradeQty':'sum', 'TradeMoney':'sum'})
            dfmin.columns =  ['open', 'high', 'low', 'close', 'volume', 'amount']
            dfmin = dfmin.between_time('930', '1456').dropna(subset = ['open'])
            dfmin[['open', 'high', 'low', 'close']] = dfmin[['open', 'high', 'low', 'close']].fillna(method = 'ffill')
            dfmin['volume'] = dfmin['volume'].fillna(0)

            dfmin['ret'] = dfmin['close'].pct_change()
            dfmin['s1'] = abs(dfmin['ret']) / (dfmin['volume'] ** 0.5)
            dfmin['s2'] = abs(dfmin['ret']) / (dfmin['volume'] ** 0.1)
            dfmin['s3'] = abs(dfmin['ret']).rank() + dfmin['volume'].rank()
            dfmin['s4'] = abs(dfmin['ret']) / dfmin['volume'].replace(0, np.nan).apply(lambda x:math.log(x, 10))
            dfmin['s5'] = dfmin['volume']

            vwap = dfmin['amount'].sum() / dfmin['volume'].sum()
            volume_t = dfmin['volume'].sum() * 0.2

            f_list = []
            for k in ['s1','s2','s3','s4', 's5']:
                temp = dfmin.sort_values(by = k, ascending = False)
                temp['volume_cs'] = temp['volume'].cumsum().shift(1).fillna(method = 'bfill')
                temp = temp[temp['volume_cs'] <= volume_t]
                f_list.append((temp['amount'].sum() / temp['volume'].sum() / vwap - 1) * 1000)

            factor[stk] = f_list

        factor = pd.DataFrame(factor, index = ['factor_736_0', 'factor_736_1', 'factor_736_2', 'factor_736_3', 'factor_736_4']).T

        return factor