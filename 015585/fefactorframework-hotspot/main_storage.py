import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import os
import datetime
import shutil
# para
strategy_list = ['Europa',
                 'Saturn',
                 'Metis',
                 'Mimas'] # 需要入库的策略名称
team_member_path = {'qyh':'/data/user/015585/01-因子挖掘/git-sell-factor/',
                    # 'sss':''
                    } # 团队成员共享的地址（根目录）
path_frame_factor = '/data/user/015585/fefactorframework-master/factor/' # 框架的factor文件夹地址

# 判断入库时间（上周四）
dt_now = datetime.datetime.now().strftime('%Y%m%d')
print('启动因子入库：{}'.format(dt_now))
weekday_now = datetime.date.today().weekday()
if weekday_now != 5:
    print('注意！本次运行时间非周六')
if weekday_now >= 3:
    last_thursday = datetime.date.today() - datetime.timedelta(days=weekday_now-3)
else:
    last_thursday = datetime.date.today() - datetime.timedelta(days=weekday_now + 7 - 3)
print('最近一个因子入库时间（周四）为{}'.format(last_thursday.strftime('%Y%m%d')))
# 按策略入库
res = {}
for strategy in strategy_list:
    print('{}策略因子开始入库'.format(strategy))
    factor_list = []
    # 清空factor文件夹
    for file in list(os.listdir(path_frame_factor)):
        if '.py' in file:
            os.remove(path_frame_factor + file)
    # 复制代码到factor文件夹
    for member,member_path in team_member_path.items():
        path = member_path + strategy + '/' + 'factor_' + last_thursday.strftime('%Y%m%d') + '/'
        if os.path.exists(path):
            for file in list(os.listdir(path)):
                if (".py" in file) & ('factor_' in file):
                    shutil.copy(path + file,path_frame_factor + file)
                # TODO:sss补充需要复制因子代码到别的位置的语句
    # 对factor文件夹内容生成待入库因子列表
    for i in os.listdir(os.path.join(os.getcwd(), "factor")):
        if (".py" in i) & ('factor_' in i):
            factor_list.append(i.split(".py")[0])
    # 入库
    # TODO:此处插入该策略的入库核心语句：Runner.run（xxxxx)
    res[strategy] = factor_list
    print('{}策略尝试入库{}个因子'.format(strategy,str(len(factor_list))))
print('所有策略入库完成')

