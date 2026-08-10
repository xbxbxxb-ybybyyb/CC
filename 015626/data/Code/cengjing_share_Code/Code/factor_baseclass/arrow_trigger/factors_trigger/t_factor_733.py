from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 孤雁出群
class t_factor_733(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['transaction']
        super(t_factor_733, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        amount_list = []
        retdf_list = []
        for stk in df['universe']:
            data = df['transaction'][stk]
            data = data[(data.TradeType == 0) & (data.TradePrice > 0)].set_index('dt')

            dfmin = data.resample('1min').agg({'TradePrice':['first','last'], 'TradeMoney':'sum'})
            dfmin.columns =  ['open', 'close', 'amount']
            dfmin = dfmin.between_time('930', '1456').dropna(subset = ['open'])
            dfmin[['open', 'close']] = dfmin[['open', 'close']].fillna(method = 'ffill')
            
            amount = dfmin[['amount']]
            amount.columns = [stk]
            amount_list.append(amount)
            
            dfmin['ret'] = dfmin['close'].pct_change()
            retdf_list.append(dfmin['ret'])

        retdf = pd.concat(retdf_list, axis = 1)
        ret_std = retdf.std(axis = 1)
        low_ret_std = ret_std[ret_std < ret_std.mean()]

        amount_all = pd.concat(amount_list, axis = 1).reindex(low_ret_std.index)

        if len(amount_all) > 1:
            factor = ((amount_all.corr(method = 'pearson').abs().sum(axis = 1) - 1) / (len(amount_all) - 1)).to_frame()
            factor.columns = [self.__class__.__name__]
        else:
            factor = pd.DataFrame([np.nan] * len(df['universe']), index = df['universe'], columns = [self.__class__.__name__])
        
        return factor