import os
import shutil
import datetime as dt


def remove_file(old_path, new_path):
    print(old_path)
    print(new_path)
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    filelist = os.listdir(old_path) #列出该目录下的所有文件,listdir返回的文件列表是不包含路径的。
    print(filelist)
    for file in filelist:
        src = os.path.join(old_path, file)
        dst = os.path.join(new_path, file)
        print('src:', src)
        print('dst:', dst)
        shutil.move(src, dst)
    os.rmdir(old_path)
        
        
if __name__ == '__main__':
    today = dt.datetime.now().strftime('%Y%m%d')
#    today = '20240802'

    old_path_1 = os.path.join('/data/group/800466/trade/overnight/hot/', today)
    new_path_1 = os.path.join('/data/group/800466/trade/overnight/hot_arch0/', today)
    old_path_2 = os.path.join('/data/group/800466/trade/overnight/history/', today)
    new_path_2 = os.path.join('/data/group/800466/trade/overnight/history_arch0/', today)

    remove_file(old_path_1, new_path_1)
    remove_file(old_path_2, new_path_2)