import pandas as pd 
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
import math

class factor_vol_std_SUOR_rt(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "vol_std_SUOR_rt"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "vol_std因子和SUOR_rt因子的极坐标融合" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    t_day_data = []
    #
    xdb_data = [
        {
       'name': 'xdb_tick1m_cs', # xdb_order1m, xdb_tick1m
       'lag': 3 # 回看日期，N为往前回看1~N天
    },
    {
        'name': 'xdb_income_cs',
        'lag':16        
    }]


    def split_intervals(self,current_intervals, volumes):
        new_intervals = []
        for (s, e) in current_intervals:
            length = e - s + 1  # 时段长度（分钟数）
            if length == 1:
                # 长度为1，不分割
                new_intervals.append((s, e))
            elif length == 2:
                # 长度为2，分割为两个1分钟时段
                new_intervals.append((s, s))
                new_intervals.append((e, e))
            else:
                # 长度≥3，找成交量峰值（排除首尾分钟）
                candidate_ts = list(range(s + 1, e))  # 候选区间：s+1到e-1（左闭右开）
                candidate_vols = [volumes[t] for t in candidate_ts]
                # 取第一个出现的成交量最大值对应的时刻
                max_vol = max(candidate_vols)
                max_idx = candidate_vols.index(max_vol)
                peak_t = candidate_ts[max_idx]
                # 分割为两个时段（峰值归第一个时段）
                new_intervals.append((s, peak_t))
                new_intervals.append((peak_t + 1, e))
                
        return new_intervals

    def vol_emerge_stat(self,df):
        df = df.set_index(np.arange(240))  
        df['VolumeTrade'] = df['VolumeTrade'].fillna(0)       
        closes = df['LastPx'].values  
        volumes = df['VolumeTrade'].values  
        
        # 初始时段：剔除开盘10分钟（0-9），从第10分钟开始
        current_intervals = [(10, 239)]
        # 迭代分割6次,理想情况下会分为64个小区间
        for _ in range(6):
            current_intervals = self.split_intervals(current_intervals, volumes)
        
        returns = []
        for (s, e) in current_intervals:
            if s > e:
                continue  # 跳过无效时段
            close_start = closes[s-1]
            close_end = closes[e]
            if close_start == 0:
                continue 
            ret = (close_end - close_start) / close_start
            returns.append(ret)
        
        if len(returns) == 0:
            return np.nan 
        return np.std(returns) 

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

    def calculate_angle_radians(self, x_series, y_series):
        # 计算初始弧度（范围 [-π, π]）
        radian = np.arctan2(y_series, x_series)
        # 将负弧度转换为 [0, 2π) 范围
        radian = np.where(radian < 0, radian + 2 * np.pi, radian)
        return pd.Series(radian, index=x_series.index)

    def rho_theta_factor(self,x,y):
        x = x.groupby('dt').apply(lambda x: (x-x.mean())/x.std())
        y = y.groupby('dt').apply(lambda x: (x-x.mean())/x.std())

        rho = np.sqrt(x**2 + y**2)

        tmp = pd.concat([x,y],axis=1)
        tmp.columns = ['x','y']
        theta = self.calculate_angle_radians(tmp['x'],tmp['y'])

        alpha = np.where((theta>0) & (theta<= 0.5*math.pi),1,
                                np.where((theta>math.pi) & (theta <= 1.5*math.pi),-1,
                                        np.where((theta>1.5 * math.pi)&(theta<=2*math.pi),0.5,0.5)))   

        factor = alpha * np.exp(-abs(theta-0.25*math.pi))*rho

        return factor
    
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m_cs']
        income_data = database['xdb_income_cs']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        daily_result = data[['VolumeTrade','LastPx','MDDate']].groupby(['Ticker','MDDate'], group_keys=False).apply(self.vol_emerge_stat)
        res_x = daily_result.groupby('Ticker',group_keys=False).std() #Series

        labels = ['OPER_REV']
        date, income_result = self.SUE_stat(income_data,labels) 
        res_y = income_result['OPER_REV_SUE'] #Series

        res_x = pd.concat({date:-res_x},names=['dt'])
        res_y = pd.concat({date:res_y},names=['dt'])

        factor = self.rho_theta_factor(res_x,res_y)
        factor = (factor - factor.mean()) / factor.std()

        res = factor.to_frame(name=self.factor_name)

        # -------------------------------------------------------------------------------------------------------------------
        database['pre_T_N'] = res[[self.factor_name]]
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
