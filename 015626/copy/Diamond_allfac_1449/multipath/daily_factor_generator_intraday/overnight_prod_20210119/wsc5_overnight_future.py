from factor_generator import FactorGenerator
from operators_wsc import *



class wsc5_overnight_future(FactorGenerator):
    def __init__(self):
        super(wsc5_overnight_future, self).__init__(required_columns=['close', 'recent_month_mask', 'close_spot'],
                                                    lookback_bars=2000)

    def on_bar(self, data_dict):
        # 尾盘基差变化情况
        future_close = data_dict['close']
        index_close = data_dict['close_spot']
        future_mask = data_dict['recent_month_mask']

        index_close_1400 = index_close.iloc[index_close.index.indexer_at_time('14:00:00')]
        index_close_1400.index = pd.to_datetime(index_close_1400.index.date)
        index_close_1400.index.name = 'dt'

        close_1400 = future_close[future_mask].sum(axis=1)
        close_1400 = close_1400.iloc[close_1400.index.indexer_at_time('14:00:00')]
        close_1400.index = pd.to_datetime(close_1400.index.date)
        close_1400.index.name = 'dt'

        index_close_1449 = index_close.iloc[index_close.index.indexer_at_time('14:49:00')]
        index_close_1449.index = pd.to_datetime(index_close_1449.index.date)
        index_close_1449.index.name = 'dt'

        close_1449 = future_close[future_mask].sum(axis=1)
        close_1449 = close_1449.iloc[close_1449.index.indexer_at_time('14:49:00')]
        close_1449.index = pd.to_datetime(close_1449.index.date)
        close_1449.index.name = 'dt'
        
        factor_raw = (index_close_1400 - index_close_1449 - close_1400 + close_1449) / index_close_1400
        factor = -ts_rank(factor_raw, 60).to_frame()
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor