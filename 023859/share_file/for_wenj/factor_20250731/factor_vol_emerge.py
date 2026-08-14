import pandas as pd 
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_vol_emerge(BaseFactor):
    strategy_name = "neptune"
    factor_name = "vol_emerge"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "根据交易量对每日的时段进行重新划分，计算各划分时段收益率的标准差" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    t_day_data = []
    #
    xdb_data = [
        {
       'name': 'xdb_tick1m_cs', # xdb_order1m, xdb_tick1m
       'lag': 3 # 回看日期，N为往前回看1~N天
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
        df = df.set_index(np.arange(min(240, len(df))))
        df['VolumeTrade'] = df['VolumeTrade'].fillna(0)       
        closes = df['LastPx'].values  
        volumes = df['VolumeTrade'].values  
        
        # 初始时段：剔除开盘10分钟（0-9），从第10分钟开始
        current_intervals = [(10, min(240,len(df))-1)] #TODO 有时候行情数据比较脏
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

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m_cs']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        daily_result = data[['VolumeTrade','LastPx','MDDate']].groupby(['Ticker','MDDate'], group_keys=False).apply(self.vol_emerge_stat)
        res = daily_result.groupby('Ticker',group_keys=False).std()
        res = res.to_frame(name=self.factor_name)
        res = pd.concat({data.index[0][0]: res}, names=['dt'])
        # res = res.groupby('dt',group_keys=False).apply(lambda x:(x-x.mean())/x.std())
        # res = res.to_frame(name=self.factor_name)
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