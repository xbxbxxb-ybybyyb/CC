import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
# from help_functions_wsc import replace_zero


    
class wsc6_overnight_hf(FactorGeneratorComplex):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, required_columns=['Bid1AmtMean_500'],
                                                lookback_bars=3000, **kwargs)

    def on_bar(self, hf_data):
        # 当天截止到14:49的一档买盘挂单总额
        Bid1AmtMean_500 = hf_data['Bid1AmtMean_500']

        a_daily = ts_mean(Bid1AmtMean_500.sum(axis=1), 15)
        a_daily = a_daily.iloc[a_daily.index.indexer_at_time('14:49:00')].to_frame()
        a_daily.index = pd.to_datetime(a_daily.index.date)
        a_daily.index.name = 'dt'
        factor = -ts_rank(a_daily, 20)
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor