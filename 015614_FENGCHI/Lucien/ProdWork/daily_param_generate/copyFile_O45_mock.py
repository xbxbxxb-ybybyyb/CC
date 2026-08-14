import pandas
import os
import datetime
import shutil
today = datetime.date.today()
date = today.strftime('%Y%m%d')
target_jyy = r'/data/user/013551/forJYY-Strong/'+date + '-O45-mock'
os.mkdir(target_jyy)

source_zuhe = r'/data/group/800463/xiely/daily/daily-zuhe-prod-O45-mock'
shutil.copytree(source_zuhe, target_jyy+'/daily-zuhe-prod-O45-mock')

source_param = r'/data/group/800463/xiely/daily/daily-param/'+date+'-prod-O45-mock.zip'
shutil.copy(source_param, target_jyy+'/'+date+'-prod-O45-mock.zip')