import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import os

'''
    不限制因子个数，不限制时间跨度

示例场景：
    1、业务人员本地研究时，计算某个因子一段时间的因子值
    2、因子批量计算
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
            precheck: 是否执行预检测。True/False, 不填默认不检测
            report: 是否输出报告。True/False, 不填默认不输出
            mode: 运行模式。默认为RunMode.research: 研究员研究模式，执行一段时间内某一因子库单个或多个因子的因子值计算及相关检测。其他模式本地不支持。
            
            
    返回值：
        result：因子计算结果，格式为dict。key为因子名+计算对应策略名，value为计算周期所有因子值
            格式示例：result = {
                "factor_test_TTickab_jupiter": df
            }
        checker_result: 金工团队因子评估测试结果。key为因子名+计算对应策略名，value为计算周期该因子的评估结果
'''
factor_list = ['factor_qyh_new_combo2']
# for i in os.listdir(os.path.join(os.getcwd(), "factor")):
#     if ".py" in i:
#         factor_list.append(i.split(".py")[0])
result, checker_result = Runner.run(factor_name_list=factor_list, start_date=20160101, end_date=20160630, strategy="europa",
                 options={
                     "calc.num_cpus": 1,
                     "local_evaluator": "",
                     'precheck': True,
                     'report':True,
                     'mode': RunMode.research})

