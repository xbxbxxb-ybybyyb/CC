import numpy as np
from xfactor.BaseFactor import BaseFactor


class IndustriesPBROE(BaseFactor):
    # 因子名称：IndustriesPBROE
    # 计算公式：二级行业内标准化的roe - 二级行业内标准化的pb
    # 因子逻辑：根据剩余收益模型，pb近似roe的线性函数，roe越大，pb也应该越大，因此roe与pb偏离越大的股票越有可能存在套利空间
    depend_data = ['FactorData.Basic_factor.mkt_cap_ard', 'FactorData.WIND_AShareIndustriesClassCITICS',
                   'FactorData.WIND_AShareIncome', 'FactorData.WIND_AShareBalanceSheet']
    financial_lag = 365 * 2

    def calc_single(self, database):
        mkt_cap = database.depend_data['FactorData.Basic_factor.mkt_cap_ard']
        ind = database.depend_data['FactorData.WIND_AShareIndustriesClassCITICS']
        income = database.depend_data['FactorData.WIND_AShareIncome']
        balance = database.depend_data['FactorData.WIND_AShareBalanceSheet']
        stk_code = mkt_cap.columns
        dt = int(mkt_cap.index[-1])
        ind = ind[(ind['ENTRY_DT'].values <= dt) &
                  ((ind['REMOVE_DT'].values >= dt) | ind['REMOVE_DT'].isnull().values)]
        ind = ind.set_index('WIND_CODE')['CITICS_IND_CODE'].reindex(stk_code).str.slice(0, 6)
        income = income[(income['ACTUAL_ANN_DT'].values <= dt) & ((income['STATEMENT_TYPE'].values == 408002000) |
                                                                  (income['STATEMENT_TYPE'].values == 408003000))]
        income = income.sort_values('ACTUAL_ANN_DT').groupby(level=[0, 1]).last()
        profit = income['NET_PROFIT_EXCL_MIN_INT_INC'].unstack().reindex(columns=stk_code).fillna(method='ffill')
        balance = balance[(balance['ACTUAL_ANN_DT'].values <= dt) & ((balance['STATEMENT_TYPE'].values <= 408005000) |
                                                                     (balance['STATEMENT_TYPE'].values == 408050000))]
        balance = balance.sort_values('ACTUAL_ANN_DT').groupby(level=[0, 1]).last()
        equity = balance['TOT_SHRHLDR_EQY_EXCL_MIN_INT'].unstack().reindex(columns=stk_code).fillna(method='ffill')
        equity[equity.values <= 0] = np.nan

        roe = profit.iloc[-1] / equity.iloc[-1]
        roe_ind_mean, roe_ind_std = ind.map(roe.groupby(ind).mean()), ind.map(roe.groupby(ind).std())
        roe = (roe - roe_ind_mean) / roe_ind_std
        roe[roe.abs() > 2] = np.nan
        pb = mkt_cap.iloc[-1] / equity.iloc[-1]
        pb_ind_mean, pb_ind_std = ind.map(pb.groupby(ind).mean()), ind.map(pb.groupby(ind).std())
        pb = (pb - pb_ind_mean) / pb_ind_std
        pb[pb.abs() > 2] = np.nan

        res = roe - pb
        return res
