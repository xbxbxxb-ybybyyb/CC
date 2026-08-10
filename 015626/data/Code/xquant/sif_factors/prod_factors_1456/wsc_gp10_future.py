from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp10_future(FactorGenerator):
    def __init__(self):
        super(wsc_gp10_future, self).__init__(required_columns=['amount', 'close', 'recent_month_mask'],
                                             lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170701-20190228，验证时间段：20190301-20190630
        # 因子逻辑：成交额的波动率*过去一段时间价量背离的最大值，两者都是正向因子，逻辑合理。
        future_amount = data_dict['amount']
        future_close = data_dict['close']
        future_mask = data_dict['recent_month_mask']
        factor_raw = mul2(ts_std(future_amount, 44), ts_argmax(ts_cov(future_amount, neg(future_close), 14), 97))[future_mask].sum(axis=1)
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor