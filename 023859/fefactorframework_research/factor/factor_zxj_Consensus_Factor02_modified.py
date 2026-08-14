import pandas as pd
import numpy as np
import statsmodels.api as sm
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Consensus_Factor02_modified(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_Consensus_Factor02_modified"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "特质覆盖度" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    t_day_data = []
    #
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80,  # 注意为正数
         'column': ['turn', 'pct_chg','mkt_cap_ard']
         }]
    t_1_factor_data_types = ['MD']
    xdb_data = [
        {
       'name': 'xdb_researchreport_cs',
       'lag': 400 # 回看日期，N为往前回看1~N天
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        df = database['xdb_researchreport_cs']
        df_md = database['MD_CHINA_STOCK_DAILY_WIND']


        # -------------------------------------------------------------------------------------------------------------------
        df.reset_index(inplace=True)

        all_tickers_for_day = df[['dt', 'Ticker']].drop_duplicates()

        # 2. 日期格式转换
        df['MDDate_dt'] = pd.to_datetime(df['MDDate'], format='%Y%m%d')
        df['dt'] = pd.to_datetime(df['dt'])

        # 3. 定义回看窗口的起始日期
        df['start_date'] = df['dt'] - pd.DateOffset(months=3)

        # 4. 筛选在3个月窗口期内的报告
        valid_reports = df[df['MDDate_dt'] > df['start_date']]

        # 5. 按 (dt, Ticker) 分组并计算唯一报告数
        daily_tot = valid_reports.groupby(['dt', 'Ticker'])['REPORTID'].nunique().to_frame('TOT').reset_index()
        tot_factor_df = pd.merge(all_tickers_for_day, daily_tot, on=['dt', 'Ticker'], how='left')
        tot_factor_df['TOT'] = tot_factor_df['TOT'].fillna(0).astype(int)
        tot_factor_df.set_index(['dt', 'Ticker'], inplace=True)

        window = 63

        # 使用前一交易日的数据来预测今天的TOT，因此对所有量价数据进行滞后处理
        df_md_lagged = df_md.copy()

        # 创建一个新的DataFrame来存储计算出的特征
        features_df = pd.DataFrame(index=df_md_lagged.index)

        # 解释变量 X1: Size (上一日对数总市值)
        features_df['size'] = np.log(df_md_lagged['mkt_cap_ard'])

        # 解释变量 X2: Turn (滚动平均换手率)
        features_df['turn_rolling'] = df_md_lagged.groupby(level='Ticker')['turn'].rolling(window=window, min_periods=int(window/2)).mean().reset_index(level=0, drop=True)

        # 解释变量 X3: Pret (滚动累计收益率)
        log_ret = np.log1p(df_md_lagged['pct_chg'])
        cum_log_ret = log_ret.groupby(level='Ticker').rolling(window=window, min_periods=int(window/2)).sum().reset_index(level=0, drop=True)
        features_df['pret_rolling'] = np.exp(cum_log_ret) - 1
        
        #处理索引问题
        df_reset = features_df.reset_index()
        latest_date = df_reset['dt'].max()
        df_reset.loc[df_reset['dt'] == latest_date, 'dt'] = tot_factor_df.index[0][0]
        df_reg_updated = df_reset.set_index(['dt', 'Ticker'])
        df_reg = df_reg_updated.join(tot_factor_df.rename(columns={'TOT': 'tot'}), how='inner')
        
        df_reg['log_1_plus_tot'] = np.log1p(df_reg['tot'])
        
        # 清理数据，去除回归所需变量中的无穷值和NaN值
        # statsmodels在拟合时会自动处理'missing'，但提前处理可以避免不必要的计算
        cols_for_regression = ['log_1_plus_tot', 'size', 'turn_rolling', 'pret_rolling']
        df_reg.replace([np.inf, -np.inf], np.nan, inplace=True)
        df_reg.dropna(subset=cols_for_regression, inplace=True)

        # 3. 逐日进行横截面回归

        current_date = pd.to_datetime(df['dt'].iloc[0])
        daily_df = df_reg.loc[current_date]
        # 定义Y和X
        Y = daily_df['log_1_plus_tot']
        X = daily_df[['size', 'turn_rolling', 'pret_rolling']]
        X = sm.add_constant(X) # 添加截距项


        model = sm.OLS(Y, X, missing='drop').fit()

        # 获取残差，残差的index是Ticker
        residuals = model.resid
        
        # 将残差和日期组合起来
        residuals_df = pd.DataFrame({self.factor_name: residuals})
        residuals_df['dt'] = current_date
        residuals_df.set_index('dt', append=True, inplace=True)
        residuals_df = residuals_df.swaplevel(0, 1) # 交换索引层级，使之与输入格式一致
        data_series = residuals_df[self.factor_name]
        mean = data_series.mean()
        std = data_series.std()
        residuals_df[self.factor_name] = (data_series - mean) / std
        # -------------------------------------------------------------------------------------------------------------------
        database['pre_T_N'] = residuals_df[[self.factor_name]]
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