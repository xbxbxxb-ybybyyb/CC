from xfactor.BaseFactor import BaseFactor


class IndustryReverse(BaseFactor):
    # 因子名称：IndustryReverse
    # 计算公式：股票所在行业（中信一级）平均收益率 - 股票收益率，取15天Sharpe
    # 因子逻辑：股票收益率均值回复到行业平均水平
    depend_data = ["FactorData.Basic_factor.pct_chg", "FactorData.Basic_factor.citics_indcode1"]
    reform_window = 15

    def calc_single(self, database):
        r = database.depend_data['FactorData.Basic_factor.pct_chg']
        ind_3 = database.depend_data['FactorData.Basic_factor.citics_indcode1']
        ind_3 = ind_3.iloc[-1, :]
        r = r.iloc[-1, :]
        r_ind_3 = ind_3.map(r.groupby(ind_3).mean())
        res = r_ind_3 - r
        return res

    def reform(self, temp_result):
        alpha = temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
        return alpha
