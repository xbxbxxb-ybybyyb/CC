import pandas as pd
import numpy as np
import statsmodels.api as sm
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_MD_Factor08_modified(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_MD_Factor08_modified"
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
         'lag': 36,
         'column': ['high', 'low', 'close','pre_close', 'pct_chg','turn','mkt_cap_ard']
    }]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database.get("skip", False):
            return database
        else:
            window_size = 20

            df_md = database['MD_CHINA_STOCK_DAILY_WIND']

            def calculate_all_factors(df_MD, window=20):
                df = df_MD.sort_index()

                def f_calc_std(factor_series):
                    return np.std(factor_series[~np.isnan(factor_series)], ddof=1)

                df['Turn20'] = df.groupby('Ticker')['turn'].rolling(window=window, min_periods=window).mean().reset_index(level=0, drop=True)
                df['STR'] = df.groupby('Ticker')['turn'].rolling(window=window, min_periods=window).apply(f_calc_std, raw=False).reset_index(level=0, drop=True)

                df_factors = df.dropna(subset=['Turn20', 'STR', 'mkt_cap_ard'])

                if df_factors.empty:
                    return pd.DataFrame()
                    
                def process_daily_group(daily_df):
                    if len(daily_df) < 10:
                        return None

                    group = daily_df.copy()

                    log_mc = np.log(group['mkt_cap_ard'])
                    X = sm.add_constant(log_mc, prepend=True)

                    group['Turn20'] = sm.OLS(group['Turn20'], X, missing='drop').fit().resid
                    group['STR'] = sm.OLS(group['STR'], X, missing='drop').fit().resid

                    group['score1'] = group['STR'].rank(method='first', ascending=True)
                    median_rank = group['score1'].median()
                    
                    stable_mask = group['score1'] <= median_rank
                    unstable_mask = group['score1'] > median_rank

                    group.loc[stable_mask, 'score2_3'] = group.loc[stable_mask, 'Turn20'].rank(method='first', ascending=False)
                    group.loc[unstable_mask, 'score2_3'] = group.loc[unstable_mask, 'Turn20'].rank(method='first', ascending=True)
                    
                    group['UTR'] = group['score1'] + group['score2_3']
                    
                    return group[['Turn20', 'STR', 'UTR']]

                final_factors = df_factors.groupby(level='dt').apply(process_daily_group)
                
                return final_factors
            # -------------------------------------------------------------------------------------------------------------------
            df_result = calculate_all_factors(df_md,window=window_size)
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
