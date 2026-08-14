import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_neptunelong_longterm_20250911_abnormal_yjl8(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "qyh_neptunelong_longterm_20250911_abnormal_yjl8"
    fill_na_value = ('industry_median',0)
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "财务：异常应计量-应计量对销售变化和固定资产的回归残差" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "长周期-财务因子-资产类" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    xdb_data = [
        {
       'name': 'xdb_balancesheet_cs', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 16
    },
        {
       'name': 'xdb_cashflow_cs', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 16
    },
        {
       'name': 'xdb_income_cs', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 16
    },
    ]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            # finance
            df_balancesheet = database['xdb_balancesheet_cs']
            df_balancesheet['单季度平均资产总额'] = df_balancesheet['TOT_ASSETS'].groupby(['dt','Ticker']).apply(lambda x : x.tail(2).mean())
            df_balancesheet['流动负债diff'] = df_balancesheet['TOT_CUR_LIAB'].groupby(['dt', 'Ticker']).diff()
            df_balancesheet['流动资产diff'] = df_balancesheet['TOT_CUR_ASSETS'].groupby(['dt', 'Ticker']).diff()
            df_cf = database['xdb_cashflow_cs']
            df_cf['折旧摊销总额'] = df_cf['DEPR_FA_COGA_DPBA'] + df_cf['AMORT_INTANG_ASSETS']
            df_income = database['xdb_income_cs']
            col = 'OPER_REV'
            df_income[f'{col}_diff'] = df_income.groupby(['dt', 'Ticker'])[col].diff()
            def get_report_period(x):
                month = x[4:6]
                if month == '03':
                    return 1
                elif month == '06':
                    return 2
                elif month == '09':
                    return 3
                elif month == '12':
                    return 4
                else:
                    return 5
            df_income['report_period'] = df_income['MDDate'].apply(get_report_period)
            df_income.loc[df_income['report_period'] == 1, f'{col}_diff'] = df_income.loc[
                df_income['report_period'] == 1, col] # 单季度处理
            ##
            res1 = (df_balancesheet['单季度平均资产总额']).groupby(['dt','Ticker'])\
                .apply(lambda x : x.tail(8).mean()).to_frame(name='单季度平均资产总额')
            res2 = (df_cf[f'折旧摊销总额']).groupby(['dt','Ticker'])\
                .apply(lambda x : x.tail(8).mean()).to_frame(name='折旧摊销总额')
            res3 = (df_balancesheet[f'流动负债diff'].fillna(0) + df_balancesheet[f'流动资产diff'].fillna(0)).groupby(['dt','Ticker'])\
                .apply(lambda x : x.tail(8).mean()).to_frame(name='流动资产与负债diff')
            res4 = (df_balancesheet['FIX_ASSETS']).groupby(['dt','Ticker'])\
                .apply(lambda x : x.tail(8).mean()).to_frame(name='固定资产')
            res5 = (df_income['OPER_REV_diff']).groupby(['dt','Ticker'])\
                .apply(lambda x : x.tail(8).mean()).to_frame(name='营业收入diff')
            res = pd.concat([res1,res2,res3,res4,res5],axis=1)
            res['应计量'] = (res['折旧摊销总额'].fillna(0) + res['流动资产与负债diff'].fillna(0)) / res['单季度平均资产总额'].replace(0,np.nan)
            res['相对固定资产'] = res['固定资产'] / res['单季度平均资产总额']
            res['相对营收diff'] = res['营业收入diff'] / res['单季度平均资产总额']
            from sklearn.linear_model import LinearRegression
            res = res[['相对营收diff','相对固定资产','应计量']].dropna()
            X = res[['相对营收diff', '相对固定资产']]
            y = res['应计量']
            model = LinearRegression(fit_intercept=True).fit(X, y)
            res[self.factor_name] = y - model.predict(X) # 异常应计量

            database['pre_T_N'] = res[[self.factor_name]] # cs要返回df
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res
