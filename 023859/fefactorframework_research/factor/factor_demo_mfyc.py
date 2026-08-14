# 卖方预测 cs
class factor_demo_mfyc(BaseFactor):
    strategy_name = "neptune"
    factor_name = "demo_mfyc"
    fill_na_value = 0 # 缺失值填充
    need_pre_calculate_T_N = True
    owner = ""  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时：是/否
    #
    t_day_data = []
    xdb_data = [
        {
        'name':'xdb_researchreport_cs',
        'lag':250
        }
    ]
    t_1_factor_data = []  # T-N factor数据，格式如上
    t_1_factor_data_types = [] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_mfyc = database['xdb_researchreport_cs']
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            res = df_mfyc.groupby(['dt', 'Ticker']).apply(lambda x : x.tail(5)['FORECASTOR'].mean() / x['FORECASTOR'].mean()).to_frame(name=self.factor_name)
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = res[[self.factor_name]] # cs要返回df
            return database
