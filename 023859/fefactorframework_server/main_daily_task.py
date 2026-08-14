import xfactor.runner.DailyRunner as Runner
from settings import RunMode
import os

'''
    不限制因子个数，时间跨度为一天

示例场景：
    1、盘前数据准备
    2、每日因子更新
'''

'''
    $$$$$因子示例$$$

    factor_name_list: 因子名称列表
    start_date、end_date： 计算起止日期，可以为非交易日
    strategy： 计算相关策略。例：jupiter/europa: 计算jupiter和europa; saturn: 仅计算saturn。
    output_dir： 输出因子值路径。
    options: 相关额外设置，
            calc.num_cpus： 因子计算的并行度，若不设置或者设置为1，则将串行计算，可用来调试
            local_evaluator: 是否使用外部因子评估框架。若不使用，可不填或填空字符串;若使用，需要填写绝对路径，如/data/user/xxxx/.../xxx.py
            precheck: 是否执行预检测。True/False, 不填默认检测
            report: 是否输出报告。True/False, 不填默认不输出
            mode: 运行模式。默认为RunMode.research: 研究员研究模式，执行一段时间内某一因子库单个或多个因子的因子值计算及相关检测。其他模式本地不支持。
            
'''
factor_list = ['factor_qyh_new_combo2']
# for i in os.listdir(os.path.join(os.getcwd(), "factor")):
#     if ".py" in i:
#         factor_list.append(i.split(".py")[0])
Runner.run(factor_name_list=factor_list, start_date=20240119, end_date=20240119, strategy="europa",
                 output_dir="/data/group/800463/project/test/",
                 mode=RunMode.daily_update,
                 options={
                     "calc.num_cpus": 1})


