import pandas as pd
import os
import shutil
import datetime

today=datetime.date.today()
today_weekday=today.weekday()
if today_weekday>=3:
    last_thursday=today-datetime.timedelta(days=today_weekday-3)
else:
    last_thursday = today - datetime.timedelta(days=today_weekday +7- 3)
last_thursday=last_thursday.strftime('%Y%m%d')
print('入库时间为{}'.format(last_thursday))

all_factor_inf_path = '/data/user/023859/factor_zooF/all_factor_inf.xlsx'

all_factor_inf_list = [pd.read_excel(all_factor_inf_path)]
update_dir = os.path.join(os.path.dirname(__file__),'factor_lib',f'factor_{last_thursday}')
for file in list(os.listdir(update_dir)):
    if (".xlsx" in file) :
        all_factor_inf_list.append(pd.read_excel(os.path.join(update_dir,file)))

all_factor_inf_update = pd.concat(all_factor_inf_list,sort=False)
all_factor_inf_update.to_excel(all_factor_inf_path, index=False)
