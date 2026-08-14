import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
from numpy.lib.stride_tricks import as_strided

class factor_volume_resid_std(BaseFactor):
    strategy_name = "neptune"
    factor_name = "volume_resid_std"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "成交量的残差波动率" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80, #注意为正数
         'column': ['pct_chg','volume','mkt_cap_ard']
         }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表

    def rolling_resid_std(self,group):
        # 输入检查（保持不变）
        if not isinstance(group, pd.DataFrame):
            raise TypeError("输入必须为pandas DataFrame类型")
        required_columns = ['volume_mean', 'mmt_volume', 'size_volume', 'volume']
        if not set(required_columns).issubset(group.columns):
            missing_cols = set(required_columns) - set(group.columns)
            raise ValueError(f"缺少必需列: {missing_cols}")
        
        data = group[required_columns].values  # 转为NumPy数组
        n, k = data.shape
        min_window_size = 20
        if n < min_window_size:
            return pd.Series(np.nan, index=group.index)
        
        # 初始化结果数组（与原逻辑一致：前19个位置为NaN）
        result = np.full(n, np.nan, dtype=np.float64)
        
        # 提取特征和目标变量（X为前3列，Y为第4列）
        X_features = data[:, :-1]  # shape: (n, 3)
        Y = data[:, -1]           # shape: (n,)
        
        # 生成滑动窗口（利用NumPy stride技巧，无显式循环）
        window_size = min_window_size
        if window_size > n:
            return pd.Series(result, index=group.index)
        
        # 确保数组连续（stride要求）
        X_reshaped = np.ascontiguousarray(X_features)
        Y_reshaped = np.ascontiguousarray(Y)
        
        # 计算窗口stride（行stride=一行字节数，列stride=一个元素字节数）
        X_stride = (X_reshaped.strides[0], X_reshaped.strides[0], X_reshaped.strides[1])
        Y_stride = (Y_reshaped.strides[0], Y_reshaped.strides[0])
        
        # 生成滑动窗口视图（shape: (n-window_size+1, window_size, *)）
        X_windows = np.lib.stride_tricks.as_strided(
            X_reshaped,
            shape=(n - window_size + 1, window_size, X_reshaped.shape[1]),
            strides=X_stride
        )
        Y_windows = np.lib.stride_tricks.as_strided(
            Y_reshaped,
            shape=(n - window_size + 1, window_size),
            strides=Y_stride
        )
        
        # 向量化处理所有窗口
        for i in range(X_windows.shape[0]):
            window_X = X_windows[i]
            window_Y = Y_windows[i]
            
            # 快速检查缺失值（向量化操作）
            if np.isnan(window_X).any() or np.isnan(window_Y).any():
                continue
            
            # 构建带常数项的设计矩阵
            X = np.hstack((np.ones((window_size, 1)), window_X))  # shape: (20, 4)
            Y = window_Y.reshape(-1, 1)                          # shape: (20, 1)
            
            # 矩阵运算求解OLS（伪逆处理不可逆问题）
            XT_X = X.T @ X
            inv_XT_X = np.linalg.pinv(XT_X)  # 伪逆替代传统求逆
            beta = inv_XT_X @ X.T @ Y
            residuals = Y - X @ beta
            
            # 计算残差标准差（总体标准差，与原代码一致）
            result[i + window_size - 1] = residuals.std(ddof=0)
        
        return pd.Series(result, index=group.index)

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            data = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            data['mmt_20'] = data['pct_chg'].groupby('Ticker').transform(lambda x: x.rolling(20).sum())
            data = data.dropna(subset=['mmt_20'])
            data['group_mmt'] = data['mmt_20'].groupby('dt').transform(lambda x: pd.qcut(x,3,labels=False,duplicates='drop'))
            data['group_size'] = data['mkt_cap_ard'].groupby('dt').transform(lambda x: pd.qcut(x,3,labels=False,duplicates='drop'))
            mmt_volume = (data.groupby(['dt','group_mmt'])['volume'].mean()).groupby('dt').apply(lambda x:x.iloc[2]-x.iloc[0])
            size_volume = (data.groupby(['dt','group_size'])['volume'].mean()).groupby('dt').apply(lambda x:x.iloc[2]-x.iloc[0])

            volume_mean = data['volume'].groupby('dt').mean()
            data['volume_mean'] = data.index.get_level_values(0).map(volume_mean)
            data['size_volume'] = data.index.get_level_values(0).map(size_volume)
            data['mmt_volume'] =  data.index.get_level_values(0).map(mmt_volume)

            data['volume_resid_std'] = data.groupby('Ticker').apply(self.rolling_resid_std).droplevel(0)


            
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = data[[self.factor_name]] # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df

