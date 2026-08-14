import xfactor.runner.BasicRunner as Runner
from settings import RunMode
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_qyh_mercury_test_ttick_1(BaseFactor):
    strategy_name = "mercury"
    factor_name = "qyh_mercury_test_ttick_1"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "xxxx" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-挂单价格激进度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['TTickab919']
    xdb_data = []

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
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
            tick_df = database['TTickab919']
            res = tick_df['Buy1Price'].mean()
            factor_dict = {self.factor_name: res}
            return pd.Series(factor_dict)
factor_list = []
strategy = 'mercury'
class_list_out = [factor_qyh_mercury_test_ttick_1]
res, check_res = Runner.run(start_date=20190101, end_date=20191231, strategy=strategy,
                 output_dir="/data/user/015585/20240116_frame/", # 结果的输出路径，包括回测报告等
                 options={
                     "calc.num_cpus": 2,
                     "local_evaluator": "",
                     'precheck': False,
                     "factor_test": True,
                     'report':False,
                     'mode': RunMode.research},class_list_out=class_list_out)
for i in factor_list:
    print(i)
    print('score:', check_res[i[7:] + '_' + strategy].result_dic['check_score_res'].loc['score','tot_score'])
    print('IC:',check_res[i[7:] + '_' + strategy].result_dic['corr_sta'].loc['corr_tot', 'value'])
    print('库内高相关因子：', check_res[i[7:] + '_' + strategy].result_dic['factor_corr_summary'])
# 因子预检测
# import pandas as pd
# pre_check = pd.read_pickle('/data/user/015585/20240116_frame/precheck/saturn/result/qyh_newsat_20240411_11.pkl')
# print(pre_check)


