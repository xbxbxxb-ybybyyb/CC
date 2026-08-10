from factor_generator import FactorGenerator
from operators_wsc import *



class wsc_1_spot_if(FactorGenerator):
    def __init__(self):
        super(wsc_1_spot_if, self).__init__(required_columns=['close_spot_if', 'volume_spot_if'],
                                            lookback_bars=2000)

    def on_bar(self, data):
        # 长江金工高频因子2：结构化反转因子
        # 因子主体由三部分组成：对数收益率，成交量倒数和收益波动率
        # 对数收益率代表动量，成交量倒数的逻辑是当多空力量悬殊时，股价会以很小的成交量迅速到达一个合理价位（这部分内容见研报），收益波动率的逻辑是只有当市场成交活跃时，趋势才强
        index_close = data['close_spot_if']
        index_volume = data['volume_spot_if']
        ret = ts_pct_change(index_close, 1)
        log_ret = log(ret+1)
        ret_std = ts_std(ret, 15)
        log_ret_weight = log_ret / index_volume * ret_std
        factor_raw = ts_sum(log_ret_weight, 120)
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor
