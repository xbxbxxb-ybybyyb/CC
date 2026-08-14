import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
from sklearn.linear_model import LinearRegression

class factor_net_profit_ttm_log_pctchg_resid(BaseFactor):
    strategy_name = "neptune"
    factor_name = "net_profit_ttm_log_pctchg_resid"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "使用TTM对数净利润用回归取残差法计算的增长率" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时

    xdb_data = [{
        'name':'xdb_income_cs',
        'lag':8
    }]

    def self_reg_resid(self,df):
        tmp = pd.concat([df,df.groupby('Ticker').shift(1)],axis=1).dropna()
        if tmp.empty:
            # tmp为空时返回空的DataFrame
            return pd.DataFrame()
        tmp.columns = ['y','x']
        result = tmp.groupby('MDDate').apply(lambda x:self.reg_resid(x[['x']],x['y']))

        return result

    def reg_resid(self, x, y):
        tmp = pd.concat([x, y],axis=1).dropna()
        if tmp.empty:
            # tmp为空时返回空的DataFrame
            return pd.DataFrame()
        model = LinearRegression(fit_intercept=True)
        model.fit(tmp.iloc[:, [0]], tmp.iloc[:, 1])
        residuals = tmp.iloc[:, 1] - model.predict(tmp.iloc[:, [0]])
        residuals.name = f'{y.name}_c'
        return residuals.to_frame()

    def quarter_stat_free(self,data,labels):
        cols = ['MDDate'] + labels
        data = data[cols].copy()  # 避免修改原数据

        data.sort_values(by=['Ticker', 'MDDate'], inplace=True)
        for label in labels:
            data[f'{label}_q'] = np.where(data['MDDate'].str[-4:] == '0331',data[label],data[label].diff())
            data[f'{label}_q_log'] = np.sign(data[f'{label}_q']) *np.log(1+abs(data[f'{label}_q']))
            data[f'{label}_ttm'] = data[f'{label}_q'].groupby('Ticker').transform(lambda x: x.rolling(4).sum())
            data[f'{label}_ttm_log'] = data[f'{label}_q_log'].groupby('Ticker').transform(lambda x: x.rolling(4).sum())
        
        cleaned = data.copy()
        cleaned = cleaned.reset_index().set_index(['dt','Ticker','MDDate'])
        for f in cleaned.columns:
            cleaned[f'{f}_pctchg'] = cleaned[f].groupby('Ticker').diff() / abs(cleaned[f].groupby('Ticker').shift(1))
            cleaned[f'{f}_pctchg_resid'] = self.self_reg_resid(cleaned[f])
        
        result = cleaned.reset_index().groupby('Ticker').last()
        date = data.index[0][0]

        return date,result


    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            data = database['xdb_income_cs']
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            labels = ['NET_PROFIT_EXCL_MIN_INT_INC']
            date,daily_result = self.quarter_stat_free(data,labels)

            res = daily_result[['NET_PROFIT_EXCL_MIN_INT_INC_ttm_log_pctchg_resid']]
            res = res.rename(columns={'NET_PROFIT_EXCL_MIN_INT_INC_ttm_log_pctchg_resid':'net_profit_ttm_log_pctchg_resid'})
            res['dt'] = date
            res = res.reset_index().set_index(['dt','Ticker'])

            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = res[[self.factor_name]] # cs要返回df
            return database

    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res
