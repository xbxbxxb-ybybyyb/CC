import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Fundamental_Factor01(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "zxj_Fundamental_Factor01"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "走势相似的股票" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    t_day_data = []
    #
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80,  # 注意为正数
         'column': ['close', 'adjfactor','pct_chg','mkt_cap_ard']
         }]
    t_1_factor_data_types = ['MD']
    
    xdb_data = [{
        'name':'xdb_balancesheet_cs',
        'lag':16
    },
        {
        'name': 'xdb_income_cs',
        'lag': 16
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        
        df_MD = database['MD_CHINA_STOCK_DAILY_WIND']
        balance_data = database['xdb_balancesheet_cs']
        income_data = database['xdb_income_cs']

        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        def get_latest_financial_data_final(balancesheet: pd.DataFrame, incomesheet: pd.DataFrame) -> pd.DataFrame:
            # --- 步骤 1: 清洗和准备数据 ---
            
            # 将MDDate列强制转换为数字，无法转换的变为NaN (Not a Number)
            balancesheet['MDDate'] = pd.to_numeric(balancesheet['MDDate'], errors='coerce')
            incomesheet['MDDate'] = pd.to_numeric(incomesheet['MDDate'], errors='coerce')
            
            # 删除MDDate转换后变成NaN的行
            balancesheet.dropna(subset=['MDDate'], inplace=True)
            incomesheet.dropna(subset=['MDDate'], inplace=True)

            # 如果数据为空，提前返回
            if balancesheet.empty or incomesheet.empty:
                final_cols = ['TOT_SHRHLDR_EQY_EXCL_MIN_INT', 'TOT_ASSETS', 'NET_PROFIT_EXCL_MIN_INT_INC']
                return pd.DataFrame(columns=final_cols, index=pd.MultiIndex(levels=[[],[]], codes=[[],[]], names=['dt', 'Ticker']))

            # --- 步骤 2: 筛选每个 Ticker 的最新数据 ---
            
            # **关键步骤**: 先排序，然后只按 'Ticker' 级别分组，取最后一条
            latest_bs = balancesheet.sort_values(by='MDDate', ascending=True).groupby(level='Ticker').tail(1)
            latest_bs_selected = latest_bs[['TOT_SHRHLDR_EQY_EXCL_MIN_INT', 'TOT_ASSETS']]

            latest_is = incomesheet.sort_values(by='MDDate', ascending=True).groupby(level='Ticker').tail(1)
            latest_is_selected = latest_is[['NET_PROFIT_EXCL_MIN_INT_INC']]
            
            # --- 步骤 3: 拼接数据 ---
            combined_df = latest_bs_selected.join(latest_is_selected, how='inner')
            combined_df.sort_index(inplace=True)
            
            return combined_df

        def merge_with_market_data_with_excess_return(df_fundamental: pd.DataFrame, df_MD: pd.DataFrame) -> pd.DataFrame:
           
            # --- 步骤 1: 确定日期范围 (逻辑不变) ---
            if df_fundamental.index.get_level_values('dt').empty:
                print("Warning: df_fundamental is empty. Returning an empty DataFrame.")
                return pd.DataFrame()
                
            target_dt = pd.to_datetime(df_fundamental.index.get_level_values('dt')[0])
            all_market_dates = pd.to_datetime(df_MD.index.get_level_values('dt').unique())
            past_dates = all_market_dates[all_market_dates < target_dt]

            if past_dates.empty:
                print(f"Warning: 在 df_MD 中找不到任何在 {target_dt.strftime('%Y-%m-%d')} 之前的日期。")
                market_data_to_merge = pd.DataFrame(columns=['mkt_cap_ard', 'ret_20', 'excess_ret_20'], index=pd.Index([], name='Ticker'))
                return df_fundamental.join(market_data_to_merge, on='Ticker')
            
            merge_dt = past_dates.max()
            #print(f"目标日期: {target_dt.strftime('%Y-%m-%d')}, 找到的前一个有效交易日: {merge_dt.strftime('%Y-%m-%d')}")

            # --- 步骤 2: 【性能优化】截断 df_MD (逻辑不变) ---
            lookback_window_days = 45 
            start_dt = merge_dt - pd.Timedelta(days=lookback_window_days)
            
            if not pd.api.types.is_datetime64_any_dtype(df_MD.index.get_level_values('dt')):
                new_dt_index = pd.to_datetime(df_MD.index.get_level_values('dt'))
                df_MD.index = pd.MultiIndex.from_arrays([new_dt_index, df_MD.index.get_level_values('Ticker')], names=['dt', 'Ticker'])
            
            df_MD_truncated = df_MD.loc[start_dt:merge_dt].copy()
            #print(f"数据已截断，仅使用 {start_dt.strftime('%Y-%m-%d')} 到 {merge_dt.strftime('%Y-%m-%d')} 的数据进行计算。")

            # --- 步骤 3: 在【小数据子集】上进行计算 ---
            # 计算 ret_20 (个股20日收益率)
            df_MD_truncated['pct_chg'] = df_MD_truncated['pct_chg'] / 100
            df_MD_truncated['gross_return'] = 1 + df_MD_truncated['pct_chg']
            rolling_gross_return = df_MD_truncated.groupby(level='Ticker')['gross_return'].rolling(window=20).apply(np.prod, raw=True)
            df_MD_truncated['ret_20'] = rolling_gross_return.reset_index(level=0, drop=True) - 1

            # --- 新增：计算 excess_ret_20 (超额收益) ---
            # 1. 计算每日市场基准收益（等权重）
            market_return_daily = df_MD_truncated.groupby(level='dt')['pct_chg'].mean().rename('market_return')
            
            # 2. 将市场收益合并回原数据
            df_MD_processed = df_MD_truncated.join(market_return_daily, on='dt')

            # 3. 计算每日超额收益
            df_MD_processed['daily_excess_ret'] = df_MD_processed['pct_chg'] - df_MD_processed['market_return']

            # 4. 累计20日超额收益
            df_MD_processed['gross_excess_return'] = 1 + df_MD_processed['daily_excess_ret']
            rolling_gross_excess = df_MD_processed.groupby(level='Ticker')['gross_excess_return'].rolling(window=20).apply(np.prod, raw=True)
            df_MD_processed['excess_ret_20'] = rolling_gross_excess.reset_index(level=0, drop=True) - 1
            # ------------------------------------

            # --- 步骤 4: 筛选并拼接数据 ---
            market_data_previous_day = df_MD_processed.xs(merge_dt, level='dt')
            
            # 在要合并的列中加入 'excess_ret_20'
            columns_to_merge = ['mkt_cap_ard', 'ret_20', 'excess_ret_20']
            market_data_to_merge = market_data_previous_day[columns_to_merge]
            
            final_df = df_fundamental.join(market_data_to_merge, on='Ticker')
            
            return final_df

        def _calculate_distance_metrics(df: pd.DataFrame) -> pd.DataFrame:
           
            metrics_df = pd.DataFrame(index=df.index)
            metrics_df['Sz'] = np.log(df['mkt_cap_ard'])
            metrics_df['BM'] = df['TOT_SHRHLDR_EQY_EXCL_MIN_INT'] / df['mkt_cap_ard']
            metrics_df['RE'] = df['NET_PROFIT_EXCL_MIN_INT_INC'] / df['TOT_SHRHLDR_EQY_EXCL_MIN_INT']
            metrics_df.replace([np.inf, -np.inf], np.nan, inplace=True)
            metrics_df = (metrics_df - metrics_df.mean()) / metrics_df.std()
            metrics_df.fillna(0, inplace=True)
            return metrics_df


        def calculate_similar_stock_momentum_factor(df: pd.DataFrame, r: int = 80) -> pd.Series:
          
            if df.empty or len(df) <= r:
                return pd.Series(index=df.index, dtype=float)
                
            metrics = _calculate_distance_metrics(df)
            distance_matrix = cdist(metrics.values, metrics.values, 'euclidean')
            np.fill_diagonal(distance_matrix, np.inf)
            neighbor_indices = np.argsort(distance_matrix, axis=1)[:, :r]
            neighbor_returns = df['ret_20'].values[neighbor_indices]
            neighbor_caps = df['mkt_cap_ard'].values[neighbor_indices]
            total_cap = neighbor_caps.sum(axis=1, keepdims=True)
            weights = neighbor_caps / (total_cap + 1e-9)
            sim_factor = (weights * neighbor_returns).sum(axis=1)
            return pd.Series(sim_factor, index=df.index)


        def calculate_original_expected_diff_factor(df: pd.DataFrame, sim_factor: pd.Series) -> pd.Series:
            return sim_factor - df['ret_20']

        def calculate_targeted_adjustment_factor(df: pd.DataFrame, 
                                                sim_factor: pd.Series, 
                                                num_quantiles: int = 5, 
                                                discount_weight: float = 0.1) -> pd.Series:
            
            # 1. 计算所有股票的“原始相似预期差因子”
            base_factor = sim_factor - df['ret_20']

            # 如果没有有效的基础因子值，则直接返回
            if base_factor.dropna().empty:
                return pd.Series(index=df.index, dtype=float, name='targeted_adjustment_factor')

            # 2. 根据这个基础因子值，将所有股票分为 n 个组
            try:
                groups = pd.qcut(base_factor, q=num_quantiles, labels=False, duplicates='drop')
            except ValueError:
                # 如果无法分箱，则直接返回原始因子值
                base_factor.name = 'targeted_adjustment_factor'
                return base_factor

            # 3. 创建最终因子值的副本，初始值与基础因子值相同
            final_factor = base_factor.copy()
            final_factor.name = 'targeted_adjustment_factor'

            # 4. 定位需要被调整的股票
            # 条件一：该股票属于因子值最高的组 (组的标签是 num_quantiles - 1)
            in_top_group = (groups == num_quantiles - 1)
            
            # 条件二：该股票没有跑赢市场 (超额收益小于等于0)
            did_not_beat_market = (df['excess_ret_20'] <= 0)
            
            # 两个条件同时满足的，就是我们要找的“陷阱股”
            trap_stocks_mask = in_top_group & did_not_beat_market

            # 5. 对这些“陷阱股”的因子值进行打折处理
            # .loc[mask]可以精准地选取并修改满足条件的行的值
            final_factor.loc[trap_stocks_mask] *= discount_weight
            
            return final_factor


        def calculate_factors_for_day(daily_df: pd.DataFrame, r: int = 80) -> pd.DataFrame:
           
            # --- 输入验证和准备 ---
            required_cols = [
                'TOT_SHRHLDR_EQY_EXCL_MIN_INT', 'TOT_ASSETS',
                'NET_PROFIT_EXCL_MIN_INT_INC', 'mkt_cap_ard', 'ret_20', 'excess_ret_20'
            ]
            if not all(col in daily_df.columns for col in required_cols):
                raise ValueError(f"输入DataFrame缺少一个或多个必需列: {required_cols}")

            if daily_df.index.get_level_values('dt').nunique() != 1:
                raise ValueError("输入DataFrame必须只包含单日数据。")

            df = daily_df.droplevel('dt').copy()
            df.dropna(subset=required_cols, inplace=True)
            
            if df.empty:
                return pd.DataFrame(columns=['相似股票动量因子', '原始相似预期差因子', '改进相似预期差因子'])

            # --- 因子计算 ---
            
            # 1. 计算基础的“相似股票动量因子(SIM)”，这是所有后续因子的基础
            sim_factor = calculate_similar_stock_momentum_factor(df, r)

            # 2. 计算“原始相似预期差因子”
            original_delta_er = calculate_original_expected_diff_factor(df, sim_factor)
            
            # 3. 计算“改进相似预期差因子”
            revised_delta_er = calculate_targeted_adjustment_factor(df, sim_factor)

            # --- 格式化输出 ---
            
            # 将三个因子合并到结果DataFrame中，并命名
            result_df = pd.DataFrame({
                '相似股票动量因子': sim_factor,
                '原始相似预期差因子': original_delta_er,
                '改进相似预期差因子': revised_delta_er
            })

            # 重新应用原始的多重索引
            result_df.index = pd.MultiIndex.from_product(
                [daily_df.index.get_level_values('dt').unique(), result_df.index],
                names=['dt', 'Ticker']
            )
            
            return result_df
        # -------------------------------------------------------------------------------------------------------------------
        r_neighbors = 80
        df_fund = get_latest_financial_data_final(balance_data,income_data)
        daily_data = merge_with_market_data_with_excess_return(df_fund,df_MD)
        daily_factors = calculate_factors_for_day(daily_data, r=r_neighbors)
        daily_factors.rename(columns={'改进相似预期差因子': self.factor_name }, inplace=True)
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