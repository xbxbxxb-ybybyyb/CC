# 财务CS
class factor_demo_finance(BaseFactor):
    strategy_name = "neptune"
    factor_name = "demo_finance"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = ""  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时

    xdb_data = [{
        'name':'xdb_balancesheet_cs',
        'lag':4
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_balancesheet = database['xdb_balancesheet_cs']
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            res = (df_balancesheet['FIX_ASSETS'] + df_balancesheet['TOT_CUR_ASSETS']).groupby(['dt','Ticker']).apply(lambda x : x.tail(4).sum()).to_frame(name=self.factor_name)
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = res[[self.factor_name]] # cs要返回df
            return database
