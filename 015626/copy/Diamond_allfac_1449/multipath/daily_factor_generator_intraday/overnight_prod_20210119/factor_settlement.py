from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import replace_zero



class factor_settlement(FactorGenerator):
    def __init__(self):
        super().__init__(required_columns=['close', 'recent_month_mask', 'amount', 'volume'],
                         lookback_bars=2000)

    def on_bar(self, data_dict):
        # 结算价与收盘价之比
        future_close = data_dict['close']
        future_mask = data_dict['recent_month_mask']
        future_amount = data_dict['amount']
        future_volume = data_dict['volume']
        
        amount_sum = ts_sum(future_amount, 60)
        volume_sum = ts_sum(future_volume, 60)
        vwap_60 = (amount_sum / volume_sum)[future_mask].sum(axis=1)
        vwap_60 = vwap_60.iloc[vwap_60.index.indexer_at_time('14:49:00')].to_frame()
        vwap_60.index = pd.to_datetime(vwap_60.index.date)
        vwap_60.index.name = 'dt'

        close_1449 = future_close[future_mask].sum(axis=1)
        close_1449 = close_1449.iloc[close_1449.index.indexer_at_time('14:49:00')].to_frame()
        close_1449.index = pd.to_datetime(close_1449.index.date)
        close_1449.index.name = 'dt'

        factor = replace_zero((vwap_60/200) / close_1449)
        factor[factor<1.0015] = 0
        factor[factor>0] = 1
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor