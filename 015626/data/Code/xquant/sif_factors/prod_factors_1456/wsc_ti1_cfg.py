from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_ti1_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti1_cfg, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data_dict):
        # abi技术指标，值越大表示市场越活跃，活动和变化频繁，反之意味着市场缺乏变化
        # 是不是意味着市场越活跃的时候未来上涨的概率就越大，但是如果跌的股票远大于涨的股票，为什么未来还会上涨呢？
        stk_close = data_dict['close_zz500']
        stk_weight = data_dict['weight_zz500']
        stk_ret = ts_delta(stk_close, 1)
        stk_ret[stk_ret>=0] = 1
        stk_ret[stk_ret<0] = -1
        factor_raw = abs((stk_ret*stk_weight).sum(axis=1))
        factor_mean = ts_mean(factor_raw, 60)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor