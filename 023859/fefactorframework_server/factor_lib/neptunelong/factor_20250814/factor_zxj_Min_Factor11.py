import pandas as pd
import numpy as np
import warnings
import statsmodels.api as sm
from datetime import time as datetime_time
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

warnings.simplefilter(action='ignore', category=FutureWarning)

class factor_zxj_Min_Factor11(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "zxj_Min_Factor11"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"
    factor_explain = "TGD"
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

        def calculate_daily_factors(df, a_date):
           
            # --- 1. 数据预处理 ---
            df = df.copy()

            # 计算分钟收益率
            df['minute_return'] = df.groupby('Ticker')['LastPx'].pct_change().fillna(0)

            # 将MDTime映射到1-240的时间戳 (FIXED)
            def map_time_to_index(md_time):
                """
                修复了时间解析逻辑，使其更健壮。
                """
                try:
                    # 假定时间的格式为 HMMSS... 或 HHMMSS...
                    # 先提取出代表时分秒的部分，如 93000 or 140500
                    time_val = md_time // 1000
                    h = time_val // 10000
                    m = (time_val // 100) % 100
                    s = time_val % 100

                    # 在创建time对象前，先校验数值范围
                    if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59):
                        return np.nan

                    t = datetime_time(h, m, s)

                    if datetime_time(9, 31) <= t <= datetime_time(11, 30):
                        return (t.hour - 9) * 60 + (t.minute - 31) + 1
                    elif datetime_time(13, 1) <= t <= datetime_time(15, 0):
                        return (t.hour - 13) * 60 + (t.minute - 1) + 121
                    else:
                        return np.nan # 非交易时间
                except (ValueError, TypeError):
                    # 如果md_time不是数字或有其他问题，返回nan
                    return np.nan


            df['time_index'] = df['MDTime'].apply(map_time_to_index)
            df.dropna(subset=['time_index'], inplace=True) # 去除非交易时间的bar

            # --- 2. 计算涨跌幅时间重心 (Gu, Gd) ---
            df['up_move'] = df['minute_return'].clip(lower=0)
            df['down_move'] = df['minute_return'].clip(upper=0).abs()

            df['up_weighted_time'] = df['up_move'] * df['time_index']
            df['down_weighted_time'] = df['down_move'] * df['time_index']

            grouped = df.groupby('Ticker')

            # 计算加权时间和权重和
            up_weighted_time_sum = grouped['up_weighted_time'].sum()
            up_move_sum = grouped['up_move'].sum()
            down_weighted_time_sum = grouped['down_weighted_time'].sum()
            down_move_sum = grouped['down_move'].sum()

            # 计算Gu和Gd, 防止除以0
            Gu = (up_weighted_time_sum / up_move_sum).replace([np.inf, -np.inf], np.nan)
            Gd = (down_weighted_time_sum / down_move_sum).replace([np.inf, -np.inf], np.nan)

            factor_df = pd.DataFrame({'Gu': Gu, 'Gd': Gd})

            # F1: 跌幅时间重心因子
            factor_df['factor_Gd'] = factor_df['Gd']

            # --- 3. 计算跌幅时间重心偏离因子 ---
            temp_df = factor_df[['Gu', 'Gd']].dropna()
            if len(temp_df) > 1:
                X = sm.add_constant(temp_df['Gu'])
                y = temp_df['Gd']
                model = sm.OLS(y, X, missing='drop').fit()
                factor_df['factor_Gd_deviation'] = model.resid

            # --- 4. 计算TGD因子 ---
            # 4.1 计算干扰因子
            # 隔夜收益率
            first_minute = df.groupby('Ticker').first()
            R_overnight = (first_minute['OpenPx'] / first_minute['pre_close']) - 1

            # 盘初收益率 R1, R2
            df_r1 = df[df['MDTime'] <= 100000000] # 09:31-10:00
            R1 = df_r1.groupby('Ticker')['minute_return'].sum()

            df_r2 = df[(df['MDTime'] > 100000000) & (df['MDTime'] <= 103000000)] # 10:01-10:30
            R2 = df_r2.groupby('Ticker')['minute_return'].sum()

            # 平均涨跌幅
            R_u_mean = grouped['up_move'].sum() / grouped.apply(lambda x: (x['up_move'] > 0).sum()).replace(0, np.nan)
            R_d_mean = grouped['down_move'].sum() / grouped.apply(lambda x: (x['down_move'] > 0).sum()).replace(0, np.nan)

            # 合并干扰因子
            interference_factors = pd.DataFrame({
                'R_overnight': R_overnight,
                'R1': R1,
                'R2': R2,
                'R_u_mean': R_u_mean,
                'R_d_mean': R_d_mean
            }).fillna(0) # 用0填充缺失的收益率和均值

            factor_df = factor_df.join(interference_factors)

            # 4.2 TGD回归
            temp_tgd_df = factor_df[['Gu', 'Gd', 'R_u_mean', 'R_d_mean', 'R1', 'R2', 'R_overnight']].dropna()

            if len(temp_tgd_df) > 5: # 确保有足够的数据点进行回归
                # 回归1: Gu
                X_u = sm.add_constant(temp_tgd_df[['R_u_mean', 'R1', 'R2', 'R_overnight']])
                model_u = sm.OLS(temp_tgd_df['Gu'], X_u, missing='drop').fit()
                epsilon_u = model_u.resid

                # 回归2: Gd
                X_d = sm.add_constant(temp_tgd_df[['R_d_mean', 'R1', 'R2', 'R_overnight']])
                model_d = sm.OLS(temp_tgd_df['Gd'], X_d, missing='drop').fit()
                epsilon_d = model_d.resid

                # 回归3: TGD
                X_final = sm.add_constant(epsilon_u)
                model_final = sm.OLS(epsilon_d, X_final, missing='drop').fit()
                factor_df['factor_TGD'] = model_final.resid

            # --- 5. 计算合成因子 ---
            if 'factor_TGD' in factor_df.columns:
                # 5.1 计算SKEW因子
                factor_df['factor_SKEW'] = grouped['minute_return'].skew()

                # 5.2 合成
                temp_composite_df = factor_df[['factor_TGD', 'factor_SKEW']].dropna()
                if len(temp_composite_df) > 1:
                    rank_tgd = temp_composite_df['factor_TGD'].rank(pct=True)
                    rank_skew = temp_composite_df['factor_SKEW'].rank(pct=True)
                    factor_df['factor_Combined'] = rank_tgd + rank_skew

            # --- 6. 整理并返回结果 ---
            result_cols = [col for col in ['factor_Gd', 'factor_Gd_deviation', 'factor_TGD', 'factor_Combined'] if col in factor_df.columns]

            # 从 factor_df 创建一个显式的副本，避免 SettingWithCopyWarning
            final_factors = factor_df[result_cols].copy()

            # 现在对这个新的 final_factors DataFrame 进行操作是安全的
            final_factors['dt'] = pd.to_datetime(a_date, format='%Y%m%d')
            final_factors = final_factors.reset_index().set_index(['dt', 'Ticker'])

            return final_factors
        
        def calculate_rolling_factors(df_single_dt):
           
            # 检查输入是否为空
            if df_single_dt.empty:
                print("警告：输入的DataFrame为空。")
                return pd.DataFrame()

            # 从索引中获取唯一的dt值
            dt_val = df_single_dt.index.get_level_values('dt')[0]
            dt_str = dt_val.strftime('%Y%m%d')
            print(f"--- 开始处理 dt: {dt_str} ---")
            
            # 存储当前dt对应的过去几天的因子计算结果
            historical_factors_list = []
            
            # 获取当前dt包含的实际分钟数据日期
            historical_dates = df_single_dt['MDDate'].unique()
            
            for mddate in historical_dates:
                mddate_str = str(int(mddate))
                #print(f"  -> 计算 MDDate: {mddate_str} 的因子...")
                
                # 筛选出当天的分钟数据
                single_day_data = df_single_dt[df_single_dt['MDDate'] == mddate].copy()
                single_day_data.sort_values(by='MDTime',inplace=True)
                
                if not single_day_data.empty:
                    # 调用单日函数计算因子
                    factors_for_one_day = calculate_daily_factors(single_day_data, mddate_str)
                    historical_factors_list.append(factors_for_one_day)

            # 如果成功计算了过去几天的因子，则进行平均
            if not historical_factors_list:
                print(f"警告：对于 dt {dt_str}，未能计算任何历史日期的因子。")
                return pd.DataFrame()

            # 合并过去几天的所有因子
            combined_historical_factors = pd.concat(historical_factors_list)
            
            # 按Ticker分组，计算平均值
            averaged_factors = combined_historical_factors.groupby('Ticker').mean()
            
            # 将结果与当前的主索引dt关联起来
            averaged_factors['dt'] = dt_val
            final_dt_factors = averaged_factors.reset_index().set_index(['dt', 'Ticker'])
            
            return final_dt_factors
        
        daily_data = database['xdb_tick1m_cs']
        daily_factors = calculate_rolling_factors(daily_data)
        daily_factors.rename(columns={'factor_TGD': self.factor_name }, inplace=True)
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