import pandas as pd
from overnight.factor_generator import FactorGenerator
from operators_wsc import *
# from help_functions_wsc import replace_zero


    
class wsc6_overnight_hf(FactorGenerator):
    def __init__(self, *args, ts_norm_bars=0, **kwargs):
        super().__init__(*args, required_columns=['Bid1AmtMean_500'],
                                                 ts_norm_bars=20, **kwargs)

    def on_bar(self, hf_data):
        # 当天截止到14:49的一档买盘挂单总额
        Bid1AmtMean_500 = hf_data['Bid1AmtMean_500']

        a_daily = ts_mean(Bid1AmtMean_500.sum(axis=1), 15)
        a_daily = a_daily.iloc[a_daily.index.indexer_at_time('14:49:00')].to_frame() * -1
        a_daily.index = pd.to_datetime(a_daily.index.date)
        a_daily.index.name = 'dt'
        # factor = -ts_rank(a_daily, 20)
        # factor[factor<=0] = np.nan
        factor = a_daily

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor