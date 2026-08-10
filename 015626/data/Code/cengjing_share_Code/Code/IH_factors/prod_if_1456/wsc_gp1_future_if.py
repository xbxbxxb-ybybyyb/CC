from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp1_future_if(FactorGenerator):
    def __init__(self):
        super(wsc_gp1_future_if, self).__init__(required_columns=['low_if' ,'amount_if', 'position_if', 'recent_month_mask'],
                                                lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170101-20180831，验证时间段：20180901-20181231
        # 因子逻辑：第一部分是low在最近一段时间的位置，属于动量；第二部分是amount和position的相关系数，两者都很大可能是持仓和交易额齐飞，看涨，两者都很小可能是反弹的预兆，看涨，如果这个逻辑也能成立的话这部分也是动量。
        # 测了一下，两部分分别作为单因子表现也都还可以，尤其是前者，可以作为单因子入库，但是都不如叠加之后表现好。
        future_low = data_dict['low_if']
        future_amount = data_dict['amount_if']
        future_position = data_dict['position_if']
        future_mask = data_dict['recent_month_mask']
        factor_raw = max2(rolling_norm(future_low, 115)[future_mask].sum(axis=1), ts_corr(future_amount, future_position, 90)[future_mask].sum(axis=1))
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor