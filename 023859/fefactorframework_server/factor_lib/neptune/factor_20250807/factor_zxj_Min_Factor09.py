import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Min_Factor09(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_Min_Factor09"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"
    factor_explain = "方正研报——云开雾散"
    zcz_adjusted = "否"
    logic_type = ""
    low_cost = ""
    t_day_data = []

    xdb_data = [
        {
        'name': 'xdb_tick1m_cs', 
        'lag': 1,
    }]

    def pre_calculate_T_N_data(self, database):
        if database.get("skip", False):
            return database
        
        def calculate_daily_factors_simplified(df_day: pd.DataFrame) -> pd.DataFrame:
            
            df_day = df_day.sort_values(by=['Ticker', 'MDTime'])

            df_day['return'] = df_day.groupby('Ticker')['LastPx'].pct_change()

            df_day['volatility'] = df_day.groupby('Ticker')['return'].transform(
                lambda x: x.rolling(5, min_periods=5).std()
            )

            df_day['ambiguity'] = df_day.groupby('Ticker')['volatility'].transform(
                lambda x: x.rolling(5, min_periods=5).std()
            )
            
            
            df_day['MinuteVolumeTrade'] = df_day.groupby('Ticker')['TotalVolumeTrade'].diff().fillna(0)
            df_day['MinuteValueTrade'] = df_day.groupby('Ticker')['TotalValueTrade'].diff().fillna(0)
            
           
            df_day.loc[df_day['MDTime'] <= 93000000, ['MinuteVolumeTrade', 'MinuteValueTrade']] = 0

            def get_factors(group):
                
                group = group.dropna(subset=['ambiguity'])
                if group.empty:
                    return pd.Series({
                        'ambiguity_corr': np.nan,
                        'ambiguity_amount_ratio': np.nan,
                        'ambiguity_volume_ratio': np.nan,
                        'ambiguity_price_diff': np.nan,
                        'clouds_disperse_factor': np.nan
                    })

                
                ambiguity_corr = group['ambiguity'].corr(group['MinuteValueTrade'])

                ambiguity_mean = group['ambiguity'].mean()
                foggy_moments = group[group['ambiguity'] > ambiguity_mean]
                
                foggy_amount_mean = foggy_moments['MinuteValueTrade'].mean()
                foggy_volume_mean = foggy_moments['MinuteVolumeTrade'].mean()
                total_amount_mean = group['MinuteValueTrade'].mean()
                total_volume_mean = group['MinuteVolumeTrade'].mean()

                ambiguity_amount_ratio = foggy_amount_mean / total_amount_mean if total_amount_mean > 0 else np.nan
                ambiguity_volume_ratio = foggy_volume_mean / total_volume_mean if total_volume_mean > 0 else np.nan
                
                ambiguity_price_diff = ambiguity_amount_ratio - ambiguity_volume_ratio
                
                clouds_disperse_factor = (ambiguity_corr + ambiguity_amount_ratio) / 2.0

                return pd.Series({
                    'ambiguity_corr': ambiguity_corr,
                    'ambiguity_amount_ratio': ambiguity_amount_ratio,
                    'ambiguity_volume_ratio': ambiguity_volume_ratio,
                    'ambiguity_price_diff': ambiguity_price_diff,
                    'clouds_disperse_factor': clouds_disperse_factor
                })

            daily_factors_df = df_day.groupby('Ticker').apply(get_factors)
            return daily_factors_df

        daily_data = database['xdb_tick1m_cs']
        current_date = daily_data.index[0][0]
        daily_factors = calculate_daily_factors_simplified(daily_data)
        daily_factors['dt'] = current_date
        df_to_store = daily_factors.reset_index().set_index(['dt','Ticker'])
        df_to_store.rename(columns={'clouds_disperse_factor': self.factor_name }, inplace=True)
        database['pre_T_N'] = df_to_store[[self.factor_name]]
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