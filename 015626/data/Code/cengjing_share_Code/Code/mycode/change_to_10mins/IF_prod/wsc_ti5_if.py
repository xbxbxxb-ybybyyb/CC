from factor_generator import FactorGenerator
from operators_wsc import *



class wsc_ti5_if(FactorGenerator):
    def __init__(self):
        super(wsc_ti5_if, self).__init__(required_columns=['close_if', 'recent_month_mask'],
                                         lookback_bars=2000)

    def on_bar(self, data_dict):
        # 布林带修正后的收益率
        index_close = data_dict['close_if']
        future_mask = data_dict['recent_month_mask']
        close_mean = ts_mean(index_close, 40)
        close_std = ts_std(index_close, 40)
        factor_raw = ts_pct_change(close_mean + 2 * close_std, 40).replace([-np.inf, np.inf], np.nan)
        factor = ts_rank(factor_raw, 1200)
        factor = factor[future_mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor