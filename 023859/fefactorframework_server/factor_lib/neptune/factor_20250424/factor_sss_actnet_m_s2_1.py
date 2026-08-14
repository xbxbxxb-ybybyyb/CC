# h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

def np_regression_res(Y,X):
    res=np.full(Y.shape,np.nan)
    for i in range(len(Y)):
        y=Y[i,:]
        x=X[[i],:].T
        data=np.concatenate([y.reshape((len(y), 1)), x], axis=1)
        ind=~(np.isnan(data).any(axis=1))
        y=y[ind]
        x=x[ind]
        if len(y)>10:
            x = np.concatenate([np.ones((len(x), 1)), x], axis=1)
            param = np.dot(np.linalg.inv(np.dot(np.transpose(x), x)), np.dot(np.transpose(x), y))
            resid=(np.dot(x, param) - y)
            res[i,ind]=resid
    return res

class factor_sss_actnet_m_s2_1(BaseFactor):
    strategy_name = "neptune"
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    factor_period = int(factor_name.split('_')[-1])
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "sss"  # 开发人员姓名
    factor_explain = "资金流入比例因子" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    t_day_data = []
    t_1_factor_data = [{'name': 'MD',
                        'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
                        'lag': factor_period+5,
                        'column': ['amt','pct_chg']},
                       {'name': 'AShareMoneyFlow',
                        'path': '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5',
                        'lag': factor_period + 5,
                        'column': ['BUY_VALUE_MED_ORDER_ACT', 'SELL_VALUE_MED_ORDER_ACT']},
                       ]
    t_1_factor_data_types = ['MD','AShareMoneyFlow'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        factor_name=self.factor_name
        factor_period = self.factor_period
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            md = database['MD']

            mf = database['AShareMoneyFlow']
            mf['net']=mf['BUY_VALUE_MED_ORDER_ACT']-mf['SELL_VALUE_MED_ORDER_ACT']
            mf['sum']=mf['BUY_VALUE_MED_ORDER_ACT']+mf['SELL_VALUE_MED_ORDER_ACT']
            fenzi = mf['net'].unstack().rolling(factor_period, min_periods=1).sum()
            fenmu = mf['sum'].unstack().rolling(factor_period, min_periods=1).sum()
            fenzi[fenzi.abs() < 1] = 0
            fenmu[fenmu.abs() < 1] = 0
            flow = fenzi / fenmu.replace(0,np.nan)
            flow[flow > 1] = 1
            flow[flow < -1] = -1

            md.loc[md['amt']==0,'pct_chg']=np.nan
            pct = md['pct_chg'].clip(lower=-10,upper=10).unstack().rolling(factor_period, min_periods=1).mean()
            col_list = [col for col in flow.columns if col in pct.columns]
            flow, pct = flow[col_list], pct[col_list]
            ratio = pd.DataFrame(np_regression_res(flow.values, pct.values), index=flow.index, columns=flow.columns)

            df = pd.DataFrame(ratio.stack())
            df.columns = [factor_name]
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
