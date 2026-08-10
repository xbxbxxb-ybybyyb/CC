from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp8_future(FactorGenerator):
    def __init__(self):
        super(wsc_gp8_future, self).__init__(required_columns=['amount', 'recent_month_mask'],
                                             lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170701-20190228，验证时间段：20190301-20190630
        # 因子逻辑：由因子逻辑的Word文档可知，ts_reg_beta也是动量的一种表现方式，另一方面，由gp6可知，交易额的成交额应该是个正向因子，那逻辑就是一个正向因子叠加动量。
        future_amount = data_dict['amount']
        future_mask = data_dict['recent_month_mask']
        amount_std = ts_std(future_amount, 68)
        factor_raw = multi_processing_joblib(df=amount_std, func=ts_reg_beta, n_jobs=-1, d=37)[future_mask].sum(axis=1)
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor