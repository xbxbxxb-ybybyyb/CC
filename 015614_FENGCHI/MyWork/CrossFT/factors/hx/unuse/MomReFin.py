from xquant.characteristic import CharacteristicData
from basic.crossUtils import *
from basic.crossConfig import *
from basic.operators import *
from basic.crossFactor import crossFactor
import numpy as np
import bottleneck


class MomReFin(crossFactor):
    cross_group='ReFin'
    cross_func='cross_corr'
    extend_days=20
    author='hx'
    logic='过于20日收益率基于财务关联度加权'
    article='兴业证券-猎金系列之三十二：财报季的财务效应研究和因子构建-211020'
    freq='daily'
    basic_datas = {'daily': ['close_badj'], '30mins': [], '5mins': [], '1min': []}

    def st_factor(self):
        pr = self.database['daily']['close_badj']
        pct = pr / dt_delay(pr, 20) - 1
        pct[~ np.isfinite(pct)] = 0
        return pct[20:, 0]

    def cal_groupst(self):
        factor = self.st_factor()
        roe = fill_quarter2daily_by_issue_date(get_quarter_1factor('roe_yearly')).reindex(
            self.date_range, self.code_list).values
        roa = fill_quarter2daily_by_issue_date(get_quarter_1factor('roa_yearly')).reindex(
            self.date_range, self.code_list).values
        pe = get_daily_1factor('pe_ttm').reindex(self.date_range, self.code_list).values
        ps_ttm = get_daily_1factor('ps_ttm').reindex(self.date_range, self.code_list).values
        ocfps_ttm = get_daily_1factor('ocfps_ttm').reindex(self.date_range, self.code_list).values
        dyr_12 = get_daily_1factor('dyr_12').reindex(self.date_range, self.code_list).values
        s_price_div_dps = get_daily_1factor('s_price_div_dps').reindex(self.date_range, self.code_list).values
        beta_100w = get_daily_1factor('beta_100w').reindex(self.date_range, self.code_list).values
        group = np.r_['0,3', roe, roa, pe, ps_ttm, ocfps_ttm, dyr_12, s_price_div_dps, beta_100w]
        res = np.empty((len(self.date_range), len(self.code_list)))
        for j in range(len(self.date_range)):
            g = pd.DataFrame(group[:, j]).corr().fillna(0).values
            p = factor[j]
            res[j] = g @ p
        res[res == 0] = np.nan
        return res

    def cal_customst(self):
        res = self.cal_groupst()
        return res[:, None]

    def result(self):
        return self.cal_customst()

if __name__=='__main__':
    val1 = cal_factor(numd={'daily':1})