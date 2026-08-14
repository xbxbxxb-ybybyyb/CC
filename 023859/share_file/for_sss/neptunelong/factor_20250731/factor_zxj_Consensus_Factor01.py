import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Consensus_Factor01(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "zxj_Consensus_Factor01"
    fill_na_value = 0 # 缺失值填充
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "分析师覆盖数" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时：是/否
    #
    t_day_data = []
    xdb_data = [
        {
        'name':'xdb_researchreport_cs',
        'lag':70
        }
    ]
    t_1_factor_data = []  # T-N factor数据，格式如上
    t_1_factor_data_types = [] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df = database['xdb_researchreport_cs']
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            df.reset_index(inplace=True)

            # 2. 日期格式转换
            df['MDDate_dt'] = pd.to_datetime(df['MDDate'], format='%Y%m%d')
            df['dt'] = pd.to_datetime(df['dt'])

            # 3. 定义回看窗口的起始日期
            df['start_date'] = df['dt'] - pd.DateOffset(months=3)

            # 4. 筛选在3个月窗口期内的报告
            valid_reports = df[df['MDDate_dt'] > df['start_date']]

            # 5. 按 (dt, Ticker) 分组并计算唯一报告数
            daily_tot = valid_reports.groupby(['dt', 'Ticker'])['REPORTID'].nunique()
            
            daily_tot_df = daily_tot.to_frame(self.factor_name)
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = daily_tot_df[[self.factor_name]] # cs要返回df
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
