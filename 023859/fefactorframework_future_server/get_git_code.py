# -*- coding: gbk -*-
import os
import shutil
import datetime

# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/021012/factorframework_neptune.git /data/user/023859/gitlab/skk/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/020412/factorframework_neptune.git /data/user/023859/gitlab/xbc/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/015585/factor_neptune_qyh.git /data/user/023859/gitlab/qyh/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/022325/factorframework_neptune.git /data/user/023859/gitlab/zwh/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/015614/factorframework_neptune.git /data/user/023859/gitlab/fc/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/013550/factorframework_neptune.git /data/user/023859/gitlab/wj/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/013551/neptune_factordevelop.git /data/user/023859/gitlab/xly/')

path_frame_factor = '/data/user/023859/fefactorframework_future_server/factor_lib' # 框架的factor文件夹地址
team_member_path = {
                'wj':'/data/user/023859/gitlab/wj/',
                'fc':'/data/user/023859/gitlab/fc/',
                'zwh':'/data/user/023859/gitlab/zwh/',
                'qyh':'/data/user/023859/gitlab/qyh/',
                'skk':'/data/user/023859/gitlab/skk/',
                'xbc':'/data/user/023859/gitlab/xbc/',
                'xly':'/data/user/023859/gitlab/xly/',
                }

ori_path = os.getcwd()
for path in team_member_path.values():
    os.chdir(path)
    os.system('git pull')

os.chdir(ori_path)

# 判断入库时间（上周四）
today=datetime.date.today()
today_weekday=today.weekday()
if today_weekday>=3:
    last_thursday=today-datetime.timedelta(days=today_weekday-3)
else:
    last_thursday = today - datetime.timedelta(days=today_weekday +7- 3)
last_thursday=last_thursday.strftime('%Y%m%d')
print('入库时间为{}'.format(last_thursday))

os.makedirs(os.path.join(path_frame_factor,f'factor_{last_thursday}'),exist_ok=True)

# 复制代码到factor文件夹
for member,member_path in team_member_path.items():
    path = member_path + 'Future' + '/' + 'factor_' + last_thursday + '/'
    if os.path.exists(path):
        for file in list(os.listdir(path)):
            if (".py" in file) & ('factor_' in file):
                shutil.copy(path + file,path_frame_factor + '/' + 'factor_' + last_thursday + '/' + file)
            if (".xlsx" in file) :
                shutil.copy(path + file,path_frame_factor + '/' + 'factor_' + last_thursday + '/' + file)

