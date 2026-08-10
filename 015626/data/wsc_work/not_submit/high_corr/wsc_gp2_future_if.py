from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp2_future_if(FactorGenerator):
    def __init__(self):
        super(wsc_gp2_future_if, self).__init__(required_columns=['close_if' ,'recent_month_mask'],
                                                lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170101-20180831，验证时间段：20180901-20181231
        # 因子逻辑：close在过去一段时间的位置，动量因子，逻辑简单但是效果较好。
        future_close = data_dict['close_if']
        future_mask = data_dict['recent_month_mask']
        factor_raw = rolling_norm(index_close, 120)
        factor = ts_rank(factor_raw, 1200)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor