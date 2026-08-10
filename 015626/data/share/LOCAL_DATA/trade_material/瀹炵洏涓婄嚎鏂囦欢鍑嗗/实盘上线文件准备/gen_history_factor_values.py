
# coding: utf-8

import pandas as pd
import sys
import os
import datetime
import json

#date_str = '2020-12-31'
#dir_name = "/data/user/015615/index_future/data_center/factor_data/minute_raw/IC/"

def gen_history_factor_values(date_str, factor_value_path):
    from_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    to_date = from_date + datetime.timedelta(1)
    to_date_str = datetime.datetime.strftime(to_date, "%Y-%m-%d")

    sp = date_str.split('-')
    file_name = ''
    for item in sp:
        file_name = file_name + item
    fw = open(file_name, "w")

    dir_name = factor_value_path
    for root, dirs, files in os.walk(dir_name):
        for f in files:
            full_name = os.path.join(root, f)
            factor_name = f[0:-3]
            data = pd.read_hdf(full_name)
            data = data.reset_index()
            col_set = set(data.columns)
            print('begin to get ' + factor_name + ' history value')
            if (col_set.__contains__('index')):
                dest_data = data[data['index']>date_str]
                dest_data = dest_data[dest_data['index'] < to_date_str]
                dest_data[factor_name] = dest_data[factor_name].astype('float64')
                factor_value_list = list(dest_data[factor_name].values)
                print(factor_name + ': ' + str(len(factor_value_list)))
                factor_dict = {}
                factor_dict['FactorName'] = factor_name
                factor_dict['Values'] = factor_value_list
                s = json.dumps(factor_dict)
                fw.write(s + '\n')
            elif col_set.__contains__("dt"):
                dest_data = data[data['dt']>date_str]
                dest_data = dest_data[dest_data['dt'] < to_date_str]
                dest_data[factor_name] = dest_data[factor_name].astype('float64')
                factor_value_list = list(dest_data[factor_name].values)
                print(factor_name + ': ' + str(len(factor_value_list)))
                factor_dict = {}
                factor_dict['FactorName'] = factor_name
                factor_dict['Values'] = factor_value_list
                s = json.dumps(factor_dict)
                fw.write(s + '\n')

    fw.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('should be 2 arguments, like 2020-12-31 /data/user/015615/index_future/data_center/factor_data/minute_raw/IC/')
    else:
        gen_history_factor_values(sys.argv[1], sys.argv[2])