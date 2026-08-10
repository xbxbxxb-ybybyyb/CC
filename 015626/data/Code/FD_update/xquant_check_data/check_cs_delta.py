# import pandas as pd
# import os

# root_cs = '/data/group/800080/pair/DATA/cs_delta/'
# root_xq = '/data/group/800080/pair/DATA/Xquant_cs_delta/'

# for dir_name in os.listdir(root_cs):
    # for csv_name in os.listdir(os.path.join(root_cs, dir_name)):
        # cs_path = os.path.join(root_cs, dir_name, csv_name)
        # xq_path = os.path.join(root_xq, dir_name, csv_name)
        
import pandas as pd
import pickle
import datetime
from QuantFramework import HDFSFileHandler
from xquant.xqutils.xqfile import HDFSFile
from xquant.pyfile import Pyfile
from multifactor.IO import IO
import os

df_all = pd.DataFrame(columns = ['dir','time','error_rate'])
count = 0
root_cs = '/data/group/800080/pair/DATA/cs_delta/'
root_xq = '/data/group/800080/pair/DATA/cs_delta_bak/'
cs_isna = False
xq_isna = False

root_path = '/data/user/015626/check_data/cs_delta/'

if not os.path.exists(root_path):
    os.makedirs(root_path)

for dir_name in os.listdir(root_cs):
    print(dir_name + '*' * 20)
    
# dir_name = 'grps'        
    for csv_name in os.listdir(os.path.join(root_cs, dir_name)):
        print(dir_name, csv_name)
        
        time = csv_name[:8]
        try:
            if int(time) < 20090101 or int (time) > 20180701:
                continue
        except Exception as e:
            print(e)
            continue
        cs_path = os.path.join(root_cs, dir_name, csv_name)
        xq_path = os.path.join(root_xq, dir_name, csv_name)
        
        try:
            df_cs = pd.read_csv(cs_path)
        except Exception as e:
            cs_isna = True
            print(e)
            
        try:
            df_xq = pd.read_csv(xq_path)
        except Exception as e:
            xq_isna = True
            print(e)
            
        if cs_isna & xq_isna:
            df_all.loc[count] = [dir_name, time, 'cs_bak_nan']
            count = count + 1
            cs_isna = False
            xq_isna = False
            continue
        elif xq_isna:
            df_all.loc[count] = [dir_name, time, 'bak_nan']
            count = count + 1
            cs_isna = False
            xq_isna = False
            continue
        elif cs_isna:
            df_all.loc[count] = [dir_name, time, 'cs_nan']
            count = count + 1
            cs_isna = False
            xq_isna = False
            continue
            
        cs_columns_name = ['Ticker','dt',dir_name]
        xq_columns_name = ['Ticker','dt',dir_name + '_bak']
        df_cs.columns = cs_columns_name
        df_xq.columns = xq_columns_name

        df = pd.merge(df_cs,df_xq,how = 'outer')
        df.fillna('NAN',inplace=True)
        
        df_error = df[df[dir_name] != df[dir_name + '_bak']]
        if len(df_error) > 0:
            dir_path = os.path.join(root_path, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            df_error.to_csv(dir_path + '/' + dir_name + '_' + time + '.csv')
        
        df_all.loc[count] = [dir_name, time, len(df_error)/len(df)]
        print(len(df_error)/len(df))
        count = count + 1

print(df_all)
df_all.to_csv(root_path + 'total_error.csv')
