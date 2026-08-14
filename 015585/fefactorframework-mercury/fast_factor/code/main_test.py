import xfactor.runner.BasicRunner as Runner
from settings import RunMode
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
from xfactor.function_factor import *
from itertools import product
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_newsat_test_1(BaseFactor):
    strategy_name = "saturn/sell"
    factor_name = "qyh_newsat_test_1"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "和过去15s均价距离的偏度" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "价格波动" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    xdb_data = [
        {
       'name': 'xdb_tickfull', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s,xdb_tickex
       'lag': 3 # 回看日期，N为往前回看1~N天
    },
        {
       'name': 'xdb_tick1s', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s,xdb_tickex
       'lag': 1 # 回看日期，N为往前回看1~N天
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        tick_df1 = database['xdb_tickfull']
        tick_df2 = database['xdb_tick1s']
        res = tick_df1['LastPx'].mean() - tick_df2['LastPx'].mean()
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
        return database
    def prepare_T_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return database
        else:
            return database
    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res1 = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res1}
            return pd.Series(factor_dict)

strategy = 'saturn'
list_class = [factor_qyh_newsat_test_1]
res, check_res = Runner.run(start_date=20160101, end_date=20191231, strategy=strategy,
                 output_dir= '/data/user/015585/20240116_frame/',
                 options={
                     "calc.num_cpus": 15,
                     "local_evaluator": "",
                     'precheck': False,
                     "factor_test": True,
                     'report':False,
                     'mode': RunMode.research},class_list_out=list_class)
for factor_class in list_class:
    i = factor_class.factor_name
    print(i)
    print('score:', check_res[i + '_' + strategy].result_dic['check_score_res'].loc['score','tot_score'])
    print('IC:',check_res[i + '_' + strategy].result_dic['corr_sta'].loc['corr_tot', 'value'])


