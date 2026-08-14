import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

warnings.simplefilter(action='ignore', category=FutureWarning)

class factor_zxj_MD_Factor10_modified(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_MD_Factor10_modified"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "相邻股票代码"
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 36,
         'column': ['high', 'low', 'close','pre_close', 'pct_chg','turn']
    }]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database.get("skip", False):
            return database
        else:
            neighbors = 10
            window_size = 10

            df_MD = database['MD_CHINA_STOCK_DAILY_WIND']

            def calculate_factors_vectorized(df_input, window_n, num_neighbors):
                """
                使用 Pandas 向量化操作为整个 DataFrame 计算因子，无中间过程打印。
                """
                df = df_input.copy()

                df['avg_ret'] = df.groupby(level='Ticker')['pct_chg'].transform(
                    lambda x: x.rolling(window=window_n, min_periods=int(window_n/2)).mean()
                )
                df['avg_tov'] = df.groupby(level='Ticker')['turn'].transform(
                    lambda x: x.rolling(window=window_n, min_periods=int(window_n/2)).mean()
                )
                
                df.sort_index(level=['dt', 'Ticker'], inplace=True)
                
                half_n = num_neighbors // 2
                neighbor_rets = []
                neighbor_tovs = []
                
                for i in range(1, half_n + 1):
                    neighbor_rets.append(df.groupby(level='dt')['avg_ret'].shift(i))
                    neighbor_rets.append(df.groupby(level='dt')['avg_ret'].shift(-i))
                    neighbor_tovs.append(df.groupby(level='dt')['avg_tov'].shift(i))
                    neighbor_tovs.append(df.groupby(level='dt')['avg_tov'].shift(-i))
                    
                df['NBR_ret'] = pd.concat(neighbor_rets, axis=1).mean(axis=1, skipna=True)
                df['NBR_tov'] = pd.concat(neighbor_tovs, axis=1).mean(axis=1, skipna=True)
                
                def get_residuals(group):
                    df_reg_ret = group[['NBR_ret', 'avg_ret']].dropna()
                    if not df_reg_ret.empty and len(df_reg_ret) > 1:
                        X = sm.add_constant(df_reg_ret['avg_ret'])
                        model = sm.OLS(df_reg_ret['NBR_ret'], X).fit()
                        group.loc[df_reg_ret.index, 'RNBR_ret'] = model.resid
                    else:
                        group['RNBR_ret'] = np.nan

                    df_reg_tov = group[['NBR_tov', 'avg_tov']].dropna()
                    if not df_reg_tov.empty and len(df_reg_tov) > 1:
                        X = sm.add_constant(df_reg_tov['avg_tov'])
                        model = sm.OLS(df_reg_tov['NBR_tov'], X).fit()
                        group.loc[df_reg_tov.index, 'RNBR_tov'] = model.resid
                    else:
                        group['RNBR_tov'] = np.nan
                        
                    return group[['RNBR_ret', 'RNBR_tov']]

                residuals = df.groupby(level='dt').apply(get_residuals)
                
                df = df.join(residuals)
                
                return df[['RNBR_ret', 'RNBR_tov']]
            # -------------------------------------------------------------------------------------------------------------------
            daily_factors = calculate_factors_vectorized(df_MD, window_size, neighbors)
            daily_factors.rename(columns={'RNBR_tov': self.factor_name }, inplace=True)
            database['pre_T_N'] = daily_factors[[self.factor_name]]
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database.get("skip", False):
            return pd.Series({self.factor_name: np.nan})
        else:
            return database['pre_T_N']
