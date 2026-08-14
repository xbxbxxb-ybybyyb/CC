import pandas as pd
import numpy as np
import warnings
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

warnings.simplefilter(action='ignore', category=FutureWarning)

class factor_zxj_Min_Factor13(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "zxj_Min_Factor13"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"
    factor_explain = "追涨因子"
    zcz_adjusted = "否"
    logic_type = ""
    low_cost = ""
    t_day_data = []

    xdb_data = [
        {
        'name': 'xdb_tick1m_cs', 
        'lag': 3,
    }]

    def pre_calculate_T_N_data(self, database):
        if database.get("skip", False):
            return database

        def cosine_similarity_robust(x, y):
            valid_mask = ~ (np.isnan(x) | np.isnan(y))
            x_valid = x[valid_mask]
            y_valid = y[valid_mask]

            if len(x_valid) == 0:
                return np.nan

            ssq_x = np.sum(x_valid**2)
            ssq_y = np.sum(y_valid**2)

            if ssq_x == 0 or ssq_y == 0:
                return np.nan

            numerator = np.sum(x_valid * y_valid)
            denominator = np.sqrt(ssq_x * ssq_y)

            if denominator == 0:
                return np.nan

            return numerator / denominator

        # ---【核心改进】---
        # 1. 新增一个辅助函数来处理每个分组的因子计算
        def _calculate_chasing_factor_for_group(group, percentile):
            """
            这是一个辅助函数，专门用于处理每个(dt, Ticker)分组的数据。
            它首先计算动态阈值，然后用该阈值筛选数据，最后计算因子值。
            """
            # 步骤 A: 筛选出所有超额收益为正的分钟，用于计算阈值
            positive_returns = group[group['excess_return'] > 0]['excess_return']
            
            # 如果在整个回看窗口内都没有正收益，则无法计算阈值，返回NaN
            if positive_returns.empty:
                return np.nan
                
            # 步骤 B: 计算分位数阈值
            # 我们只关心那些超过了特定百分比的上涨，这才是“显著的”追涨
            threshold = positive_returns.quantile(percentile)
            
            # 步骤 C: 使用新的动态阈值来筛选数据
            strong_chasing_df = group[group['excess_return'] > threshold]
            
            # 如果没有分钟的收益能超过该阈值，说明没有发生显著追涨，返回NaN
            if strong_chasing_df.empty:
                return np.nan
                
            # 步骤 D: 在筛选后的高质量数据上计算余弦相似度
            return cosine_similarity_robust(
                strong_chasing_df['excess_return'].values,
                strong_chasing_df['excess_return_t1'].values
            )


        def calculate_factors_with_percentile_threshold(df_daily, chasing_percentile=0.7):
            """
            针对单日数据，计算全时段、尾盘和偏离因子。
            集成了基于分位数的动态阈值来识别“追涨”行为。

            Args:
                df_daily (pd.DataFrame): 包含(dt, Ticker) MultiIndex的分钟数据。
                chasing_percentile (float): 用于确定追涨行为强度的分位数，范围(0, 1)。
                                            例如0.7代表只将最强的30%的上涨视为“追涨”。

            Returns:
                pd.DataFrame: 包含三个因子值的DataFrame。
            """
            df_daily = df_daily.sort_values(by=['Ticker', 'MDDate', 'MDTime'])
            
            # --- 步骤 1: 计算超额收益率 (与之前相同) ---
            df_daily['minute_return'] = df_daily.groupby('Ticker')['LastPx'].pct_change()
            df_daily.replace([np.inf, -np.inf], np.nan, inplace=True)
            market_median_return = df_daily.groupby(['MDDate', 'MDTime'])['minute_return'].transform('median')
            df_daily['excess_return'] = df_daily['minute_return'] - market_median_return
            
            # --- 步骤 2: 创建t+1时刻数据并清洗 (与之前相同) ---
            df_daily['excess_return_t1'] = df_daily.groupby('Ticker')['excess_return'].shift(-1)
            df_clean = df_daily.dropna(subset=['excess_return', 'excess_return_t1'])
            
            # --- 步骤 3: 计算因子 ---
            # 因子1: 全时段追涨杀跌因子 (保持不变，作为基准)
            factor_all_day = df_clean.groupby(['dt', 'Ticker']).apply(
                lambda x: cosine_similarity_robust(x['excess_return'].values, x['excess_return_t1'].values)
            ).rename('factor_all_day')

            # ---【核心改进】---
            # 2. 对尾盘追涨因子的计算方式进行升级
            
            # 首先，筛选出尾盘时段的数据
            df_late_trading_base = df_clean[df_clean['MDTime'] >= 133100000]
            
            # 然后，对每个(dt, Ticker)分组应用我们新的、更复杂的计算逻辑
            factor_late_trading = df_late_trading_base.groupby(['dt', 'Ticker']).apply(
                _calculate_chasing_factor_for_group,
                percentile=chasing_percentile
            ).rename('factor_late_trading')
            
            # 合并因子
            factors = pd.concat([factor_all_day, factor_late_trading], axis=1)
            
            # 因子3: 尾盘追涨偏离因子 (计算方式不变)
            factors['factor_deviation'] = factors['factor_late_trading'] - factors['factor_all_day']
            
            return factors

        threshold = 0.8
        daily_data = database['xdb_tick1m_cs']
        daily_factors = calculate_factors_with_percentile_threshold(daily_data, threshold)
        daily_factors.rename(columns={'factor_deviation': self.factor_name }, inplace=True)
        database['pre_T_N'] = daily_factors[[self.factor_name]]
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