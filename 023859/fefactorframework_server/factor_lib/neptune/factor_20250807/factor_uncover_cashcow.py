import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
import math
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_uncover_cashcow(BaseFactor):
    strategy_name = "neptune"
    factor_name = "uncover_cashcow"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "找到未被过度炒作的现金牛股票" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    t_day_data = []
    #
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 30,  # 注意为正数
         'column': ['pct_chg']
         }]
    t_1_factor_data_types = ['MD']
    xdb_data = [
        {
       'name': 'xdb_cashflow_cs', # xdb_order1m, xdb_tick1m
       'lag': 12 # 回看日期，N为往前回看1~N天
    }]
      
    
    def calculate_angle_radians(self, x, y):
        # 计算弧度（范围 [-π, π]）
        radian = math.atan2(y, x)
        
        # 将负角度转换为正角度，范围 [0, 2π)
        if radian < 0:
            radian += 2 * math.pi
        
        return radian

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_cashflow_cs']
        md_data = database['MD_CHINA_STOCK_DAILY_WIND']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        labels = ['NET_CASH_FLOWS_OPER_ACT', 'CASH_PAY_ACQ_CONST_FIOLTA']
        cols = ['MDDate'] + labels
        data = data[cols].copy() 
        data.sort_values(by=['Ticker', 'MDDate'], inplace=True)
        annual_data = data[data['MDDate'].str[-4:] == '1231']
        annual_data.loc[:,'MDDate'] = (annual_data.loc[:,'MDDate'].astype(int) - 10000).astype(str)

        annual_data.columns = ['MDDate'] + [f'{label}_last_annual' for label in labels]

        data = pd.merge(data,annual_data,on=['dt','Ticker','MDDate'],how='left')
        data = data.groupby('Ticker').fillna(method='bfill')
        for label in labels:
            data[f'{label}_shift4'] = data.groupby('Ticker')[label].shift(4)  # 四季度前同期数据
            data[f'{label}_ttm'] = data[label] + data[f'{label}_last_annual'] - data[f'{label}_shift4']
        data['free_cash_flow'] = data['NET_CASH_FLOWS_OPER_ACT_ttm'] - data['CASH_PAY_ACQ_CONST_FIOLTA_ttm']

        ttm_data = data.groupby('Ticker').last()

        cash_flow = ttm_data[['free_cash_flow']].reset_index()
        cash_flow['dt'] = data.index[0][0]
        cash_flow = cash_flow.set_index(['dt','Ticker'])

        res_md = md_data.groupby('Ticker').transform(lambda x:x.rolling(20).sum()).unstack().iloc[[-1]].stack().reset_index()
        res_md['dt'] = data.index[0][0]
        res_md = res_md.set_index(['dt', 'Ticker'])
        
        cash_flow['mmt_20'] = res_md
        cash_flow['mmt_20'] = cash_flow['mmt_20'].groupby('dt').apply(lambda x: (x.mean()-x)/x.std())
        cash_flow['free_cash_flow'] = cash_flow['free_cash_flow'].groupby('dt').apply(lambda x: (x-x.mean())/x.std())

        cash_flow['rho'] = np.sqrt(cash_flow['free_cash_flow']**2 + cash_flow['mmt_20']**2)
        cash_flow['theta'] = cash_flow.apply(lambda x: self.calculate_angle_radians(x['mmt_20'], x['free_cash_flow']),axis=1)

        cash_flow['alpha'] = np.where((cash_flow['theta']>0) & (cash_flow['theta']<= 0.5*math.pi),1,
                            np.where((cash_flow['theta']>math.pi) & (cash_flow['theta'] <= 1.5*math.pi),-1,
                                    np.where((cash_flow['theta']>1.5 * math.pi)&(cash_flow['theta']<=2*math.pi),0.75,0.5)))   
        
        factor = cash_flow['alpha'] * np.exp(-abs(cash_flow['theta']-0.25*math.pi))*cash_flow['rho']
        factor = factor.groupby('dt',group_keys=False).apply(lambda x: (x-x.mean())/x.std())
        factor = factor.to_frame(self.factor_name)
        # factor['dt'] = data.index[0][0]
        # factor = factor.reset_index().set_index(['dt','Ticker'])



        # -------------------------------------------------------------------------------------------------------------------
        database['pre_T_N'] = factor[[self.factor_name]]
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