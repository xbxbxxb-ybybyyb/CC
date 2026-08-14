import os
import shutil

# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/021012/factorframework_neptune.git /data/user/023859/gitlab/skk/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/020412/factorframework_neptune.git /data/user/023859/gitlab/xbc/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/015585/factor_neptune_qyh.git /data/user/023859/gitlab/qyh/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/022325/factorframework_neptune.git /data/user/023859/gitlab/zwh/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/015614/factorframework_neptune.git /data/user/023859/gitlab/fc/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/013550/factorframework_neptune.git /data/user/023859/gitlab/wj/')
# os.system('git clone http://023859:\TSQbpf#551683@168.7.21.84/013551/neptune_factordevelop.git /data/user/023859/gitlab/xly/')

strategy_list = ['Neptune'] # 需要入库的策略名称

path_frame_factor = '/data/user/023859/fefactorframework_server/factor_lib/' # 框架的factor文件夹地址
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
for last_thursday in ['20250320','20250327','20250403','20250410','20250417','20250424','20250508','20250515','20250522','20250529',\
                      '20250605','20250612','20250619','20250626','20250703','20250710','20250717']:
    for member, member_path in team_member_path.items():
        path = member_path + 'NewNeptune' + '/' + 'factor_' + last_thursday + '/'
        if os.path.exists(path):
            for file in list(os.listdir(path)):
                if (".py" in file) & ('factor_' in file):
                    shutil.copy(path + file,
                                path_frame_factor + 'neptune' + '/' + 'factor_' + last_thursday + '/' + file)

factor_code_path = '/data/user/023859/fefactorframework_server/factor_lib/neptune/'
path_frame_train_factor_code = '/data/user/023859/fefactorframework_train/factor'

for root, _, files in os.walk(factor_code_path):
    for file in files:
        if (file.endswith('.py')) & ('factor_' in file):
            shutil.copy(os.path.join(root,file), os.path.join(path_frame_train_factor_code,file))