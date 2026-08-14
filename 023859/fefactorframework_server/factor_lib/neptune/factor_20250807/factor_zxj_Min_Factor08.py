import pandas as pd
import numpy as np
from scipy.stats import boxcox
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Min_Factor08(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_Min_Factor08"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"
    factor_explain = "一视同仁因子"
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

        def calculate_factors_for_stock(stock_df: pd.DataFrame) -> pd.Series:
            # 确保数据按时间排序
            stock_df = stock_df.sort_values('MDTime').reset_index(drop=True)
            
            # 计算后续会用到的分钟收益率
            stock_df['minute_return'] = stock_df['LastPx'].pct_change()

            if stock_df.shape[0] < 5: # 数据太少，无法有效计算
                return pd.Series(index=['volatility_fairness', 'return_fairness', 'equal_treatment'], dtype=np.float64)
            
            intraday_df = stock_df.iloc[1:-1].copy()

            pos_vol_df = intraday_df[intraday_df['VolumeTrade'] > 0].copy()

            # 如果正成交量的数据点少于3个，无法进行有效差分和统计
            if pos_vol_df.shape[0] < 3:
                return pd.Series(index=['volatility_fairness', 'return_fairness', 'equal_treatment'], dtype=np.float64)


            pos_vol_df['VolumeTrade'] = pos_vol_df['VolumeTrade'] / pos_vol_df['VolumeTrade'].max()


            try:
                pos_vol_df['boxcox_volume'], _ = boxcox(pos_vol_df['VolumeTrade'])
            except ValueError:
                pos_vol_df['boxcox_volume'] = np.log(pos_vol_df['VolumeTrade'])

            
            pos_vol_df['volume_change'] = pos_vol_df['boxcox_volume'].diff()
            pos_vol_df.dropna(subset=['volume_change'], inplace=True)
            
            if pos_vol_df.empty:
                return pd.Series(index=['volatility_fairness', 'return_fairness', 'equal_treatment'], dtype=np.float64)

            mean_change = pos_vol_df['volume_change'].mean()
            std_change = pos_vol_df['volume_change'].std()

            if std_change == 0 or np.isnan(std_change):
                return pd.Series(index=['volatility_fairness', 'return_fairness', 'equal_treatment'], dtype=np.float64)

            surge_moments = pos_vol_df[pos_vol_df['volume_change'] > (mean_change + std_change)]
            plunge_moments = pos_vol_df[pos_vol_df['volume_change'] < (mean_change - std_change)]

            
            open_price = stock_df['OpenPx'].iloc[0]
            close_price = stock_df['LastPx'].iloc[-1]
            intraday_return = (close_price / open_price) - 1 if open_price != 0 else 0.0

            
            volatility_fairness_factor = np.nan
            if not surge_moments.empty and not plunge_moments.empty:
                
                dazzling_vols = []
                for idx in surge_moments.index:
                    # 窗口为当前分钟及随后的4分钟
                    window = stock_df.loc[idx : idx + pd.Timedelta(minutes=4)] if isinstance(idx, pd.Timestamp) else stock_df.loc[idx:idx+4]
                    if window.shape[0] > 1:
                        dazzling_vols.append(window['minute_return'].std())
                
                dim_vols = []
                for idx in plunge_moments.index:
                    window = stock_df.loc[idx : idx + pd.Timedelta(minutes=4)] if isinstance(idx, pd.Timestamp) else stock_df.loc[idx:idx+4]
                    if window.shape[0] > 1:
                        dim_vols.append(window['minute_return'].std())
                
                
                avg_dazzling_vol = np.nanmean(dazzling_vols)
                avg_dim_vol = np.nanmean(dim_vols)

                if not np.isnan(avg_dazzling_vol) and not np.isnan(avg_dim_vol):
                    
                    vol_fairness_degree = abs(avg_dazzling_vol - avg_dim_vol)
                    
                    volatility_fairness_factor = intraday_return * vol_fairness_degree

            
            return_fairness_factor = np.nan
            if not surge_moments.empty and not plunge_moments.empty:
                
                avg_dazzling_ret = surge_moments['minute_return'].mean()
                avg_dim_ret = plunge_moments['minute_return'].mean()

                if not np.isnan(avg_dazzling_ret) and not np.isnan(avg_dim_ret):
                    
                    ret_fairness_degree = abs(avg_dazzling_ret - avg_dim_ret)
                    
                    return_fairness_factor = intraday_return * ret_fairness_degree

            
            equal_treatment_factor = np.nan
            
            if not np.isnan(volatility_fairness_factor) and not np.isnan(return_fairness_factor):
                equal_treatment_factor = 0.5 * volatility_fairness_factor + 0.5 * return_fairness_factor
                
            return pd.Series({
                'volatility_fairness': volatility_fairness_factor,
                'return_fairness': return_fairness_factor,
                'equal_treatment': equal_treatment_factor
            })
        
        daily_data = database['xdb_tick1m_cs']
        current_date = daily_data.index[0][0]
        df_today_factors = daily_data.groupby('Ticker').apply(calculate_factors_for_stock)
        df_today_factors['dt'] = current_date
        df_to_store = df_today_factors.reset_index().set_index(['dt', 'Ticker'])
        df_to_store.rename(columns={'equal_treatment': self.factor_name }, inplace=True) 
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