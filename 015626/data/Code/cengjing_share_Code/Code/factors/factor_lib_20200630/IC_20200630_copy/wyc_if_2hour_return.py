from factor_generator import FactorGenerator
from operators_wyc import *

def rolling_normalize(df,x):
    def normalize(dd):
        a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
        b = (a-0.5)*2
        return b
    return df.rolling(x, min_periods=int(x/2)).apply(normalize)

class wyc_if_2hour_return(FactorGenerator):
    def __init__(self):
        required_columns=['close_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_if_2hour_return, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']

        ifreturn = df['close_if'] / df['close_if'].shift(1) - 1
        factor = mean(ifreturn, 200)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor[factor<0]=0
        return factor