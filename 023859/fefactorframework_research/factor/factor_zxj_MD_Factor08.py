import pandas as pd
import numpy as np
import statsmodels.api as sm
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_MD_Factor08(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_MD_Factor08"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "优加换手率"
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 100,
         'column': ['high', 'low', 'close','pre_close', 'pct_chg','turn','mkt_cap_ard']
    }]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database.get("skip", False):
            return database
        else:
            window_size = 20

            df_md = database['MD_CHINA_STOCK_DAILY_WIND']
            date =df_md.index.get_level_values('dt').unique()[-1]
            
            def calculate_factors_for_day(date, full_df, window=20):
                """
                为单个指定日期计算Turn20, STR, 和 UTR 因子，并进行市值中性化。
                (适用于以 (dt, Ticker) 为 MultiIndex 的 DataFrame)
                """
                # 利用 MultiIndex 的第一层进行日期切片，效率很高
                start_date = date - pd.offsets.BDay(window - 1)
                window_data = full_df.loc[start_date:date]
                
                if window_data.empty:
                    return None

                # a. 计算原始Turn20和STR
                def calc_raw_factors(x):
                    # 使用 groupby('Ticker') 会自动按索引的 'Ticker' 层级分组
                    if len(x) == window:
                        return pd.Series({'Turn20': x.mean(), 'STR': x.std()})
                    return None

                # 此处 apply 的结果是一个以 (Ticker, FactorName) 为 MultiIndex 的 Series
                raw_factors = window_data.groupby('Ticker')['turn'].apply(calc_raw_factors).dropna()
                
                if raw_factors.empty:
                    return None

                # b. 合并当日市值数据
                # 利用 MultiIndex，这行代码可以正确地获取以 Ticker 为索引的 Series
                market_caps = window_data.loc[date, 'mkt_cap_ard']

                # c. 市值中性化前的合并 *** 此处是唯一的修改点 ***
                # 使用 .unstack() 将 raw_factors 从 Series 转换为 DataFrame 后再 join
                df_today = raw_factors.unstack().join(market_caps).dropna()

                if len(df_today) < 10:  # 回归需要足够的数据点
                    return None

                # d. 市值中性化 (回归取残差)
                log_mc = np.log(df_today['mkt_cap_ard'])
                X = sm.add_constant(log_mc, prepend=True)

                # 中性化 Turn20
                model_turn20 = sm.OLS(df_today['Turn20'], X, missing='drop').fit()
                df_today['Turn20'] = model_turn20.resid

                # 中性化 STR
                model_str = sm.OLS(df_today['STR'], X, missing='drop').fit()
                df_today['STR'] = model_str.resid

                # e. 使用中性化后的因子计算UTR
                df_today['score1'] = df_today['STR'].rank(method='first', ascending=True)
                median_rank = df_today['score1'].median()
                stable_mask = df_today['score1'] <= median_rank
                unstable_mask = df_today['score1'] > median_rank

                df_today.loc[stable_mask, 'score2_3'] = df_today.loc[stable_mask, 'Turn20'].rank(method='first', ascending=False)
                df_today.loc[unstable_mask, 'score2_3'] = df_today.loc[unstable_mask, 'Turn20'].rank(method='first', ascending=True)
                df_today['UTR'] = df_today['score1'] + df_today['score2_3']

                # f. 整理并返回当日结果
                final_cols = ['Turn20', 'STR', 'UTR']
                df_today['dt'] = date
                return df_today.reset_index().set_index(['dt', 'Ticker'])[final_cols]
            # -------------------------------------------------------------------------------------------------------------------
            df_result = calculate_factors_for_day(date, df_md, window=window_size)
            df_result.rename(columns={'UTR': self.factor_name }, inplace=True)
            database['pre_T_N'] = df_result[[self.factor_name]]
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database.get("skip", False):
            return pd.Series({self.factor_name: np.nan})
        else:
            return database['pre_T_N']
