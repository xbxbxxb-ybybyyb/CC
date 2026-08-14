import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
import math
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_uncover_npcow(BaseFactor):
    strategy_name = "neptune"
    factor_name = "uncover_npcow"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "找到未被过度炒作的净利润高的股票" # 因子逻辑解释
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
       'name': 'xdb_income_cs', # xdb_order1m, xdb_tick1m
       'lag': 12 # 回看日期，N为往前回看1~N天
    }]
      
    
    def calculate_angle_radians(self, x, y):
        # 计算弧度（范围 [-π, π]）
        radian = math.atan2(y, x)
        
        # 将负角度转换为正角度，范围 [0, 2π)
        if radian < 0:
            radian += 2 * math.pi
        
        return radian

    def rho_theta_factor(self,x,y):
        x = x.groupby('dt').apply(lambda x: (x-x.mean())/x.std())
        y = y.groupby('dt').apply(lambda x: (x-x.mean())/x.std())

        rho = np.sqrt(x**2 + y**2)

        tmp = pd.concat([x,y],axis=1)
        tmp.columns = ['x','y']
        theta = tmp.apply(lambda x: self.calculate_angle_radians(x['x'], x['y']),axis=1)

        alpha = np.where((theta>0) & (theta<= 0.5*math.pi),1,
                                np.where((theta>math.pi) & (theta <= 1.5*math.pi),-1,
                                        np.where((theta>1.5 * math.pi)&(theta<=2*math.pi),0.75,0.5)))   

        factor = alpha * np.exp(-abs(theta-0.25*math.pi))*rho

        return factor

    def quarter_stat_free(self,data,labels):
        cols = ['MDDate'] + labels
        data = data[cols].copy()  # 避免修改原数据

        data.sort_values(by=['Ticker', 'MDDate'], inplace=True)
        for label in labels:
            data[f'{label}_q'] = np.where(data['MDDate'].str[-4:] == '0331',data[label],data[label].diff())
            data[f'{label}_q_log'] = np.sign(data[f'{label}_q']) *np.log(1+abs(data[f'{label}_q']))
            data[f'{label}_ttm'] = data[f'{label}_q'].groupby('Ticker').transform(lambda x: x.rolling(4).sum())
            data[f'{label}_ttm_log'] = data[f'{label}_q_log'].groupby('Ticker').transform(lambda x: x.rolling(4).sum())
        
        
        result = data.reset_index().groupby('Ticker').last()
        date = data.index[0][0]

        return date,result

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_income_cs']
        md_data = database['MD_CHINA_STOCK_DAILY_WIND']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        labels = ['NET_PROFIT_EXCL_MIN_INT_INC']
        date,daily_result = self.quarter_stat_free(data,labels)

        res_income = daily_result[['NET_PROFIT_EXCL_MIN_INT_INC_ttm_log']]
        res_income['dt'] = date
        res_income = res_income.reset_index().set_index(['dt','Ticker'])

        res_md = md_data['pct_chg'].groupby('Ticker').transform(lambda x: x.rolling(20).sum()).unstack().iloc[[-1]].stack().reset_index()
        res_md['dt'] = data.index[0][0]
        res_md = res_md.set_index(['dt', 'Ticker'])

        res_income['mmt_20'] = -res_md
        factor = self.rho_theta_factor(res_income['mmt_20'],res_income['NET_PROFIT_EXCL_MIN_INT_INC_ttm_log'])
        factor = factor.groupby('dt',group_keys=False).apply(lambda x: (x-x.mean())/x.std())
        factor = factor.to_frame(self.factor_name)
        # factor['dt'] = date
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