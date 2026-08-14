import pandas as pd
import numpy as np
import math
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_rho_theta_PV(BaseFactor):
    strategy_name = "neptune"
    factor_name = "rho_theta_PV"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "极坐标价量融合因子" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 30, #注意为正数
         'column': ['adjfactor','close','volume']
         }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            df_ori['adj_close'] = df_ori['adjfactor'] * df_ori['close']
            P = df_ori['adj_close'].groupby('Ticker',group_keys=False).diff(20) / df_ori['adj_close']
            V = (df_ori['volume'].groupby('Ticker',group_keys=False).diff(20) / df_ori['volume']).replace([np.inf,-np.inf],np.nan)

            P = P.groupby('dt',group_keys=False).apply(lambda x: (x-x.mean())/x.std())
            V = V.groupby('dt',group_keys=False).apply(lambda x: (x-x.mean())/x.std())

            rho = np.sqrt(P**2 + V**2)

            tmp = pd.concat([P,V],axis=1)
            tmp.columns = ['P','V']
            theta = tmp.apply(lambda x: self.calculate_angle_radians(x['P'], x['V']),axis=1)

            alpha = np.where((theta>0) & (theta<= 0.5*math.pi),1,
                                np.where((theta>math.pi) & (theta <= 1.5*math.pi),-1,
                                        np.where((theta>1.5 * math.pi)&(theta<=2*math.pi),0.75,0.5)))   
            
            factor = alpha * np.exp(-abs(theta-0.25*math.pi))*rho
            factor = factor.groupby('dt',group_keys=False).apply(lambda x: (x-x.mean())/x.std())
            df_ori[self.factor_name] = factor

            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df_ori[[self.factor_name]] # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df

    def calculate_angle_radians(self, x, y):
        # 计算弧度（范围 [-π, π]）
        radian = math.atan2(y, x)
        
        # 将负角度转换为正角度，范围 [0, 2π)
        if radian < 0:
            radian += 2 * math.pi
        
        return radian
