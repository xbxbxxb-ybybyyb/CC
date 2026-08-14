import os
import shutil
import datetime
from loguru import logger
from settings import RunMode
from xfactor.FactorUtil import update_xlsx, get_factor_class
import xfactor.runner.BasicRunner as Runner

#参数设置
# strategy_list = ['Europa','Saturn','Metis','Mimas'] # 需要入库的策略名称
strategy_list = ['Neptune'] # 需要入库的策略名称

path_frame_factor = '/data/user/023859/fefactorframework_server/factor_lib/' # 框架的factor文件夹地址

# team_member_path = {'xly':'/data/user/018107/gitlab/xly/',
#                 'skk':'/data/user/018107/gitlab/skk/',
#                 'fc':'/data/user/018107/gitlab/fc/',
#                 'zwh':'/data/user/018107/gitlab/zwh/',
#                 'qyh':'/data/user/018107/gitlab/qyh/',
#                 'wj':'/data/user/018107/gitlab/wj/',
#                 'xbc':'/data/user/018107/gitlab/xbc/'}

# 判断入库时间（上周四）
today=datetime.date.today()
today_weekday=today.weekday()
if today_weekday>=3:
    last_thursday=today-datetime.timedelta(days=today_weekday-3)
else:
    last_thursday = today - datetime.timedelta(days=today_weekday +7- 3)
last_thursday=last_thursday.strftime('%Y%m%d')
#last_thursday='20240307'
print('入库时间为{}'.format(last_thursday))

# 按策略入库
res = {}
module_base_dir = "factor_lib"
skip_update_xslx = True

for strategy in strategy_list:
    print('{}策略因子开始入库'.format(strategy))
    factor_list = []
    # 清空factor文件夹
    # for file in list(os.listdir(path_frame_factor)):
    #     if '.py' in file:
    #         os.remove(path_frame_factor + file)
    # # 复制代码到factor文件夹
    # for member,member_path in team_member_path.items():
    #     path = member_path +'New'+ strategy + '/' + 'factor_' + last_thursday + '/'
    #     if os.path.exists(path):
    #         for file in list(os.listdir(path)):
    #             if (".py" in file) & ('factor_' in file):
    #                 shutil.copy(path + file,path_frame_factor + file)
    #                 # TODO:需要补充复制到策略名/factor_日期/的代码
    #  #加到excel
    #
    # if not skip_update_xslx:
    #     new_factors_local_dir = os.path.join(module_base_dir, strategy, 'factor_' + str(int(last_thursday)))
    #     new_factors_dir = os.path.join(os.getcwd(), new_factors_local_dir)
    #     factor_list = [i[:-3] for i in os.listdir(new_factors_dir) if i.endswith(".py")]
    #     kls_list = [get_factor_class(new_factors_local_dir, i) for i in factor_list]
    #     update_xlsx(strategy, kls_list, last_thursday)


    # 筛选df后
    # filtered_df = pd.DataFrame()

    # for index, inf in filtered_df.iterrows():
    #     if strategy.lower() in ["saturn", "sell", "mimas"]:
    #         factor_name, factor_date = inf['factor_name'], inf['提交时间']
    #     elif strategy.lower() in ["europa", "jupiter", "metis"]:
    #         factor_name, factor_date = inf['factor_name'], inf['factor_date']
    #     else:
    #         raise Exception("策略名不在规定范围内！input_strategy={}".format(strategy))

    # module_path = os.path.join(module_base_dir, strategy.lower(), 'factor_'+str(int(factor_date)))
    for i in range(10,11):
        factor_list.append({
            "module_path": 'factor_lib/neptune/factor_20250828',
            "factor_name": 'factor_demo_md'
        }
        )

    # 入库
    if len(factor_list) > 0:
        print(strategy,len(factor_list),factor_list)
        Runner.run(factor_name_list=factor_list, start_date=20170110, end_date=20211231,
                   strategy=strategy.lower(), upload_date=last_thursday,
                   mode=RunMode.factor_warehouse,
                   options={
                       "calc.num_cpus": 24,
                       'precheck': True,
                       'factor_test':True,
                       'report': False,
                       'warehouse': False,
                       'override': True
                   })
        res[strategy] = factor_list
        print('{}策略尝试入库{}个因子'.format(strategy,str(len(factor_list))))
print('所有策略入库完成')