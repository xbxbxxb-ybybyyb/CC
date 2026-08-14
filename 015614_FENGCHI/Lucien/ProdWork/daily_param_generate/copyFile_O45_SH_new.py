import pandas
import os
import datetime
import shutil
today = datetime.date.today()
date = today.strftime('%Y%m%d')
target_jyy = r'/data/user/013551/forJYY-Strong/'+date + '-O45-SH-new'
os.mkdir(target_jyy)

source_sell = r'/data/group/800463/xiely/daily/daily-zuhe-prod-O45-SH-new/new-O45组合-SH-sell-%s.xlsx'%date
if os.path.exists(source_sell):
    target_sell = r'/data/user/013551/fotT0'
    shutil.copy(source_sell, target_sell)

source_t0_json = r'/data/group/800463/xiely/daily/daily-param/'+date+'_forT0_O45_SH_new.json'
target_t0_json = r'/data/user/013551/fotT0'
shutil.copy(source_t0_json, target_t0_json)

source_zuhe = r'/data/group/800463/xiely/daily/daily-zuhe-prod-O45-SH-new'
shutil.copytree(source_zuhe, target_jyy+'/daily-zuhe-prod-O45-SH-new')

source_param = r'/data/group/800463/xiely/daily/daily-param/'+date+'-prod-O45-SH-new.zip'
shutil.copy(source_param, target_jyy+'/'+date+'-prod-O45-SH-new.zip')