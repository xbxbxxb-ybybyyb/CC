# coding: utf-8
# Author：fengchi863
# Date ：2023/3/16 11:05

import datetime
import os
import shutil
import zipfile

date = datetime.date.today().strftime('%Y%m%d')
# date = '20230805'


def unzip_file(fp):
    with zipfile.ZipFile(fp, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(fp))


log_commonPath = r'/data/group/800463/sim-lite-log/%s/' % date
write_log_path = r'/data/group/800463/xiely/日内强势股/log/'

for filename in os.listdir(log_commonPath):
    if filename.endswith('.zip'):
        print(filename)
        date_actual = filename.split('-')[1]
        unzip_file(log_commonPath + filename)
        for filename in os.listdir(log_commonPath):
            if '.log.gz' in filename:
                shutil.copy(log_commonPath + filename, write_log_path + r'StrongStrategy-%s-%s-%s-%s-%s.log.gz' % (date_actual[:4], date_actual[4:6], date_actual[6:8], 'uat_lite', date))
                os.remove(log_commonPath + filename)
                os.remove(log_commonPath + 'StrongStrategy-%s.zip' % date_actual)
