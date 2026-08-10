from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp4_future(FactorGenerator):
    def __init__(self):
        super(wsc_gp4_future, self).__init__(required_columns=['amount', 'recent_month_mask'],
                                         lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170701-20190228，验证时间段：20190301-20190630
        # 因子逻辑：过去30分钟amount的最大值的线性外推，amount越大收益越高，逻辑合理。
        future_amount = data_dict['amount']
        future_mask = data_dict['recent_month_mask']
        amount_max = ts_max(future_amount, 39)
        factor_raw = multi_processing_joblib(df=amount_max, func=ts_pred, n_jobs=-1, d=64)[future_mask].sum(axis=1)
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor