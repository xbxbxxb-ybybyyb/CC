import os
import time
import subprocess
import datetime as dt
from multiprocessing import Process
from overnight.utility import get_current_date


def minute_flag_check(date):
    path1 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_IC_cfg_and_mask.success'
    path2 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_IF_cfg_and_mask.success'
    path3 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_spot_minute.success'
    path4 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(
        date) + '_tick_to_minute_future_data_and_mask.success'
    path5 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_china_rates.success'
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(
        path4) and os.path.exists(path5)


def alter(file, old_str, new_str):
    """
    替换文件中的字符串
    :param file:文件名
    :param old_str:就字符串
    :param new_str:新字符串
    :return:
    """
    file_data = ""
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            if old_str in line:
                line = line.replace(old_str, new_str)
            file_data += line
    with open(file, "w", encoding="utf-8") as f:
        f.write(file_data)


def sub_run(python_file, python_location=None, process_type='subprocess'):
    # run python file in subprocess with cwd changed to file path
    file_path = os.path.dirname(os.path.abspath(python_file))
    if python_location is None:
        # use system python
        python_location = 'python3'
    if process_type == 'subprocess':
        return subprocess.run([python_location, python_file], shell=False, cwd=file_path)
    elif process_type == 'multiprocess':
        handler = Process(target=sub_run, kwargs={'python_file': python_file,
                                                  'python_location': python_location,
                                                  'process_type': 'subprocess'})
        handler.start()
        return handler
    else:
        raise AssertionError


if __name__ == '__main__':
    date = get_current_date()
    #    date = 20240802
    flag_root = '/data/group/800466/trade/overnight/flag/' + str(date) + '/'
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)
    flag_path_start = flag_root + str(date) + '_Diamond_factors_afterday.start'
    with open(flag_path_start, 'w') as file:
        pass

    print('------wait minute flag')
    while True:
        if minute_flag_check(date):
            break
        time.sleep(60)
    print('flag check finished!')

    t1 = dt.datetime.now()
    sub_run(os.path.join(os.path.dirname(__file__), 'update_Diamond_factors_helper.py'))
    alter(os.path.join(os.path.dirname(__file__), 'naming_config.py'), 'trade_stop_time = datetime.time(14, 49)',
          'trade_stop_time = datetime.time(14, 29)')
    sub_run(os.path.join(os.path.dirname(__file__), 'update_Diamond_factors_helper.py'))
    alter(os.path.join(os.path.dirname(__file__), 'naming_config.py'), 'trade_stop_time = datetime.time(14, 29)',
          'trade_stop_time = datetime.time(14, 49)')
    t2 = dt.datetime.now()

    flag_path_success = flag_root + str(date) + '_Diamond_factors_afterday.success'
    with open(flag_path_success, 'w') as file:
        pass


