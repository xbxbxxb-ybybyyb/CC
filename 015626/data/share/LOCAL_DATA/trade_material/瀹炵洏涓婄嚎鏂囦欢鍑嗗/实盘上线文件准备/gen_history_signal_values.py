
# coding: utf-8

import pandas as pd
import sys
import os
import datetime
import json

def gen_history_signal_values(date_str, signal_value_path):
    from_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    to_date = from_date + datetime.timedelta(1)
    to_date_str = datetime.datetime.strftime(to_date, "%Y-%m-%d")

    sp = date_str.split('-')
    file_name = ''
    for item in sp:
        file_name = file_name + item
    fw = open(file_name, "w")

    dir_name = signal_value_path
    for root, dirs, files in os.walk(dir_name):
        for f in files:
            full_name = os.path.join(root, f)
            print(full_name)
            data = pd.read_pickle(full_name)
            col_set = set(data.columns)

            dest_data = data[data.index>date_str]
            dest_data = dest_data[dest_data.index < to_date_str]
            for col in list(dest_data.columns):
                dest_data[col[:-5]] = dest_data[col].astype('float64')
                signal_value_list = list(dest_data[col].values)
                print(col + ': ' + str(len(signal_value_list)))
                factor_dict = {}
                factor_dict['SignalName'] = col[:-5]
                factor_dict['Values'] = signal_value_list
                s = json.dumps(factor_dict)
                fw.write(s + '\n')
    fw.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('should be 2 arguments, like 2020-12-31 /data/user/015615/index_future/data_center/factor_data/minute_raw/IC/')
    else:
        gen_history_signal_values(sys.argv[1], sys.argv[2])
