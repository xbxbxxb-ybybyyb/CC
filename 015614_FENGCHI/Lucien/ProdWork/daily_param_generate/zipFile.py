import pandas as pd
import datetime
import os
import zipfile
today = datetime.date.today()
date = today.strftime('%Y%m%d')
commonPath = r'/data/group/800463/xiely/daily/daily-param/'

def zip_ya(start_dir):
    start_dir = start_dir  # 要压缩的文件夹路径
    file_news = start_dir + '.zip'  # 压缩后文件夹的名字
    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)
    for dir_path, dir_names, file_names in os.walk(start_dir):
#        print(dir_path, dir_names, file_names)
        f_path = dir_path.replace(os.path.dirname(start_dir), '')  # 这一句很重要，不replace的话，就从根目录开始复制
        f_path = f_path and f_path + os.sep or ''  # 实现当前文件夹以及包含的所有文件的压缩
        for filename in file_names:
            z.write(os.path.join(dir_path, filename), f_path + filename)
    z.close()
    return file_news

zip_ya(commonPath+date+'-prod-O45-SZ-new')
zip_ya(commonPath+date+'-prod-O45-SH-new')
