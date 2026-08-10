from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp6_future(FactorGenerator):
    def __init__(self):
        super(wsc_gp6_future, self).__init__(required_columns=['volume', 'recent_month_mask'],
                                             lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170701-20190228，验证时间段：20190301-20190630
        # 因子逻辑：成交量的波动率，如果逻辑成立的话就是成交量波动越大，未来收益越高
        future_volume = data_dict['volume']
        future_mask = data_dict['recent_month_mask']
        factor_raw = ts_std(future_volume, 22)[future_mask].sum(axis=1)
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor