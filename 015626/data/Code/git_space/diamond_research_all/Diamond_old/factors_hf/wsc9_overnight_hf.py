from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
# from help_functions_wsc import replace_zero


    
class wsc9_overnight_hf(FactorGeneratorComplex):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, required_columns=['buy_bigorder_money_500'],
                                                lookback_bars=3000, **kwargs)

    def on_bar(self, hf_data):
        # 当天截止到14:49的主买大单总成交额
        buy_bigorder_money_500 = hf_data['buy_bigorder_money_500']
        
        a_daily = ts_sum(buy_bigorder_money_500.sum(axis=1), 230)
        a_daily = a_daily.iloc[a_daily.index.indexer_at_time('14:49:00')].to_frame()
        a_daily.index = pd.to_datetime(a_daily.index.date)
        a_daily.index.name = 'dt'
        factor = -ts_rank(a_daily, 20)
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor