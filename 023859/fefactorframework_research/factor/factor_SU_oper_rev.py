import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
from sklearn.linear_model import LinearRegression

class factor_SU_oper_rev(BaseFactor):
    strategy_name = "neptune"
    factor_name = "SU_oper_rev"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "标准化超预期营业收入" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时

    xdb_data = [{
        'name':'xdb_income_cs',
        'lag':16
    }]

    def SUE_stat(self,data,labels):
        cols = ['MDDate'] + labels
        data = data[cols].copy() 

        data.sort_values(by=['Ticker', 'MDDate'], inplace=True)    

        for label in labels:
            data[f'{label}_q'] = np.where(data['MDDate'].str[-4:] == '0331',data[label],data[label].diff())
            data[f'{label}_diff4'] = data[f'{label}_q'].groupby('Ticker').diff(4)
            data[f'{label}_mean'] = data[f'{label}_diff4'].groupby('Ticker').transform(lambda x: x.rolling(8).mean())
            data[f'{label}_std'] = data[f'{label}_diff4'].groupby('Ticker').transform(lambda x: x.rolling(8).std())
            data[f'{label}_E'] = data[f'{label}_q'].groupby('Ticker').shift(4) + data[f'{label}_mean']
            data[f'{label}_SUE'] = (data[f'{label}_q'] - data[f'{label}_E']) / data[f'{label}_std']

        result = data.groupby('Ticker').last()
        result_list = [col for col in result.columns if 'SUE' in col]

        result = result[result_list]
        date = data.index[0][0]

        return date,result


    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            data = database['xdb_income_cs']
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            labels = ['OPER_REV']
            date,daily_result = self.SUE_stat(data,labels)

            res = daily_result[['OPER_REV_SUE']]
            res = res.rename(columns={'OPER_REV_SUE':self.factor_name})
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
