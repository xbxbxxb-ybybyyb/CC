from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd


class FR20d_1001(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", 
                   "FactorData.Basic_factor.close", 
                  "FactorData.Basic_factor.turn", 
                  "FactorData.Basic_factor.adjfactor",
                  "FactorData.Basic_factor.is_valid", ]
    lag = 20
    minute_lag = 20

    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']
        turn = database.depend_data['FactorData.Basic_factor.turn']
        close = database.depend_data['FactorData.Basic_factor.close']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        turn_former = turn.shift(1).iloc[-20:]
        close_minute['timeindex'] = [e.strftime('%H%M') for e in close_minute.index]
        close_1001 = close_minute[close_minute['timeindex'] == '1000']
        close_1001.drop(columns=['timeindex'],inplace=True)
        close_1001.index = close.index
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns)
        close_1001 = close_1001[valid]
        close = close[valid]

        re = pd.DataFrame((close_1001*adjfactor).values/((close*adjfactor).shift(1)).values-1,
            index=adjfactor.index,columns=adjfactor.columns).iloc[-20:] 
        turn_former = turn_former.reindex(re.columns, axis=1)
        condi = pd.DataFrame(re.values<0, index=re.index, columns=re.columns)
        FR = Util.array_coef(turn_former[condi], re.abs())
        return -FR


    