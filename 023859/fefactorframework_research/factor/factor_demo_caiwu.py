
# 单独财务数据，非CS
class factor_qyh_finance_new_test1(BaseFactor):
    strategy_name = "neptune"
    factor_name = "qyh_finance_new_test1"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    xdb_data = [{
        'name':'xdb_balancesheet',
        'lag':4
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_balancesheet = database['xdb_balancesheet']
            df_balancesheet = df_balancesheet[df_balancesheet['ANN_DT']
                                                  .apply(int) >= df_balancesheet['S_INFO_LISTDATE'].apply(int)]
            res = (df_balancesheet['FIX_ASSETS'] + df_balancesheet['TOT_CUR_ASSETS']).tail(4).sum()
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
            return database